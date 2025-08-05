"""ABC与DSM-5评估对比分析模块"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple


def analyze_evaluation_consistency(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def compare_evaluation_methods(record: Dict[str, Any]) -> Dict[str, Any]:
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


def generate_comparison_report(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    
    # 添加相关性分析
    if len(comparisons) > 2:
        abc_totals = [c['abc_total_score'] for c in comparisons]
        dsm5_cores = [c['dsm5_core_average'] for c in comparisons]
        
        correlation = np.corrcoef(abc_totals, dsm5_cores)[0, 1]
        
        # 简单的显著性判断
        n = len(comparisons)
        t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
        # 自由度为n-2的t分布，双尾检验
        # 这里使用简化的判断
        significant = abs(t_stat) > 2.0  # 约等于p<0.05的临界值
        
        report['correlation_analysis'] = {
            'abc_dsm5_correlation': f"{correlation:.3f}",
            'significance': '显著' if significant else '不显著',
            'interpretation': f"ABC总分与DSM-5核心症状存在{'强' if abs(correlation) > 0.7 else '中等' if abs(correlation) > 0.4 else '弱'}相关"
        }
    
    # 构建一致性矩阵
    severity_mapping = {
        'abc': ['非孤独症', '轻度孤独症', '中度孤独症', '重度孤独症'],
        'dsm5': ['轻度', '中度', '重度']
    }
    
    # 创建一致性矩阵
    matrix = {}
    for abc_sev in severity_mapping['abc']:
        matrix[abc_sev] = {}
        for dsm5_sev in severity_mapping['dsm5']:
            matrix[abc_sev][dsm5_sev] = 0
    
    # 填充矩阵
    for comp in comparisons:
        abc_sev = comp['abc_severity']
        
        # 根据DSM5核心症状判断严重程度
        if comp['dsm5_core_average'] >= 4.0:
            dsm5_sev = '重度'
        elif comp['dsm5_core_average'] >= 3.0:
            dsm5_sev = '中度'
        else:
            dsm5_sev = '轻度'
        
        if abc_sev in matrix and dsm5_sev in matrix[abc_sev]:
            matrix[abc_sev][dsm5_sev] += 1
    
    report['consistency_matrix'] = matrix
    
    # 基于对比的建议
    report['recommendations'] = [
        "两种评估工具侧重点不同：ABC注重行为频率统计，DSM-5注重功能缺陷程度",
        "建议结合使用两种评估工具，全面了解个体表现",
        "当两种评估结果不一致时，需要进一步的临床观察和评估",
        "ABC量表适合行为筛查和监测，DSM-5标准适合诊断分类和支持需求评估"
    ]
    
    return report


def analyze_evaluation_tendencies(comparisons: List[Dict[str, Any]]) -> Dict[str, str]:
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