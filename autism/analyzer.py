"""孤独症数据分析模块"""
import numpy as np
import pandas as pd
from .config import CLINICAL_EVALUATION_METRICS


def generate_clinical_analysis(records):
    """生成临床标准的统计分析报告"""
    if not records:
        return {}
    
    analysis = {}
    
    # 基础临床统计
    analysis['临床评估概况'] = {
        '评估总数': len(records),
        '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及严重程度数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # 按严重程度分析
    severity_stats = {}
    for record in records:
        severity = record.get('template', '自定义')
        if severity not in severity_stats:
            severity_stats[severity] = {
                '评估次数': 0,
                '社交互动得分': [],
                '沟通交流得分': [],
                '刻板行为得分': [],
                '感官处理得分': [],
                '情绪调节得分': [],
                '认知适应得分': []
            }
        severity_stats[severity]['评估次数'] += 1
        severity_stats[severity]['社交互动得分'].append(record['evaluation_scores']['社交互动质量'])
        severity_stats[severity]['沟通交流得分'].append(record['evaluation_scores']['沟通交流能力'])
        severity_stats[severity]['刻板行为得分'].append(record['evaluation_scores']['刻板重复行为'])
        severity_stats[severity]['感官处理得分'].append(record['evaluation_scores']['感官处理能力'])
        severity_stats[severity]['情绪调节得分'].append(record['evaluation_scores']['情绪行为调节'])
        severity_stats[severity]['认知适应得分'].append(record['evaluation_scores']['认知适应功能'])
    
    # 计算统计值
    for severity, stats in severity_stats.items():
        for metric in ['社交互动得分', '沟通交流得分', '刻板行为得分', '感官处理得分', '情绪调节得分', '认知适应得分']:
            scores = stats[metric]
            stats[f'{metric}_均值'] = np.mean(scores)
            stats[f'{metric}_标准差'] = np.std(scores)
            stats[f'{metric}_范围'] = f"{np.min(scores):.1f}-{np.max(scores):.1f}"
            del stats[metric]
    
    analysis['严重程度分析'] = severity_stats
    
    # 按评估情境分析
    context_stats = {}
    for record in records:
        context = record['scene']
        if context not in context_stats:
            context_stats[context] = {
                '评估次数': 0,
                '社交表现': [],
                '沟通表现': [],
                '适应表现': []
            }
        context_stats[context]['评估次数'] += 1
        context_stats[context]['社交表现'].append(record['evaluation_scores']['社交互动质量'])
        context_stats[context]['沟通表现'].append(record['evaluation_scores']['沟通交流能力'])
        context_stats[context]['适应表现'].append(record['evaluation_scores']['认知适应功能'])
    
    for context, stats in context_stats.items():
        for metric in ['社交表现', '沟通表现', '适应表现']:
            scores = stats[metric]
            stats[f'{metric}_均值'] = np.mean(scores)
            del stats[metric]
    
    analysis['情境分析'] = context_stats
    
    # 整体临床表现
    all_social = [r['evaluation_scores']['社交互动质量'] for r in records]
    all_comm = [r['evaluation_scores']['沟通交流能力'] for r in records]
    all_repetitive = [r['evaluation_scores']['刻板重复行为'] for r in records]
    all_sensory = [r['evaluation_scores']['感官处理能力'] for r in records]
    all_emotion = [r['evaluation_scores']['情绪行为调节'] for r in records]
    all_cognitive = [r['evaluation_scores']['认知适应功能'] for r in records]
    
    analysis['整体临床表现'] = {
        '社交互动缺陷程度': f"{np.mean(all_social):.2f} ± {np.std(all_social):.2f}",
        '沟通交流缺陷程度': f"{np.mean(all_comm):.2f} ± {np.std(all_comm):.2f}",
        '刻板重复行为程度': f"{np.mean(all_repetitive):.2f} ± {np.std(all_repetitive):.2f}",
        '感官处理异常程度': f"{np.mean(all_sensory):.2f} ± {np.std(all_sensory):.2f}",
        '情绪调节困难程度': f"{np.mean(all_emotion):.2f} ± {np.std(all_emotion):.2f}",
        '认知适应缺陷程度': f"{np.mean(all_cognitive):.2f} ± {np.std(all_cognitive):.2f}",
        '核心症状综合严重度': f"{(np.mean(all_social) + np.mean(all_comm) + np.mean(all_repetitive))/3:.2f}"
    }
    
    # 临床发现和建议
    findings = []
    
    # 分析核心症状
    core_symptom_avg = (np.mean(all_social) + np.mean(all_comm) + np.mean(all_repetitive)) / 3
    if core_symptom_avg >= 4.0:
        findings.append("核心症状严重，建议密集型干预治疗")
    elif core_symptom_avg >= 3.0:
        findings.append("核心症状中等，建议结构化教学和行为干预")
    else:
        findings.append("核心症状相对较轻，建议社交技能训练")
    
    # 分析共患情况
    if np.mean(all_sensory) >= 4.0:
        findings.append("存在明显感官处理异常，建议感觉统合治疗")
    
    if np.mean(all_emotion) >= 4.0:
        findings.append("情绪调节困难显著，建议心理行为干预")
    
    # 分析最优情境
    if context_stats:
        best_context = min(context_stats.keys(), 
                          key=lambda x: (context_stats[x]['社交表现_均值'] + 
                                       context_stats[x]['沟通表现_均值']) / 2)
        findings.append(f"在{best_context}中表现相对较好，可作为干预起点")
    
    analysis['临床发现与建议'] = findings
    
    return analysis


def prepare_clinical_export_data(records):
    """准备临床数据导出"""
    export_data = []
    
    for record in records:
        profile = record.get('autism_profile', {})
        scores = record['evaluation_scores']
        core_symptom_severity = (scores['社交互动质量'] + scores['沟通交流能力'] + scores['刻板重复行为']) / 3
        
        export_row = {
            '评估ID': record['experiment_id'],
            '评估时间': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '严重程度分级': record.get('template', '自定义'),
            '评估情境': record['scene'],
            '观察活动': record.get('activity', ''),
            '触发因素': record.get('trigger', ''),
            '社交互动缺陷程度': scores['社交互动质量'],
            '沟通交流缺陷程度': scores['沟通交流能力'],
            '刻板重复行为程度': scores['刻板重复行为'],
            '感官处理异常程度': scores['感官处理能力'],
            '情绪调节困难程度': scores['情绪行为调节'],
            '认知适应缺陷程度': scores['认知适应功能'],
            '核心症状综合严重度': round(core_symptom_severity, 2),
            '备注': record.get('notes', '')
        }
        
        # 添加DSM-5特征
        if profile:
            export_row.update({
                'DSM5严重程度': profile.get('dsm5_severity', ''),
                '所需支持水平': profile.get('support_needs', ''),
                '社交沟通缺陷设置': profile.get('social_communication', ''),
                '刻板重复行为设置': profile.get('restricted_repetitive', ''),
                '感官处理异常设置': profile.get('sensory_processing', ''),
                '认知功能水平设置': profile.get('cognitive_function', ''),
                '适应行为能力设置': profile.get('adaptive_behavior', ''),
                '语言发展水平设置': profile.get('language_level', ''),
                '特殊兴趣描述': profile.get('special_interests', '')
            })
        
        export_data.append(export_row)
    
    return export_data