"""孤独症儿童评估逻辑"""
import datetime
import numpy as np
from common.api_client import call_kimi_api
from common.ui_components import generate_unique_id, add_random_variation
from .config import CLINICAL_SCENE_CONFIG, CLINICAL_EVALUATION_METRICS


def build_autism_prompt(autism_profile):
    """构建孤独症儿童特征描述"""
    profile_description = f"""
    孤独症儿童临床特征配置（基于DSM-5标准）：
    - DSM-5严重程度: {autism_profile.get('dsm5_severity', '未指定')}
    - 社交沟通缺陷程度: {autism_profile['social_communication']}/5 (5为最严重)
    - 刻板重复行为程度: {autism_profile['restricted_repetitive']}/5
    - 感官处理异常: {autism_profile['sensory_processing']}/5
    - 认知功能水平: {autism_profile['cognitive_function']}/5 (1为重度障碍，5为正常)
    - 适应行为能力: {autism_profile['adaptive_behavior']}/5
    - 语言发展水平: {autism_profile['language_level']}/5
    - 特殊兴趣领域: {autism_profile['special_interests']}
    - 所需支持水平: {autism_profile.get('support_needs', '未指定')}
    """
    
    system_prompt = (
        "你是一个专业的孤独症临床行为专家，请严格按照以下DSM-5诊断标准和临床特征来模拟孤独症儿童的行为：\n"
        + profile_description +
        "\n核心症状表现要求："
        "\n1. 社交沟通缺陷：根据严重程度展现眼神回避、社交发起困难、情感分享受限等"
        "\n2. 刻板重复行为：体现重复动作、仪式化行为、狭隘兴趣、感官异常等"
        "\n3. 感官处理：根据敏感度显示过敏、寻求或逃避特定感官刺激"
        "\n4. 语言特点：根据语言水平展现回声式语言、字面理解、语用困难等"
        "\n5. 情绪调节：根据调节能力显示情绪爆发、自我安抚行为等"
        "\n严格格式：\"角色名:发言内容\"。每句换行，语言真实自然，行为符合临床观察特点。"
    )
    
    return system_prompt


def call_kimi_with_autism_profile(prompt, autism_profile):
    """调用API生成孤独症儿童对话"""
    system_prompt = build_autism_prompt(autism_profile)
    return call_kimi_api(prompt, system_prompt, temperature=0.6)


def clinical_evaluate_dialogue(dialogue, autism_profile, scene_info):
    """基于临床标准评估对话质量"""
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    
    if not autism_child_lines:
        return {metric: 0.0 for metric in CLINICAL_EVALUATION_METRICS.keys()}
    
    evaluation_scores = {}
    
    # 社交互动质量评估
    social_base = autism_profile['social_communication']
    interaction_indicators = 0
    
    # 检查社交发起行为
    proactive_social = len([line for line in autism_child_lines if any(word in line for word in ['我想', '我们一起', '可以吗', '你好'])])
    if proactive_social > 0:
        interaction_indicators += 1
    
    # 检查社交反应
    responsive_social = len([line for line in autism_child_lines if any(word in line for word in ['好的', '是的', '不要', '谢谢'])])
    if responsive_social > len(autism_child_lines) * 0.3:
        interaction_indicators += 1
    
    social_score = social_base - (interaction_indicators * 0.5)
    evaluation_scores["社交互动质量"] = max(1, min(5, social_score))
    
    # 沟通交流能力评估
    comm_base = autism_profile['social_communication']
    communication_quality = 0
    
    # 检查语言功能性
    functional_language = len([line for line in autism_child_lines if any(word in line for word in ['我要', '帮助', '不懂', '为什么'])])
    if functional_language > 0:
        communication_quality += 1
    
    # 检查回声式语言（重复他人话语）
    echolalia_signs = len([line for line in autism_child_lines if '?' in line and len(line.split()) < 5])
    if echolalia_signs > 0:
        communication_quality -= 0.5
    
    # 根据语言水平调整
    language_modifier = (autism_profile['language_level'] - 3) * 0.3
    comm_score = comm_base - communication_quality + language_modifier
    evaluation_scores["沟通交流能力"] = max(1, min(5, comm_score))
    
    # 刻板重复行为评估
    repetitive_base = autism_profile['restricted_repetitive']
    repetitive_indicators = 0
    
    # 检查重复表达
    repeated_phrases = len(set(autism_child_lines)) / len(autism_child_lines) if autism_child_lines else 1
    if repeated_phrases < 0.7:  # 如果重复率高
        repetitive_indicators += 1
    
    # 检查特殊兴趣相关表达
    special_interest_mentions = len([line for line in autism_child_lines 
                                   if any(interest.lower() in line.lower() 
                                         for interest in autism_profile['special_interests'].split('、'))])
    if special_interest_mentions > len(autism_child_lines) * 0.3:
        repetitive_indicators += 1
    
    repetitive_score = repetitive_base + (repetitive_indicators * 0.5)
    evaluation_scores["刻板重复行为"] = max(1, min(5, repetitive_score))
    
    # 感官处理能力评估  
    sensory_base = autism_profile['sensory_processing']
    sensory_responses = 0
    
    # 检查感官相关反应
    sensory_words = ['太吵', '太亮', '不喜欢', '害怕', '疼', '舒服']
    sensory_mentions = len([line for line in autism_child_lines 
                           if any(word in line for word in sensory_words)])
    if sensory_mentions > 0:
        sensory_responses = min(sensory_mentions * 0.3, 1.0)
    
    sensory_score = sensory_base - (sensory_responses * 0.5)
    evaluation_scores["感官处理能力"] = max(1, min(5, sensory_score))
    
    # 情绪行为调节评估
    emotion_base = autism_profile['social_communication']  # 基于社交沟通缺陷推断情绪调节
    emotion_regulation = 0
    
    # 检查情绪表达
    emotion_words = ['开心', '难过', '生气', '害怕', '着急', '不高兴']
    emotion_expressions = len([line for line in autism_child_lines 
                              if any(word in line for word in emotion_words)])
    if emotion_expressions > 0:
        emotion_regulation += 0.5
    
    # 检查调节策略
    regulation_words = ['我需要', '休息', '安静', '停止']
    regulation_attempts = len([line for line in autism_child_lines 
                              if any(word in line for word in regulation_words)])
    if regulation_attempts > 0:
        emotion_regulation += 0.5
    
    emotion_score = emotion_base - emotion_regulation
    evaluation_scores["情绪行为调节"] = max(1, min(5, emotion_score))
    
    # 认知适应功能评估
    cognitive_base = 6 - autism_profile['cognitive_function']  # 转换评分方向
    adaptation_quality = 0
    
    # 检查问题解决尝试
    problem_solving = len([line for line in autism_child_lines 
                          if any(word in line for word in ['怎么办', '试试', '想想', '办法'])])
    if problem_solving > 0:
        adaptation_quality += 0.5
    
    # 检查学习表现
    learning_indicators = len([line for line in autism_child_lines 
                              if any(word in line for word in ['学会', '知道了', '明白', '记住'])])
    if learning_indicators > 0:
        adaptation_quality += 0.5
    
    cognitive_score = cognitive_base - adaptation_quality
    evaluation_scores["认知适应功能"] = max(1, min(5, cognitive_score))
    
    # 添加随机变异模拟真实评估的不确定性
    for metric in evaluation_scores:
        variation = np.random.normal(0, 0.2)  # 小幅随机变化
        evaluation_scores[metric] = max(1, min(5, evaluation_scores[metric] + variation))
        evaluation_scores[metric] = round(evaluation_scores[metric], 2)
    
    return evaluation_scores


def extract_clinical_observations(dialogue):
    """从对话中提取临床观察要点"""
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    
    observations = {
        "社交行为观察": [],
        "语言沟通特点": [],
        "重复行为表现": [],
        "感官反应": [],
        "情绪调节": []
    }
    
    for line in autism_child_lines:
        # 社交行为识别
        if any(word in line for word in ['你好', '再见', '一起', '朋友']):
            observations["社交行为观察"].append("主动社交尝试")
        elif any(word in line for word in ['不要', '不喜欢', '走开']):
            observations["社交行为观察"].append("社交回避行为")
        
        # 语言特点识别  
        if line.count('是') > 2 or line.count('不') > 2:
            observations["语言沟通特点"].append("回声式语言特征")
        if any(word in line for word in ['为什么', '什么时候', '在哪里']):
            observations["语言沟通特点"].append("疑问句使用")
        
        # 重复行为识别
        if any(word in line for word in ['又', '还要', '一直', '再']):
            observations["重复行为表现"].append("重复需求表达")
        
        # 感官反应识别
        if any(word in line for word in ['太吵', '太亮', '疼', '痒']):
            observations["感官反应"].append("感官过敏反应")
        
        # 情绪识别
        if any(word in line for word in ['生气', '难过', '害怕', '开心']):
            observations["情绪调节"].append("情绪表达尝试")
    
    # 清理空列表
    observations = {k: v for k, v in observations.items() if v}
    
    return observations


def run_single_experiment(experiment_config):
    """运行单个实验"""
    try:
        scene_data = CLINICAL_SCENE_CONFIG[experiment_config['scene']]
        
        # 构建基于临床观察的prompt
        prompt = (
            f"临床观察情境：{experiment_config['scene']} - {experiment_config['activity']}\n"
            f"观察要点：{', '.join(scene_data['observation_points'][:3])}\n"
            f"触发因素：{experiment_config['trigger']}\n"
            f"参与角色：孤独症儿童、{scene_data['roles'][1]}、{scene_data['roles'][2]}\n"
            f"请基于DSM-5孤独症诊断标准，模拟该儿童在此情境下的真实行为表现。\n"
            f"要求：15-20轮对话，体现核心症状（社交沟通缺陷、刻板重复行为），"
            f"语言和行为符合该严重程度的临床特征。\n"
            f"格式：'角色名:内容'，每句换行。"
        )
        
        dialogue = call_kimi_with_autism_profile(prompt, experiment_config['autism_profile'])
        
        # 使用临床标准评估
        evaluation_scores = clinical_evaluate_dialogue(
            dialogue, 
            experiment_config['autism_profile'], 
            CLINICAL_SCENE_CONFIG[experiment_config['scene']]
        )
        
        record = {
            'experiment_id': experiment_config['experiment_id'],
            'timestamp': datetime.datetime.now(),
            'template': experiment_config['template'],
            'scene': experiment_config['scene'],
            'activity': experiment_config['activity'],
            'trigger': experiment_config['trigger'],
            'autism_profile': experiment_config['autism_profile'],
            'dialogue': dialogue,
            'evaluation_scores': evaluation_scores,
            'clinical_observations': extract_clinical_observations(dialogue),
            'notes': f"临床标准评估 - {experiment_config['template']}"
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


def generate_experiment_batch(templates, scenes, num_experiments_per_combo=3):
    """生成批量实验配置"""
    experiments = []
    experiment_counter = 0
    
    for template_name, profile in templates.items():
        for scene_name, scene_data in scenes.items():
            for activity in scene_data['activities'][:2]:
                for trigger in scene_data['triggers'][:2]:
                    for i in range(num_experiments_per_combo):
                        experiment_counter += 1
                        
                        # 添加轻微临床变异
                        varied_profile = add_random_variation(
                            profile, 
                            ['social_communication', 'restricted_repetitive', 'sensory_processing']
                        )
                        
                        experiment_id = generate_unique_id(
                            "CLIN", template_name, scene_name, experiment_counter
                        )
                        
                        experiments.append({
                            'template': template_name,
                            'scene': scene_name,
                            'activity': activity,
                            'trigger': trigger,
                            'autism_profile': varied_profile,
                            'experiment_id': experiment_id,
                            'batch_index': experiment_counter
                        })
    
    return experiments