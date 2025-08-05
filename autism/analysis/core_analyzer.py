"""孤独症数据分析核心模块"""
import numpy as np
from typing import List, Dict, Any, Tuple

from .abc_analyzer import analyze_abc_evaluations, generate_abc_analysis
from .dsm5_analyzer import analyze_dsm5_evaluations, generate_dsm5_analysis
from .comparison_analyzer import analyze_evaluation_consistency


def generate_clinical_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def detect_data_format(records: List[Dict[str, Any]]) -> str:
    """检测数据格式类型
    
    Returns:
        'unified': 统一评估格式
        'mixed': 混合格式
        'legacy': 旧格式
    """
    has_unified = any('abc_evaluation' in r and 'dsm5_evaluation' in r for r in records)
    has_legacy = any('assessment_standard' in r and r.get('assessment_standard') in ['ABC', 'DSM5'] for r in records)
    
    if has_unified and not has_legacy:
        return 'unified'
    elif has_unified and has_legacy:
        return 'mixed'
    else:
        return 'legacy'


def generate_unified_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def generate_legacy_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def generate_mixed_format_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def generate_unified_findings(records: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
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