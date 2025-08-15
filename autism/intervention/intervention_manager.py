"""干预管理器模块

实现干预策略的应用、效果模拟和对比分析
"""
import datetime
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import copy

from common.api_client import call_kimi_api
from autism.configs import CLINICAL_SCENE_CONFIG, UNIFIED_AUTISM_PROFILES
from autism.evaluation.unified_evaluator import build_unified_autism_prompt
from autism.evaluation.enhanced_unified_evaluator import run_enhanced_experiment

from .intervention_config import (
    BEHAVIORAL_INTERVENTIONS,
    SOCIAL_INTERVENTIONS,
    COMMUNICATION_INTERVENTIONS,
    SENSORY_INTERVENTIONS,
    COGNITIVE_INTERVENTIONS,
    COMPREHENSIVE_PACKAGES,
    INTERVENTION_COMBINATIONS
)


class InterventionManager:
    """干预管理器 - 处理干预策略的应用和效果评估"""
    
    def __init__(self):
        """初始化干预管理器"""
        self.intervention_strategies = {
            "行为干预": BEHAVIORAL_INTERVENTIONS,
            "社交干预": SOCIAL_INTERVENTIONS,
            "沟通干预": COMMUNICATION_INTERVENTIONS,
            "感觉干预": SENSORY_INTERVENTIONS,
            "认知干预": COGNITIVE_INTERVENTIONS,
            "综合干预": COMPREHENSIVE_PACKAGES
        }
        
        self.intervention_history = []
    
    def get_available_interventions(self, category: Optional[str] = None) -> Dict[str, Any]:
        """获取可用的干预策略"""
        if category:
            return self.intervention_strategies.get(category, {})
        
        # 返回所有干预策略
        all_interventions = {}
        for cat_name, cat_strategies in self.intervention_strategies.items():
            for strat_name, strat_data in cat_strategies.items():
                all_interventions[f"{cat_name}-{strat_name}"] = strat_data
        return all_interventions
    
    def recommend_interventions(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """基于评估结果推荐干预策略"""
        recommendations = {
            "primary_interventions": [],
            "secondary_interventions": [],
            "rationale": [],
            "expected_outcomes": {}
        }
        
        # 分析评估结果确定严重程度
        severity = self._determine_severity(assessment_results)
        
        # 获取推荐的干预组合
        if severity in INTERVENTION_COMBINATIONS:
            combo = INTERVENTION_COMBINATIONS[severity]
            recommendations["primary_interventions"] = combo["primary"]
            recommendations["secondary_interventions"] = combo["secondary"]
            recommendations["intensity"] = combo["intensity"]
            recommendations["duration"] = combo["duration"]
            recommendations["expected_outcomes"]["overall"] = combo["expected_outcome"]
        
        # 基于具体问题添加针对性建议
        specific_needs = self._analyze_specific_needs(assessment_results)
        for need, interventions in specific_needs.items():
            recommendations["rationale"].append(f"{need}: 推荐{', '.join(interventions)}")
        
        return recommendations
    
    def apply_intervention(
        self, 
        baseline_config: Dict[str, Any],
        intervention_type: str,
        intervention_name: str,
        intervention_duration: str = "3个月",
        intervention_intensity: str = "每周20小时"
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        应用干预策略并生成干预后的行为表现
        
        Returns:
            Tuple[干预后的评估结果, 干预配置信息]
        """
        # 获取干预策略详情
        intervention_details = self._get_intervention_details(intervention_type, intervention_name)
        if not intervention_details:
            raise ValueError(f"未找到干预策略: {intervention_type}-{intervention_name}")
        
        # 修改autism_profile以反映干预效果
        modified_profile = self._apply_intervention_effects(
            baseline_config['autism_profile'],
            intervention_details,
            intervention_duration,
            intervention_intensity
        )
        
        # 构建干预后的prompt
        intervention_prompt = self._build_intervention_prompt(
            baseline_config,
            intervention_details,
            intervention_duration,
            intervention_intensity
        )
        
        # 生成干预后的对话
        scene_data = CLINICAL_SCENE_CONFIG[baseline_config['scene']]
        
        dialogue_prompt = (
            f"临床观察情境：{baseline_config['scene']} - {baseline_config['activity']}\n"
            f"观察要点：{', '.join(scene_data['observation_points'][:3])}\n"
            f"触发因素：{baseline_config['trigger']}\n"
            f"参与角色：孤独症儿童、{scene_data['roles'][1]}、{scene_data['roles'][2]}\n"
            f"\n重要说明：该儿童已接受{intervention_name}干预{intervention_duration}，"
            f"强度为{intervention_intensity}。\n"
            f"请展现干预后的行为改善，包括：\n"
            f"- {intervention_details.get('target_behaviors', intervention_details.get('target_skills', []))[0]}\n"
            f"要求：15-20轮对话，真实体现干预效果。"
        )
        
        # 调用API生成干预后的对话
        dialogue_with_intervention = call_kimi_api(
            dialogue_prompt,
            intervention_prompt,
            temperature=0.7
        )
        
        # 创建干预后的实验配置
        intervention_config = baseline_config.copy()
        intervention_config['autism_profile'] = modified_profile
        intervention_config['dialogue'] = dialogue_with_intervention
        intervention_config['intervention_applied'] = {
            'type': intervention_type,
            'name': intervention_name,
            'duration': intervention_duration,
            'intensity': intervention_intensity,
            'details': intervention_details
        }
        
        # 评估干预后的行为（使用增强版评估器）
        scales_to_use = baseline_config.get('selected_scales', ['ABC', 'DSM5', 'CARS', 'ASSQ'])
        intervention_result = self._evaluate_with_intervention(
            intervention_config,
            scales_to_use
        )
        
        # 记录干预历史
        self.intervention_history.append({
            'timestamp': datetime.datetime.now(),
            'baseline_id': baseline_config.get('experiment_id', 'unknown'),
            'intervention': f"{intervention_type}-{intervention_name}",
            'duration': intervention_duration,
            'intensity': intervention_intensity
        })
        
        return intervention_result, intervention_config
    
    def compare_intervention_effects(
        self,
        baseline_results: Dict[str, Any],
        intervention_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """比较干预前后的效果"""
        comparison = {
            'summary': {},
            'detailed_changes': {},
            'improvement_areas': [],
            'no_change_areas': [],
            'deterioration_areas': [],
            'clinical_significance': {}
        }
        
        # 比较各量表得分变化
        if 'abc_evaluation' in baseline_results and 'abc_evaluation' in intervention_results:
            abc_change = self._compare_abc_scores(
                baseline_results['abc_evaluation'],
                intervention_results['abc_evaluation']
            )
            comparison['detailed_changes']['ABC'] = abc_change
            comparison['summary']['ABC总分变化'] = abc_change['total_change']
            comparison['summary']['ABC改善率'] = f"{abc_change['improvement_rate']:.1%}"
        
        if 'dsm5_evaluation' in baseline_results and 'dsm5_evaluation' in intervention_results:
            dsm5_change = self._compare_dsm5_scores(
                baseline_results['dsm5_evaluation'],
                intervention_results['dsm5_evaluation']
            )
            comparison['detailed_changes']['DSM5'] = dsm5_change
            comparison['summary']['DSM5核心症状变化'] = dsm5_change['core_change']
            comparison['summary']['DSM5改善率'] = f"{dsm5_change['improvement_rate']:.1%}"
        
        if 'cars_evaluation' in baseline_results and 'cars_evaluation' in intervention_results:
            cars_change = self._compare_cars_scores(
                baseline_results['cars_evaluation'],
                intervention_results['cars_evaluation']
            )
            comparison['detailed_changes']['CARS'] = cars_change
            comparison['summary']['CARS总分变化'] = cars_change['total_change']
        
        if 'assq_evaluation' in baseline_results and 'assq_evaluation' in intervention_results:
            assq_change = self._compare_assq_scores(
                baseline_results['assq_evaluation'],
                intervention_results['assq_evaluation']
            )
            comparison['detailed_changes']['ASSQ'] = assq_change
            comparison['summary']['ASSQ筛查分变化'] = assq_change['total_change']
        
        # 识别改善领域
        comparison['improvement_areas'] = self._identify_improvements(comparison['detailed_changes'])
        comparison['no_change_areas'] = self._identify_no_changes(comparison['detailed_changes'])
        comparison['deterioration_areas'] = self._identify_deteriorations(comparison['detailed_changes'])
        
        # 评估临床意义
        comparison['clinical_significance'] = self._assess_clinical_significance(
            comparison['detailed_changes']
        )
        
        # 生成干预建议
        comparison['recommendations'] = self._generate_intervention_recommendations(
            comparison
        )
        
        return comparison
    
    def generate_intervention_report(
        self,
        baseline_results: Dict[str, Any],
        intervention_results: Dict[str, Any],
        comparison: Dict[str, Any]
    ) -> str:
        """生成干预效果报告"""
        report = []
        report.append("=" * 60)
        report.append("孤独症儿童干预效果评估报告")
        report.append("=" * 60)
        report.append(f"\n生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 基本信息
        if 'intervention_applied' in intervention_results:
            intervention_info = intervention_results['intervention_applied']
            report.append("一、干预信息")
            report.append("-" * 30)
            report.append(f"干预类型: {intervention_info['type']}")
            report.append(f"干预策略: {intervention_info['name']}")
            report.append(f"干预时长: {intervention_info['duration']}")
            report.append(f"干预强度: {intervention_info['intensity']}")
            report.append("")
        
        # 整体效果摘要
        report.append("二、整体效果摘要")
        report.append("-" * 30)
        for key, value in comparison['summary'].items():
            report.append(f"{key}: {value}")
        report.append("")
        
        # 具体改善领域
        report.append("三、改善领域分析")
        report.append("-" * 30)
        
        if comparison['improvement_areas']:
            report.append("显著改善领域:")
            for area in comparison['improvement_areas']:
                report.append(f"  • {area}")
        
        if comparison['no_change_areas']:
            report.append("\n无明显变化领域:")
            for area in comparison['no_change_areas']:
                report.append(f"  • {area}")
        
        if comparison['deterioration_areas']:
            report.append("\n需要关注领域:")
            for area in comparison['deterioration_areas']:
                report.append(f"  • {area}")
        report.append("")
        
        # 临床意义
        report.append("四、临床意义评估")
        report.append("-" * 30)
        for key, value in comparison['clinical_significance'].items():
            report.append(f"{key}: {value}")
        report.append("")
        
        # 建议
        report.append("五、后续建议")
        report.append("-" * 30)
        for rec in comparison['recommendations']:
            report.append(f"• {rec}")
        
        return "\n".join(report)
    
    # ========== 私有辅助方法 ==========
    
    def _determine_severity(self, assessment_results: Dict[str, Any]) -> str:
        """根据评估结果判断严重程度"""
        # 优先使用ABC总分判断
        if 'abc_evaluation' in assessment_results:
            abc_total = assessment_results['abc_evaluation']['total_score']
            if abc_total >= 101:
                return "重度孤独症"
            elif abc_total >= 67:
                return "中度孤独症"
            else:
                return "轻度孤独症"
        
        # 使用DSM5核心症状判断
        if 'dsm5_evaluation' in assessment_results:
            core_avg = assessment_results['dsm5_evaluation']['core_symptom_average']
            if core_avg >= 4:
                return "重度孤独症"
            elif core_avg >= 3:
                return "中度孤独症"
            else:
                return "轻度孤独症"
        
        return "中度孤独症"  # 默认值
    
    def _analyze_specific_needs(self, assessment_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """分析具体需求并推荐针对性干预"""
        needs = {}
        
        if 'abc_evaluation' in assessment_results:
            abc_eval = assessment_results['abc_evaluation']
            
            # 分析各领域得分
            if 'domain_scores' in abc_eval:
                scores = abc_eval['domain_scores']
                
                if scores.get('语言', 0) > 15:
                    needs["语言沟通缺陷"] = ["图片交换系统", "功能性沟通训练"]
                
                if scores.get('社交', 0) > 20:
                    needs["社交技能不足"] = ["同伴介入", "社交故事"]
                
                if scores.get('感觉', 0) > 10:
                    needs["感觉处理问题"] = ["感觉调节策略", "深压觉输入"]
        
        if 'dsm5_evaluation' in assessment_results:
            dsm5_eval = assessment_results['dsm5_evaluation']
            
            if 'scores' in dsm5_eval:
                scores = dsm5_eval['scores']
                
                if scores.get('刻板重复行为', 0) > 4:
                    needs["刻板行为严重"] = ["行为消退", "功能性沟通训练"]
                
                if scores.get('情绪行为调节', 0) > 4:
                    needs["情绪调节困难"] = ["认知行为治疗", "感觉调节策略"]
        
        return needs
    
    def _get_intervention_details(self, intervention_type: str, intervention_name: str) -> Optional[Dict[str, Any]]:
        """获取干预策略的详细信息"""
        category_strategies = self.intervention_strategies.get(intervention_type, {})
        return category_strategies.get(intervention_name)
    
    def _apply_intervention_effects(
        self,
        original_profile: Dict[str, Any],
        intervention_details: Dict[str, Any],
        duration: str,
        intensity: str
    ) -> Dict[str, Any]:
        """根据干预效果修改autism_profile"""
        modified_profile = copy.deepcopy(original_profile)
        
        # 计算干预效果系数（基于时长和强度）
        duration_factor = self._calculate_duration_factor(duration)
        intensity_factor = self._calculate_intensity_factor(intensity)
        effect_multiplier = duration_factor * intensity_factor
        
        # 应用预期改善
        improvements = intervention_details.get('expected_improvements', {})
        
        # 修改行为特征描述
        if 'social_interaction' in improvements and improvements['social_interaction'] > 0:
            improvement_level = improvements['social_interaction'] * effect_multiplier
            modified_profile['social_characteristics'] = self._improve_description(
                modified_profile['social_characteristics'],
                "社交",
                improvement_level
            )
        
        if 'communication' in improvements and improvements['communication'] > 0:
            improvement_level = improvements['communication'] * effect_multiplier
            modified_profile['communication_characteristics'] = self._improve_description(
                modified_profile['communication_characteristics'],
                "沟通",
                improvement_level
            )
        
        if 'repetitive_behaviors' in improvements and improvements['repetitive_behaviors'] < 0:
            reduction_level = abs(improvements['repetitive_behaviors']) * effect_multiplier
            modified_profile['behavioral_characteristics'] = self._reduce_problem_description(
                modified_profile['behavioral_characteristics'],
                "刻板",
                reduction_level
            )
        
        # 修改行为示例
        if 'behavioral_examples' in modified_profile:
            modified_examples = []
            for example in modified_profile['behavioral_examples']:
                # 减少问题行为的描述
                if any(word in example for word in ['重复', '刻板', '自伤', '攻击']):
                    if np.random.random() > 0.5:  # 50%概率保留但修改
                        example = example.replace('经常', '偶尔').replace('总是', '有时')
                        modified_examples.append(example)
                else:
                    modified_examples.append(example)
            
            # 添加改善后的行为示例
            if 'social_interaction' in improvements and improvements['social_interaction'] > 0:
                modified_examples.append("开始主动与他人打招呼或寻求互动")
            if 'communication' in improvements and improvements['communication'] > 0:
                modified_examples.append("能够使用简单句子表达需求和感受")
            
            modified_profile['behavioral_examples'] = modified_examples
        
        return modified_profile
    
    def _build_intervention_prompt(
        self,
        baseline_config: Dict[str, Any],
        intervention_details: Dict[str, Any],
        duration: str,
        intensity: str
    ) -> str:
        """构建反映干预效果的system prompt"""
        modified_profile = baseline_config['autism_profile']
        
        profile_description = f"""
        孤独症儿童行为特征（接受干预后）：
        
        【干预背景】：
        该儿童已接受{intervention_details['name']}干预
        - 干预时长：{duration}
        - 干预强度：{intensity}
        - 主要改善：{', '.join(intervention_details.get('target_behaviors', intervention_details.get('target_skills', [])))}
        
        【当前表现】：
        【社交特征】：{modified_profile['social_characteristics']}（有所改善）
        【沟通特征】：{modified_profile['communication_characteristics']}（进步中）
        【行为特征】：{modified_profile['behavioral_characteristics']}（减少问题行为）
        【认知特征】：{modified_profile['cognitive_characteristics']}
        【情绪特征】：{modified_profile['emotional_characteristics']}（更稳定）
        【日常生活】：{modified_profile['daily_living']}（独立性提高）
        
        【干预后的积极变化】：
        """
        
        # 添加具体的改善表现
        improvements = intervention_details.get('expected_improvements', {})
        positive_changes = []
        
        if improvements.get('social_interaction', 0) > 0:
            positive_changes.append("社交主动性增加，能够回应他人的互动邀请")
        if improvements.get('communication', 0) > 0:
            positive_changes.append("沟通能力提升，能够表达基本需求")
        if improvements.get('problem_behaviors', 0) < 0:
            positive_changes.append("问题行为减少，情绪更加稳定")
        if improvements.get('functional_communication', 0) > 0:
            positive_changes.append("学会使用功能性沟通替代问题行为")
        
        for i, change in enumerate(positive_changes, 1):
            profile_description += f"\n    {i}. {change}"
        
        system_prompt = (
            "你是一个专业的临床行为观察专家。请基于以下接受干预后的孤独症儿童特征，"
            "真实地模拟该儿童在特定情境下的行为表现。\n"
            + profile_description +
            "\n\n行为表现要求："
            "\n1. 展现干预带来的积极变化，但要符合实际"
            "\n2. 保留一些原有特征，改善是渐进的"
            "\n3. 体现新学会的技能和策略"
            "\n4. 问题行为减少但可能仍偶尔出现"
            "\n5. 整体表现比基线有明显进步"
            "\n\n格式：'角色名:内容'，每句换行。"
        )
        
        return system_prompt
    
    def _evaluate_with_intervention(
        self,
        intervention_config: Dict[str, Any],
        scales: List[str]
    ) -> Dict[str, Any]:
        """评估干预后的行为表现"""
        # 准备评估配置
        eval_config = {
            'experiment_id': f"INT_{intervention_config.get('experiment_id', 'unknown')}",
            'template': intervention_config.get('template', '干预后'),
            'scene': intervention_config['scene'],
            'activity': intervention_config['activity'],
            'trigger': intervention_config['trigger'],
            'autism_profile': intervention_config['autism_profile'],
            'selected_scales': scales
        }
        
        # 如果已有对话，直接评估
        if 'dialogue' in intervention_config:
            from autism.evaluation.enhanced_unified_evaluator import evaluate_dialogue_with_scales
            
            scene_data = CLINICAL_SCENE_CONFIG[intervention_config['scene']]
            result = evaluate_dialogue_with_scales(
                intervention_config['dialogue'],
                intervention_config['autism_profile'],
                scene_data,
                scales
            )
            
            # 添加干预信息
            result['intervention_applied'] = intervention_config.get('intervention_applied')
            result['experiment_id'] = eval_config['experiment_id']
            result['timestamp'] = datetime.datetime.now()
            result['template'] = eval_config['template']
            result['scene'] = eval_config['scene']
            result['activity'] = eval_config['activity']
            result['trigger'] = eval_config['trigger']
            
            return result
        else:
            # 生成新对话并评估
            return run_enhanced_experiment(eval_config)
    
    def _calculate_duration_factor(self, duration: str) -> float:
        """计算干预时长对效果的影响系数"""
        if "1个月" in duration:
            return 0.3
        elif "3个月" in duration:
            return 0.6
        elif "6个月" in duration:
            return 0.8
        elif "12个月" in duration or "1年" in duration:
            return 1.0
        else:
            return 0.5
    
    def _calculate_intensity_factor(self, intensity: str) -> float:
        """计算干预强度对效果的影响系数"""
        if "40小时" in intensity:
            return 1.0
        elif "30小时" in intensity:
            return 0.9
        elif "25小时" in intensity:
            return 0.8
        elif "20小时" in intensity:
            return 0.7
        elif "15小时" in intensity:
            return 0.6
        elif "10小时" in intensity:
            return 0.5
        else:
            return 0.6
    
    def _improve_description(self, original: str, aspect: str, level: float) -> str:
        """改善特征描述"""
        if level > 0.3:
            return original.replace("很少", "偶尔").replace("困难", "有所改善").replace("缺乏", "正在发展")
        elif level > 0.2:
            return original.replace("极少", "偶尔").replace("严重", "中度")
        else:
            return original.replace("完全不", "很少").replace("无法", "困难")
    
    def _reduce_problem_description(self, original: str, aspect: str, level: float) -> str:
        """减少问题行为描述"""
        if level > 0.3:
            return original.replace("频繁", "偶尔").replace("严重", "轻度").replace("明显", "较少")
        elif level > 0.2:
            return original.replace("经常", "有时").replace("很多", "一些")
        else:
            return original.replace("总是", "经常").replace("极度", "比较")
    
    def _compare_abc_scores(self, baseline: Dict, intervention: Dict) -> Dict[str, Any]:
        """比较ABC量表得分变化"""
        comparison = {
            'total_change': float(intervention['total_score'] - baseline['total_score']),  # 确保是浮点数
            'severity_change': f"{baseline['severity']} -> {intervention['severity']}",
            'domain_changes': {},
            'improvement_rate': 0.0
        }
        
        # 计算改善率（分数降低为改善）
        if baseline['total_score'] > 0:
            improvement = (baseline['total_score'] - intervention['total_score']) / baseline['total_score']
            comparison['improvement_rate'] = max(0, improvement)  # 确保非负
        
        # 比较各领域变化
        for domain in baseline.get('domain_scores', {}):
            if domain in intervention.get('domain_scores', {}):
                baseline_score = baseline['domain_scores'][domain]
                intervention_score = intervention['domain_scores'][domain]
                change = intervention_score - baseline_score
                
                comparison['domain_changes'][domain] = {
                    'baseline': baseline_score,
                    'intervention': intervention_score,
                    'change': float(change),  # 确保是浮点数
                    'direction': '改善' if change < 0 else ('恶化' if change > 0 else '无变化')
                }
        
        return comparison
    
    def _compare_dsm5_scores(self, baseline: Dict, intervention: Dict) -> Dict[str, Any]:
        """比较DSM-5评分变化"""
        baseline_core = baseline.get('core_symptom_average', 0)
        intervention_core = intervention.get('core_symptom_average', 0)
        
        comparison = {
            'core_change': intervention_core - baseline_core,
            'improvement_rate': (baseline_core - intervention_core) / baseline_core if baseline_core > 0 else 0,
            'dimension_changes': {}
        }
        
        # 比较各维度变化
        for dim in baseline.get('scores', {}):
            if dim in intervention.get('scores', {}):
                change = intervention['scores'][dim] - baseline['scores'][dim]
                comparison['dimension_changes'][dim] = {
                    'change': change,
                    'direction': '改善' if change < 0 else '恶化' if change > 0 else '无变化'
                }
        
        return comparison
    
    def _compare_cars_scores(self, baseline: Dict, intervention: Dict) -> Dict[str, Any]:
        """比较CARS量表得分变化"""
        comparison = {
            'total_change': float(intervention['total_score'] - baseline['total_score']),  # 确保是浮点数
            'severity_change': f"{baseline['severity']} -> {intervention['severity']}",
            'item_changes': {}
        }
        
        # 比较各项目变化
        for item in baseline.get('item_scores', {}):
            if item in intervention.get('item_scores', {}):
                change = intervention['item_scores'][item] - baseline['item_scores'][item]
                comparison['item_changes'][item] = float(change)  # 确保是浮点数
        
        return comparison
    
    def _compare_assq_scores(self, baseline: Dict, intervention: Dict) -> Dict[str, Any]:
        """比较ASSQ筛查得分变化"""
        comparison = {
            'total_change': float(intervention['total_score'] - baseline['total_score']),  # 确保是浮点数
            'risk_change': f"{baseline['risk_level']} -> {intervention['risk_level']}",
            'category_changes': {}
        }
        
        # 比较各类别变化
        for cat in baseline.get('category_scores', {}):
            if cat in intervention.get('category_scores', {}):
                change = intervention['category_scores'][cat] - baseline['category_scores'][cat]
                comparison['category_changes'][cat] = float(change)  # 确保是浮点数
        
        return comparison
    
    def _identify_improvements(self, detailed_changes: Dict) -> List[str]:
        """识别改善的领域"""
        improvements = []
        
        if 'ABC' in detailed_changes:
            abc = detailed_changes['ABC']
            if abc['improvement_rate'] > 0.1:
                improvements.append(f"ABC总分改善{abc['improvement_rate']:.1%}")
            for domain, change in abc.get('domain_changes', {}).items():
                if change['direction'] == '改善':
                    improvements.append(f"{domain}领域改善")
        
        if 'DSM5' in detailed_changes:
            dsm5 = detailed_changes['DSM5']
            if dsm5['improvement_rate'] > 0.1:
                improvements.append(f"DSM-5核心症状改善{dsm5['improvement_rate']:.1%}")
        
        return improvements
    
    def _identify_no_changes(self, detailed_changes: Dict) -> List[str]:
        """识别无变化的领域"""
        no_changes = []
        
        if 'ABC' in detailed_changes:
            for domain, change in detailed_changes['ABC'].get('domain_changes', {}).items():
                if change['direction'] == '无变化':
                    no_changes.append(f"{domain}领域")
        
        return no_changes
    
    def _identify_deteriorations(self, detailed_changes: Dict) -> List[str]:
        """识别恶化的领域"""
        deteriorations = []
        
        if 'ABC' in detailed_changes:
            for domain, change in detailed_changes['ABC'].get('domain_changes', {}).items():
                if change['direction'] == '恶化':
                    deteriorations.append(f"{domain}领域需要调整干预策略")
        
        return deteriorations
    
    def _assess_clinical_significance(self, detailed_changes: Dict) -> Dict[str, str]:
        """评估临床意义"""
        significance = {}
        
        # ABC量表的临床意义
        if 'ABC' in detailed_changes:
            abc_change = detailed_changes['ABC']['total_change']
            if abc_change <= -20:
                significance['ABC量表'] = "具有显著临床意义的改善"
            elif abc_change <= -10:
                significance['ABC量表'] = "具有临床意义的改善"
            elif abc_change <= -5:
                significance['ABC量表'] = "轻微改善"
            else:
                significance['ABC量表'] = "无明显改善"
        
        # DSM-5的临床意义
        if 'DSM5' in detailed_changes:
            dsm5_change = detailed_changes['DSM5']['core_change']
            if dsm5_change <= -1.0:
                significance['DSM-5标准'] = "支持需求等级可能下降"
            elif dsm5_change <= -0.5:
                significance['DSM-5标准'] = "功能有所改善"
            else:
                significance['DSM-5标准'] = "需要继续干预"
        
        return significance
    
    def _generate_intervention_recommendations(self, comparison: Dict) -> List[str]:
        """生成干预建议"""
        recommendations = []
        
        # 基于改善情况的建议
        if len(comparison['improvement_areas']) > 3:
            recommendations.append("干预效果良好，建议继续当前干预策略")
            recommendations.append("可以考虑逐步降低干预强度，观察维持效果")
        elif len(comparison['improvement_areas']) > 0:
            recommendations.append("干预有一定效果，建议保持并适当调整")
            recommendations.append("针对未改善领域增加专门干预")
        else:
            recommendations.append("干预效果不明显，需要重新评估和调整策略")
            recommendations.append("考虑增加干预强度或更换干预方法")
        
        # 基于问题领域的建议
        if comparison['deterioration_areas']:
            recommendations.append(f"关注以下领域：{', '.join(comparison['deterioration_areas'])}")
        
        # 基于临床意义的建议
        for scale, significance in comparison.get('clinical_significance', {}).items():
            if "显著" in significance:
                recommendations.append(f"{scale}显示显著改善，可考虑泛化训练")
            elif "需要继续" in significance:
                recommendations.append(f"{scale}提示需要加强干预")
        
        return recommendations