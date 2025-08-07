"""ZIP包导入器实现"""
import zipfile
import io
import json
import datetime  # 添加这一行
from typing import List, Dict, Any, Tuple, Union
from .base_importer import BaseImporter, ImportError, ImportResult, ImportStatus
from .csv_importer import CSVImporter
from .json_importer import JSONImporter
from .excel_importer import ExcelImporter


class ZipImporter(BaseImporter):
    """ZIP包导入器，支持批量导入多种格式文件"""
    
    def __init__(self, assessment_type: str = 'autism'):
        super().__init__(assessment_type)
        self.supported_extensions = {
            '.csv': CSVImporter,
            '.json': JSONImporter,
            '.xlsx': ExcelImporter,
            '.xls': ExcelImporter,
            '.txt': None  # 文本文件特殊处理
        }
    
    def parse_file(self, file_content: bytes, **kwargs) -> List[Dict[str, Any]]:
        """
        解析ZIP文件内容
        
        Args:
            file_content: ZIP文件字节内容
            **kwargs: 额外参数
                
        Returns:
            解析后的记录列表
        """
        all_records = []
        metadata = {
            'files_processed': [],
            'files_skipped': [],
            'file_errors': {}
        }
        
        try:
            with zipfile.ZipFile(io.BytesIO(file_content), 'r') as zip_file:
                # 获取所有文件列表
                file_list = zip_file.namelist()
                
                # 查找并读取元数据文件
                meta_file = self._find_metadata_file(file_list)
                if meta_file:
                    meta_content = zip_file.read(meta_file)
                    metadata['package_metadata'] = json.loads(meta_content.decode('utf-8'))
                
                # 处理每个文件
                for file_name in file_list:
                    # 跳过目录和元数据文件
                    if file_name.endswith('/') or file_name == meta_file:
                        continue
                    
                    # 跳过隐藏文件和系统文件
                    if file_name.startswith('.') or file_name.startswith('__'):
                        metadata['files_skipped'].append(file_name)
                        continue
                    
                    # 获取文件扩展名
                    ext = self._get_file_extension(file_name).lower()
                    
                    if ext not in self.supported_extensions:
                        metadata['files_skipped'].append(file_name)
                        continue
                    
                    try:
                        # 读取文件内容
                        file_content = zip_file.read(file_name)
                        
                        # 处理不同类型的文件
                        if ext == '.txt':
                            # 文本文件可能是对话记录或观察记录
                            records = self._parse_text_file(file_content, file_name)
                        else:
                            # 使用对应的导入器
                            importer_class = self.supported_extensions[ext]
                            importer = importer_class(self.assessment_type)
                            records = importer.parse_file(file_content)
                        
                        # 添加文件来源信息
                        for record in records:
                            record['_source_file'] = file_name
                            record['_source_type'] = 'zip_archive'
                        
                        all_records.extend(records)
                        metadata['files_processed'].append(file_name)
                        
                    except Exception as e:
                        metadata['file_errors'][file_name] = str(e)
                
        except zipfile.BadZipFile:
            raise ImportError("无效的ZIP文件")
        except Exception as e:
            raise ImportError(f"ZIP文件处理错误: {str(e)}")
        
        # 将元数据存储到记录中
        if all_records:
            all_records[0]['_import_metadata'] = metadata
        
        return all_records
    
    def validate_structure(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证ZIP包中的数据结构
        
        Args:
            data: 数据列表
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        if not data:
            errors.append("ZIP包中无有效数据")
            return False, errors
        
        # 提取元数据
        metadata = data[0].get('_import_metadata', {})
        
        # 报告处理情况
        files_processed = metadata.get('files_processed', [])
        files_skipped = metadata.get('files_skipped', [])
        file_errors = metadata.get('file_errors', {})
        
        if not files_processed:
            errors.append("ZIP包中没有找到可处理的文件")
        
        if file_errors:
            for file_name, error in file_errors.items():
                errors.append(f"文件 '{file_name}' 处理失败: {error}")
        
        # 按文件来源分组验证
        files_data = {}
        for record in data:
            source_file = record.get('_source_file', 'unknown')
            if source_file not in files_data:
                files_data[source_file] = []
            files_data[source_file].append(record)
        
        # 验证每个文件的数据基本结构
        for file_name, file_records in files_data.items():
            if len(file_records) == 0:
                errors.append(f"文件 '{file_name}' 无有效记录")
        
        return len(errors) == 0, errors
    
    def import_data(self, file_content: Any, **kwargs) -> ImportResult:
        """
        重写导入方法以提供更详细的结果
        
        Args:
            file_content: ZIP文件内容
            **kwargs: 额外参数
            
        Returns:
            ImportResult: 导入结果
        """
        result = super().import_data(file_content, **kwargs)
        
        # 添加ZIP特定的元数据
        if result.records:
            metadata = result.records[0].get('_import_metadata', {})
            result.metadata.update({
                'package_info': metadata.get('package_metadata', {}),
                'files_processed': metadata.get('files_processed', []),
                'files_skipped': metadata.get('files_skipped', []),
                'file_errors': metadata.get('file_errors', {})
            })
            
            # 清理内部元数据
            for record in result.records:
                record.pop('_import_metadata', None)
                record.pop('_source_file', None)
                record.pop('_source_type', None)
        
        return result
    
    def _find_metadata_file(self, file_list: List[str]) -> str:
        """查找元数据文件"""
        metadata_names = ['metadata.json', 'meta.json', 'info.json', 'package.json']
        
        for file_name in file_list:
            if any(file_name.endswith(meta) for meta in metadata_names):
                return file_name
        
        return None
    
    def _get_file_extension(self, file_name: str) -> str:
        """获取文件扩展名"""
        parts = file_name.lower().split('.')
        if len(parts) > 1:
            return '.' + parts[-1]
        return ''
    
    def _parse_text_file(self, content: bytes, file_name: str) -> List[Dict[str, Any]]:
        """解析文本文件（对话记录或观察记录）"""
        try:
            text = content.decode('utf-8')
            lines = text.strip().split('\n')
            
            # 判断文件类型
            if '对话记录' in file_name or 'conversation' in file_name.lower():
                return self._parse_conversation_text(lines)
            elif '观察记录' in file_name or 'observation' in file_name.lower():
                return self._parse_observation_text(lines)
            else:
                # 尝试自动识别
                if any('角色:' in line or 'Role:' in line for line in lines):
                    return self._parse_conversation_text(lines)
                else:
                    return self._parse_observation_text(lines)
                    
        except Exception as e:
            raise ImportError(f"文本文件解析错误: {str(e)}")
    
    def _parse_conversation_text(self, lines: List[str]) -> List[Dict[str, Any]]:
        """解析对话记录文本"""
        records = []
        current_conversation = None
        current_messages = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别对话开始标记
            if line.startswith('===') or line.startswith('---'):
                # 保存上一个对话
                if current_conversation and current_messages:
                    current_conversation['messages'] = current_messages
                    records.append(current_conversation)
                
                # 开始新对话
                current_conversation = {
                    'type': 'conversation',
                    'timestamp': self._extract_timestamp_from_line(line)
                }
                current_messages = []
            
            # 识别对话内容
            elif ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    role = parts[0].strip()
                    content = parts[1].strip()
                    
                    if role in ['用户', 'User', '治疗师', 'Therapist', 
                              '观察者', 'Observer', '儿童', 'Child']:
                        current_messages.append({
                            'role': role,
                            'content': content
                        })
        
        # 保存最后一个对话
        if current_conversation and current_messages:
            current_conversation['messages'] = current_messages
            records.append(current_conversation)
        
        return records
    
    def _parse_observation_text(self, lines: List[str]) -> List[Dict[str, Any]]:
        """解析观察记录文本"""
        records = []
        current_record = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别记录开始
            if line.startswith('观察记录') or line.startswith('Observation'):
                if current_record:
                    records.append(current_record)
                
                current_record = {
                    'type': 'observation',
                    'timestamp': self._extract_timestamp_from_line(line)
                }
            
            # 解析字段
            elif ':' in line and current_record:
                field, value = line.split(':', 1)
                field = field.strip()
                value = value.strip()
                
                # 映射字段名
                field_mapping = {
                    '情境': 'scene',
                    '活动': 'activity',
                    '触发': 'trigger',
                    '行为': 'behavior',
                    '反应': 'response',
                    '备注': 'notes',
                    'Scene': 'scene',
                    'Activity': 'activity',
                    'Trigger': 'trigger',
                    'Behavior': 'behavior',
                    'Response': 'response',
                    'Notes': 'notes'
                }
                
                if field in field_mapping:
                    current_record[field_mapping[field]] = value
        
        # 保存最后一条记录
        if current_record:
            records.append(current_record)
        
        return records
    
    def _extract_timestamp_from_line(self, line: str) -> datetime.datetime:
        """从文本行中提取时间戳"""
        # 尝试多种日期格式
        import re
        
        # 查找日期模式
        date_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp = self._parse_timestamp(match.group())
                if timestamp:
                    return timestamp
        
        return datetime.datetime.now()