"""业务逻辑验证器"""
import datetime
from typing import List, Dict, Any, Union, Set
from collections import defaultdict
from . import ValidationResult


class BusinessValidator:
    """业务逻辑验证器"""
    
    def __init__(self, assessment_type: str = 'autism'):
        self.assessment_type = assessment_type
        
        # ABC评分项目
        self.abc_items = [
            '感觉', '交往', '躯体运动', '语言', '生活自理',
            '视而不见听而不闻', '人际交往困难', '刻板活动',
            '对环境变化适应困难', '感觉异常', '重复性语言',
            '情感反应异常', '固定兴趣', '多动', '注意力不集中'
        ]
        
        # DSM-5评估指标
        self.dsm5_metrics = [
            '社交情感互惠缺陷', '非言语交流缺陷', '发展维持关系缺陷',
            '刻板重复动作', '坚持同一性', '狭隘兴趣', '感觉异常'
        ]
        
        # 儿童发展维度
        self.development_dimensions = [
            '语言沟通发展', '社交互动能力', '认知学习能力',
            '情绪调节发展', '运动技能发展', '独立自理能力'
        ]
    
    def validate(self, data: Union[List[Dict], Dict]) -> ValidationResult:
        """
        验证业务逻辑
        
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
            return result
        
        # 单条记录验证
        for idx, record in enumerate(data):
            self._validate_single_record(record, idx + 1, result)
        
        # 批量数据验证
        self._validate_batch_data(data, result)
        
        return result
    
    def _validate_single_record(self, record: Dict[str, Any], row_num: int, 
                               result: ValidationResult):
        """验证单条记录的业务逻辑"""
        # 验证时间戳合理性
        self._validate_timestamp(record, row_num, result)
        
        # 根据评估类型验证
        if self.assessment_type == 'autism':
            self._validate_autism_record(record, row_num, result)
        else:
            self._validate_children_record(record, row_num, result)
        
        # 验证数据一致性
        self._validate_data_consistency(record, row_num, result)
    
    def _validate_timestamp(self, record: Dict, row_num: int, result: ValidationResult):
        """验证时间戳合理性"""
        timestamp = record.get('timestamp')
        if not timestamp:
            return
        
        if isinstance(timestamp, str):
            # 字符串会在导入时转换，这里跳过
            return
        
        if isinstance(timestamp, datetime.datetime):
            # 检查是否是未来时间
            if timestamp > datetime.datetime.now():
                result.add_warning(
                    f"时间戳是未来时间: {timestamp}",
                    field='timestamp', row=row_num
                )
            
            # 检查是否太久远（比如10年前）
            ten_years_ago = datetime.datetime.now() - datetime.timedelta(days=3650)
            if timestamp < ten_years_ago:
                result.add_warning(
                    f"时间戳过于久远: {timestamp}",
                    field='timestamp', row=row_num
                )
    
    def _validate_autism_record(self, record: Dict, row_num: int, result: ValidationResult):
        """验证孤独症评估记录"""
        standard = record.get('assessment_standard')
        
        if standard == 'UNIFIED':
            self._validate_unified_assessment(record, row_num, result)
        elif standard == 'ABC':
            self._validate_abc_assessment(record, row_num, result)
        elif standard == 'DSM5':
            self._validate_dsm5_assessment(record, row_num, result)
    
    def _validate_unified_assessment(self, record: Dict, row_num: int, 
                                   result: ValidationResult):
        """验证统一评估数据"""
        # 验证ABC部分
        if 'abc_evaluation' in record:
            abc_eval = record['abc_evaluation']
            
            # 验证总分与各项分数的一致性
            if 'total_score' in abc_eval and 'domain_scores' in abc_eval:
                domain_scores = abc_eval['domain_scores']
                
                # ABC总分应该等于各项分数之和
                if domain_scores:
                    calculated_total = sum(domain_scores.values())
                    reported_total = abc_eval['total_score']
                    
                    # 允许小的误差（浮点数计算）
                    if abs(calculated_total - reported_total) > 1:
                        result.add_error(
                            f"ABC总分不一致: 报告值={reported_total}, "
                            f"计算值={calculated_total}",
                            row=row_num
                        )
            
            # 验证严重程度与总分的对应关系
            if 'severity' in abc_eval and 'total_score' in abc_eval:
                self._validate_abc_severity(
                    abc_eval['total_score'],
                    abc_eval['severity'],
                    row_num, result
                )
        
        # 验证DSM-5部分
        if 'dsm5_evaluation' in record:
            dsm5_eval = record['dsm5_evaluation']
            
            # 验证核心症状均分
            if 'scores' in dsm5_eval and 'core_symptom_average' in dsm5_eval:
                scores = dsm5_eval['scores']
                core_metrics = ['社交情感互惠缺陷', '非言语交流缺陷', 
                              '发展维持关系缺陷', '刻板重复动作']
                
                core_scores = [scores.get(m, 0) for m in core_metrics if m in scores]
                if core_scores:
                    calculated_avg = sum(core_scores) / len(core_scores)
                    reported_avg = dsm5_eval['core_symptom_average']
                    
                    if abs(calculated_avg - reported_avg) > 0.1:
                        result.add_warning(
                            f"DSM-5核心症状均分可能有误: 报告值={reported_avg:.2f}, "
                            f"计算值={calculated_avg:.2f}",
                            row=row_num
                        )
    
    def _validate_abc_assessment(self, record: Dict, row_num: int, 
                                result: ValidationResult):
        """验证ABC评估数据"""
        if 'evaluation_scores' not in record:
            return
        
        scores = record['evaluation_scores']
        
        # 检查是否包含所有ABC项目
        missing_items = []
        for item in self.abc_items:
            if item not in scores:
                missing_items.append(item)
        
        if missing_items:
            if len(missing_items) > 5:
                result.add_error(
                    f"缺少{len(missing_items)}个ABC评分项",
                    row=row_num
                )
            else:
                result.add_warning(
                    f"缺少ABC评分项: {', '.join(missing_items[:3])}...",
                    row=row_num
                )
        
        # 验证分数范围（ABC每项0-4分）
        for item, score in scores.items():
            if item in self.abc_items and isinstance(score, (int, float)):
                if score < 0 or score > 4:
                    result.add_error(
                        f"ABC项目'{item}'分数超出范围: {score}",
                        row=row_num
                    )
    
    def _validate_dsm5_assessment(self, record: Dict, row_num: int, 
                                 result: ValidationResult):
        """验证DSM-5评估数据"""
        if 'evaluation_scores' not in record:
            return
        
        scores = record['evaluation_scores']
        
        # 检查关键指标
        dsm5_scores = {k: v for k, v in scores.items() 
                      if any(metric in k for metric in self.dsm5_metrics)}
        
        if not dsm5_scores:
            result.add_error(
                "未找到DSM-5评估指标",
                row=row_num
            )
    
    def _validate_children_record(self, record: Dict, row_num: int, 
                                 result: ValidationResult):
        """验证儿童发展评估记录"""
        if 'evaluation_scores' not in record:
            return
        
        scores = record['evaluation_scores']
        
        # 验证发展维度完整性
        present_dimensions = [d for d in self.development_dimensions if d in scores]
        
        if len(present_dimensions) < 4:
            result.add_warning(
                f"发展维度不完整，仅有{len(present_dimensions)}/6个维度",
                row=row_num
            )
        
        # 验证综合发展指数
        if present_dimensions:
            total_score = sum(scores.get(d, 0) for d in present_dimensions)
            avg_score = total_score / len(present_dimensions)
            
            # 检查是否有极端值
            for dim in present_dimensions:
                score = scores[dim]
                if abs(score - avg_score) > 3:
                    result.add_warning(
                        f"维度'{dim}'分数({score})与平均值({avg_score:.1f})差异较大",
                        row=row_num
                    )
    
    def _validate_data_consistency(self, record: Dict, row_num: int, 
                                  result: ValidationResult):
        """验证数据内部一致性"""
        # 场景与活动的匹配
        scene = record.get('scene', '')
        activity = record.get('activity', '')
        
        if scene and activity:
            # 检查常见的不匹配情况
            if '户外' in scene and '室内' in activity:
                result.add_warning(
                    "场景与活动可能不匹配：户外场景但室内活动",
                    row=row_num
                )
            elif '教室' in scene and '户外' in activity:
                result.add_warning(
                    "场景与活动可能不匹配：教室场景但户外活动",
                    row=row_num
                )
    
    def _validate_abc_severity(self, total_score: float, severity: str, 
                             row_num: int, result: ValidationResult):
        """验证ABC严重程度与总分的对应关系"""
        # 定义严重程度对应的分数范围
        severity_ranges = {
            '无明显症状': (0, 30),
            '轻度': (31, 67),
            '中度': (68, 100),
            '重度': (101, 174)
        }
        
        if severity in severity_ranges:
            min_score, max_score = severity_ranges[severity]
            if total_score < min_score or total_score > max_score:
                # 找出正确的严重程度
                correct_severity = None
                for sev, (min_s, max_s) in severity_ranges.items():
                    if min_s <= total_score <= max_s:
                        correct_severity = sev
                        break
                
                result.add_error(
                    f"ABC严重程度与总分不匹配: 总分={total_score}, "
                    f"严重程度={severity} (应为{correct_severity})",
                    row=row_num
                )
    
    def _validate_batch_data(self, data: List[Dict], result: ValidationResult):
        """验证批量数据的整体逻辑"""
        # 检查重复记录
        self._check_duplicates(data, result)
        
        # 检查时间序列
        self._check_time_sequence(data, result)
        
        # 检查数据分布
        self._check_data_distribution(data, result)
    
    def _check_duplicates(self, data: List[Dict], result: ValidationResult):
        """检查重复记录"""
        # 使用多个字段组合来识别潜在重复
        seen_records = defaultdict(list)
        
        for idx, record in enumerate(data):
            # 创建记录指纹
            timestamp = str(record.get('timestamp', ''))
            scene = record.get('scene', '')
            
            # 根据评估类型选择关键字段
            if self.assessment_type == 'autism':
                if 'abc_evaluation' in record:
                    key_score = record['abc_evaluation'].get('total_score', '')
                elif 'evaluation_scores' in record:
                    scores = record['evaluation_scores']
                    key_score = sum(scores.values()) if scores else ''
                else:
                    key_score = ''
            else:
                scores = record.get('evaluation_scores', {})
                key_score = sum(scores.values()) if scores else ''
            
            fingerprint = f"{timestamp}|{scene}|{key_score}"
            
            if fingerprint in seen_records:
                # 可能是重复记录
                prev_indices = seen_records[fingerprint]
                result.add_warning(
                    f"可能的重复记录: 行{idx+1}与行{prev_indices[0]+1}相似"
                )
            
            seen_records[fingerprint].append(idx)
    
    def _check_time_sequence(self, data: List[Dict], result: ValidationResult):
        """检查时间序列的合理性"""
        # 按时间排序
        timed_records = []
        for idx, record in enumerate(data):
            timestamp = record.get('timestamp')
            if timestamp and isinstance(timestamp, datetime.datetime):
                timed_records.append((timestamp, idx))
        
        if len(timed_records) < 2:
            return
        
        timed_records.sort()
        
        # 检查时间间隔
        for i in range(1, len(timed_records)):
            curr_time, curr_idx = timed_records[i]
            prev_time, prev_idx = timed_records[i-1]
            
            time_diff = curr_time - prev_time
            
            # 检查是否有极短的时间间隔（可能是错误）
            if time_diff.total_seconds() < 60:  # 小于1分钟
                result.add_warning(
                    f"记录时间间隔过短: 行{prev_idx+1}与行{curr_idx+1}间隔"
                    f"{time_diff.total_seconds()}秒"
                )
    
    def _check_data_distribution(self, data: List[Dict], result: ValidationResult):
        """检查数据分布的合理性"""
        if self.assessment_type == 'autism':
            # 收集所有ABC总分
            abc_scores = []
            for record in data:
                if 'abc_evaluation' in record:
                    score = record['abc_evaluation'].get('total_score')
                    if score is not None:
                        abc_scores.append(score)
            
            if len(abc_scores) > 10:
                # 检查是否所有分数都相同
                if len(set(abc_scores)) == 1:
                    result.add_warning("所有ABC总分都相同，请检查数据是否正确")
                
                # 检查分数分布
                avg_score = sum(abc_scores) / len(abc_scores)
                if avg_score < 20:
                    result.add_info("ABC平均分较低，多数为轻症或无症状")
                elif avg_score > 100:
                    result.add_info("ABC平均分较高，多数为重症")