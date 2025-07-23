"""孤独症数据分析模块 - 基于ABC量表"""
import numpy as np
import pandas as pd
from .config import ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS


def generate_clinical_analysis(records):
    """生成基于ABC量表的统计分析报告"""
    if not records:
        return {}
    
    analysis = {}
    
    # 基础统计
    analysis['评估概况'] = {
        '评估总数': len(records),
        '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及严重程度数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # ABC总分分析
    total_scores = [r['abc_total_score'] for r in records]
    analysis['ABC总分统计'] = {
        '平均总分': f"{np.mean(total_scores):.1f}",
        '总分范围': f"{np.min(total_scores):.0f}-{np.max(total_scores):.0f}",
        '标准差': f"{np.std(total_scores):.1f}",
        '中位数': f"{np.median(total_scores):.0f}"
    }
    
    # 严重程度分布
    severity_distribution = {}
    for record in records:
        severity = record['abc_severity']
        if severity not in severity_distribution:
            severity_distribution[severity] = 0
        severity_distribution[severity] += 1
    
    analysis['严重程度分布'] = {
        k: f"{v} ({v/len(records)*100:.1f}%)" 
        for k, v in severity_distribution.items()
    }
    
    # 各领域得分分析
    domain_stats = {}
    for domain in ABC_EVALUATION_METRICS.keys():
        scores = [r['evaluation_scores'][domain] for r in records]
        domain_stats[domain] = {
            '平均分': f"{np.mean(scores):.1f}",
            '最高分': f"{np.max(scores):.0f}",
            '最低分': f"{np.min(scores):.0f}",
            '占满分比例': f"{np.mean(scores)/ABC_EVALUATION_METRICS[domain]['max_score']*100:.1f}%"
        }
    
    analysis['各领域得分分析'] = domain_stats
    
    # 行为出现频率分析
    behavior_frequency = analyze_behavior_frequency(records)
    analysis['高频行为表现'] = behavior_frequency
    
    # 按严重程度组分析
    severity_group_analysis = {}
    for template in set(r.get('template', '自定义') for r in records):
        template_records = [r for r in records if r.get('template', '自定义') == template]
        
        avg_total = np.mean([r['abc_total_score'] for r in template_records])
        domain_avgs = {}
        for domain in ABC_EVALUATION_METRICS.keys():
            scores = [r['evaluation_scores'][domain] for r in template_records]
            domain_avgs[domain] = f"{np.mean(scores):.1f}"
        
        severity_group_analysis[template] = {
            '样本数': len(template_records),
            'ABC平均总分': f"{avg_total:.1f}",
            '各领域平均分': domain_avgs
        }
    
    analysis['严重程度组间分析'] = severity_group_analysis
    
    # 情境效应分析
    context_analysis = {}
    for scene in set(r['scene'] for r in records):
        scene_records = [r for r in records if r['scene'] == scene]
        avg_total = np.mean([r['abc_total_score'] for r in scene_records])
        
        context_analysis[scene] = {
            '评估次数': len(scene_records),
            'ABC平均总分': f"{avg_total:.1f}",
            '主要表现': get_main_behaviors_in_context(scene_records)
        }
    
    analysis['情境效应分析'] = context_analysis
    
    # 临床发现和建议
    findings = generate_clinical_findings(records, analysis)
    analysis['临床发现与建议'] = findings
    
    return analysis


def analyze_behavior_frequency(records):
    """分析行为出现频率"""
    all_behaviors = {}
    
    for record in records:
        if 'identified_behaviors' in record:
            for domain, behaviors in record['identified_behaviors'].items():
                for behavior in behaviors:
                    if behavior not in all_behaviors:
                        all_behaviors[behavior] = 0
                    all_behaviors[behavior] += 1
    
    # 排序并返回前10个高频行为
    sorted_behaviors = sorted(all_behaviors.items(), key=lambda x: x[1], reverse=True)
    
    return {
        behavior: f"出现{count}次 ({count/len(records)*100:.1f}%)" 
        for behavior, count in sorted_behaviors[:10]
    }


def get_main_behaviors_in_context(scene_records):
    """获取特定情境下的主要行为表现"""
    behavior_counts = {}
    
    for record in scene_records:
        if 'identified_behaviors' in record:
            for behaviors in record['identified_behaviors'].values():
                for behavior in behaviors:
                    if behavior not in behavior_counts:
                        behavior_counts[behavior] = 0
                    behavior_counts[behavior] += 1
    
    # 返回前3个最常见的行为
    sorted_behaviors = sorted(behavior_counts.items(), key=lambda x: x[1], reverse=True)
    return [behavior for behavior, _ in sorted_behaviors[:3]]


def generate_clinical_findings(records, analysis):
    """生成临床发现和建议"""
    findings = []
    
    # 基于ABC总分的发现
    avg_total = np.mean([r['abc_total_score'] for r in records])
    
    if avg_total >= 67:
        findings.append("ABC总分显示明确的孤独症表现，建议进行全面的干预治疗")
    elif avg_total >= 53:
        findings.append("ABC总分处于轻度范围，建议早期干预和定期评估")
    elif avg_total >= 40:
        findings.append("ABC总分处于边缘状态，需要密切观察和跟踪评估")
    else:
        findings.append("ABC总分未达到孤独症诊断标准，但仍需关注个别领域的表现")
    
    # 分析各领域表现
    domain_scores = {}
    for domain in ABC_EVALUATION_METRICS.keys():
        scores = [r['evaluation_scores'][domain] for r in records]
        avg_score = np.mean(scores)
        max_score = ABC_EVALUATION_METRICS[domain]['max_score']
        percentage = avg_score / max_score * 100
        domain_scores[domain] = percentage
    
    # 找出最严重的领域
    most_severe_domain = max(domain_scores.items(), key=lambda x: x[1])
    if most_severe_domain[1] > 60:
        domain_name = most_severe_domain[0].replace("得分", "")
        findings.append(f"{domain_name}问题最为突出，应作为干预的重点")
    
    # 基于高频行为的建议
    if '高频行为表现' in analysis:
        high_freq_behaviors = list(analysis['高频行为表现'].keys())
        if any("自伤" in behavior for behavior in high_freq_behaviors[:3]):
            findings.append("存在自伤行为，需要立即采取保护措施和行为干预")
        if any("无语言" in behavior for behavior in high_freq_behaviors[:3]):
            findings.append("语言发展严重滞后，建议加强语言和沟通训练")
        if any("攻击" in behavior for behavior in high_freq_behaviors[:3]):
            findings.append("有攻击性行为，需要行为管理和情绪调节训练")
    
    # 基于领域分析的具体建议
    if domain_scores.get("感觉领域得分", 0) > 50:
        findings.append("感觉处理异常明显，建议进行感觉统合训练")
    
    if domain_scores.get("交往领域得分", 0) > 60:
        findings.append("社交障碍严重，需要加强社交技能训练和同伴互动")
    
    if domain_scores.get("语言领域得分", 0) > 60:
        findings.append("语言沟通严重受损，建议语言治疗和替代沟通方式")
    
    # 情境相关建议
    if '情境效应分析' in analysis:
        # 找出表现最好的情境
        context_scores = {
            context: float(data['ABC平均总分']) 
            for context, data in analysis['情境效应分析'].items()
        }
        best_context = min(context_scores.items(), key=lambda x: x[1])
        findings.append(f"在{best_context[0]}中表现相对较好，可作为干预的起点")
    
    return findings


def prepare_clinical_export_data(records):
    """准备ABC量表数据导出"""
    export_data = []
    
    for record in records:
        profile = record.get('autism_profile', {})
        scores = record['evaluation_scores']
        
        export_row = {
            '评估ID': record['experiment_id'],
            '评估时间': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '严重程度分级': record.get('template', '自定义'),
            'ABC严重程度判定': record['abc_severity'],
            '评估情境': record['scene'],
            '观察活动': record.get('activity', ''),
            '触发因素': record.get('trigger', ''),
            'ABC总分': record['abc_total_score'],
            '感觉领域得分': scores['感觉领域得分'],
            '交往领域得分': scores['交往领域得分'],
            '躯体运动领域得分': scores['躯体运动领域得分'],
            '语言领域得分': scores['语言领域得分'],
            '社交与自理领域得分': scores['社交与自理领域得分'],
            '备注': record.get('notes', '')
        }
        
        # 添加ABC配置信息
        if profile:
            export_row.update({
                '配置描述': profile.get('description', ''),
                '感觉异常程度': f"{profile.get('sensory_abnormal', 0)*100:.0f}%",
                '交往障碍程度': f"{profile.get('social_impairment', 0)*100:.0f}%",
                '运动刻板程度': f"{profile.get('motor_stereotypy', 0)*100:.0f}%",
                '语言缺陷程度': f"{profile.get('language_deficit', 0)*100:.0f}%",
                '自理缺陷程度': f"{profile.get('self_care_deficit', 0)*100:.0f}%",
                '行为频率': f"{profile.get('behavior_frequency', 0)*100:.0f}%"
            })
        
        # 添加识别到的具体行为
        if 'identified_behaviors' in record:
            all_behaviors = []
            for domain, behaviors in record['identified_behaviors'].items():
                all_behaviors.extend(behaviors)
            export_row['识别到的行为'] = '; '.join(all_behaviors[:10])  # 最多显示10个
        
        export_data.append(export_row)
    
    return export_data

# ========== 新增：小群体特征提取功能 ==========

def extract_behavior_specific_samples(records, target_behaviors, logic='OR'):
    """
    从评估记录中提取包含特定行为的样本
    
    参数:
    - records: 所有评估记录列表
    - target_behaviors: 目标行为列表，如["无语言", "重复动作", "目光回避"]
    - logic: 'OR'表示包含任一行为，'AND'表示必须包含所有行为
    
    返回:
    - matched_samples: 符合条件的样本列表
    - behavior_stats: 行为统计信息
    """
    matched_samples = []
    behavior_stats = {behavior: 0 for behavior in target_behaviors}
    
    for record in records:
        if 'identified_behaviors' not in record:
            continue
            
        # 收集该记录中的所有行为
        all_behaviors = []
        for domain, behaviors in record['identified_behaviors'].items():
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


def calculate_sample_similarity(record1, record2, weights=None):
    """
    计算两个样本之间的相似度
    
    参数:
    - record1, record2: 两个评估记录
    - weights: 各领域权重字典，默认均等权重
    
    返回:
    - similarity: 相似度分数（0-1）
    - details: 详细的相似度信息
    """
    if weights is None:
        weights = {
            '感觉领域得分': 1.0,
            '交往领域得分': 1.0,
            '躯体运动领域得分': 1.0,
            '语言领域得分': 1.0,
            '社交与自理领域得分': 1.0
        }
    
    # 计算各领域得分的差异
    score_diffs = {}
    weighted_diff_sum = 0
    weight_sum = 0
    
    for domain in record1['evaluation_scores'].keys():
        score1 = record1['evaluation_scores'][domain]
        score2 = record2['evaluation_scores'][domain]
        max_score = ABC_EVALUATION_METRICS[domain]['max_score']
        
        # 归一化差异
        normalized_diff = abs(score1 - score2) / max_score
        score_diffs[domain] = normalized_diff
        
        # 加权求和
        weight = weights.get(domain, 1.0)
        weighted_diff_sum += normalized_diff * weight
        weight_sum += weight
    
    # 计算相似度（1 - 平均差异）
    avg_diff = weighted_diff_sum / weight_sum if weight_sum > 0 else 1.0
    similarity = 1 - avg_diff
    
    # 计算行为相似度
    behaviors1 = set()
    behaviors2 = set()
    
    if 'identified_behaviors' in record1:
        for behaviors in record1['identified_behaviors'].values():
            behaviors1.update(behaviors)
    
    if 'identified_behaviors' in record2:
        for behaviors in record2['identified_behaviors'].values():
            behaviors2.update(behaviors)
    
    # Jaccard相似度
    if behaviors1 or behaviors2:
        intersection = len(behaviors1 & behaviors2)
        union = len(behaviors1 | behaviors2)
        behavior_similarity = intersection / union if union > 0 else 0
    else:
        behavior_similarity = 0
    
    # 综合相似度（得分相似度和行为相似度的加权平均）
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


def find_similar_samples(target_record, all_records, threshold=0.7, max_results=10):
    """
    查找与目标样本相似的其他样本
    
    参数:
    - target_record: 目标评估记录
    - all_records: 所有评估记录列表
    - threshold: 相似度阈值（0-1）
    - max_results: 最大返回结果数
    
    返回:
    - similar_samples: 相似样本列表，按相似度降序排列
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


def analyze_behavior_associations(records, min_support=0.1):
    """
    分析行为之间的关联关系
    
    参数:
    - records: 评估记录列表
    - min_support: 最小支持度（出现频率阈值）
    
    返回:
    - associations: 行为关联规则列表
    - co_occurrence_matrix: 行为共现矩阵
    """
    # 收集所有行为
    all_behaviors_list = []
    unique_behaviors = set()
    
    for record in records:
        if 'identified_behaviors' in record:
            behaviors = []
            for domain_behaviors in record['identified_behaviors'].values():
                behaviors.extend(domain_behaviors)
            all_behaviors_list.append(behaviors)
            unique_behaviors.update(behaviors)
    
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
    total_records = len(records)
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


def get_behavior_summary_stats(records):
    """
    获取行为出现的汇总统计
    
    参数:
    - records: 评估记录列表
    
    返回:
    - behavior_stats: 行为统计信息字典
    """
    behavior_counts = {}
    domain_behavior_counts = {
        "感觉领域": {},
        "交往领域": {},
        "躯体运动领域": {},
        "语言领域": {},
        "社交与自理领域": {}
    }
    
    for record in records:
        if 'identified_behaviors' in record:
            for domain, behaviors in record['identified_behaviors'].items():
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
    
    # 计算百分比
    total_records = len(records)
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
    
    return {
        'total_records': total_records,
        'unique_behaviors_count': len(behavior_counts),
        'behavior_rankings': sorted_behaviors,
        'domain_breakdown': domain_behavior_counts,
        'most_common': sorted_behaviors[:10] if sorted_behaviors else [],
        'least_common': sorted_behaviors[-10:] if len(sorted_behaviors) > 10 else sorted_behaviors
    }