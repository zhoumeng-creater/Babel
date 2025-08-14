"""
增强版统一评估核心模块 - 支持多量表选择和评估
支持ABC、DSM-5、CARS、ASSQ四种量表的独立或组合评估
"""
import datetime
import numpy as np
from typing import Dict, List, Any, Optional, Set

from common.api_client import call_kimi_api
from autism.configs import (
    CLINICAL_SCENE_CONFIG, 
    UNIFIED_AUTISM_PROFILES
)

# 导入各量表评估器
from .abc_evaluator import evaluate_abc_behaviors, get_abc_severity_level
from .dsm5_evaluator import evaluate_dsm5_dialogue, extract_dsm5_observations
from .cars_evaluator import evaluate_cars_behaviors, get_cars_severity_level, get_cars_interpretation
from .assq_evaluator import evaluate_assq_behaviors, get_assq_screening_result, get_assq_category_interpretation
from .unified_evaluator import build_unified_autism_prompt, call_kimi_with_unified_profile


# 量表配置
AVAILABLE_SCALES = {
    'ABC': {
        'name': 'ABC量表',
        'full_name': '孤独症行为量表',
        'type': 'diagnostic',
        'age_range': '18个月以上',
        'items': 57,
        'time': '10-15分钟'
    },
    'DSM5': {
        'name': 'DSM-5标准',
        'full_name': 'DSM-5诊断标准',
        'type': 'diagnostic',
        'age_range': '所有年龄',
        'items': '核心症状评估',
        'time': '20-30分钟'
    },
    'CARS': {
        'name': 'CARS量表',
        'full_name': '儿童孤独症评定量表',
        'type': 'diagnostic',
        'age_range': '2岁以上',
        'items': 15,
        'time': '20-30分钟'
    },
    'ASSQ': {
        'name': 'ASSQ筛查',
        'full_name': '孤独症谱系筛查问卷',
        'type': 'screening',
        'age_range': '6-17岁',
        'items': 27,
        'time': '10分钟'
    }
}

# 默认量表组合
DEFAULT_SCALES = ['ABC', 'DSM5']
COMPREHENSIVE_SCALES = ['ABC', 'DSM5', 'CARS', 'ASSQ']


def run_enhanced_experiment(experiment_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行增强版实验 - 支持量表选择
    
    Args:
        experiment_config: 实验配置，包含：
            - selected_scales: 选择的量表列表（默认['ABC', 'DSM5']）
            - 其他标准配置项
    
    Returns:
        包含所选量表评估结果的完整记录
    """
    try:
        # 获取选择的量表（默认使用ABC和DSM5）
        selected_scales = experiment_config.get('selected_scales', DEFAULT_SCALES)
        
        # 验证量表选择
        valid_scales = validate_scale_selection(selected_scales)
        if not valid_scales:
            return {
                'error': '未选择有效的评估量表',
                'available_scales': list(AVAILABLE_SCALES.keys())
            }
        
        scene_data = CLINICAL_SCENE_CONFIG[experiment_config['scene']]
        
        # 构建统一的prompt（不偏向任何评估标准）
        prompt = (
            f"临床观察情境：{experiment_config['scene']} - {experiment_config['activity']}\n"
            f"观察要点：{', '.join(scene_data['observation_points'][:3])}\n"
            f"触发因素：{experiment_config['trigger']}\n"
            f"参与角色：孤独症儿童、{scene_data['roles'][1]}、{scene_data['roles'][2]}\n"
            f"请模拟该孤独症儿童在此情境下的真实行为表现。\n"
            f"要求：15-20轮对话，真实体现儿童的特征，包含具体的行为细节。\n"
            f"格式：'角色名:内容'，每句换行。非语言行为用括号描述。"
        )
        
        # 生成对话（只生成一次，供所有量表评估）
        dialogue = call_kimi_with_unified_profile(prompt, experiment_config['autism_profile'])
        
        # 初始化记录
        record = {
            'experiment_id': experiment_config['experiment_id'],
            'timestamp': datetime.datetime.now(),
            'template': experiment_config['template'],
            'scene': experiment_config['scene'],
            'activity': experiment_config['activity'],
            'trigger': experiment_config['trigger'],
            'autism_profile': experiment_config['autism_profile'],
            'dialogue': dialogue,
            'selected_scales': valid_scales,
            'assessment_standard': 'MULTI_SCALE',  # 多量表评估
        }
        
        # 执行选定的量表评估
        evaluation_results = {}
        
        if 'ABC' in valid_scales:
            abc_results = perform_abc_evaluation(dialogue, experiment_config['autism_profile'], scene_data)
            evaluation_results['abc_evaluation'] = abc_results
            record['abc_evaluation'] = abc_results
        
        if 'DSM5' in valid_scales:
            dsm5_results = perform_dsm5_evaluation(dialogue, experiment_config['autism_profile'], scene_data)
            evaluation_results['dsm5_evaluation'] = dsm5_results
            record['dsm5_evaluation'] = dsm5_results
        
        if 'CARS' in valid_scales:
            cars_results = perform_cars_evaluation(dialogue, experiment_config['autism_profile'], scene_data)
            evaluation_results['cars_evaluation'] = cars_results
            record['cars_evaluation'] = cars_results
        
        if 'ASSQ' in valid_scales:
            assq_results = perform_assq_evaluation(dialogue, experiment_config['autism_profile'], scene_data)
            evaluation_results['assq_evaluation'] = assq_results
            record['assq_evaluation'] = assq_results
        
        # 添加综合分析
        if len(valid_scales) > 1:
            comparison = compare_scale_results(evaluation_results)
            record['scale_comparison'] = comparison
        
        # 添加评估摘要
        record['evaluation_summary'] = generate_evaluation_summary(evaluation_results, valid_scales)
        
        # 添加备注
        scales_used = ', '.join([AVAILABLE_SCALES[s]['name'] for s in valid_scales])
        record['notes'] = f"多量表评估 - 使用: {scales_used}"
        
        return record
        
    except Exception as e:
        return {
            'error': f'评估失败: {str(e)}',
            'experiment_id': experiment_config.get('experiment_id', 'unknown')
        }


def validate_scale_selection(selected_scales: List[str]) -> List[str]:
    """
    验证量表选择的有效性
    
    Args:
        selected_scales: 用户选择的量表列表
    
    Returns:
        有效的量表列表
    """
    valid_scales = []
    
    for scale in selected_scales:
        # 处理不同格式的输入
        scale_key = scale.upper().replace('量表', '').replace('筛查', '').strip()
        
        # 映射常见输入到标准键
        scale_mapping = {
            'ABC': 'ABC',
            'DSM-5': 'DSM5',
            'DSM5': 'DSM5',
            'DSM': 'DSM5',
            'CARS': 'CARS',
            'ASSQ': 'ASSQ'
        }
        
        if scale_key in scale_mapping:
            valid_scales.append(scale_mapping[scale_key])
    
    # 去重并保持顺序
    return list(dict.fromkeys(valid_scales))


def perform_abc_evaluation(dialogue: str, autism_profile: Dict, scene_data: Dict) -> Dict[str, Any]:
    """执行ABC量表评估"""
    abc_scores, identified_behaviors = evaluate_abc_behaviors(
        dialogue, 
        autism_profile, 
        scene_data
    )
    abc_total_score = sum(abc_scores.values())
    abc_severity = get_abc_severity_level(abc_total_score)
    
    return {
        'total_score': abc_total_score,
        'severity': abc_severity,
        'domain_scores': abc_scores,
        'identified_behaviors': identified_behaviors,
        'interpretation': {
            'clinical_range': abc_total_score >= 67,
            'severity_level': abc_severity,
            'recommendation': '需要进一步评估' if abc_total_score >= 53 else '继续观察'
        }
    }


def perform_dsm5_evaluation(dialogue: str, autism_profile: Dict, scene_data: Dict) -> Dict[str, Any]:
    """执行DSM-5标准评估"""
    dsm5_scores = evaluate_dsm5_dialogue(
        dialogue, 
        autism_profile, 
        scene_data
    )
    clinical_observations = extract_dsm5_observations(dialogue)
    
    core_symptom_average = (
        dsm5_scores.get('社交互动质量', 0) + 
        dsm5_scores.get('沟通交流能力', 0) + 
        dsm5_scores.get('刻板重复行为', 0)
    ) / 3
    
    return {
        'scores': dsm5_scores,
        'clinical_observations': clinical_observations,
        'core_symptom_average': core_symptom_average,
        'severity_level': (
            '需要支持' if core_symptom_average < 3 else
            '需要大量支持' if core_symptom_average < 4 else
            '需要非常大量支持'
        ),
        'meets_criteria': {
            'social_communication': core_symptom_average >= 2,
            'restricted_repetitive': dsm5_scores.get('刻板重复行为', 0) >= 2,
            'overall': core_symptom_average >= 2
        }
    }


def perform_cars_evaluation(dialogue: str, autism_profile: Dict, scene_data: Dict) -> Dict[str, Any]:
    """执行CARS量表评估"""
    item_scores, identified_behaviors, total_score = evaluate_cars_behaviors(
        dialogue,
        autism_profile,
        scene_data
    )
    
    severity = get_cars_severity_level(total_score)
    interpretation = get_cars_interpretation(total_score)
    
    return {
        'total_score': total_score,
        'severity': severity,
        'item_scores': item_scores,
        'identified_behaviors': identified_behaviors,
        'interpretation': interpretation,
        'clinical_cutoff': total_score >= 30,
        'severity_category': (
            '非孤独症' if total_score < 30 else
            '轻中度孤独症' if total_score <= 36.5 else
            '重度孤独症'
        )
    }


def perform_assq_evaluation(dialogue: str, autism_profile: Dict, scene_data: Dict) -> Dict[str, Any]:
    """执行ASSQ筛查评估"""
    item_scores, identified_traits, total_score, category_scores = evaluate_assq_behaviors(
        dialogue,
        autism_profile,
        scene_data
    )
    
    screening_result = get_assq_screening_result(total_score, 'parent')
    category_interpretation = get_assq_category_interpretation(category_scores)
    
    return {
        'total_score': total_score,
        'item_scores': item_scores,
        'category_scores': category_scores,
        'identified_traits': identified_traits,
        'screening_result': screening_result,
        'category_interpretation': category_interpretation,
        'positive_screen': total_score >= 13,  # 使用临床截断分
        'risk_level': screening_result['risk_level']
    }


def compare_scale_results(evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    比较不同量表的评估结果
    
    Args:
        evaluation_results: 各量表的评估结果
    
    Returns:
        量表间的比较分析
    """
    comparison = {
        'consistency': {},
        'severity_agreement': {},
        'key_findings': []
    }
    
    # 收集严重程度判断
    severity_assessments = {}
    
    if 'abc_evaluation' in evaluation_results:
        abc = evaluation_results['abc_evaluation']
        severity_assessments['ABC'] = (
            '重度' if abc['total_score'] >= 101 else
            '中度' if abc['total_score'] >= 67 else
            '轻度' if abc['total_score'] >= 53 else
            '正常'
        )
    
    if 'dsm5_evaluation' in evaluation_results:
        dsm5 = evaluation_results['dsm5_evaluation']
        severity_assessments['DSM5'] = (
            '重度' if dsm5['core_symptom_average'] >= 4 else
            '中度' if dsm5['core_symptom_average'] >= 3 else
            '轻度' if dsm5['core_symptom_average'] >= 2 else
            '正常'
        )
    
    if 'cars_evaluation' in evaluation_results:
        cars = evaluation_results['cars_evaluation']
        severity_assessments['CARS'] = (
            '重度' if cars['total_score'] >= 37 else
            '中度' if cars['total_score'] >= 30 else
            '正常'
        )
    
    if 'assq_evaluation' in evaluation_results:
        assq = evaluation_results['assq_evaluation']
        severity_assessments['ASSQ'] = (
            '高风险' if assq['total_score'] >= 19 else
            '中风险' if assq['total_score'] >= 13 else
            '低风险'
        )
    
    # 计算一致性
    if len(severity_assessments) > 1:
        severity_values = list(severity_assessments.values())
        # 简化的一致性计算
        if all(s == severity_values[0] for s in severity_values):
            comparison['consistency']['overall'] = '完全一致'
        elif any(s == severity_values[0] for s in severity_values[1:]):
            comparison['consistency']['overall'] = '部分一致'
        else:
            comparison['consistency']['overall'] = '存在差异'
        
        comparison['severity_agreement'] = severity_assessments
    
    # 提取关键发现
    if 'abc_evaluation' in evaluation_results and 'dsm5_evaluation' in evaluation_results:
        abc_positive = evaluation_results['abc_evaluation']['total_score'] >= 67
        dsm5_positive = evaluation_results['dsm5_evaluation']['meets_criteria']['overall']
        
        if abc_positive and dsm5_positive:
            comparison['key_findings'].append('ABC和DSM-5均提示孤独症特征')
        elif abc_positive or dsm5_positive:
            comparison['key_findings'].append('评估结果存在分歧，建议综合判断')
    
    if 'cars_evaluation' in evaluation_results:
        if evaluation_results['cars_evaluation']['clinical_cutoff']:
            comparison['key_findings'].append(f"CARS评分达到临床阈值（{evaluation_results['cars_evaluation']['total_score']}分）")
    
    if 'assq_evaluation' in evaluation_results:
        if evaluation_results['assq_evaluation']['positive_screen']:
            comparison['key_findings'].append(f"ASSQ筛查阳性（{evaluation_results['assq_evaluation']['total_score']}分）")
    
    return comparison


def generate_evaluation_summary(evaluation_results: Dict[str, Any], scales_used: List[str]) -> Dict[str, Any]:
    """
    生成评估摘要
    
    Args:
        evaluation_results: 各量表评估结果
        scales_used: 使用的量表列表
    
    Returns:
        评估摘要
    """
    summary = {
        'scales_used': scales_used,
        'scale_count': len(scales_used),
        'primary_findings': [],
        'severity_consensus': None,
        'recommendations': []
    }
    
    # 收集主要发现
    positive_indicators = 0
    total_indicators = 0
    
    if 'abc_evaluation' in evaluation_results:
        abc = evaluation_results['abc_evaluation']
        total_indicators += 1
        if abc['clinical_range']:
            positive_indicators += 1
            summary['primary_findings'].append(f"ABC总分{abc['total_score']}，达到孤独症范围")
    
    if 'dsm5_evaluation' in evaluation_results:
        dsm5 = evaluation_results['dsm5_evaluation']
        total_indicators += 1
        if dsm5['meets_criteria']['overall']:
            positive_indicators += 1
            summary['primary_findings'].append(f"符合DSM-5孤独症诊断标准")
    
    if 'cars_evaluation' in evaluation_results:
        cars = evaluation_results['cars_evaluation']
        total_indicators += 1
        if cars['clinical_cutoff']:
            positive_indicators += 1
            summary['primary_findings'].append(f"CARS评分{cars['total_score']}，{cars['severity']}")
    
    if 'assq_evaluation' in evaluation_results:
        assq = evaluation_results['assq_evaluation']
        total_indicators += 1
        if assq['positive_screen']:
            positive_indicators += 1
            summary['primary_findings'].append(f"ASSQ筛查阳性，{assq['risk_level']}")
    
    # 确定整体严重程度共识
    if total_indicators > 0:
        positive_rate = positive_indicators / total_indicators
        if positive_rate >= 0.75:
            summary['severity_consensus'] = '高度一致提示孤独症'
            summary['recommendations'].append('强烈建议进行全面诊断评估')
            summary['recommendations'].append('尽早开始干预服务')
        elif positive_rate >= 0.5:
            summary['severity_consensus'] = '中度一致提示孤独症可能'
            summary['recommendations'].append('建议进一步专业评估')
            summary['recommendations'].append('密切观察和早期干预')
        else:
            summary['severity_consensus'] = '评估结果不一致'
            summary['recommendations'].append('建议综合临床观察')
            summary['recommendations'].append('可考虑重复评估或使用其他工具')
    
    # 添加量表特定建议
    if len(scales_used) < 3:
        summary['recommendations'].append(f"可考虑增加{', '.join([AVAILABLE_SCALES[s]['name'] for s in AVAILABLE_SCALES if s not in scales_used][:2])}评估")
    
    return summary


def get_scale_selection_recommendations(
    age: int = None,
    purpose: str = 'diagnostic',
    time_available: int = 30
) -> Dict[str, Any]:
    """
    根据条件推荐合适的量表组合
    
    Args:
        age: 儿童年龄（月）
        purpose: 评估目的 ('screening'筛查, 'diagnostic'诊断, 'comprehensive'全面)
        time_available: 可用时间（分钟）
    
    Returns:
        推荐的量表组合和说明
    """
    recommendations = {
        'recommended_scales': [],
        'reason': '',
        'estimated_time': 0,
        'alternatives': []
    }
    
    # 根据目的推荐
    if purpose == 'screening':
        recommendations['recommended_scales'] = ['ASSQ', 'ABC']
        recommendations['reason'] = '快速筛查，覆盖主要症状领域'
        recommendations['estimated_time'] = 20
    elif purpose == 'diagnostic':
        recommendations['recommended_scales'] = ['DSM5', 'CARS', 'ABC']
        recommendations['reason'] = '诊断评估，多维度验证'
        recommendations['estimated_time'] = 45
    elif purpose == 'comprehensive':
        recommendations['recommended_scales'] = COMPREHENSIVE_SCALES
        recommendations['reason'] = '全面评估，最大化诊断准确性'
        recommendations['estimated_time'] = 60
    else:
        recommendations['recommended_scales'] = DEFAULT_SCALES
        recommendations['reason'] = '标准评估组合'
        recommendations['estimated_time'] = 30
    
    # 根据年龄调整
    if age is not None:
        age_years = age / 12
        if age_years < 2:
            # CARS和ASSQ不适合2岁以下
            recommendations['recommended_scales'] = [s for s in recommendations['recommended_scales'] 
                                                    if s not in ['CARS', 'ASSQ']]
            recommendations['reason'] += '；考虑年龄因素'
        elif age_years < 6:
            # ASSQ主要用于6岁以上
            recommendations['recommended_scales'] = [s for s in recommendations['recommended_scales'] 
                                                    if s != 'ASSQ']
            if 'CARS' not in recommendations['recommended_scales']:
                recommendations['recommended_scales'].append('CARS')
            recommendations['reason'] += '；CARS适合该年龄段'
    
    # 根据时间限制调整
    if time_available < 30:
        if len(recommendations['recommended_scales']) > 2:
            recommendations['alternatives'].append({
                'scales': recommendations['recommended_scales'][:2],
                'reason': '时间有限，优先核心量表'
            })
    
    return recommendations