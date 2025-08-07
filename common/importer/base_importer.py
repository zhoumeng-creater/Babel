"""基础导入器类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import datetime
from dataclasses import dataclass, field
from enum import Enum


class ImportStatus(Enum):
    """导入状态枚举"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ImportError(Exception):
    """导入错误异常类"""
    pass


@dataclass
class ImportResult:
    """导入结果数据类"""
    status: ImportStatus
    imported_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    total_count: int = 0
    records: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_count == 0:
            return 0.0
        return self.imported_count / self.total_count
    
    def add_error(self, row_num: int, field: str, message: str):
        """添加错误信息"""
        self.errors.append({
            'row': row_num,
            'field': field,
            'message': message,
            'timestamp': datetime.datetime.now()
        })
    
    def add_warning(self, message: str):
        """添加警告信息"""
        self.warnings.append(message)


class BaseImporter(ABC):
    """基础导入器抽象类"""
    
    def __init__(self, assessment_type: str = 'autism'):
        """
        初始化导入器
        
        Args:
            assessment_type: 评估类型 ('autism' 或 'children')
        """
        self.assessment_type = assessment_type
        self.batch_size = 100  # 批处理大小
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
    @abstractmethod
    def parse_file(self, file_content: Any, **kwargs) -> List[Dict[str, Any]]:
        """
        解析文件内容
        
        Args:
            file_content: 文件内容
            **kwargs: 额外参数
            
        Returns:
            解析后的记录列表
        """
        pass
    
    @abstractmethod
    def validate_structure(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据结构
        
        Args:
            data: 数据列表
            
        Returns:
            (是否有效, 错误信息列表)
        """
        pass
    
    def import_data(self, file_content: Any, **kwargs) -> ImportResult:
        """
        导入数据的主方法
        
        Args:
            file_content: 文件内容
            **kwargs: 额外参数
            
        Returns:
            ImportResult: 导入结果
        """
        result = ImportResult(status=ImportStatus.FAILED)
        
        try:
            # 1. 解析文件
            raw_data = self.parse_file(file_content, **kwargs)
            result.total_count = len(raw_data)
            
            if not raw_data:
                result.add_error(0, 'file', '文件为空或无有效数据')
                return result
            
            # 2. 验证结构
            is_valid, structure_errors = self.validate_structure(raw_data)
            if not is_valid:
                for error in structure_errors:
                    result.add_error(0, 'structure', error)
                return result
            
            # 3. 批量处理数据
            for i in range(0, len(raw_data), self.batch_size):
                batch = raw_data[i:i + self.batch_size]
                batch_result = self._process_batch(batch, i)
                
                result.imported_count += batch_result['imported']
                result.failed_count += batch_result['failed']
                result.skipped_count += batch_result['skipped']
                result.records.extend(batch_result['records'])
                
                # 合并错误信息
                for error in batch_result.get('errors', []):
                    result.add_error(
                        error['row'] + i,
                        error['field'],
                        error['message']
                    )
            
            # 4. 设置最终状态
            if result.failed_count == 0:
                result.status = ImportStatus.SUCCESS
            elif result.imported_count > 0:
                result.status = ImportStatus.PARTIAL
                result.add_warning(
                    f"部分导入成功: {result.imported_count}/{result.total_count}"
                )
            
        except Exception as e:
            result.add_error(0, 'system', f'导入失败: {str(e)}')
            result.status = ImportStatus.FAILED
        
        return result
    
    def _process_batch(self, batch: List[Dict[str, Any]], start_idx: int) -> Dict[str, Any]:
        """
        处理一批数据
        
        Args:
            batch: 数据批次
            start_idx: 起始索引
            
        Returns:
            处理结果字典
        """
        batch_result = {
            'imported': 0,
            'failed': 0,
            'skipped': 0,
            'records': [],
            'errors': []
        }
        
        for idx, record in enumerate(batch):
            try:
                # 转换数据格式
                converted_record = self._convert_record(record)
                
                # 验证业务逻辑
                if self._validate_record(converted_record):
                    # 检查重复
                    if not self._is_duplicate(converted_record):
                        batch_result['records'].append(converted_record)
                        batch_result['imported'] += 1
                    else:
                        batch_result['skipped'] += 1
                else:
                    batch_result['failed'] += 1
                    batch_result['errors'].append({
                        'row': idx,
                        'field': 'validation',
                        'message': '数据验证失败'
                    })
                    
            except Exception as e:
                batch_result['failed'] += 1
                batch_result['errors'].append({
                    'row': idx,
                    'field': 'processing',
                    'message': str(e)
                })
        
        return batch_result
    
    def _convert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换单条记录格式
        
        Args:
            record: 原始记录
            
        Returns:
            转换后的记录
        """
        # 基础转换，子类可以覆盖
        converted = {
            'timestamp': self._parse_timestamp(record.get('timestamp', '')),
            'assessment_type': self.assessment_type
        }
        
        # 保留原始数据
        converted.update(record)
        
        return converted
    
    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        验证单条记录
        
        Args:
            record: 记录数据
            
        Returns:
            是否有效
        """
        # 基础验证，子类可以扩展
        required_fields = self._get_required_fields()
        for field in required_fields:
            if field not in record or record[field] is None:
                return False
        return True
    
    def _is_duplicate(self, record: Dict[str, Any]) -> bool:
        """
        检查是否重复记录
        
        Args:
            record: 记录数据
            
        Returns:
            是否重复
        """
        # 基础实现返回False，子类可以实现具体逻辑
        return False
    
    def _get_required_fields(self) -> List[str]:
        """
        获取必需字段列表
        
        Returns:
            必需字段列表
        """
        # 基础必需字段，子类可以扩展
        return ['timestamp']
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime.datetime]:
        """
        解析时间戳字符串
        
        Args:
            timestamp_str: 时间戳字符串
            
        Returns:
            datetime对象或None
        """
        if not timestamp_str:
            return datetime.datetime.now()
        
        # 尝试多种日期格式
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None