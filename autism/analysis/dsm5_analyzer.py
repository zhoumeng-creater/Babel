"""DSM-5标准专项分析模块"""
import numpy as np
from typing import List, Dict, Any

from ..config import DSM5_EVALUATION_METRICS


def analyze_dsm5_evaluations(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析DSM-5评估结果（从统一格式中提取）"""
    dsm5_data = []
    
    for record in records:
        if 'dsm5_evaluation' in record:
            dsm5_eval = record['dsm5_evaluation']
            dsm5_data.append({
                'scores': dsm5_eval['scores'],
                'core_symptom_average': dsm5_eval.get('core_symptom_average', 0),
                'clinical_observations': dsm5_eval.get('clinical_observations', {}),
                'template': record.get('template', '自定义'),
                'scene': record['scene']
            })
    
    if not dsm5_data:
        return None
    
    analysis = {}
    
    # 整体表现统计
    overall_stats = {}
    for metric in DSM5_EVALUATION_METRICS.keys():
        scores = [d['scores'].get(metric, 0) for d in dsm5_data]
        if scores:
            overall_stats[f'{metric}程度'] = f"{np.mean(scores):.2f} ± {np.std(scores):.2f}"
    
    # 核心症状统计
    core_averages = [d['core_symptom_average'] for d in dsm5_data if d['core_symptom_average'] > 0]
    if core_averages:
        overall_stats['核心症状综合严重度'] = f"{np.mean(core_averages):.2f}"
    
    analysis['整体临床表现'] = overall_stats
    
    # 按配置类型分析
    template_stats = {}
    for data in dsm5_data:
        template = data['template']
        if template not in template_stats:
            template_stats[template] = {
                'count': 0,
                'core_scores': []
            }
        template_stats[template]['count'] += 1
        template_stats[template]['core_scores'].append(data['core_symptom_average'])
    
    analysis['配置类型分析'] = {}
    for template, stats in template_stats.items():
        if stats['core_scores']:
            analysis['配置类型分析'][template] = {
                '样本数': stats['count'],
                '核心症状均值': f"{np.mean(stats['core_scores']):.2f}",
                '严重程度': '轻度' if np.mean(stats['core_scores']) < 2.5 else '中度' if np.mean(stats['core_scores']) < 3.5 else '重度'
            }
    
    return analysis


def generate_dsm5_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成基于DSM-5标准的统计分析报告（旧格式）"""
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


def analyze_by_severity_dsm5(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def analyze_by_context_dsm5(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def analyze_overall_dsm5(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def generate_dsm5_findings(records: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
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