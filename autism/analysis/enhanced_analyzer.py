"""增强版分析器 - 支持CARS和ASSQ量表分析"""
import numpy as np
from typing import List, Dict, Any
from collections import defaultdict


def analyze_cars_evaluations(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析CARS评估结果"""
    if not records:
        return {}
    
    cars_scores = []
    severity_distribution = defaultdict(int)
    item_score_aggregates = defaultdict(list)
    
    for record in records:
        if 'cars_evaluation' in record:
            cars = record['cars_evaluation']
            total_score = cars.get('total_score', 0)
            cars_scores.append(total_score)
            
            # 严重程度分布
            severity = cars.get('severity', '未知')
            severity_distribution[severity] += 1
            
            # 各项目得分汇总
            for item, score in cars.get('item_scores', {}).items():
                item_score_aggregates[item].append(score)
    
    # 计算统计指标
    analysis = {
        '评估数量': len(cars_scores),
        '平均总分': np.mean(cars_scores) if cars_scores else 0,
        '总分标准差': np.std(cars_scores) if cars_scores else 0,
        '最高分': max(cars_scores) if cars_scores else 0,
        '最低分': min(cars_scores) if cars_scores else 0,
        '严重程度分布': dict(severity_distribution)
    }
    
    # 找出得分最高的项目（问题最严重的领域）
    if item_score_aggregates:
        problem_areas = {}
        for item, scores in item_score_aggregates.items():
            avg_score = np.mean(scores)
            if avg_score >= 3.0:  # CARS中3分及以上表示明显异常
                problem_areas[item] = {
                    '平均分': round(avg_score, 2),
                    '评估次数': len(scores)
                }
        
        if problem_areas:
            # 按平均分排序，找出前5个问题最严重的领域
            sorted_problems = sorted(problem_areas.items(), 
                                   key=lambda x: x[1]['平均分'], 
                                   reverse=True)[:5]
            analysis['主要问题领域'] = dict(sorted_problems)
    
    # 临床建议
    avg_score = analysis['平均总分']
    if avg_score >= 37:
        analysis['临床建议'] = "重度孤独症表现，需要密集的综合干预"
    elif avg_score >= 30:
        analysis['临床建议'] = "轻-中度孤独症表现，建议早期干预"
    else:
        analysis['临床建议'] = "低于临床截断分，但仍需关注发展"
    
    return analysis


def analyze_assq_evaluations(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析ASSQ筛查结果"""
    if not records:
        return {}
    
    assq_scores = []
    positive_screens = 0
    risk_levels = defaultdict(int)
    category_scores = defaultdict(list)
    
    for record in records:
        if 'assq_evaluation' in record:
            assq = record['assq_evaluation']
            total_score = assq.get('total_score', 0)
            assq_scores.append(total_score)
            
            # 阳性筛查统计
            if assq.get('positive_screen', False):
                positive_screens += 1
            
            # 风险等级分布
            risk = assq.get('risk_level', '未知')
            risk_levels[risk] += 1
            
            # 类别得分汇总
            for category, score in assq.get('category_scores', {}).items():
                category_scores[category].append(score)
    
    # 计算统计指标
    analysis = {
        '筛查数量': len(assq_scores),
        '平均总分': np.mean(assq_scores) if assq_scores else 0,
        '总分标准差': np.std(assq_scores) if assq_scores else 0,
        '阳性筛查数': positive_screens,
        '阳性筛查率': f"{(positive_screens/len(assq_scores)*100):.1f}%" if assq_scores else "0%",
        '风险等级分布': dict(risk_levels)
    }
    
    # 分析各类别表现
    if category_scores:
        category_analysis = {}
        for category, scores in category_scores.items():
            category_analysis[category] = {
                '平均分': round(np.mean(scores), 2),
                '最高分': max(scores),
                '最低分': min(scores)
            }
        analysis['类别分析'] = category_analysis
    
    # 筛查建议
    avg_score = analysis['平均总分']
    if avg_score >= 19:
        analysis['筛查建议'] = "强烈建议进行全面的孤独症诊断评估"
    elif avg_score >= 13:
        analysis['筛查建议'] = "达到筛查阳性标准，建议进一步评估"
    elif avg_score >= 8:
        analysis['筛查建议'] = "存在一定风险，建议密切观察"
    else:
        analysis['筛查建议'] = "低风险，继续常规发展监测"
    
    return analysis


def analyze_multi_scale_consistency(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析多量表评估的一致性"""
    consistency_analysis = {
        '多量表评估数': 0,
        '量表组合': defaultdict(int),
        '一致性分析': [],
        '诊断建议汇总': []
    }
    
    for record in records:
        scales_used = []
        severity_assessments = {}
        
        # 收集各量表的严重程度判断
        if 'abc_evaluation' in record:
            scales_used.append('ABC')
            abc = record['abc_evaluation']
            severity_assessments['ABC'] = {
                'score': abc.get('total_score', 0),
                'severity': abc.get('severity', ''),
                'clinical': abc.get('clinical_range', False)
            }
        
        if 'dsm5_evaluation' in record:
            scales_used.append('DSM5')
            dsm5 = record['dsm5_evaluation']
            severity_assessments['DSM5'] = {
                'score': dsm5.get('core_symptom_average', 0) * 20,  # 标准化到0-100
                'severity': dsm5.get('severity_level', ''),
                'clinical': dsm5.get('meets_criteria', {}).get('overall', False)
            }
        
        if 'cars_evaluation' in record:
            scales_used.append('CARS')
            cars = record['cars_evaluation']
            severity_assessments['CARS'] = {
                'score': cars.get('total_score', 0),
                'severity': cars.get('severity', ''),
                'clinical': cars.get('clinical_cutoff', False)
            }
        
        if 'assq_evaluation' in record:
            scales_used.append('ASSQ')
            assq = record['assq_evaluation']
            severity_assessments['ASSQ'] = {
                'score': assq.get('total_score', 0),
                'severity': assq.get('screening_result', {}).get('screening_result', ''),
                'clinical': assq.get('positive_screen', False)
            }
        
        # 记录量表组合
        if len(scales_used) >= 2:
            consistency_analysis['多量表评估数'] += 1
            scale_combo = '+'.join(sorted(scales_used))
            consistency_analysis['量表组合'][scale_combo] += 1
            
            # 分析一致性
            clinical_agreements = []
            for scale, assessment in severity_assessments.items():
                if assessment['clinical']:
                    clinical_agreements.append(scale)
            
            if len(clinical_agreements) == len(scales_used):
                consistency = "完全一致（均为阳性）"
            elif len(clinical_agreements) == 0:
                consistency = "完全一致（均为阴性）"
            else:
                consistency = f"部分一致（{len(clinical_agreements)}/{len(scales_used)}阳性）"
            
            consistency_analysis['一致性分析'].append({
                'ID': record.get('experiment_id', ''),
                '量表': scale_combo,
                '一致性': consistency,
                '阳性量表': clinical_agreements
            })
    
    # 计算整体一致性率
    if consistency_analysis['一致性分析']:
        total = len(consistency_analysis['一致性分析'])
        fully_consistent = sum(1 for item in consistency_analysis['一致性分析'] 
                             if '完全一致' in item['一致性'])
        consistency_analysis['整体一致性率'] = f"{(fully_consistent/total*100):.1f}%"
    
    # 生成综合建议
    consistency_analysis['量表组合'] = dict(consistency_analysis['量表组合'])
    
    # 找出最常用的量表组合
    if consistency_analysis['量表组合']:
        most_common = max(consistency_analysis['量表组合'].items(), key=lambda x: x[1])
        consistency_analysis['最常用组合'] = f"{most_common[0]} ({most_common[1]}次)"
    
    return consistency_analysis


def generate_intervention_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """基于分析结果生成干预建议"""
    recommendations = []
    
    # 基于ABC分析的建议
    if 'ABC分析' in analysis:
        abc = analysis['ABC分析']
        if abc.get('平均总分', 0) >= 67:
            recommendations.append("ABC评估显示需要综合干预，建议结合ABA、TEACCH等循证方法")
    
    # 基于DSM-5分析的建议
    if 'DSM5分析' in analysis:
        dsm5 = analysis['DSM5分析']
        if dsm5.get('核心症状均值', 0) >= 3.5:
            recommendations.append("DSM-5评估显示需要大量支持，建议增加干预强度至每周25小时以上")
    
    # 基于CARS分析的建议
    if 'CARS分析' in analysis:
        cars = analysis['CARS分析']
        if '主要问题领域' in cars:
            problem_areas = list(cars['主要问题领域'].keys())[:3]
            recommendations.append(f"CARS评估显示主要问题领域：{', '.join(problem_areas)}，建议针对性干预")
    
    # 基于ASSQ分析的建议
    if 'ASSQ分析' in analysis:
        assq = analysis['ASSQ分析']
        if float(assq.get('阳性筛查率', '0%').rstrip('%')) > 50:
            recommendations.append("ASSQ筛查阳性率较高，建议进行全面诊断评估")
    
    # 基于多量表一致性的建议
    if '多量表对比' in analysis:
        consistency = analysis['多量表对比']
        if consistency.get('整体一致性率'):
            rate = float(consistency['整体一致性率'].rstrip('%'))
            if rate < 70:
                recommendations.append("多量表评估一致性较低，建议增加观察次数或调整评估情境")
    
    # 如果没有特定建议，提供通用建议
    if not recommendations:
        recommendations.append("建议继续监测发展情况，定期进行评估")
        recommendations.append("保持早期干预，关注儿童的个体化需求")
    
    return recommendations