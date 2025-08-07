"""数据验证器"""
import datetime
from typing import List, Dict, Any, Union, Optional
from . import ValidationResult


class DataValidator:
    """数据层验证器"""
    
    def __init__(self, assessment_type: str = 'autism'):
        self.assessment_type = assessment_type
        
        # 定义必需字段
        self.required_fields = {
            'autism': ['timestamp', 'scene'],
            'children': ['timestamp', 'scene']
        }
        
        # 定义字段类型
        self.field_types = {
            'timestamp': datetime.datetime,
            'experiment_id': str,
            'observation_id': str,
            'scene': str,
            'activity': str,
            'trigger': str,
            'notes': str,
            'template': str,
            'abc_total_score': (int, float),
            'dsm5_core_average': (int, float)
        }
        
        # 定义数值范围
        self.value_ranges = {
            # ABC相关分数
            'abc_total_score': (0, 174),  # ABC总分范围
            'abc_domain_score': (0, 5),   # ABC各领域分数
            
            # DSM-5相关分数
            'dsm5_score': (0, 5),          # DSM-5单项分数
            'dsm5_core_average': (0, 5),   # DSM-5核心症状均分
            
            # 儿童发展评分
            'development_score': (0, 5),    # 发展评分范围
            
            # 百分比
            'percentage': (0, 100),         # 百分比范围
            
            # 一致性评分
            'consistency_score': (0, 100)   # 一致性评分
        }
        
        # 有效的枚举值
        self.enum_values = {
            'abc_severity': ['无明显症状', '轻度', '中度', '重度'],
            'assessment_standard': ['ABC', 'DSM5', 'UNIFIED'],
            'role': ['用户', 'User', '治疗师', 'Therapist', 
                    '观察者', 'Observer', '儿童', 'Child', 
                    'assistant', 'user']
        }
    
    def validate(self, data: Union[List[Dict], Dict]) -> ValidationResult:
        """
        验证数据
        
        Args:
            data: 单条记录或记录列表
        
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()
        
        # 处理单条记录的情况
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            result.add_error("数据为空")
            return result
        
        # 验证每条记录
        for idx, record in enumerate(data):
            self._validate_record(record, idx + 1, result)
            
            # 限制错误数量
            if result.error_count > 100:
                result.add_error("错误过多，停止验证")
                break
        
        # 添加统计信息
        result.add_info(f"共验证 {len(data)} 条记录")
        
        return result
    
    def _validate_record(self, record: Dict[str, Any], row_num: int, result: ValidationResult):
        """验证单条记录"""
        if not isinstance(record, dict):
            result.add_error(f"记录不是字典类型", row=row_num)
            return
        
        # 验证必需字段
        self._validate_required_fields(record, row_num, result)
        
        # 验证字段类型
        self._validate_field_types(record, row_num, result)
        
        # 验证数值范围
        self._validate_value_ranges(record, row_num, result)
        
        # 验证枚举值
        self._validate_enum_values(record, row_num, result)
        
        # 验证特定格式的数据
        if self.assessment_type == 'autism':
            self._validate_autism_data(record, row_num, result)
        else:
            self._validate_children_data(record, row_num, result)
    
    def _validate_required_fields(self, record: Dict, row_num: int, result: ValidationResult):
        """验证必需字段"""
        required = self.required_fields.get(self.assessment_type, [])
        
        for field in required:
            if field not in record or record[field] is None:
                # 检查替代字段
                alternatives = self._get_field_alternatives(field)
                if not any(alt in record and record[alt] is not None for alt in alternatives):
                    result.add_error(f"缺少必需字段: {field}", field=field, row=row_num)
    
    def _validate_field_types(self, record: Dict, row_num: int, result: ValidationResult):
        """验证字段类型"""
        for field, expected_type in self.field_types.items():
            if field in record and record[field] is not None:
                value = record[field]
                
                # 处理多种可能的类型
                if isinstance(expected_type, tuple):
                    if not isinstance(value, expected_type):
                        result.add_error(
                            f"字段 {field} 类型错误: 期望 {expected_type}, 实际 {type(value)}",
                            field=field, row=row_num
                        )
                else:
                    if not isinstance(value, expected_type):
                        # 特殊处理datetime
                        if expected_type == datetime.datetime:
                            if not isinstance(value, (datetime.datetime, str)):
                                result.add_error(
                                    f"字段 {field} 应为日期时间类型",
                                    field=field, row=row_num
                                )
                        else:
                            result.add_error(
                                f"字段 {field} 类型错误: 期望 {expected_type.__name__}, "
                                f"实际 {type(value).__name__}",
                                field=field, row=row_num
                            )
    
    def _validate_value_ranges(self, record: Dict, row_num: int, result: ValidationResult):
        """验证数值范围"""
        # ABC总分
        if 'abc_total_score' in record:
            self._check_range(
                record['abc_total_score'], 
                self.value_ranges['abc_total_score'],
                'ABC总分', row_num, result
            )
        
        # ABC各领域分数
        if 'abc_evaluation' in record and isinstance(record['abc_evaluation'], dict):
            domain_scores = record['abc_evaluation'].get('domain_scores', {})
            for domain, score in domain_scores.items():
                self._check_range(
                    score,
                    self.value_ranges['abc_domain_score'],
                    f'ABC_{domain}', row_num, result
                )
        
        # DSM-5分数
        if 'dsm5_evaluation' in record and isinstance(record['dsm5_evaluation'], dict):
            # 核心症状均分
            core_avg = record['dsm5_evaluation'].get('core_symptom_average')
            if core_avg is not None:
                self._check_range(
                    core_avg,
                    self.value_ranges['dsm5_core_average'],
                    'DSM5核心症状均分', row_num, result
                )
            
            # 各项分数
            scores = record['dsm5_evaluation'].get('scores', {})
            for metric, score in scores.items():
                self._check_range(
                    score,
                    self.value_ranges['dsm5_score'],
                    f'DSM5_{metric}', row_num, result
                )
        
        # 儿童发展评分
        if 'evaluation_scores' in record and isinstance(record['evaluation_scores'], dict):
            for metric, score in record['evaluation_scores'].items():
                if isinstance(score, (int, float)):
                    self._check_range(
                        score,
                        self.value_ranges['development_score'],
                        metric, row_num, result
                    )
    
    def _validate_enum_values(self, record: Dict, row_num: int, result: ValidationResult):
        """验证枚举值"""
        # ABC严重程度
        if 'abc_severity' in record and record['abc_severity']:
            if record['abc_severity'] not in self.enum_values['abc_severity']:
                result.add_warning(
                    f"ABC严重程度值无效: {record['abc_severity']}",
                    field='abc_severity', row=row_num
                )
        
        # 评估标准
        if 'assessment_standard' in record and record['assessment_standard']:
            if record['assessment_standard'] not in self.enum_values['assessment_standard']:
                result.add_warning(
                    f"评估标准值无效: {record['assessment_standard']}",
                    field='assessment_standard', row=row_num
                )
    
    def _validate_autism_data(self, record: Dict, row_num: int, result: ValidationResult):
        """验证孤独症评估数据"""
        # 检查评估数据的完整性
        if 'assessment_standard' in record:
            standard = record['assessment_standard']
            
            if standard == 'UNIFIED':
                # 统一评估应该同时有ABC和DSM-5数据
                if 'abc_evaluation' not in record:
                    result.add_error("统一评估缺少ABC评估数据", row=row_num)
                if 'dsm5_evaluation' not in record:
                    result.add_error("统一评估缺少DSM-5评估数据", row=row_num)
            
            elif standard == 'ABC':
                if 'evaluation_scores' not in record:
                    result.add_error("ABC评估缺少评分数据", row=row_num)
            
            elif standard == 'DSM5':
                if 'evaluation_scores' not in record:
                    result.add_error("DSM-5评估缺少评分数据", row=row_num)
    
    def _validate_children_data(self, record: Dict, row_num: int, result: ValidationResult):
        """验证儿童发展评估数据"""
        # 检查评分数据
        if 'evaluation_scores' in record:
            scores = record['evaluation_scores']
            expected_dimensions = [
                '语言沟通发展', '社交互动能力', '认知学习能力',
                '情绪调节发展', '运动技能发展', '独立自理能力'
            ]
            
            missing_dimensions = []
            for dim in expected_dimensions:
                if dim not in scores:
                    missing_dimensions.append(dim)
            
            if missing_dimensions:
                result.add_warning(
                    f"缺少发展维度评分: {', '.join(missing_dimensions)}",
                    row=row_num
                )
    
    def _check_range(self, value: Any, range_tuple: tuple, field_name: str, 
                     row_num: int, result: ValidationResult):
        """检查数值范围"""
        if not isinstance(value, (int, float)):
            return
        
        min_val, max_val = range_tuple
        if value < min_val or value > max_val:
            result.add_error(
                f"{field_name} 超出范围: {value} (应在 {min_val}-{max_val} 之间)",
                field=field_name, row=row_num
            )
    
    def _get_field_alternatives(self, field: str) -> List[str]:
        """获取字段的替代名称"""
        alternatives = {
            'timestamp': ['评估时间', '观察时间', 'created_at', 'date'],
            'scene': ['评估情境', '观察情境'],
            'experiment_id': ['评估ID'],
            'observation_id': ['观察ID']
        }
        
        return alternatives.get(field, [])