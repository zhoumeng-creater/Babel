"""统一评估核心模块 - 生成行为并同时进行ABC和DSM-5评估"""
import datetime
import numpy as np
from typing import Dict, List, Any, Optional

from common.api_client import call_kimi_api
from autism.configs import (
    CLINICAL_SCENE_CONFIG, 
    UNIFIED_AUTISM_PROFILES
)

from .abc_evaluator import evaluate_abc_behaviors, get_abc_severity_level
from .dsm5_evaluator import evaluate_dsm5_dialogue, extract_dsm5_observations


def build_unified_autism_prompt(autism_profile: Dict[str, Any]) -> str:
    """构建统一的孤独症儿童特征描述（不偏向任何评估标准）"""
    profile_description = f"""
    孤独症儿童行为特征配置：
    
    【社交特征】：{autism_profile['social_characteristics']}
    
    【沟通特征】：{autism_profile['communication_characteristics']}
    
    【行为特征】：{autism_profile['behavioral_characteristics']}
    
    【认知特征】：{autism_profile['cognitive_characteristics']}
    
    【情绪特征】：{autism_profile['emotional_characteristics']}
    
    【日常生活】：{autism_profile['daily_living']}
    
    【典型行为示例】：
    """
    
    # 添加行为示例
    for i, example in enumerate(autism_profile['behavioral_examples'], 1):
        profile_description += f"\n    {i}. {example}"
    
    system_prompt = (
        "你是一个专业的临床行为观察专家。请基于以下孤独症儿童的特征描述，"
        "真实地模拟该儿童在特定情境下的行为表现。\n"
        + profile_description +
        "\n\n行为表现要求："
        "\n1. 准确体现该儿童的社交、沟通、行为等各方面特征"
        "\n2. 行为表现要具体、生动、符合真实的孤独症儿童"
        "\n3. 包含足够的细节供后续评估（如具体动作、语言、反应等）"
        "\n4. 避免过于戏剧化，保持真实性"
        "\n\n严格格式：\"角色名:发言内容\"。每句换行。"
        "\n如需描述非语言行为，使用括号说明，如：孤独症儿童:（拍手）（看着窗外）"
    )
    
    return system_prompt


def call_kimi_with_unified_profile(prompt: str, autism_profile: Dict[str, Any]) -> str:
    """调用API生成基于统一配置的孤独症儿童对话"""
    system_prompt = build_unified_autism_prompt(autism_profile)
    return call_kimi_api(prompt, system_prompt, temperature=0.7)


def run_single_experiment(experiment_config: Dict[str, Any]) -> Dict[str, Any]:
    """运行单个实验 - 生成一次对话，同时进行ABC和DSM-5评估"""
    try:
        scene_data = CLINICAL_SCENE_CONFIG[experiment_config['scene']]
        
        # 构建统一的prompt（不提及任何评估标准）
        prompt = (
            f"临床观察情境：{experiment_config['scene']} - {experiment_config['activity']}\n"
            f"观察要点：{', '.join(scene_data['observation_points'][:3])}\n"
            f"触发因素：{experiment_config['trigger']}\n"
            f"参与角色：孤独症儿童、{scene_data['roles'][1]}、{scene_data['roles'][2]}\n"
            f"请模拟该孤独症儿童在此情境下的真实行为表现。\n"
            f"要求：15-20轮对话，真实体现儿童的特征，包含具体的行为细节。\n"
            f"格式：'角色名:内容'，每句换行。非语言行为用括号描述。"
        )
        
        # 生成对话（只生成一次）
        dialogue = call_kimi_with_unified_profile(prompt, experiment_config['autism_profile'])
        
        # 同时进行两种评估
        # 1. ABC评估
        abc_scores, identified_behaviors = evaluate_abc_behaviors(
            dialogue, 
            experiment_config['autism_profile'], 
            scene_data
        )
        abc_total_score = sum(abc_scores.values())
        abc_severity = get_abc_severity_level(abc_total_score)
        
        # 2. DSM-5评估
        dsm5_scores = evaluate_dsm5_dialogue(
            dialogue, 
            experiment_config['autism_profile'], 
            scene_data
        )
        clinical_observations = extract_dsm5_observations(dialogue)
        
        # 构建统一的记录结构
        record = {
            'experiment_id': experiment_config['experiment_id'],
            'timestamp': datetime.datetime.now(),
            'template': experiment_config['template'],
            'scene': experiment_config['scene'],
            'activity': experiment_config['activity'],
            'trigger': experiment_config['trigger'],
            'autism_profile': experiment_config['autism_profile'],
            'dialogue': dialogue,
            
            # ABC评估结果
            'abc_evaluation': {
                'total_score': abc_total_score,
                'severity': abc_severity,
                'domain_scores': abc_scores,
                'identified_behaviors': identified_behaviors
            },
            
            # DSM-5评估结果
            'dsm5_evaluation': {
                'scores': dsm5_scores,
                'clinical_observations': clinical_observations,
                'core_symptom_average': (dsm5_scores.get('社交互动质量', 0) + 
                                        dsm5_scores.get('沟通交流能力', 0) + 
                                        dsm5_scores.get('刻板重复行为', 0)) / 3
            },
            
            'notes': f"统一评估 - {experiment_config['template']}",
            
            # 保留兼容性字段（用于旧代码）
            'assessment_standard': 'UNIFIED',
            'evaluation_scores': {**abc_scores, **dsm5_scores},  # 合并两种评分
            'abc_total_score': abc_total_score,
            'abc_severity': abc_severity,
            'identified_behaviors': identified_behaviors,
            'clinical_observations': clinical_observations
        }
        
        return record
        
    except Exception as e:
        return {
            'experiment_id': experiment_config['experiment_id'],
            'timestamp': datetime.datetime.now(),
            'error': str(e),
            'template': experiment_config.get('template', 'unknown'),
            'scene': experiment_config.get('scene', 'unknown')
        }


def generate_experiment_batch(
    templates: Dict[str, Dict[str, Any]], 
    scenes: Dict[str, Dict[str, Any]], 
    num_experiments_per_combo: int = 3,
    assessment_standard: Optional[str] = None
) -> List[Dict[str, Any]]:
    """生成批量实验配置 - 不再需要指定评估标准"""
    # assessment_standard参数保留但忽略，用于向后兼容
    experiments = []
    experiment_counter = 0
    
    for template_name, profile in templates.items():
        for scene_name, scene_data in scenes.items():
            for activity in scene_data['activities'][:2]:
                for trigger in scene_data['triggers'][:2]:
                    for i in range(num_experiments_per_combo):
                        experiment_counter += 1
                        
                        # 添加轻微的随机变异
                        varied_profile = profile.copy()
                        
                        # 对行为示例进行轻微变化（随机选择部分示例）
                        if 'behavioral_examples' in varied_profile:
                            examples = varied_profile['behavioral_examples']
                            if len(examples) > 3:
                                # 随机选择3-5个示例
                                num_examples = np.random.randint(3, min(6, len(examples) + 1))
                                selected_examples = np.random.choice(examples, num_examples, replace=False)
                                varied_profile['behavioral_examples'] = list(selected_examples)
                        
                        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                        unique_id = f"UNI_{experiment_counter:03d}_{template_name[:4]}_{scene_name[:4]}_{timestamp}"
                        
                        experiments.append({
                            'template': template_name,
                            'scene': scene_name,
                            'activity': activity,
                            'trigger': trigger,
                            'autism_profile': varied_profile,
                            'experiment_id': unique_id,
                            'batch_index': experiment_counter
                        })
    
    return experiments