"""孤独症数据分析模块 - 支持统一评估架构"""
import numpy as np
import pandas as pd
from .config import ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS, DSM5_EVALUATION_METRICS


def generate_clinical_analysis(records):
    """生成临床分析报告 - 支持新旧数据格式"""
    if not records:
        return {}
    
    # 检测数据格式
    data_format = detect_data_format(records)
    
    if data_format == 'unified':
        # 新格式：统一评估
        return generate_unified_analysis(records)
    elif data_format == 'mixed':
        # 混合格式：部分新格式，部分旧格式
        return generate_mixed_format_analysis(records)
    else:
        # 旧格式：分离的ABC/DSM5评估
        return generate_legacy_analysis(records)


def detect_data_format(records):
    """检测数据格式类型"""
    has_unified = any('abc_evaluation' in r and 'dsm5_evaluation' in r for r in records)
    has_legacy = any('assessment_standard' in r and r.get('assessment_standard') in ['ABC', 'DSM5'] for r in records)
    
    if has_unified and not has_legacy:
        return 'unified'
    elif has_unified and has_legacy:
        return 'mixed'
    else:
        return 'legacy'


def generate_unified_analysis(records):
    """生成基于统一评估的分析报告"""
    analysis = {}
    
    # 基础统计
    analysis['评估概况'] = {
        '评估总数': len(records),
        '评估标准': '统一评估（ABC + DSM-5）',
        '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及配置类型数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # ABC评估分析
    abc_analysis = analyze_abc_evaluations(records)
    if abc_analysis:
        analysis['ABC量表分析'] = abc_analysis
    
    # DSM-5评估分析
    dsm5_analysis = analyze_dsm5_evaluations(records)
    if dsm5_analysis:
        analysis['DSM-5标准分析'] = dsm5_analysis
    
    # 评估一致性分析
    consistency_analysis = analyze_evaluation_consistency(records)
    if consistency_analysis:
        analysis['评估一致性分析'] = consistency_analysis
    
    # 综合临床发现
    findings = generate_unified_findings(records, analysis)
    analysis['临床发现与建议'] = findings
    
    return analysis


def analyze_abc_evaluations(records):
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


def analyze_dsm5_evaluations(records):
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


def analyze_evaluation_consistency(records):
    """分析ABC和DSM-5评估的一致性"""
    consistency_data = []
    
    for record in records:
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            abc_total = record['abc_evaluation']['total_score']
            dsm5_core = record['dsm5_evaluation'].get('core_symptom_average', 0)
            
            # 将ABC总分转换为1-5的尺度以便比较
            abc_normalized = min(5, max(1, (abc_total - 20) / 30 + 1))  # 简单的线性转换
            
            consistency_data.append({
                'abc_total': abc_total,
                'abc_severity': record['abc_evaluation']['severity'],
                'dsm5_core': dsm5_core,
                'abc_normalized': abc_normalized,
                'difference': abs(abc_normalized - dsm5_core),
                'template': record.get('template', '自定义')
            })
    
    if not consistency_data:
        return None
    
    analysis = {}
    
    # 计算相关性
    if len(consistency_data) > 3:
        abc_scores = [d['abc_normalized'] for d in consistency_data]
        dsm5_scores = [d['dsm5_core'] for d in consistency_data]
        correlation = np.corrcoef(abc_scores, dsm5_scores)[0, 1]
        analysis['评估相关性'] = f"{correlation:.3f}"
    
    # 一致性统计
    differences = [d['difference'] for d in consistency_data]
    analysis['一致性指标'] = {
        '平均差异': f"{np.mean(differences):.2f}",
        '差异标准差': f"{np.std(differences):.2f}",
        '高度一致（差异<0.5）': f"{sum(d < 0.5 for d in differences)} ({sum(d < 0.5 for d in differences)/len(differences)*100:.1f}%)",
        '中度一致（差异0.5-1.0）': f"{sum(0.5 <= d < 1.0 for d in differences)} ({sum(0.5 <= d < 1.0 for d in differences)/len(differences)*100:.1f}%)",
        '低度一致（差异>1.0）': f"{sum(d >= 1.0 for d in differences)} ({sum(d >= 1.0 for d in differences)/len(differences)*100:.1f}%)"
    }
    
    # 严重程度判定一致性
    severity_agreement = 0
    for data in consistency_data:
        abc_severity = data['abc_severity']
        dsm5_severity = '轻度' if data['dsm5_core'] < 2.5 else '中度' if data['dsm5_core'] < 3.5 else '重度'
        
        # 简化的一致性判断
        if (('轻度' in abc_severity and dsm5_severity == '轻度') or
            ('中度' in abc_severity and dsm5_severity == '中度') or
            ('重度' in abc_severity and dsm5_severity == '重度')):
            severity_agreement += 1
    
    analysis['严重程度判定一致率'] = f"{severity_agreement}/{len(consistency_data)} ({severity_agreement/len(consistency_data)*100:.1f}%)"
    
    return analysis


def generate_unified_findings(records, analysis):
    """生成基于统一评估的临床发现和建议"""
    findings = []
    
    # 基于ABC分析的发现
    if 'ABC量表分析' in analysis and 'ABC总分统计' in analysis['ABC量表分析']:
        avg_total = float(analysis['ABC量表分析']['ABC总分统计']['平均总分'])
        
        if avg_total >= 67:
            findings.append("ABC评估显示明确的孤独症表现，建议综合干预治疗")
        elif avg_total >= 53:
            findings.append("ABC评估处于轻度范围，建议早期干预")
    
    # 基于DSM-5分析的发现
    if 'DSM-5标准分析' in analysis and '整体临床表现' in analysis['DSM-5标准分析']:
        if '核心症状综合严重度' in analysis['DSM-5标准分析']['整体临床表现']:
            core_severity = float(analysis['DSM-5标准分析']['整体临床表现']['核心症状综合严重度'])
            
            if core_severity >= 4.0:
                findings.append("DSM-5评估显示严重核心症状，需要密集支持")
            elif core_severity >= 3.0:
                findings.append("DSM-5评估显示中度核心症状，需要大量支持")
    
    # 基于一致性分析的发现
    if '评估一致性分析' in analysis:
        if '评估相关性' in analysis['评估一致性分析']:
            correlation = float(analysis['评估一致性分析']['评估相关性'])
            if correlation > 0.7:
                findings.append(f"ABC与DSM-5评估高度相关(r={correlation:.2f})，评估结果可靠")
            elif correlation > 0.5:
                findings.append(f"ABC与DSM-5评估中度相关(r={correlation:.2f})，建议综合考虑")
            else:
                findings.append(f"ABC与DSM-5评估相关性较低(r={correlation:.2f})，需要进一步评估")
    
    # 基于高频行为的建议
    if 'ABC量表分析' in analysis and '高频行为表现' in analysis['ABC量表分析']:
        high_freq_behaviors = list(analysis['ABC量表分析']['高频行为表现'].keys())
        if any("自伤" in behavior for behavior in high_freq_behaviors[:3]):
            findings.append("存在自伤行为，需要立即采取保护措施")
        if any("无语言" in behavior for behavior in high_freq_behaviors[:3]):
            findings.append("语言发展严重滞后，建议加强语言和沟通训练")
    
    # 添加综合建议
    findings.append("建议结合ABC行为观察和DSM-5功能评估制定个体化干预方案")
    
    return findings


def generate_legacy_analysis(records):
    """处理旧格式数据的分析（向后兼容）"""
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
        "建议使用统一评估模式以获得更好的对比分析"
    ]
    
    return analysis


def generate_mixed_format_analysis(records):
    """处理混合格式数据的分析"""
    unified_records = [r for r in records if 'abc_evaluation' in r and 'dsm5_evaluation' in r]
    legacy_records = [r for r in records if 'assessment_standard' in r and r.get('assessment_standard') in ['ABC', 'DSM5']]
    
    analysis = {
        '评估概况': {
            '总评估数': len(records),
            '统一评估数': len(unified_records),
            '旧格式评估数': len(legacy_records),
            '数据格式': '混合格式（包含新旧两种格式）'
        }
    }
    
    # 分别分析不同格式的数据
    if unified_records:
        unified_analysis = generate_unified_analysis(unified_records)
        for key, value in unified_analysis.items():
            if key != '评估概况':
                analysis[f'[统一评估] {key}'] = value
    
    if legacy_records:
        legacy_analysis = generate_legacy_analysis(legacy_records)
        for key, value in legacy_analysis.items():
            if key != '评估概况':
                analysis[f'[旧格式] {key}'] = value
    
    return analysis


def prepare_clinical_export_data(records):
    """准备临床数据导出 - 支持新旧格式"""
    export_data = []
    
    for record in records:
        # 基础信息
        export_row = {
            '评估ID': record['experiment_id'],
            '评估时间': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '配置类型': record.get('template', '自定义'),
            '评估情境': record['scene'],
            '观察活动': record.get('activity', ''),
            '触发因素': record.get('trigger', ''),
            '备注': record.get('notes', '')
        }
        
        # 检查数据格式
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            # 新格式：统一评估
            export_row['数据格式'] = '统一评估'
            
            # ABC评估结果
            abc_eval = record['abc_evaluation']
            export_row['ABC总分'] = abc_eval['total_score']
            export_row['ABC严重程度'] = abc_eval['severity']
            for domain, score in abc_eval['domain_scores'].items():
                export_row[f'ABC_{domain}'] = score
            
            # DSM-5评估结果
            dsm5_eval = record['dsm5_evaluation']
            export_row['DSM5核心症状均分'] = round(dsm5_eval.get('core_symptom_average', 0), 2)
            for metric, score in dsm5_eval['scores'].items():
                export_row[f'DSM5_{metric}'] = score
            
            # 评估一致性
            abc_normalized = min(5, max(1, (abc_eval['total_score'] - 20) / 30 + 1))
            dsm5_core = dsm5_eval.get('core_symptom_average', 0)
            export_row['评估差异'] = abs(abc_normalized - dsm5_core)
            
        else:
            # 旧格式
            assessment_standard = record.get('assessment_standard', 'ABC')
            export_row['数据格式'] = f'旧格式-{assessment_standard}'
            
            if assessment_standard == 'ABC':
                export_row['ABC总分'] = record.get('abc_total_score', '')
                export_row['ABC严重程度'] = record.get('abc_severity', '')
                scores = record.get('evaluation_scores', {})
                for domain in ABC_EVALUATION_METRICS.keys():
                    export_row[domain] = scores.get(domain, '')
            else:  # DSM-5
                scores = record.get('evaluation_scores', {})
                if all(metric in scores for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                    core_severity = (scores['社交互动质量'] + 
                                   scores['沟通交流能力'] + 
                                   scores['刻板重复行为']) / 3
                    export_row['核心症状综合'] = round(core_severity, 2)
                
                for metric in DSM5_EVALUATION_METRICS.keys():
                    export_row[metric] = scores.get(metric, '')
        
        export_data.append(export_row)
    
    return export_data


# ==================== 保留原有的分析函数（向后兼容） ====================
def generate_abc_analysis(records):
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


def generate_dsm5_analysis(records):
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


# ==================== 新增：对比分析功能 ====================
def compare_evaluation_methods(record):
    """比较单个记录的ABC和DSM-5评估结果"""
    if 'abc_evaluation' not in record or 'dsm5_evaluation' not in record:
        return None
    
    abc_eval = record['abc_evaluation']
    dsm5_eval = record['dsm5_evaluation']
    
    # ABC严重程度映射
    abc_severity_level = {
        '非孤独症': 1,
        '边缘状态': 2,
        '轻度孤独症': 3,
        '中度孤独症': 4,
        '重度孤独症': 5
    }.get(abc_eval['severity'], 3)
    
    # DSM-5严重程度
    dsm5_core = dsm5_eval.get('core_symptom_average', 0)
    dsm5_severity_level = 1 if dsm5_core < 2 else 2 if dsm5_core < 3 else 3 if dsm5_core < 4 else 4 if dsm5_core < 5 else 5
    
    comparison = {
        'abc_total_score': abc_eval['total_score'],
        'abc_severity': abc_eval['severity'],
        'abc_severity_level': abc_severity_level,
        'dsm5_core_average': dsm5_core,
        'dsm5_severity_level': dsm5_severity_level,
        'severity_agreement': abs(abc_severity_level - dsm5_severity_level) <= 1,
        'severity_difference': abs(abc_severity_level - dsm5_severity_level),
        
        # 具体领域对比
        'social_comparison': {
            'abc_score': abc_eval['domain_scores'].get('交往领域得分', 0),
            'dsm5_score': dsm5_eval['scores'].get('社交互动质量', 0)
        },
        'communication_comparison': {
            'abc_score': abc_eval['domain_scores'].get('语言领域得分', 0),
            'dsm5_score': dsm5_eval['scores'].get('沟通交流能力', 0)
        },
        'repetitive_comparison': {
            'abc_score': abc_eval['domain_scores'].get('躯体运动领域得分', 0),
            'dsm5_score': dsm5_eval['scores'].get('刻板重复行为', 0)
        }
    }
    
    return comparison


def generate_comparison_report(records):
    """生成ABC和DSM-5评估对比报告"""
    comparisons = []
    
    for record in records:
        comp = compare_evaluation_methods(record)
        if comp:
            comp['template'] = record.get('template', '自定义')
            comp['scene'] = record['scene']
            comparisons.append(comp)
    
    if not comparisons:
        return None
    
    report = {
        '对比样本数': len(comparisons),
        '严重程度一致性': {
            '完全一致': sum(c['severity_difference'] == 0 for c in comparisons),
            '基本一致（差1级）': sum(c['severity_difference'] == 1 for c in comparisons),
            '中度差异（差2级）': sum(c['severity_difference'] == 2 for c in comparisons),
            '显著差异（差3级以上）': sum(c['severity_difference'] >= 3 for c in comparisons)
        },
        '平均严重程度差异': np.mean([c['severity_difference'] for c in comparisons]),
        '评估倾向': analyze_evaluation_tendencies(comparisons)
    }
    
    return report


def analyze_evaluation_tendencies(comparisons):
    """分析两种评估方法的倾向性"""
    abc_higher = sum(c['abc_severity_level'] > c['dsm5_severity_level'] for c in comparisons)
    dsm5_higher = sum(c['dsm5_severity_level'] > c['abc_severity_level'] for c in comparisons)
    equal = sum(c['abc_severity_level'] == c['dsm5_severity_level'] for c in comparisons)
    
    total = len(comparisons)
    
    return {
        'ABC评估更严重': f"{abc_higher} ({abc_higher/total*100:.1f}%)",
        'DSM-5评估更严重': f"{dsm5_higher} ({dsm5_higher/total*100:.1f}%)",
        '评估一致': f"{equal} ({equal/total*100:.1f}%)"
    }


# ==================== 保留原有的辅助函数（向后兼容） ====================
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


# ==================== ABC专用高级分析功能（保留原有功能） ====================
def extract_behavior_specific_samples(records, target_behaviors, logic='OR'):
    """
    从评估记录中提取包含特定行为的样本
    注意：此功能仅适用于包含identified_behaviors字段的记录
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


def calculate_sample_similarity(record1, record2, weights=None):
    """
    计算两个样本之间的相似度
    支持新旧格式的记录
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


def calculate_abc_similarity_internal(data1, data2, weights=None):
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


def calculate_dsm5_similarity_internal(data1, data2, weights=None):
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
            
            # 归一化差异
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


def find_similar_samples(target_record, all_records, threshold=0.7, max_results=10):
    """
    查找与目标样本相似的其他样本
    支持新旧格式的记录
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
    支持新旧格式的记录
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


def get_behavior_summary_stats(records):
    """
    获取行为出现的汇总统计
    支持新旧格式的记录
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
    
    return {
        'total_records': total_records,
        'unique_behaviors_count': len(behavior_counts),
        'behavior_rankings': sorted_behaviors,
        'domain_breakdown': domain_behavior_counts,
        'most_common': sorted_behaviors[:10] if sorted_behaviors else [],
        'least_common': sorted_behaviors[-10:] if len(sorted_behaviors) > 10 else sorted_behaviors
    }