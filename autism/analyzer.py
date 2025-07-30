"""孤独症数据分析模块 - 支持DSM-5和ABC双标准"""
import numpy as np
import pandas as pd
from .config import ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS, DSM5_EVALUATION_METRICS


def generate_clinical_analysis(records):
    """生成临床分析报告 - 自动识别并处理DSM-5和ABC两种标准"""
    if not records:
        return {}
    
    # 识别数据类型
    assessment_standards = [r.get('assessment_standard', 'ABC') for r in records]
    unique_standards = list(set(assessment_standards))
    
    if len(unique_standards) == 1:
        # 单一标准
        if unique_standards[0] == 'DSM5':
            return generate_dsm5_analysis(records)
        else:
            return generate_abc_analysis(records)
    else:
        # 混合标准
        return generate_mixed_analysis(records)


def generate_abc_analysis(records):
    """生成基于ABC量表的统计分析报告"""
    if not records:
        return {}
    
    analysis = {}
    
    # 基础统计
    analysis['评估概况'] = {
        '评估总数': len(records),
        '评估标准': 'ABC孤独症行为量表',
        '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及严重程度数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # ABC总分分析
    total_scores = [r['abc_total_score'] for r in records if 'abc_total_score' in r]
    if total_scores:
        analysis['ABC总分统计'] = {
            '平均总分': f"{np.mean(total_scores):.1f}",
            '总分范围': f"{np.min(total_scores):.0f}-{np.max(total_scores):.0f}",
            '标准差': f"{np.std(total_scores):.1f}",
            '中位数': f"{np.median(total_scores):.0f}"
        }
    
    # 严重程度分布
    severity_distribution = {}
    for record in records:
        if 'abc_severity' in record:
            severity = record['abc_severity']
            if severity not in severity_distribution:
                severity_distribution[severity] = 0
            severity_distribution[severity] += 1
    
    if severity_distribution:
        analysis['严重程度分布'] = {
            k: f"{v} ({v/len(records)*100:.1f}%)" 
            for k, v in severity_distribution.items()
        }
    
    # 各领域得分分析
    domain_stats = {}
    for domain in ABC_EVALUATION_METRICS.keys():
        scores = [r['evaluation_scores'][domain] for r in records if domain in r.get('evaluation_scores', {})]
        if scores:
            domain_stats[domain] = {
                '平均分': f"{np.mean(scores):.1f}",
                '最高分': f"{np.max(scores):.0f}",
                '最低分': f"{np.min(scores):.0f}",
                '占满分比例': f"{np.mean(scores)/ABC_EVALUATION_METRICS[domain]['max_score']*100:.1f}%"
            }
    
    if domain_stats:
        analysis['各领域得分分析'] = domain_stats
    
    # 行为出现频率分析
    behavior_frequency = analyze_abc_behavior_frequency(records)
    if behavior_frequency:
        analysis['高频行为表现'] = behavior_frequency
    
    # 按严重程度组分析
    severity_group_analysis = analyze_by_severity_abc(records)
    if severity_group_analysis:
        analysis['严重程度组间分析'] = severity_group_analysis
    
    # 情境效应分析
    context_analysis = analyze_by_context_abc(records)
    if context_analysis:
        analysis['情境效应分析'] = context_analysis
    
    # 临床发现和建议
    findings = generate_abc_findings(records, analysis)
    analysis['临床发现与建议'] = findings
    
    return analysis


def generate_dsm5_analysis(records):
    """生成基于DSM-5标准的统计分析报告"""
    if not records:
        return {}
    
    analysis = {}
    
    # 基础统计
    analysis['评估概况'] = {
        '评估总数': len(records),
        '评估标准': 'DSM-5孤独症诊断标准',
        '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及严重程度数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # 按严重程度分析
    severity_stats = analyze_by_severity_dsm5(records)
    if severity_stats:
        analysis['严重程度分析'] = severity_stats
    
    # 按评估情境分析
    context_stats = analyze_by_context_dsm5(records)
    if context_stats:
        analysis['情境分析'] = context_stats
    
    # 整体临床表现
    overall_performance = analyze_overall_dsm5(records)
    if overall_performance:
        analysis['整体临床表现'] = overall_performance
    
    # 临床发现和建议
    findings = generate_dsm5_findings(records, analysis)
    analysis['临床发现与建议'] = findings
    
    return analysis


def generate_mixed_analysis(records):
    """生成混合标准（ABC和DSM-5）的分析报告"""
    # 分离不同标准的记录
    abc_records = [r for r in records if r.get('assessment_standard', 'ABC') == 'ABC']
    dsm5_records = [r for r in records if r.get('assessment_standard', 'ABC') == 'DSM5']
    
    analysis = {
        '评估概况': {
            '总评估数': len(records),
            'ABC评估数': len(abc_records),
            'DSM-5评估数': len(dsm5_records),
            '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}"
        }
    }
    
    # 分别分析
    if abc_records:
        analysis['ABC量表分析'] = generate_abc_analysis(abc_records)
    
    if dsm5_records:
        analysis['DSM-5标准分析'] = generate_dsm5_analysis(dsm5_records)
    
    # 综合建议
    analysis['综合临床建议'] = [
        f"共进行了{len(abc_records)}次ABC评估和{len(dsm5_records)}次DSM-5评估",
        "建议结合两种评估标准的结果制定综合干预方案",
        "ABC量表侧重行为频率统计，DSM-5侧重症状严重程度评估"
    ]
    
    return analysis


# ABC分析辅助函数
def analyze_abc_behavior_frequency(records):
    """分析ABC行为出现频率"""
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


def analyze_by_severity_abc(records):
    """按严重程度分析ABC数据"""
    severity_stats = {}
    
    for record in records:
        severity = record.get('template', '自定义')
        if severity not in severity_stats:
            severity_stats[severity] = {
                '评估次数': 0,
                'ABC总分': [],
                '各领域得分': {domain: [] for domain in ABC_EVALUATION_METRICS.keys()}
            }
        
        severity_stats[severity]['评估次数'] += 1
        if 'abc_total_score' in record:
            severity_stats[severity]['ABC总分'].append(record['abc_total_score'])
        
        for domain in ABC_EVALUATION_METRICS.keys():
            if domain in record.get('evaluation_scores', {}):
                severity_stats[severity]['各领域得分'][domain].append(record['evaluation_scores'][domain])
    
    # 计算统计值
    for severity, stats in severity_stats.items():
        if stats['ABC总分']:
            stats['ABC平均总分'] = f"{np.mean(stats['ABC总分']):.1f}"
            stats['ABC总分标准差'] = f"{np.std(stats['ABC总分']):.1f}"
        
        for domain, scores in stats['各领域得分'].items():
            if scores:
                stats[f'{domain}_均值'] = np.mean(scores)
                stats[f'{domain}_标准差'] = np.std(scores)
        
        del stats['ABC总分']
        del stats['各领域得分']
    
    return severity_stats


def analyze_by_context_abc(records):
    """按情境分析ABC数据"""
    context_stats = {}
    
    for record in records:
        context = record['scene']
        if context not in context_stats:
            context_stats[context] = {
                '评估次数': 0,
                'ABC总分': []
            }
        
        context_stats[context]['评估次数'] += 1
        if 'abc_total_score' in record:
            context_stats[context]['ABC总分'].append(record['abc_total_score'])
    
    # 计算统计值并获取主要行为
    for context, stats in context_stats.items():
        if stats['ABC总分']:
            stats['ABC平均总分'] = f"{np.mean(stats['ABC总分']):.1f}"
        
        # 获取该情境下的主要行为
        context_records = [r for r in records if r['scene'] == context]
        stats['主要表现'] = get_main_behaviors_in_context(context_records)
        
        del stats['ABC总分']
    
    return context_stats


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


def generate_abc_findings(records, analysis):
    """生成ABC的临床发现和建议"""
    findings = []
    
    # 基于ABC总分的发现
    if 'ABC总分统计' in analysis:
        avg_total = float(analysis['ABC总分统计']['平均总分'])
        
        if avg_total >= 67:
            findings.append("ABC总分显示明确的孤独症表现，建议进行全面的干预治疗")
        elif avg_total >= 53:
            findings.append("ABC总分处于轻度范围，建议早期干预和定期评估")
        elif avg_total >= 40:
            findings.append("ABC总分处于边缘状态，需要密切观察和跟踪评估")
        else:
            findings.append("ABC总分未达到孤独症诊断标准，但仍需关注个别领域的表现")
    
    # 分析各领域表现
    if '各领域得分分析' in analysis:
        domain_scores = {}
        for domain, stats in analysis['各领域得分分析'].items():
            avg_score = float(stats['平均分'])
            max_score = ABC_EVALUATION_METRICS[domain]['max_score']
            percentage = avg_score / max_score * 100
            domain_scores[domain] = percentage
        
        # 找出最严重的领域
        if domain_scores:
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
    if '各领域得分分析' in analysis:
        for domain in analysis['各领域得分分析']:
            avg_score = float(analysis['各领域得分分析'][domain]['平均分'])
            max_score = ABC_EVALUATION_METRICS[domain]['max_score']
            percentage = avg_score / max_score * 100
            
            if "感觉" in domain and percentage > 50:
                findings.append("感觉处理异常明显，建议进行感觉统合训练")
            elif "交往" in domain and percentage > 60:
                findings.append("社交障碍严重，需要加强社交技能训练和同伴互动")
            elif "语言" in domain and percentage > 60:
                findings.append("语言沟通严重受损，建议语言治疗和替代沟通方式")
    
    # 情境相关建议
    if '情境效应分析' in analysis:
        # 找出表现最好的情境
        context_scores = {
            context: float(data['ABC平均总分']) 
            for context, data in analysis['情境效应分析'].items()
            if 'ABC平均总分' in data
        }
        if context_scores:
            best_context = min(context_scores.items(), key=lambda x: x[1])
            findings.append(f"在{best_context[0]}中表现相对较好，可作为干预的起点")
    
    return findings


# DSM-5分析辅助函数
def analyze_by_severity_dsm5(records):
    """按严重程度分析DSM-5数据"""
    severity_stats = {}
    
    for record in records:
        severity = record.get('template', '自定义')
        if severity not in severity_stats:
            severity_stats[severity] = {
                '评估次数': 0,
                '各指标得分': {metric: [] for metric in DSM5_EVALUATION_METRICS.keys()}
            }
        
        severity_stats[severity]['评估次数'] += 1
        
        for metric in DSM5_EVALUATION_METRICS.keys():
            if metric in record.get('evaluation_scores', {}):
                severity_stats[severity]['各指标得分'][metric].append(record['evaluation_scores'][metric])
    
    # 计算统计值
    for severity, stats in severity_stats.items():
        for metric, scores in stats['各指标得分'].items():
            if scores:
                stats[f'{metric}_均值'] = np.mean(scores)
                stats[f'{metric}_标准差'] = np.std(scores)
                stats[f'{metric}_范围'] = f"{np.min(scores):.1f}-{np.max(scores):.1f}"
        
        del stats['各指标得分']
    
    return severity_stats


def analyze_by_context_dsm5(records):
    """按情境分析DSM-5数据"""
    context_stats = {}
    
    for record in records:
        context = record['scene']
        if context not in context_stats:
            context_stats[context] = {
                '评估次数': 0,
                '核心症状得分': []
            }
        
        context_stats[context]['评估次数'] += 1
        
        # 计算核心症状综合得分
        if all(metric in record.get('evaluation_scores', {}) for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
            core_score = (record['evaluation_scores']['社交互动质量'] + 
                         record['evaluation_scores']['沟通交流能力'] + 
                         record['evaluation_scores']['刻板重复行为']) / 3
            context_stats[context]['核心症状得分'].append(core_score)
    
    # 计算统计值
    for context, stats in context_stats.items():
        if stats['核心症状得分']:
            stats['核心症状均值'] = f"{np.mean(stats['核心症状得分']):.2f}"
            stats['核心症状标准差'] = f"{np.std(stats['核心症状得分']):.2f}"
        
        del stats['核心症状得分']
    
    return context_stats


def analyze_overall_dsm5(records):
    """分析DSM-5整体表现"""
    metrics = {metric: [] for metric in DSM5_EVALUATION_METRICS.keys()}
    
    for record in records:
        for metric in DSM5_EVALUATION_METRICS.keys():
            if metric in record.get('evaluation_scores', {}):
                metrics[metric].append(record['evaluation_scores'][metric])
    
    overall = {}
    for metric, scores in metrics.items():
        if scores:
            overall[f'{metric}程度'] = f"{np.mean(scores):.2f} ± {np.std(scores):.2f}"
    
    # 计算核心症状综合严重度
    if all(len(metrics[m]) > 0 for m in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
        core_severity = (np.mean(metrics['社交互动质量']) + 
                        np.mean(metrics['沟通交流能力']) + 
                        np.mean(metrics['刻板重复行为'])) / 3
        overall['核心症状综合严重度'] = f"{core_severity:.2f}"
    
    return overall


def generate_dsm5_findings(records, analysis):
    """生成DSM-5的临床发现和建议"""
    findings = []
    
    # 分析核心症状
    if '整体临床表现' in analysis and '核心症状综合严重度' in analysis['整体临床表现']:
        core_severity = float(analysis['整体临床表现']['核心症状综合严重度'])
        
        if core_severity >= 4.0:
            findings.append("核心症状严重，建议密集型干预治疗")
        elif core_severity >= 3.0:
            findings.append("核心症状中等，建议结构化教学和行为干预")
        else:
            findings.append("核心症状相对较轻，建议社交技能训练")
    
    # 分析各维度表现
    if '整体临床表现' in analysis:
        for metric, value in analysis['整体临床表现'].items():
            if '±' in value:  # 这是一个统计值
                avg_score = float(value.split('±')[0].strip())
                
                if '感官处理' in metric and avg_score >= 4.0:
                    findings.append("存在明显感官处理异常，建议感觉统合治疗")
                elif '情绪行为调节' in metric and avg_score >= 4.0:
                    findings.append("情绪调节困难显著，建议心理行为干预")
                elif '认知适应' in metric and avg_score >= 4.0:
                    findings.append("认知适应功能严重受损，需要特殊教育支持")
    
    # 分析最优情境
    if '情境分析' in analysis:
        context_scores = {}
        for context, data in analysis['情境分析'].items():
            if '核心症状均值' in data:
                context_scores[context] = float(data['核心症状均值'])
        
        if context_scores:
            best_context = min(context_scores.items(), key=lambda x: x[1])
            findings.append(f"在{best_context[0]}中表现相对较好，可作为干预起点")
    
    return findings


def prepare_clinical_export_data(records):
    """准备临床数据导出 - 支持DSM-5和ABC双标准"""
    export_data = []
    
    for record in records:
        assessment_standard = record.get('assessment_standard', 'ABC')
        
        # 基础信息
        export_row = {
            '评估ID': record['experiment_id'],
            '评估时间': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '评估标准': assessment_standard,
            '严重程度分级': record.get('template', '自定义'),
            '评估情境': record['scene'],
            '观察活动': record.get('activity', ''),
            '触发因素': record.get('trigger', ''),
            '备注': record.get('notes', '')
        }
        
        # 根据评估标准添加不同的数据
        if assessment_standard == 'ABC':
            # ABC特有数据
            export_row.update({
                'ABC总分': record.get('abc_total_score', ''),
                'ABC严重程度判定': record.get('abc_severity', ''),
            })
            
            # ABC各领域得分
            scores = record.get('evaluation_scores', {})
            for domain in ABC_EVALUATION_METRICS.keys():
                export_row[domain] = scores.get(domain, '')
            
            # ABC配置信息
            if record.get('autism_profile'):
                profile = record['autism_profile']
                export_row.update({
                    '配置描述': profile.get('description', ''),
                    '感觉异常程度': f"{profile.get('sensory_abnormal', 0)*100:.0f}%",
                    '交往障碍程度': f"{profile.get('social_impairment', 0)*100:.0f}%",
                    '运动刻板程度': f"{profile.get('motor_stereotypy', 0)*100:.0f}%",
                    '语言缺陷程度': f"{profile.get('language_deficit', 0)*100:.0f}%",
                    '自理缺陷程度': f"{profile.get('self_care_deficit', 0)*100:.0f}%",
                    '行为频率': f"{profile.get('behavior_frequency', 0)*100:.0f}%"
                })
            
            # 识别到的行为
            if 'identified_behaviors' in record:
                all_behaviors = []
                for domain, behaviors in record['identified_behaviors'].items():
                    all_behaviors.extend(behaviors)
                export_row['识别到的行为'] = '; '.join(all_behaviors[:10])
                
        else:  # DSM-5
            # DSM-5特有数据
            scores = record.get('evaluation_scores', {})
            
            # 计算核心症状综合严重度
            if all(metric in scores for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                core_severity = (scores['社交互动质量'] + 
                               scores['沟通交流能力'] + 
                               scores['刻板重复行为']) / 3
                export_row['核心症状综合严重度'] = round(core_severity, 2)
            
            # DSM-5各维度得分
            for metric in DSM5_EVALUATION_METRICS.keys():
                export_row[metric] = scores.get(metric, '')
            
            # DSM-5配置信息
            if record.get('autism_profile'):
                profile = record['autism_profile']
                export_row.update({
                    'DSM5严重程度': profile.get('dsm5_severity', ''),
                    '所需支持水平': profile.get('support_needs', ''),
                    '社交沟通缺陷设置': profile.get('social_communication', ''),
                    '刻板重复行为设置': profile.get('restricted_repetitive', ''),
                    '感官处理设置': profile.get('sensory_processing', ''),
                    '认知功能设置': profile.get('cognitive_function', ''),
                    '适应行为设置': profile.get('adaptive_behavior', ''),
                    '语言发展设置': profile.get('language_level', ''),
                    '特殊兴趣': profile.get('special_interests', '')
                })
            
            # 临床观察
            if 'clinical_observations' in record:
                observations = []
                for category, obs_list in record['clinical_observations'].items():
                    observations.extend([f"[{category}] {obs}" for obs in obs_list])
                export_row['临床观察'] = '; '.join(observations[:10])
        
        export_data.append(export_row)
    
    return export_data


# ========== ABC专用高级分析功能 ==========
# 注意：以下功能仅适用于ABC量表评估数据

def extract_behavior_specific_samples(records, target_behaviors, logic='OR'):
    """
    从评估记录中提取包含特定行为的样本 【仅支持ABC评估数据】
    
    参数:
    - records: 所有评估记录列表
    - target_behaviors: 目标行为列表，如["无语言", "重复动作", "目光回避"]
    - logic: 'OR'表示包含任一行为，'AND'表示必须包含所有行为
    
    返回:
    - matched_samples: 符合条件的样本列表
    - behavior_stats: 行为统计信息
    
    注意：此功能仅适用于ABC量表评估，因为只有ABC评估包含详细的行为识别数据
    """
    matched_samples = []
    behavior_stats = {behavior: 0 for behavior in target_behaviors}
    
    # 只处理ABC记录（有identified_behaviors字段）
    abc_records = [r for r in records if 'identified_behaviors' in r and r.get('assessment_standard', 'ABC') == 'ABC']
    
    if not abc_records:
        print("警告：没有找到ABC评估记录，无法进行行为筛选")
        return matched_samples, behavior_stats
    
    for record in abc_records:
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
    
    注意：ABC和DSM-5使用不同的相似度计算方法
    """
    # 检查是否为相同评估标准
    if record1.get('assessment_standard', 'ABC') != record2.get('assessment_standard', 'ABC'):
        return 0.0, {'error': '评估标准不同，无法比较'}
    
    assessment_standard = record1.get('assessment_standard', 'ABC')
    
    if assessment_standard == 'ABC':
        return calculate_abc_similarity(record1, record2, weights)
    else:
        return calculate_dsm5_similarity(record1, record2, weights)


def calculate_abc_similarity(record1, record2, weights=None):
    """计算ABC样本相似度"""
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
        if domain in ABC_EVALUATION_METRICS:
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


def calculate_dsm5_similarity(record1, record2, weights=None):
    """计算DSM-5样本相似度"""
    if weights is None:
        weights = {metric: 1.0 for metric in DSM5_EVALUATION_METRICS.keys()}
    
    # 计算各维度得分的差异
    score_diffs = {}
    weighted_diff_sum = 0
    weight_sum = 0
    
    for metric in record1['evaluation_scores'].keys():
        if metric in DSM5_EVALUATION_METRICS:
            score1 = record1['evaluation_scores'][metric]
            score2 = record2['evaluation_scores'][metric]
            
            # 归一化差异（DSM-5使用1-5分制）
            normalized_diff = abs(score1 - score2) / 4.0  # 最大差异为4
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
    
    注意：只能比较相同评估标准的记录
    """
    similar_samples = []
    
    for record in all_records:
        # 跳过自身
        if record['experiment_id'] == target_record['experiment_id']:
            continue
        
        # 只比较相同评估标准的记录
        if record.get('assessment_standard', 'ABC') != target_record.get('assessment_standard', 'ABC'):
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
    分析行为之间的关联关系 【仅支持ABC评估数据】
    
    参数:
    - records: 评估记录列表
    - min_support: 最小支持度（出现频率阈值）
    
    返回:
    - associations: 行为关联规则列表
    - co_occurrence_matrix: 行为共现矩阵
    
    注意：此功能仅适用于ABC量表评估，因为只有ABC评估包含详细的行为识别数据
    """
    # 只处理ABC记录
    abc_records = [r for r in records if 'identified_behaviors' in r and r.get('assessment_standard', 'ABC') == 'ABC']
    
    if not abc_records:
        print("警告：没有找到ABC评估记录，无法进行行为关联分析")
        return [], None
    
    # 收集所有行为
    all_behaviors_list = []
    unique_behaviors = set()
    
    for record in abc_records:
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
    total_records = len(abc_records)
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
    获取行为出现的汇总统计 【仅支持ABC评估数据】
    
    参数:
    - records: 评估记录列表
    
    返回:
    - behavior_stats: 行为统计信息字典
    
    注意：此功能仅适用于ABC量表评估，因为只有ABC评估包含详细的行为识别数据
    """
    # 只处理ABC记录
    abc_records = [r for r in records if 'identified_behaviors' in r and r.get('assessment_standard', 'ABC') == 'ABC']
    
    if not abc_records:
        return {
            'total_records': 0,
            'unique_behaviors_count': 0,
            'behavior_rankings': [],
            'domain_breakdown': {},
            'most_common': [],
            'least_common': [],
            'note': '无ABC评估数据，无法进行行为统计'
        }
    
    behavior_counts = {}
    domain_behavior_counts = {
        "感觉领域": {},
        "交往领域": {},
        "躯体运动领域": {},
        "语言领域": {},
        "社交与自理领域": {}
    }
    
    for record in abc_records:
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
    total_records = len(abc_records)
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