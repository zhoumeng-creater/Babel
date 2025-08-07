"""Excel导入器实现"""
import pandas as pd
import io
from typing import List, Dict, Any, Tuple, Union, Optional
from .base_importer import BaseImporter, ImportError


class ExcelImporter(BaseImporter):
    """Excel文件导入器"""
    
    def __init__(self, assessment_type: str = 'autism'):
        super().__init__(assessment_type)
        self.sheet_mappings = {
            # 孤独症相关工作表
            '评估数据': 'autism_assessment',
            '临床评估': 'autism_assessment',
            'ABC评估': 'abc_assessment',
            'DSM5评估': 'dsm5_assessment',
            '统一评估': 'unified_assessment',
            '对话记录': 'conversations',
            '行为观察': 'observations',
            
            # 儿童发展相关工作表
            '发展评估': 'children_development',
            '观察记录': 'children_observations',
            '发展数据': 'children_data'
        }
    
    def parse_file(self, file_content: Union[bytes, io.IOBase], **kwargs) -> List[Dict[str, Any]]:
        """
        解析Excel文件内容
        
        Args:
            file_content: 文件内容（字节或文件对象）
            **kwargs: 额外参数
                - sheet_name: 指定工作表名称
                - merge_sheets: 是否合并多个工作表
                
        Returns:
            解析后的记录列表
        """
        try:
            # 读取Excel文件
            if isinstance(file_content, bytes):
                excel_file = pd.ExcelFile(io.BytesIO(file_content))
            else:
                excel_file = pd.ExcelFile(file_content)
            
            # 获取所有工作表名称
            sheet_names = excel_file.sheet_names
            
            # 确定要读取的工作表
            target_sheet = kwargs.get('sheet_name', None)
            merge_sheets = kwargs.get('merge_sheets', False)
            
            if target_sheet:
                # 指定了特定工作表
                if target_sheet not in sheet_names:
                    raise ImportError(f"工作表 '{target_sheet}' 不存在")
                sheets_to_read = [target_sheet]
            else:
                # 根据评估类型自动选择工作表
                sheets_to_read = self._select_sheets(sheet_names)
            
            # 读取数据
            all_records = []
            
            for sheet_name in sheets_to_read:
                df = pd.read_excel(
                    excel_file,
                    sheet_name=sheet_name,
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None']
                )
                
                # 清理列名
                df.columns = df.columns.str.strip()
                
                # 删除完全空的行
                df = df.dropna(how='all')
                
                # 转换为记录
                records = df.to_dict('records')
                
                # 添加来源信息
                for record in records:
                    record['_source_sheet'] = sheet_name
                    # 处理NaN值
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = None
                
                if merge_sheets or len(sheets_to_read) == 1:
                    all_records.extend(records)
                else:
                    # 返回第一个有数据的工作表
                    if records:
                        return records
            
            return all_records
            
        except Exception as e:
            raise ImportError(f"Excel文件解析错误: {str(e)}")
    
    def validate_structure(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证Excel数据结构
        
        Args:
            data: 数据列表
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        if not data:
            errors.append("Excel文件无有效数据")
            return False, errors
        
        # 按来源工作表分组验证
        sheets_data = {}
        for record in data:
            sheet = record.get('_source_sheet', 'unknown')
            if sheet not in sheets_data:
                sheets_data[sheet] = []
            sheets_data[sheet].append(record)
        
        # 验证每个工作表的数据
        for sheet_name, sheet_records in sheets_data.items():
            sheet_errors = self._validate_sheet_data(sheet_name, sheet_records)
            errors.extend(sheet_errors)
        
        return len(errors) == 0, errors
    
    def _select_sheets(self, available_sheets: List[str]) -> List[str]:
        """根据评估类型选择要读取的工作表"""
        selected = []
        
        for sheet in available_sheets:
            sheet_lower = sheet.lower()
            
            if self.assessment_type == 'autism':
                # 孤独症相关工作表
                if any(keyword in sheet_lower for keyword in 
                       ['评估', 'abc', 'dsm', '临床', '统一', 'assessment', 'clinical']):
                    selected.append(sheet)
            else:
                # 儿童发展相关工作表
                if any(keyword in sheet_lower for keyword in 
                       ['发展', '观察', '儿童', 'development', 'observation', 'children']):
                    selected.append(sheet)
        
        # 如果没有找到相关工作表，返回第一个
        if not selected and available_sheets:
            selected = [available_sheets[0]]
        
        return selected
    
    def _validate_sheet_data(self, sheet_name: str, records: List[Dict[str, Any]]) -> List[str]:
        """验证单个工作表的数据"""
        errors = []
        
        if not records:
            errors.append(f"工作表 '{sheet_name}' 无数据")
            return errors
        
        # 获取工作表类型
        sheet_type = self._identify_sheet_type(sheet_name, records[0])
        
        # 根据类型验证必需字段
        if sheet_type == 'autism_assessment':
            required = ['评估时间', '评估情境']
        elif sheet_type == 'children_development':
            required = ['观察时间', '观察情境']
        elif sheet_type == 'conversations':
            required = ['timestamp', 'role', 'content']
        else:
            # 通用验证
            required = []
        
        # 检查必需字段
        first_record = records[0]
        for field in required:
            if field not in first_record:
                errors.append(f"工作表 '{sheet_name}' 缺少必需字段: {field}")
        
        # 检查数据一致性
        columns = set(first_record.keys())
        for idx, record in enumerate(records[1:], start=2):
            record_columns = set(record.keys())
            if record_columns != columns:
                diff = columns.symmetric_difference(record_columns)
                errors.append(
                    f"工作表 '{sheet_name}' 第{idx}行列不一致: {diff}"
                )
                if len(errors) > 10:
                    break
        
        return errors
    
    def _identify_sheet_type(self, sheet_name: str, sample_record: Dict[str, Any]) -> str:
        """识别工作表类型"""
        sheet_lower = sheet_name.lower()
        
        # 基于工作表名称
        for key, value in self.sheet_mappings.items():
            if key in sheet_name:
                return value
        
        # 基于列名特征
        columns = set(sample_record.keys())
        
        if 'ABC总分' in columns or 'ABC_' in str(columns):
            return 'abc_assessment'
        elif 'DSM5_' in str(columns) or 'DSM-5' in str(columns):
            return 'dsm5_assessment'
        elif '语言沟通发展' in columns or '社交互动能力' in columns:
            return 'children_development'
        elif 'role' in columns and 'content' in columns:
            return 'conversations'
        
        # 默认类型
        return 'autism_assessment' if self.assessment_type == 'autism' else 'children_development'
    
    def _convert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换Excel记录为标准格式
        
        Args:
            record: Excel记录
            
        Returns:
            转换后的记录
        """
        # 获取工作表类型
        sheet_type = self._identify_sheet_type(
            record.get('_source_sheet', ''),
            record
        )
        
        # 移除内部字段
        converted = {k: v for k, v in record.items() if not k.startswith('_')}
        
        # 根据工作表类型进行转换
        if sheet_type in ['autism_assessment', 'abc_assessment', 
                         'dsm5_assessment', 'unified_assessment']:
            converted.update(self._convert_autism_excel_record(record))
        elif sheet_type == 'children_development':
            converted.update(self._convert_children_excel_record(record))
        elif sheet_type == 'conversations':
            converted.update(self._convert_conversation_record(record))
        
        # 确保有评估类型
        if 'assessment_type' not in converted:
            converted['assessment_type'] = self.assessment_type
        
        return converted
    
    def _convert_autism_excel_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """转换孤独症评估Excel记录"""
        # 复用CSV导入器的转换逻辑
        from .csv_importer import CSVImporter
        csv_importer = CSVImporter(self.assessment_type)
        return csv_importer._convert_autism_record(record)
    
    def _convert_children_excel_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """转换儿童发展评估Excel记录"""
        # 复用CSV导入器的转换逻辑
        from .csv_importer import CSVImporter
        csv_importer = CSVImporter(self.assessment_type)
        return csv_importer._convert_children_record(record)
    
    def _convert_conversation_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """转换对话记录"""
        converted = {
            'type': 'conversation',
            'timestamp': self._parse_timestamp(str(record.get('timestamp', ''))),
            'role': record.get('role', ''),
            'content': record.get('content', ''),
            'context': record.get('context', '')
        }
        
        return converted