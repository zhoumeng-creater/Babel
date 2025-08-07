"""数据验证器模块"""
from .format_validator import FormatValidator
from .data_validator import DataValidator
from .business_validator import BusinessValidator

__all__ = [
    'FormatValidator',
    'DataValidator',
    'BusinessValidator'
]


class ValidationResult:
    """验证结果类"""
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.info = []
    
    def add_error(self, message: str, field: str = None, row: int = None):
        """添加错误"""
        self.is_valid = False
        error = {'message': message, 'level': 'error'}
        if field:
            error['field'] = field
        if row is not None:
            error['row'] = row
        self.errors.append(error)
    
    def add_warning(self, message: str, field: str = None, row: int = None):
        """添加警告"""
        warning = {'message': message, 'level': 'warning'}
        if field:
            warning['field'] = field
        if row is not None:
            warning['row'] = row
        self.warnings.append(warning)
    
    def add_info(self, message: str):
        """添加信息"""
        self.info.append({'message': message, 'level': 'info'})
    
    def merge(self, other: 'ValidationResult'):
        """合并其他验证结果"""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
    
    @property
    def error_count(self) -> int:
        """错误数量"""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """警告数量"""
        return len(self.warnings)
    
    def get_summary(self) -> str:
        """获取验证摘要"""
        if self.is_valid:
            return f"验证通过 (警告: {self.warning_count})"
        else:
            return f"验证失败 (错误: {self.error_count}, 警告: {self.warning_count})"


def validate_all(data, file_info=None, assessment_type='autism'):
    """
    执行所有层次的验证
    
    Args:
        data: 要验证的数据
        file_info: 文件信息（用于格式验证）
        assessment_type: 评估类型
    
    Returns:
        ValidationResult: 综合验证结果
    """
    result = ValidationResult()
    
    # 1. 格式验证
    if file_info:
        format_validator = FormatValidator()
        format_result = format_validator.validate(file_info)
        result.merge(format_result)
    
    # 2. 数据验证
    data_validator = DataValidator(assessment_type)
    data_result = data_validator.validate(data)
    result.merge(data_result)
    
    # 3. 业务验证
    business_validator = BusinessValidator(assessment_type)
    business_result = business_validator.validate(data)
    result.merge(business_result)
    
    return result