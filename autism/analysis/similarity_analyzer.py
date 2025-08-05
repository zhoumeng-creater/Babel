"""孤独症评估相似度计算模块"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

from ..configs import ABC_EVALUATION_METRICS, DSM5_EVALUATION_METRICS


def calculate_sample_similarity(record1: Dict[str, Any], 
                              record2: Dict[str, Any], 
                              weights: Optional[Dict[str, float]] = None) -> Tuple[float, Dict[str, Any]]:
    """
    计算两个样本之间的相似度
    支持新旧格式的记录
    
    Args:
        record1: 第一个评估记录
        record2: 第二个评估记录
        weights: 各维度权重（可选）
        
    Returns:
        similarity: 相似度分数（0-1）
        details: 相似度计算细节
    """
    # 提取评估数据
    def extract_evaluation_data(record):
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            # 新格式
            return {
                'format': 'unified',
                'abc_scores': record['abc_evaluation']['domain_scores'],
                'abc_behaviors': record['abc_evaluation'].get('identified_behaviors', {}),
                'dsm5_scores': record['dsm5_evaluation']['scores']
            }
        elif 'assessment_standard' in record:
            # 旧格式
            if record['assessment_standard'] == 'ABC':
                return {
                    'format': 'abc',
                    'abc_scores': record.get('evaluation_scores', {}),
                    'abc_behaviors': record.get('identified_behaviors', {})
                }
            else:
                return {
                    'format': 'dsm5',
                    'dsm5_scores': record.get('evaluation_scores', {})
                }
        return None
    
    data1 = extract_evaluation_data(record1)
    data2 = extract_evaluation_data(record2)
    
    if not data1 or not data2:
        return 0.0, {'error': '无法提取评估数据'}
    
    # 如果两者都有ABC数据，计算ABC相似度
    if 'abc_scores' in data1 and 'abc_scores' in data2:
        return calculate_abc_similarity_internal(data1, data2, weights)
    
    # 如果两者都有DSM5数据，计算DSM5相似度
    if 'dsm5_scores' in data1 and 'dsm5_scores' in data2:
        return calculate_dsm5_similarity_internal(data1, data2, weights)
    
    return 0.0, {'error': '无共同评估标准'}


def calculate_abc_similarity_internal(data1: Dict[str, Any], 
                                    data2: Dict[str, Any], 
                                    weights: Optional[Dict[str, float]] = None) -> Tuple[float, Dict[str, Any]]:
    """计算ABC相似度（内部函数）"""
    if weights is None:
        weights = {domain: 1.0 for domain in ABC_EVALUATION_METRICS.keys()}
    
    scores1 = data1['abc_scores']
    scores2 = data2['abc_scores']
    
    # 计算各领域得分的差异
    score_diffs = {}
    weighted_diff_sum = 0
    weight_sum = 0
    
    for domain in ABC_EVALUATION_METRICS.keys():
        if domain in scores1 and domain in scores2:
            score1 = scores1[domain]
            score2 = scores2[domain]
            max_score = ABC_EVALUATION_METRICS[domain]['max_score']
            
            # 归一化差异
            normalized_diff = abs(score1 - score2) / max_score
            score_diffs[domain] = normalized_diff
            
            # 加权求和
            weight = weights.get(domain, 1.0)
            weighted_diff_sum += normalized_diff * weight
            weight_sum += weight
    
    # 计算相似度
    avg_diff = weighted_diff_sum / weight_sum if weight_sum > 0 else 1.0
    similarity = 1 - avg_diff
    
    # 计算行为相似度
    behaviors1 = set()
    behaviors2 = set()
    
    for behaviors in data1.get('abc_behaviors', {}).values():
        behaviors1.update(behaviors)
    
    for behaviors in data2.get('abc_behaviors', {}).values():
        behaviors2.update(behaviors)
    
    # Jaccard相似度
    behavior_similarity = 0
    if behaviors1 or behaviors2:
        intersection = len(behaviors1 & behaviors2)
        union = len(behaviors1 | behaviors2)
        behavior_similarity = intersection / union if union > 0 else 0
    
    # 综合相似度
    total_similarity = 0.7 * similarity + 0.3 * behavior_similarity
    
    details = {
        'score_similarity': similarity,
        'behavior_similarity': behavior_similarity,
        'total_similarity': total_similarity,
        'score_differences': score_diffs,
        'common_behaviors': list(behaviors1 & behaviors2),
        'unique_to_record1': list(behaviors1 - behaviors2),
        'unique_to_record2': list(behaviors2 - behaviors1)
    }
    
    return total_similarity, details


def calculate_dsm5_similarity_internal(data1: Dict[str, Any], 
                                     data2: Dict[str, Any], 
                                     weights: Optional[Dict[str, float]] = None) -> Tuple[float, Dict[str, Any]]:
    """计算DSM-5相似度（内部函数）"""
    if weights is None:
        weights = {metric: 1.0 for metric in DSM5_EVALUATION_METRICS.keys()}
    
    scores1 = data1['dsm5_scores']
    scores2 = data2['dsm5_scores']
    
    # 计算各维度得分的差异
    score_diffs = {}
    weighted_diff_sum = 0
    weight_sum = 0
    
    for metric in DSM5_EVALUATION_METRICS.keys():
        if metric in scores1 and metric in scores2:
            score1 = scores1[metric]
            score2 = scores2[metric]
            
            # 归一化差异（DSM-5分数范围是1-5）
            normalized_diff = abs(score1 - score2) / 4.0
            score_diffs[metric] = normalized_diff
            
            # 加权求和
            weight = weights.get(metric, 1.0)
            weighted_diff_sum += normalized_diff * weight
            weight_sum += weight
    
    # 计算相似度
    avg_diff = weighted_diff_sum / weight_sum if weight_sum > 0 else 1.0
    similarity = 1 - avg_diff
    
    details = {
        'score_similarity': similarity,
        'total_similarity': similarity,
        'score_differences': score_diffs
    }
    
    return similarity, details


def find_similar_samples(target_record: Dict[str, Any], 
                        all_records: List[Dict[str, Any]], 
                        threshold: float = 0.7, 
                        max_results: int = 10) -> List[Dict[str, Any]]:
    """
    查找与目标样本相似的其他样本
    支持新旧格式的记录
    
    Args:
        target_record: 目标记录
        all_records: 所有记录列表
        threshold: 相似度阈值
        max_results: 最大返回结果数
        
    Returns:
        相似样本列表
    """
    similar_samples = []
    
    for record in all_records:
        # 跳过自身
        if record['experiment_id'] == target_record['experiment_id']:
            continue
        
        similarity, details = calculate_sample_similarity(target_record, record)
        
        if similarity >= threshold:
            similar_samples.append({
                'record': record,
                'similarity': similarity,
                'details': details
            })
    
    # 按相似度降序排序
    similar_samples.sort(key=lambda x: x['similarity'], reverse=True)
    
    # 限制返回数量
    return similar_samples[:max_results]