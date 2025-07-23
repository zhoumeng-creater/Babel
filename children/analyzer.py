"""正常儿童发展数据分析模块"""
import numpy as np
import pandas as pd
from .config import DEVELOPMENT_EVALUATION_METRICS


def generate_development_analysis(records):
    """生成儿童发展的统计分析报告"""
    if not records:
        return {}
    
    analysis = {}
    
    # 基础发展统计
    analysis['发展观察概况'] = {
        '观察总数': len(records),
        '观察时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及年龄段数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # 按年龄段分析
    age_stats = {}
    for record in records:
        age_group = record.get('template', '自定义')
        if age_group not in age_stats:
            age_stats[age_group] = {
                '观察次数': 0,
                '语言发展得分': [],
                '社交能力得分': [],
                '认知学习得分': [],
                '情绪调节得分': [],
                '运动技能得分': [],
                '独立能力得分': []
            }
        age_stats[age_group]['观察次数'] += 1
        age_stats[age_group]['语言发展得分'].append(record['evaluation_scores']['语言沟通发展'])
        age_stats[age_group]['社交能力得分'].append(record['evaluation_scores']['社交互动能力'])
        age_stats[age_group]['认知学习得分'].append(record['evaluation_scores']['认知学习能力'])
        age_stats[age_group]['情绪调节得分'].append(record['evaluation_scores']['情绪调节发展'])
        age_stats[age_group]['运动技能得分'].append(record['evaluation_scores']['运动技能发展'])
        age_stats[age_group]['独立能力得分'].append(record['evaluation_scores']['独立自理能力'])
    
    # 计算统计值
    for age_group, stats in age_stats.items():
        for metric in ['语言发展得分', '社交能力得分', '认知学习得分', '情绪调节得分', '运动技能得分', '独立能力得分']:
            scores = stats[metric]
            stats[f'{metric}_均值'] = np.mean(scores)
            stats[f'{metric}_标准差'] = np.std(scores)
            stats[f'{metric}_范围'] = f"{np.min(scores):.1f}-{np.max(scores):.1f}"
            del stats[metric]
    
    analysis['年龄段分析'] = age_stats
    
    # 按观察情境分析
    context_stats = {}
    for record in records:
        context = record['scene']
        if context not in context_stats:
            context_stats[context] = {
                '观察次数': 0,
                '语言表现': [],
                '社交表现': [],
                '学习表现': []
            }
        context_stats[context]['观察次数'] += 1
        context_stats[context]['语言表现'].append(record['evaluation_scores']['语言沟通发展'])
        context_stats[context]['社交表现'].append(record['evaluation_scores']['社交互动能力'])
        context_stats[context]['学习表现'].append(record['evaluation_scores']['认知学习能力'])
    
    for context, stats in context_stats.items():
        for metric in ['语言表现', '社交表现', '学习表现']:
            scores = stats[metric]
            stats[f'{metric}_均值'] = np.mean(scores)
            del stats[metric]
    
    analysis['情境分析'] = context_stats
    
    # 整体发展表现
    all_language = [r['evaluation_scores']['语言沟通发展'] for r in records]
    all_social = [r['evaluation_scores']['社交互动能力'] for r in records]
    all_cognitive = [r['evaluation_scores']['认知学习能力'] for r in records]
    all_emotional = [r['evaluation_scores']['情绪调节发展'] for r in records]
    all_motor = [r['evaluation_scores']['运动技能发展'] for r in records]
    all_independence = [r['evaluation_scores']['独立自理能力'] for r in records]
    
    analysis['整体发展表现'] = {
        '语言沟通发展水平': f"{np.mean(all_language):.2f} ± {np.std(all_language):.2f}",
        '社交互动能力水平': f"{np.mean(all_social):.2f} ± {np.std(all_social):.2f}",
        '认知学习能力水平': f"{np.mean(all_cognitive):.2f} ± {np.std(all_cognitive):.2f}",
        '情绪调节发展水平': f"{np.mean(all_emotional):.2f} ± {np.std(all_emotional):.2f}",
        '运动技能发展水平': f"{np.mean(all_motor):.2f} ± {np.std(all_motor):.2f}",
        '独立自理能力水平': f"{np.mean(all_independence):.2f} ± {np.std(all_independence):.2f}",
        '综合发展指数': f"{(np.mean(all_language) + np.mean(all_social) + np.mean(all_cognitive))/3:.2f}"
    }
    
    # 发展建议和指导
    recommendations = []
    
    # 分析整体发展水平
    overall_avg = (np.mean(all_language) + np.mean(all_social) + np.mean(all_cognitive) + 
                   np.mean(all_emotional) + np.mean(all_motor) + np.mean(all_independence)) / 6
    
    if overall_avg >= 4.5:
        recommendations.append("整体发展优秀，建议继续保持良好的成长环境")
    elif overall_avg >= 4.0:
        recommendations.append("发展水平良好，可适当增加挑战性活动")
    elif overall_avg >= 3.5:
        recommendations.append("发展基本正常，建议多样化成长体验")
    else:
        recommendations.append("某些领域需要重点关注，建议增加针对性活动")
    
    # 分析强弱项
    domains = {
        '语言': np.mean(all_language),
        '社交': np.mean(all_social),
        '认知': np.mean(all_cognitive),
        '情绪': np.mean(all_emotional),
        '运动': np.mean(all_motor),
        '独立': np.mean(all_independence)
    }
    
    strongest = max(domains.keys(), key=lambda x: domains[x])
    weakest = min(domains.keys(), key=lambda x: domains[x])
    
    recommendations.append(f"{strongest}发展是优势领域，可以作为其他能力发展的支撑")
    
    if domains[weakest] < 3.5:
        recommendations.append(f"{weakest}发展需要特别关注，建议增加相关活动")
    
    # 分析最佳发展情境
    if context_stats:
        best_context = max(context_stats.keys(), 
                          key=lambda x: (context_stats[x]['语言表现_均值'] + 
                                       context_stats[x]['社交表现_均值'] + 
                                       context_stats[x]['学习表现_均值']) / 3)
        recommendations.append(f"在{best_context}中表现最佳，可多安排类似活动")
    
    analysis['发展建议与指导'] = recommendations
    
    return analysis


def prepare_development_export_data(records):
    """准备发展数据导出"""
    export_data = []
    
    for record in records:
        profile = record.get('child_profile', {})
        scores = record['evaluation_scores']
        development_index = sum(scores.values()) / len(scores)
        
        export_row = {
            '观察ID': record['observation_id'],
            '观察时间': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '年龄发展阶段': record.get('template', '自定义'),
            '观察情境': record['scene'],
            '观察活动': record.get('activity', ''),
            '情境触发': record.get('trigger', ''),
            '语言沟通发展': scores['语言沟通发展'],
            '社交互动能力': scores['社交互动能力'],
            '认知学习能力': scores['认知学习能力'],
            '情绪调节发展': scores['情绪调节发展'],
            '运动技能发展': scores['运动技能发展'],
            '独立自理能力': scores['独立自理能力'],
            '综合发展指数': round(development_index, 2),
            '备注': record.get('notes', '')
        }
        
        # 添加儿童发展特征
        if profile:
            export_row.update({
                '发展阶段特征': profile.get('stage_characteristics', ''),
                '发展重点': profile.get('development_focus', ''),
                '语言发展配置': profile.get('language_development', ''),
                '社交技能配置': profile.get('social_skills', ''),
                '认知能力配置': profile.get('cognitive_ability', ''),
                '情绪调节配置': profile.get('emotional_regulation', ''),
                '运动技能配置': profile.get('motor_skills', ''),
                '独立性配置': profile.get('independence_level', ''),
                '典型兴趣描述': profile.get('typical_interests', '')
            })
        
        export_data.append(export_row)
    
    return export_data