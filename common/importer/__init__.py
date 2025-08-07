"""数据导入模块"""
from .csv_importer import CSVImporter
from .json_importer import JSONImporter
from .excel_importer import ExcelImporter
from .zip_importer import ZipImporter
from .base_importer import ImportResult, ImportError, ImportStatus  # 添加 ImportStatus

__all__ = [
    'CSVImporter',
    'JSONImporter', 
    'ExcelImporter',
    'ZipImporter',
    'ImportResult',
    'ImportError',
    'ImportStatus',  # 添加到导出列表
    'get_importer'
]

# 导入器注册表
IMPORTERS = {
    'csv': CSVImporter,
    'json': JSONImporter,
    'excel': ExcelImporter,
    'xlsx': ExcelImporter,
    'xls': ExcelImporter,
    'zip': ZipImporter
}


def get_importer(file_type):
    """根据文件类型获取对应的导入器
    
    Args:
        file_type: 文件类型/扩展名
        
    Returns:
        导入器类
        
    Raises:
        ValueError: 不支持的文件类型
    """
    file_type = file_type.lower().lstrip('.')
    if file_type not in IMPORTERS:
        raise ValueError(f"不支持的文件类型: {file_type}")
    return IMPORTERS[file_type]