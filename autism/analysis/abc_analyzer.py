"""ABC量表专项分析模块"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

from ..config import ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS


def analyze_abc_evaluations(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析ABC评估结果（从统一格式中提取）"""
    abc_data = []
    
    for record in records:
        if 'abc_evaluation' in record:
            abc_eval = record['abc_evaluation']
            abc_data.append({
                'total_score': abc_eval['total_score'],
                'severity': abc_eval['severity'],
                'domain_scores': abc_eval['domain_scores'],
                'identified_behaviors': abc_eval.get('identified_behaviors', {}),
                'template': record.get('template', '自定义'),
                'scene': record['scene']
            })
    
    if not abc_data:
        return None
    
    analysis = {}
    
    # ABC总分统计
    total_scores = [d['total_score'] for d in abc_data]
    analysis['ABC总分统计'] = {
        '平均总分': f"{np.mean(total_scores):.1f}",
        '总分范围': f"{np.min(total_scores):.0f}-{np.max(total_scores):.0f}",
        '标准差': f"{np.std(total_scores):.1f}",
        '中位数': f"{np.median(total_scores):.0f}"
    }
    
    # 严重程度分布
    severity_distribution = {}
    for data in abc_data:
        severity = data['severity']
        if severity not in severity_distribution:
            severity_distribution[severity] = 0
        severity_distribution[severity] += 1
    
    analysis['严重程度分布'] = {
        k: f"{v} ({v/len(abc_data)*100:.1f}%)" 
        for k, v in severity_distribution.items()
    }
    
    # 各领域得分分析
    domain_stats = {}
    for domain in ABC_EVALUATION_METRICS.keys():
        scores = [d['domain_scores'][domain] for d in abc_data if domain in d['domain_scores']]
        if scores:
            domain_stats[domain] = {
                '平均分': f"{np.mean(scores):.1f}",
                '最高分': f"{np.max(scores):.0f}",
                '最低分': f"{np.min(scores):.0f}",
                '占满分比例': f"{np.mean(scores)/ABC_EVALUATION_METRICS[domain]['max_score']*100:.1f}%"
            }
    
    analysis['各领域得分分析'] = domain_stats
    
    # 高频行为分析
    all_behaviors = {}
    for data in abc_data:
        if 'identified_behaviors' in data:
            for domain, behaviors in data['identified_behaviors'].items():
                for behavior in behaviors:
                    if behavior not in all_behaviors:
                        all_behaviors[behavior] = 0
                    all_behaviors[behavior] += 1
    
    sorted_behaviors = sorted(all_behaviors.items(), key=lambda x: x[1], reverse=True)[:10]
    analysis['高频行为表现'] = {
        behavior: f"出现{count}次 ({count/len(abc_data)*100:.1f}%)" 
        for behavior, count in sorted_behaviors
    }
    
    return analysis


def generate_abc_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成基于ABC量表的统计分析报告（旧格式）"""
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


def analyze_abc_behavior_frequency(records: List[Dict[str, Any]]) -> Dict[str, str]:
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


def analyze_by_severity_abc(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def analyze_by_context_abc(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def get_main_behaviors_in_context(scene_records: List[Dict[str, Any]]) -> List[str]:
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


def generate_abc_findings(records: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
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