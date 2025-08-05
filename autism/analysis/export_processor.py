"""孤独症数据导出处理模块"""
import numpy as np
from typing import List, Dict, Any

from ..config import ABC_EVALUATION_METRICS, DSM5_EVALUATION_METRICS


def prepare_clinical_export_data(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    准备临床数据导出 - 支持新旧格式
    
    Args:
        records: 评估记录列表
        
    Returns:
        准备好的导出数据列表
    """
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
            
            # 识别到的行为（前10个）
            if 'identified_behaviors' in abc_eval:
                all_behaviors = []
                for behaviors in abc_eval['identified_behaviors'].values():
                    all_behaviors.extend(behaviors)
                export_row['ABC识别行为'] = '; '.join(all_behaviors[:10])
            
            # 临床观察
            if 'clinical_observations' in dsm5_eval:
                observations = []
                for category, obs_list in dsm5_eval['clinical_observations'].items():
                    observations.extend([f"[{category}] {obs}" for obs in obs_list])
                export_row['DSM5临床观察'] = '; '.join(observations[:10])
                
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
                    
                # 识别到的行为
                if 'identified_behaviors' in record:
                    all_behaviors = []
                    for behaviors in record['identified_behaviors'].values():
                        all_behaviors.extend(behaviors)
                    export_row['识别的行为'] = '; '.join(all_behaviors[:10])
                    
            else:  # DSM-5
                scores = record.get('evaluation_scores', {})
                if all(metric in scores for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                    core_severity = (scores['社交互动质量'] + 
                                   scores['沟通交流能力'] + 
                                   scores['刻板重复行为']) / 3
                    export_row['核心症状综合'] = round(core_severity, 2)
                
                for metric in DSM5_EVALUATION_METRICS.keys():
                    export_row[metric] = scores.get(metric, '')
                
                # 临床观察
                if 'clinical_observations' in record:
                    observations = []
                    for category, obs_list in record['clinical_observations'].items():
                        observations.extend([f"[{category}] {obs}" for obs in obs_list])
                    export_row['临床观察'] = '; '.join(observations[:10])
        
        # 添加孤独症特征（如果存在）
        if 'autism_profile' in record:
            profile = record['autism_profile']
            export_row.update({
                '社交特征': profile.get('social_characteristics', ''),
                '沟通特征': profile.get('communication_characteristics', ''),
                '行为特征': profile.get('behavioral_characteristics', ''),
                '认知特征': profile.get('cognitive_characteristics', ''),
                '情绪特征': profile.get('emotional_characteristics', ''),
                '日常生活': profile.get('daily_living', ''),
                '功能水平': profile.get('overall_functioning', '')
            })
        
        export_data.append(export_row)
    
    return export_data