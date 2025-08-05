"""孤独症行为分析模块"""
import numpy as np
from typing import List, Dict, Any, Tuple


def extract_behavior_specific_samples(records: List[Dict[str, Any]], 
                                    target_behaviors: List[str], 
                                    logic: str = 'OR') -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    从评估记录中提取包含特定行为的样本
    注意：此功能仅适用于包含identified_behaviors字段的记录
    
    Args:
        records: 评估记录列表
        target_behaviors: 目标行为列表
        logic: 'OR' 或 'AND'，决定多个行为之间的逻辑关系
        
    Returns:
        matched_samples: 匹配的样本列表
        behavior_stats: 行为统计
    """
    matched_samples = []
    behavior_stats = {behavior: 0 for behavior in target_behaviors}
    
    # 处理各种格式的记录
    for record in records:
        # 获取行为数据
        behaviors_data = None
        
        # 新格式
        if 'abc_evaluation' in record and 'identified_behaviors' in record['abc_evaluation']:
            behaviors_data = record['abc_evaluation']['identified_behaviors']
        # 旧格式
        elif 'identified_behaviors' in record:
            behaviors_data = record['identified_behaviors']
        
        if not behaviors_data:
            continue
        
        # 收集该记录中的所有行为
        all_behaviors = []
        for domain, behaviors in behaviors_data.items():
            all_behaviors.extend(behaviors)
        
        # 检查是否匹配目标行为
        matches = []
        for target in target_behaviors:
            # 模糊匹配（包含关键词即可）
            if any(target in behavior for behavior in all_behaviors):
                matches.append(target)
                behavior_stats[target] += 1
        
        # 根据逻辑判断是否加入结果
        if logic == 'OR' and len(matches) > 0:
            matched_samples.append({
                'record': record,
                'matched_behaviors': matches,
                'match_count': len(matches)
            })
        elif logic == 'AND' and len(matches) == len(target_behaviors):
            matched_samples.append({
                'record': record,
                'matched_behaviors': matches,
                'match_count': len(matches)
            })
    
    return matched_samples, behavior_stats


def analyze_behavior_associations(records: List[Dict[str, Any]], 
                                min_support: float = 0.1) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    分析行为之间的关联关系
    支持新旧格式的记录
    
    Args:
        records: 评估记录列表
        min_support: 最小支持度阈值
        
    Returns:
        associations: 关联规则列表
        matrix_data: 共现矩阵数据
    """
    # 收集所有行为
    all_behaviors_list = []
    unique_behaviors = set()
    
    for record in records:
        behaviors_data = None
        
        # 新格式
        if 'abc_evaluation' in record and 'identified_behaviors' in record['abc_evaluation']:
            behaviors_data = record['abc_evaluation']['identified_behaviors']
        # 旧格式
        elif 'identified_behaviors' in record:
            behaviors_data = record['identified_behaviors']
        
        if behaviors_data:
            behaviors = []
            for domain_behaviors in behaviors_data.values():
                behaviors.extend(domain_behaviors)
            all_behaviors_list.append(behaviors)
            unique_behaviors.update(behaviors)
    
    if not all_behaviors_list:
        return [], None
    
    unique_behaviors = list(unique_behaviors)
    n_behaviors = len(unique_behaviors)
    
    # 构建共现矩阵
    co_occurrence = np.zeros((n_behaviors, n_behaviors))
    
    for behaviors in all_behaviors_list:
        for i, behavior1 in enumerate(unique_behaviors):
            if behavior1 in behaviors:
                for j, behavior2 in enumerate(unique_behaviors):
                    if behavior2 in behaviors and i != j:
                        co_occurrence[i][j] += 1
    
    # 计算支持度和置信度
    total_records = len(all_behaviors_list)
    associations = []
    
    for i, behavior1 in enumerate(unique_behaviors):
        behavior1_count = sum(1 for behaviors in all_behaviors_list if behavior1 in behaviors)
        if behavior1_count / total_records < min_support:
            continue
            
        for j, behavior2 in enumerate(unique_behaviors):
            if i == j:
                continue
                
            co_occur_count = co_occurrence[i][j]
            support = co_occur_count / total_records
            
            if support >= min_support:
                confidence = co_occur_count / behavior1_count if behavior1_count > 0 else 0
                lift = (confidence * total_records) / sum(1 for behaviors in all_behaviors_list if behavior2 in behaviors) if sum(1 for behaviors in all_behaviors_list if behavior2 in behaviors) > 0 else 0
                
                associations.append({
                    'behavior1': behavior1,
                    'behavior2': behavior2,
                    'support': support,
                    'confidence': confidence,
                    'lift': lift,
                    'co_occurrences': int(co_occur_count)
                })
    
    # 按置信度排序
    associations.sort(key=lambda x: x['confidence'], reverse=True)
    
    return associations, {'behaviors': unique_behaviors, 'matrix': co_occurrence}


def get_behavior_summary_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    获取行为出现的汇总统计
    支持新旧格式的记录
    
    Returns:
        包含行为统计信息的字典
    """
    behavior_counts = {}
    domain_behavior_counts = {
        "感觉领域": {},
        "交往领域": {},
        "躯体运动领域": {},
        "语言领域": {},
        "社交与自理领域": {}
    }
    
    total_records = 0
    
    for record in records:
        behaviors_data = None
        
        # 新格式
        if 'abc_evaluation' in record and 'identified_behaviors' in record['abc_evaluation']:
            behaviors_data = record['abc_evaluation']['identified_behaviors']
        # 旧格式
        elif 'identified_behaviors' in record:
            behaviors_data = record['identified_behaviors']
        
        if behaviors_data:
            total_records += 1
            
            for domain, behaviors in behaviors_data.items():
                for behavior in behaviors:
                    # 总体统计
                    if behavior not in behavior_counts:
                        behavior_counts[behavior] = 0
                    behavior_counts[behavior] += 1
                    
                    # 分领域统计
                    if domain in domain_behavior_counts:
                        if behavior not in domain_behavior_counts[domain]:
                            domain_behavior_counts[domain][behavior] = 0
                        domain_behavior_counts[domain][behavior] += 1
    
    if total_records == 0:
        return {
            'total_records': 0,
            'unique_behaviors_count': 0,
            'behavior_rankings': [],
            'domain_breakdown': {},
            'most_common': [],
            'least_common': [],
            'note': '无包含行为数据的记录'
        }
    
    # 计算百分比
    behavior_percentages = {
        behavior: {
            'count': count,
            'percentage': count / total_records * 100 if total_records > 0 else 0
        }
        for behavior, count in behavior_counts.items()
    }
    
    # 按出现频率排序
    sorted_behaviors = sorted(
        behavior_percentages.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    # 特殊的相关性分析（适用于统一评估数据）
    correlation_data = _analyze_abc_dsm5_correlation(records)
    
    return {
        'total_records': total_records,
        'unique_behaviors_count': len(behavior_counts),
        'behavior_rankings': sorted_behaviors,
        'domain_breakdown': domain_behavior_counts,
        'most_common': sorted_behaviors[:10] if sorted_behaviors else [],
        'least_common': sorted_behaviors[-10:] if len(sorted_behaviors) > 10 else sorted_behaviors,
        **correlation_data  # 添加相关性分析结果
    }


def _analyze_abc_dsm5_correlation(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析ABC和DSM-5评估的相关性（内部函数）
    仅用于统一评估数据
    """
    # 检查是否有统一评估数据
    unified_records = [r for r in records if 'abc_evaluation' in r and 'dsm5_evaluation' in r]
    
    if len(unified_records) < 3:  # 样本太少，无法计算有效相关性
        return {}
    
    # 收集配对数据
    abc_scores = []
    dsm5_scores = []
    
    for record in unified_records:
        abc_total = record['abc_evaluation']['total_score']
        dsm5_core = record['dsm5_evaluation']['core_symptom_average']
        
        # 标准化ABC分数到0-1范围
        abc_normalized = abc_total / 158  # ABC最高分158
        # DSM-5已经是1-5范围，标准化到0-1
        dsm5_normalized = (dsm5_core - 1) / 4
        
        abc_scores.append(abc_normalized)
        dsm5_scores.append(dsm5_normalized)
    
    # 计算相关系数
    correlation = np.corrcoef(abc_scores, dsm5_scores)[0, 1]
    
    # 计算p值（简化版本）
    n = len(unified_records)
    t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
    # 使用简化的p值判断
    p_value = 2 * (1 - 0.975) if abs(t_stat) > 2.0 else 0.05  # 粗略估计
    
    # 计算一致性
    agreement_count = 0
    for record in unified_records:
        abc_severe = record['abc_evaluation']['total_score'] >= 67
        dsm5_severe = record['dsm5_evaluation']['core_symptom_average'] >= 3.5
        if abc_severe == dsm5_severe:
            agreement_count += 1
    
    agreement_rate = (agreement_count / len(unified_records)) * 100
    
    # 计算平均差异
    differences = []
    for i in range(len(abc_scores)):
        diff = abs(abc_scores[i] - dsm5_scores[i])
        differences.append(diff)
    
    mean_difference = np.mean(differences)
    
    return {
        'correlation': correlation,
        'p_value': p_value,
        'agreement_rate': agreement_rate,
        'mean_difference': mean_difference,
        'unified_sample_size': len(unified_records)
    }