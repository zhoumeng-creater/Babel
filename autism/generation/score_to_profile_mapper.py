"""分数到特征映射器

将目标评估分数映射为孤独症特征配置
"""
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import copy

from autism.configs.profile_config import UNIFIED_AUTISM_PROFILES


class ScoreToProfileMapper:
    """将评估分数映射为autism_profile"""
    
    def __init__(self):
        """初始化映射器"""
        # ABC量表分数范围和对应特征
        self.abc_score_ranges = {
            (0, 40): "极轻度表现",
            (40, 53): "轻度表现",
            (53, 67): "中度表现",
            (67, 85): "中重度表现",
            (85, 101): "重度表现",
            (101, 158): "极重度表现"
        }
        
        # DSM-5核心症状评分范围
        self.dsm5_score_ranges = {
            (1.0, 2.0): "极轻度表现",
            (2.0, 2.5): "轻度表现",
            (2.5, 3.0): "中度表现",
            (3.0, 3.5): "中重度表现",
            (3.5, 4.0): "重度表现",
            (4.0, 5.0): "极重度表现"
        }
        
        # CARS总分范围（15-60分）
        self.cars_score_ranges = {
            (15, 25): "极轻度表现",
            (25, 30): "轻度表现",
            (30, 37): "中度表现",
            (37, 45): "中重度表现",
            (45, 52): "重度表现",
            (52, 60): "极重度表现"
        }
        
        # ASSQ筛查分范围（0-54分）
        self.assq_score_ranges = {
            (0, 10): "极轻度表现",
            (10, 15): "轻度表现",
            (15, 22): "中度表现",
            (22, 30): "中重度表现",
            (30, 40): "重度表现",
            (40, 54): "极重度表现"
        }
        
        # 行为特征与分数的映射关系
        self.behavior_score_mappings = self._initialize_behavior_mappings()
    
    def map_scores_to_profile(
        self,
        target_scores: Dict[str, float],
        base_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将目标分数映射为autism_profile
        
        Args:
            target_scores: 目标分数字典 {'abc_total': 75, 'dsm5_core': 3.5, ...}
            base_template: 基础模板名称
        
        Returns:
            autism_profile配置
        """
        # 确定严重程度
        severity = self._determine_severity_from_scores(target_scores)
        
        # 获取基础配置
        if base_template and base_template in UNIFIED_AUTISM_PROFILES:
            base_profile = copy.deepcopy(UNIFIED_AUTISM_PROFILES[base_template])
        else:
            base_profile = copy.deepcopy(UNIFIED_AUTISM_PROFILES.get(severity, UNIFIED_AUTISM_PROFILES["中度表现"]))
        
        # 根据具体分数调整配置
        adjusted_profile = self._adjust_profile_for_scores(base_profile, target_scores)
        
        # 生成符合分数的行为示例
        adjusted_profile['behavioral_examples'] = self._generate_behavioral_examples(target_scores)
        
        # 添加分数映射信息
        adjusted_profile['target_scores'] = target_scores
        adjusted_profile['severity_level'] = severity
        
        return adjusted_profile
    
    def calculate_profile_distance(
        self,
        profile: Dict[str, Any],
        target_scores: Dict[str, float]
    ) -> float:
        """
        计算profile与目标分数的距离
        
        用于验证生成的profile是否符合目标分数
        """
        # 预测该profile可能产生的分数
        predicted_scores = self._predict_scores_from_profile(profile)
        
        # 计算距离
        distance = 0.0
        weight_sum = 0.0
        
        if 'abc_total' in target_scores and 'abc_total' in predicted_scores:
            abc_diff = abs(target_scores['abc_total'] - predicted_scores['abc_total'])
            abc_weight = 1.0 / 158  # 归一化
            distance += abc_diff * abc_weight
            weight_sum += 1.0
        
        if 'dsm5_core' in target_scores and 'dsm5_core' in predicted_scores:
            dsm5_diff = abs(target_scores['dsm5_core'] - predicted_scores['dsm5_core'])
            dsm5_weight = 1.0 / 5  # 归一化
            distance += dsm5_diff * dsm5_weight
            weight_sum += 1.0
        
        if 'cars_total' in target_scores and 'cars_total' in predicted_scores:
            cars_diff = abs(target_scores['cars_total'] - predicted_scores['cars_total'])
            cars_weight = 1.0 / 60  # 归一化
            distance += cars_diff * cars_weight
            weight_sum += 1.0
        
        if 'assq_total' in target_scores and 'assq_total' in predicted_scores:
            assq_diff = abs(target_scores['assq_total'] - predicted_scores['assq_total'])
            assq_weight = 1.0 / 54  # 归一化
            distance += assq_diff * assq_weight
            weight_sum += 1.0
        
        return distance / weight_sum if weight_sum > 0 else 1.0
    
    def optimize_profile_for_scores(
        self,
        initial_profile: Dict[str, Any],
        target_scores: Dict[str, float],
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        优化profile以更好地匹配目标分数
        
        使用迭代方法调整profile特征
        """
        current_profile = copy.deepcopy(initial_profile)
        best_profile = copy.deepcopy(initial_profile)
        best_distance = self.calculate_profile_distance(initial_profile, target_scores)
        
        for iteration in range(max_iterations):
            # 预测当前profile的分数
            predicted_scores = self._predict_scores_from_profile(current_profile)
            
            # 计算差距
            adjustments_needed = self._calculate_adjustments(predicted_scores, target_scores)
            
            if not adjustments_needed:
                break
            
            # 应用调整
            current_profile = self._apply_adjustments(current_profile, adjustments_needed)
            
            # 计算新的距离
            current_distance = self.calculate_profile_distance(current_profile, target_scores)
            
            # 如果改善了，保存
            if current_distance < best_distance:
                best_profile = copy.deepcopy(current_profile)
                best_distance = current_distance
            
            # 如果足够接近，停止
            if best_distance < 0.1:
                break
        
        return best_profile
    
    # ========== 私有辅助方法 ==========
    
    def _initialize_behavior_mappings(self) -> Dict[str, Dict[str, Any]]:
        """初始化行为特征与分数的映射关系"""
        return {
            "社交缺陷": {
                "behaviors": [
                    "避免目光接触",
                    "不回应名字",
                    "独自玩耍",
                    "不寻求安慰",
                    "不分享兴趣"
                ],
                "score_contribution": {
                    "abc": 20,  # 对ABC总分的贡献
                    "dsm5": 1.5,  # 对DSM5核心症状的贡献
                    "cars": 8,
                    "assq": 10
                }
            },
            "沟通问题": {
                "behaviors": [
                    "语言发育迟缓",
                    "鹦鹉学舌",
                    "代词混用",
                    "不会对话",
                    "语调异常"
                ],
                "score_contribution": {
                    "abc": 25,
                    "dsm5": 1.5,
                    "cars": 10,
                    "assq": 12
                }
            },
            "刻板行为": {
                "behaviors": [
                    "重复拍手",
                    "转圈",
                    "摇摆身体",
                    "排列物品",
                    "固执于常规"
                ],
                "score_contribution": {
                    "abc": 30,
                    "dsm5": 1.5,
                    "cars": 12,
                    "assq": 15
                }
            },
            "感觉异常": {
                "behaviors": [
                    "捂耳朵",
                    "触觉敏感",
                    "视觉寻求",
                    "嗅觉异常",
                    "痛觉迟钝"
                ],
                "score_contribution": {
                    "abc": 15,
                    "dsm5": 1.0,
                    "cars": 6,
                    "assq": 8
                }
            }
        }
    
    def _determine_severity_from_scores(self, target_scores: Dict[str, float]) -> str:
        """根据目标分数确定严重程度"""
        severities = []
        weights = []
        
        # 根据ABC总分判断
        if 'abc_total' in target_scores:
            abc_score = target_scores['abc_total']
            for range_tuple, severity in self.abc_score_ranges.items():
                if range_tuple[0] <= abc_score < range_tuple[1]:
                    severities.append(severity)
                    weights.append(2.0)  # ABC权重较高
                    break
        
        # 根据DSM5核心症状判断
        if 'dsm5_core' in target_scores:
            dsm5_score = target_scores['dsm5_core']
            for range_tuple, severity in self.dsm5_score_ranges.items():
                if range_tuple[0] <= dsm5_score < range_tuple[1]:
                    severities.append(severity)
                    weights.append(2.0)  # DSM5权重较高
                    break
        
        # 根据CARS总分判断
        if 'cars_total' in target_scores:
            cars_score = target_scores['cars_total']
            for range_tuple, severity in self.cars_score_ranges.items():
                if range_tuple[0] <= cars_score <= range_tuple[1]:
                    severities.append(severity)
                    weights.append(1.5)
                    break
        
        # 根据ASSQ筛查分判断
        if 'assq_total' in target_scores:
            assq_score = target_scores['assq_total']
            for range_tuple, severity in self.assq_score_ranges.items():
                if range_tuple[0] <= assq_score <= range_tuple[1]:
                    severities.append(severity)
                    weights.append(1.0)
                    break
        
        # 加权投票确定最终严重程度
        if not severities:
            return "中度表现"
        
        severity_votes = {}
        for severity, weight in zip(severities, weights):
            severity_votes[severity] = severity_votes.get(severity, 0) + weight
        
        return max(severity_votes, key=severity_votes.get)
    
    def _adjust_profile_for_scores(
        self,
        base_profile: Dict[str, Any],
        target_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """根据具体分数调整profile"""
        adjusted = copy.deepcopy(base_profile)
        
        # 根据ABC分数调整
        if 'abc_total' in target_scores:
            abc_score = target_scores['abc_total']
            
            if abc_score >= 100:
                # 重度：加强所有问题描述
                adjusted['social_characteristics'] = self._intensify_description(
                    adjusted['social_characteristics'], "社交", 0.8
                )
                adjusted['communication_characteristics'] = self._intensify_description(
                    adjusted['communication_characteristics'], "沟通", 0.8
                )
                adjusted['behavioral_characteristics'] = self._intensify_description(
                    adjusted['behavioral_characteristics'], "行为", 0.9
                )
            elif abc_score >= 67:
                # 中度：适度调整
                adjusted['social_characteristics'] = self._moderate_description(
                    adjusted['social_characteristics'], "社交", 0.6
                )
                adjusted['communication_characteristics'] = self._moderate_description(
                    adjusted['communication_characteristics'], "沟通", 0.6
                )
            else:
                # 轻度：减弱问题描述
                adjusted['social_characteristics'] = self._mild_description(
                    adjusted['social_characteristics'], "社交", 0.3
                )
        
        # 根据DSM5分数调整
        if 'dsm5_core' in target_scores:
            dsm5_score = target_scores['dsm5_core']
            
            if dsm5_score >= 4.0:
                adjusted['emotional_characteristics'] = "情绪极不稳定，频繁崩溃，无法自我调节"
                adjusted['daily_living'] = "完全依赖他人，需要24小时监护"
            elif dsm5_score >= 3.0:
                adjusted['emotional_characteristics'] = "情绪调节困难，容易崩溃"
                adjusted['daily_living'] = "大部分生活技能需要协助"
            else:
                adjusted['emotional_characteristics'] = "情绪基本稳定，偶有焦虑"
                adjusted['daily_living'] = "生活基本自理，需要提醒"
        
        # 根据CARS分数调整认知特征
        if 'cars_total' in target_scores:
            cars_score = target_scores['cars_total']
            
            if cars_score >= 45:
                adjusted['cognitive_characteristics'] = "严重认知障碍，学习极其困难"
            elif cars_score >= 37:
                adjusted['cognitive_characteristics'] = "认知发展明显迟缓，需要特殊教育"
            elif cars_score >= 30:
                adjusted['cognitive_characteristics'] = "认知能力不均衡，部分领域落后"
            else:
                adjusted['cognitive_characteristics'] = "智力正常或接近正常，可能有特殊才能"
        
        return adjusted
    
    def _generate_behavioral_examples(self, target_scores: Dict[str, float]) -> List[str]:
        """生成符合目标分数的行为示例"""
        examples = []
        
        # 根据分数选择行为类别和数量
        behavior_categories = []
        
        # 分析需要包含哪些行为类别
        if 'abc_total' in target_scores:
            abc_score = target_scores['abc_total']
            
            if abc_score >= 80:
                # 高分：包含所有类别的严重行为
                behavior_categories = ["社交缺陷", "沟通问题", "刻板行为", "感觉异常"]
                severity_modifier = "频繁"
            elif abc_score >= 60:
                # 中等分：包含主要类别
                behavior_categories = ["社交缺陷", "刻板行为", "沟通问题"]
                severity_modifier = "经常"
            else:
                # 低分：包含轻度行为
                behavior_categories = ["社交缺陷", "沟通问题"]
                severity_modifier = "偶尔"
        
        # 生成具体行为示例
        for category in behavior_categories:
            if category in self.behavior_score_mappings:
                behaviors = self.behavior_score_mappings[category]["behaviors"]
                # 随机选择1-2个行为
                selected_behaviors = np.random.choice(
                    behaviors,
                    min(2, len(behaviors)),
                    replace=False
                )
                
                for behavior in selected_behaviors:
                    if 'abc_total' in target_scores and target_scores['abc_total'] >= 80:
                        example = f"{severity_modifier}{behavior}，影响日常功能"
                    else:
                        example = f"{severity_modifier}{behavior}"
                    examples.append(example)
        
        # 根据DSM5分数添加功能相关的例子
        if 'dsm5_core' in target_scores:
            dsm5_score = target_scores['dsm5_core']
            
            if dsm5_score >= 4.0:
                examples.append("完全沉浸在自己的世界中，对外界刺激几乎无反应")
                examples.append("无法进行任何形式的功能性沟通")
            elif dsm5_score >= 3.0:
                examples.append("需要大量支持才能参与日常活动")
                examples.append("在熟悉环境中能完成简单任务，但泛化困难")
            else:
                examples.append("在结构化环境中表现较好")
                examples.append("能够学习和使用补偿策略")
        
        # 确保至少有3个例子
        while len(examples) < 3:
            examples.append("表现出与年龄不相符的行为特征")
        
        # 限制最多10个例子
        return examples[:10]
    
    def _predict_scores_from_profile(self, profile: Dict[str, Any]) -> Dict[str, float]:
        """从profile预测可能的评估分数"""
        predicted = {}
        
        # 预测ABC总分
        abc_score = 40  # 基础分
        
        # 根据特征描述调整分数
        if "严重" in profile.get('social_characteristics', '') or "极少" in profile.get('social_characteristics', ''):
            abc_score += 25
        elif "困难" in profile.get('social_characteristics', ''):
            abc_score += 15
        
        if "无语言" in profile.get('communication_characteristics', '') or "极其有限" in profile.get('communication_characteristics', ''):
            abc_score += 30
        elif "有限" in profile.get('communication_characteristics', ''):
            abc_score += 20
        
        if "频繁" in profile.get('behavioral_characteristics', '') or "持续" in profile.get('behavioral_characteristics', ''):
            abc_score += 35
        elif "明显" in profile.get('behavioral_characteristics', ''):
            abc_score += 20
        
        predicted['abc_total'] = min(158, max(0, abc_score))
        
        # 预测DSM5核心症状分
        dsm5_score = 2.0  # 基础分
        
        if "完全" in profile.get('daily_living', '') or "24小时" in profile.get('daily_living', ''):
            dsm5_score = 4.5
        elif "大部分" in profile.get('daily_living', ''):
            dsm5_score = 3.5
        elif "需要支持" in profile.get('daily_living', ''):
            dsm5_score = 2.5
        
        predicted['dsm5_core'] = min(5.0, max(1.0, dsm5_score))
        
        # 预测CARS总分（基于整体功能）
        if profile.get('overall_functioning') == 'need_very_substantial_support':
            predicted['cars_total'] = 45
        elif profile.get('overall_functioning') == 'need_substantial_support':
            predicted['cars_total'] = 37
        elif profile.get('overall_functioning') == 'need_support':
            predicted['cars_total'] = 30
        else:
            predicted['cars_total'] = 25
        
        # 预测ASSQ筛查分
        assq_score = 10  # 基础分
        
        # 根据行为示例数量和内容调整
        behavioral_examples = profile.get('behavioral_examples', [])
        assq_score += len(behavioral_examples) * 2
        
        for example in behavioral_examples:
            if any(word in example for word in ['频繁', '严重', '完全']):
                assq_score += 3
        
        predicted['assq_total'] = min(54, max(0, assq_score))
        
        return predicted
    
    def _calculate_adjustments(
        self,
        predicted_scores: Dict[str, float],
        target_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """计算需要的调整"""
        adjustments = {}
        
        for scale in target_scores:
            if scale in predicted_scores:
                diff = target_scores[scale] - predicted_scores[scale]
                if abs(diff) > 0.1:  # 容差
                    adjustments[scale] = diff
        
        return adjustments
    
    def _apply_adjustments(
        self,
        profile: Dict[str, Any],
        adjustments: Dict[str, float]
    ) -> Dict[str, Any]:
        """应用调整到profile"""
        adjusted = copy.deepcopy(profile)
        
        # 根据ABC分数差调整
        if 'abc_total' in adjustments:
            diff = adjustments['abc_total']
            
            if diff > 10:  # 需要增加分数
                adjusted['social_characteristics'] = self._intensify_description(
                    adjusted['social_characteristics'], "社交", 0.2
                )
                adjusted['behavioral_characteristics'] = self._intensify_description(
                    adjusted['behavioral_characteristics'], "行为", 0.3
                )
            elif diff < -10:  # 需要减少分数
                adjusted['social_characteristics'] = self._mild_description(
                    adjusted['social_characteristics'], "社交", 0.2
                )
                adjusted['behavioral_characteristics'] = self._mild_description(
                    adjusted['behavioral_characteristics'], "行为", 0.2
                )
        
        # 根据DSM5分数差调整
        if 'dsm5_core' in adjustments:
            diff = adjustments['dsm5_core']
            
            if diff > 0.5:  # 需要增加分数
                adjusted['daily_living'] = self._worsen_functioning(adjusted['daily_living'])
            elif diff < -0.5:  # 需要减少分数
                adjusted['daily_living'] = self._improve_functioning(adjusted['daily_living'])
        
        return adjusted
    
    def _intensify_description(self, text: str, aspect: str, level: float) -> str:
        """加强问题描述"""
        if level > 0.5:
            text = text.replace("偶尔", "经常").replace("轻度", "中度").replace("有时", "频繁")
        if level > 0.7:
            text = text.replace("经常", "总是").replace("中度", "重度").replace("困难", "极其困难")
        return text
    
    def _moderate_description(self, text: str, aspect: str, level: float) -> str:
        """适度调整描述"""
        text = text.replace("很少", "有时").replace("轻微", "明显").replace("偶尔", "经常")
        return text
    
    def _mild_description(self, text: str, aspect: str, level: float) -> str:
        """减弱问题描述"""
        text = text.replace("总是", "经常").replace("经常", "有时").replace("严重", "中度")
        text = text.replace("极其", "比较").replace("完全", "大部分")
        return text
    
    def _worsen_functioning(self, text: str) -> str:
        """恶化功能描述"""
        if "基本自理" in text:
            return "需要日常生活的持续提醒和协助"
        elif "需要支持" in text:
            return "大部分生活技能需要协助，依赖他人照顾"
        else:
            return "完全依赖他人，需要24小时监护"
    
    def _improve_functioning(self, text: str) -> str:
        """改善功能描述"""
        if "完全依赖" in text:
            return "大部分生活技能需要协助"
        elif "大部分" in text:
            return "需要日常生活的支持和引导"
        else:
            return "生活基本自理，需要适当提醒"