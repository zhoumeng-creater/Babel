"""正常儿童发展评估逻辑"""
import datetime
import numpy as np
from common.api_client import call_kimi_api
from common.ui_components import generate_unique_id, add_random_variation
from .config import DEVELOPMENT_SCENE_CONFIG, DEVELOPMENT_EVALUATION_METRICS


def build_child_prompt(child_profile):
    """构建正常儿童特征描述"""
    profile_description = f"""
    正常儿童发展特征配置（基于发育心理学理论）：
    - 年龄发展阶段: {child_profile.get('stage_characteristics', '未指定')}
    - 语言发展水平: {child_profile['language_development']}/5 (5为最高水平)
    - 社交技能水平: {child_profile['social_skills']}/5
    - 认知能力水平: {child_profile['cognitive_ability']}/5
    - 情绪调节能力: {child_profile['emotional_regulation']}/5
    - 运动技能发展: {child_profile['motor_skills']}/5
    - 独立性水平: {child_profile['independence_level']}/5
    - 典型兴趣爱好: {child_profile['typical_interests']}
    - 发展重点: {child_profile.get('development_focus', '未指定')}
    """
    
    system_prompt = (
        "你是一个专业的儿童发展心理学专家，请严格按照以下儿童发展理论来模拟正常健康儿童的行为：\n"
        + profile_description +
        "\n正常儿童行为表现要求："
        "\n1. 语言沟通：根据年龄展现相应的语言能力、词汇量和表达方式"
        "\n2. 社交互动：体现同龄儿童的社交兴趣、友谊建立和合作能力"
        "\n3. 认知学习：展现好奇心、学习兴趣和相应的思维能力"
        "\n4. 情绪发展：表现年龄适宜的情绪表达和调节能力"
        "\n5. 运动发展：体现相应的大运动和精细运动发展水平"
        "\n6. 独立能力：展现符合年龄的自理能力和独立性"
        "\n严格格式：\"角色名:发言内容\"。每句换行，语言生动自然，行为符合正常儿童发展特点。"
        "\n要求：展现儿童的纯真、好奇、活跃和成长特点，避免过于成熟或不符合年龄的表达。"
    )
    
    return system_prompt


def call_kimi_with_child_profile(prompt, child_profile):
    """调用API生成正常儿童对话"""
    system_prompt = build_child_prompt(child_profile)
    return call_kimi_api(prompt, system_prompt, temperature=0.7)


def evaluate_child_development(dialogue, child_profile, scene_info):
    """基于发育心理学评估儿童发展水平"""
    lines = dialogue.split('\n')
    child_lines = [line for line in lines if '儿童' in line]
    
    if not child_lines:
        return {metric: 3.0 for metric in DEVELOPMENT_EVALUATION_METRICS.keys()}
    
    evaluation_scores = {}
    
    # 语言沟通发展评估
    language_base = child_profile['language_development']
    language_indicators = 0
    
    # 检查语言表达质量
    expressive_quality = len([line for line in child_lines if any(word in line for word in ['我觉得', '我想要', '我喜欢', '因为'])])
    if expressive_quality > 0:
        language_indicators += 1
    
    # 检查交流主动性
    initiative_communication = len([line for line in child_lines if any(word in line for word in ['你好', '我们', '一起', '可以吗'])])
    if initiative_communication > 0:
        language_indicators += 1
    
    # 检查问题询问
    questioning = len([line for line in child_lines if '?' in line or any(word in line for word in ['为什么', '怎么', '什么'])])
    if questioning > 0:
        language_indicators += 0.5
    
    language_score = min(5, language_base + (language_indicators * 0.3))
    evaluation_scores["语言沟通发展"] = max(1, language_score)
    
    # 社交互动能力评估
    social_base = child_profile['social_skills']
    social_quality = 0
    
    # 检查友善互动
    friendly_interaction = len([line for line in child_lines if any(word in line for word in ['谢谢', '对不起', '分享', '帮助'])])
    if friendly_interaction > 0:
        social_quality += 1
    
    # 检查合作行为
    cooperation = len([line for line in child_lines if any(word in line for word in ['一起', '我们', '大家', '合作'])])
    if cooperation > 0:
        social_quality += 0.5
    
    # 检查情感表达
    emotional_expression = len([line for line in child_lines if any(word in line for word in ['开心', '高兴', '难过', '生气'])])
    if emotional_expression > 0:
        social_quality += 0.5
    
    social_score = min(5, social_base + (social_quality * 0.3))
    evaluation_scores["社交互动能力"] = max(1, social_score)
    
    # 认知学习能力评估
    cognitive_base = child_profile['cognitive_ability']
    cognitive_indicators = 0
    
    # 检查好奇探索
    curiosity = len([line for line in child_lines if any(word in line for word in ['为什么', '怎么', '想知道', '有趣'])])
    if curiosity > 0:
        cognitive_indicators += 1
    
    # 检查学习兴趣
    learning_interest = len([line for line in child_lines if any(word in line for word in ['学会', '明白', '知道了', '我懂了'])])
    if learning_interest > 0:
        cognitive_indicators += 0.5
    
    # 检查创造想象
    creativity = len([line for line in child_lines if any(word in line for word in ['想象', '创造', '发明', '设计'])])
    if creativity > 0:
        cognitive_indicators += 0.5
    
    cognitive_score = min(5, cognitive_base + (cognitive_indicators * 0.3))
    evaluation_scores["认知学习能力"] = max(1, cognitive_score)
    
    # 情绪调节发展评估  
    emotion_base = child_profile['emotional_regulation']
    emotion_regulation = 0
    
    # 检查情绪表达
    emotion_words = ['开心', '难过', '生气', '害怕', '兴奋', '紧张']
    emotion_expressions = len([line for line in child_lines 
                              if any(word in line for word in emotion_words)])
    if emotion_expressions > 0:
        emotion_regulation += 0.5
    
    # 检查同理心表现
    empathy_words = ['你还好吗', '没关系', '安慰', '关心']
    empathy_attempts = len([line for line in child_lines 
                           if any(word in line for word in empathy_words)])
    if empathy_attempts > 0:
        emotion_regulation += 0.5
    
    # 检查问题解决
    problem_solving = len([line for line in child_lines 
                          if any(word in line for word in ['试试', '想办法', '解决', '努力'])])
    if problem_solving > 0:
        emotion_regulation += 0.5
    
    emotion_score = min(5, emotion_base + (emotion_regulation * 0.3))
    evaluation_scores["情绪调节发展"] = max(1, emotion_score)
    
    # 运动技能发展评估
    motor_base = child_profile['motor_skills']
    motor_performance = 0
    
    # 检查运动相关活动
    motor_activities = len([line for line in child_lines 
                           if any(word in line for word in ['跑', '跳', '爬', '画', '拿', '做'])])
    if motor_activities > 0:
        motor_performance += 0.5
    
    # 检查精细动作
    fine_motor = len([line for line in child_lines 
                     if any(word in line for word in ['画画', '写字', '剪纸', '拼图'])])
    if fine_motor > 0:
        motor_performance += 0.5
    
    motor_score = min(5, motor_base + (motor_performance * 0.3))
    evaluation_scores["运动技能发展"] = max(1, motor_score)
    
    # 独立自理能力评估
    independence_base = child_profile['independence_level']
    independence_quality = 0
    
    # 检查自主行为
    autonomous_behavior = len([line for line in child_lines 
                              if any(word in line for word in ['我自己', '我来', '我会', '我能'])])
    if autonomous_behavior > 0:
        independence_quality += 0.5
    
    # 检查责任意识
    responsibility = len([line for line in child_lines 
                         if any(word in line for word in ['我的', '应该', '负责', '任务'])])
    if responsibility > 0:
        independence_quality += 0.5
    
    independence_score = min(5, independence_base + (independence_quality * 0.3))
    evaluation_scores["独立自理能力"] = max(1, independence_score)
    
    # 添加随机变异模拟真实发展的不确定性
    for metric in evaluation_scores:
        variation = np.random.normal(0, 0.15)  # 小幅随机变化
        evaluation_scores[metric] = max(1, min(5, evaluation_scores[metric] + variation))
        evaluation_scores[metric] = round(evaluation_scores[metric], 2)
    
    return evaluation_scores


def extract_developmental_observations(dialogue):
    """从对话中提取发展观察要点"""
    lines = dialogue.split('\n')
    child_lines = [line for line in lines if '儿童' in line]
    
    observations = {
        "语言表达特点": [],
        "社交互动表现": [],
        "认知学习行为": [],
        "情绪情感反应": [],
        "运动活动参与": []
    }
    
    for line in child_lines:
        # 语言表达识别
        if any(word in line for word in ['我想', '我觉得', '因为', '如果']):
            observations["语言表达特点"].append("复杂句式表达")
        elif any(word in line for word in ['为什么', '怎么', '什么']):
            observations["语言表达特点"].append("主动提问询问")
        
        # 社交互动识别  
        if any(word in line for word in ['一起', '我们', '分享', '帮助']):
            observations["社交互动表现"].append("合作分享意识")
        elif any(word in line for word in ['谢谢', '对不起', '请']):
            observations["社交互动表现"].append("礼貌社交行为")
        
        # 认知学习识别
        if any(word in line for word in ['学会', '明白', '知道', '理解']):
            observations["认知学习行为"].append("学习理解能力")
        elif any(word in line for word in ['想象', '创造', '发明']):
            observations["认知学习行为"].append("创造想象表现")
        
        # 情绪反应识别
        if any(word in line for word in ['开心', '高兴', '兴奋']):
            observations["情绪情感反应"].append("积极情绪表达")
        elif any(word in line for word in ['难过', '生气', '害怕']):
            observations["情绪情感反应"].append("情绪认知表达")
        
        # 运动活动识别
        if any(word in line for word in ['跑', '跳', '爬', '玩']):
            observations["运动活动参与"].append("大运动活动")
        elif any(word in line for word in ['画', '写', '做', '拼']):
            observations["运动活动参与"].append("精细动作表现")
    
    # 清理空列表
    observations = {k: v for k, v in observations.items() if v}
    
    return observations


def run_single_observation(observation_config):
    """运行单个观察"""
    try:
        scene_data = DEVELOPMENT_SCENE_CONFIG[observation_config['scene']]
        
        # 构建基于儿童发展的prompt
        prompt = (
            f"儿童成长观察情境：{observation_config['scene']} - {observation_config['activity']}\n"
            f"观察要点：{', '.join(scene_data['observation_points'][:3])}\n"
            f"情境触发：{observation_config['trigger']}\n"
            f"参与角色：儿童、{scene_data['roles'][1]}、{scene_data['roles'][2]}\n"
            f"请基于儿童发展心理学理论，模拟该年龄段儿童在此情境下的自然行为表现。\n"
            f"要求：15-20轮对话，体现儿童的天真好奇、活泼可爱，"
            f"语言和行为符合该年龄段的正常发展特征。\n"
            f"格式：'角色名:内容'，每句换行。体现儿童的纯真和成长活力。"
        )
        
        dialogue = call_kimi_with_child_profile(prompt, observation_config['child_profile'])
        
        # 使用发展标准评估
        evaluation_scores = evaluate_child_development(
            dialogue, 
            observation_config['child_profile'], 
            DEVELOPMENT_SCENE_CONFIG[observation_config['scene']]
        )
        
        record = {
            'observation_id': observation_config['observation_id'],
            'timestamp': datetime.datetime.now(),
            'template': observation_config['template'],
            'scene': observation_config['scene'],
            'activity': observation_config['activity'],
            'trigger': observation_config['trigger'],
            'child_profile': observation_config['child_profile'],
            'dialogue': dialogue,
            'evaluation_scores': evaluation_scores,
            'developmental_observations': extract_developmental_observations(dialogue),
            'notes': f"发展观察 - {observation_config['template']}"
        }
        
        return record
        
    except Exception as e:
        return {
            'observation_id': observation_config['observation_id'],
            'timestamp': datetime.datetime.now(),
            'error': str(e),
            'template': observation_config.get('template', 'unknown'),
            'scene': observation_config.get('scene', 'unknown')
        }


def generate_observation_batch(templates, scenes, num_observations_per_combo=3):
    """生成批量观察配置"""
    observations = []
    observation_counter = 0
    
    for template_name, profile in templates.items():
        for scene_name, scene_data in scenes.items():
            for activity in scene_data['activities'][:2]:
                for trigger in scene_data['triggers'][:2]:
                    for i in range(num_observations_per_combo):
                        observation_counter += 1
                        
                        # 添加轻微发展变异
                        varied_profile = add_random_variation(
                            profile, 
                            ['language_development', 'social_skills', 'cognitive_ability']
                        )
                        
                        observation_id = generate_unique_id(
                            "DEV", template_name, scene_name, observation_counter
                        )
                        
                        observations.append({
                            'template': template_name,
                            'scene': scene_name,
                            'activity': activity,
                            'trigger': trigger,
                            'child_profile': varied_profile,
                            'observation_id': observation_id,
                            'batch_index': observation_counter
                        })
    
    return observations