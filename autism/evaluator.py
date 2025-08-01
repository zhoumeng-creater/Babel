"""孤独症儿童评估逻辑 - 支持统一生成、双标准评估"""
import datetime
import numpy as np
from common.api_client import call_kimi_api
from common.ui_components import generate_unique_id, add_random_variation
from .config import (
    CLINICAL_SCENE_CONFIG, UNIFIED_AUTISM_PROFILES,
    ABC_BEHAVIOR_ITEMS, ABC_EVALUATION_METRICS,
    DSM5_EVALUATION_METRICS
)


# ==================== 统一的对话生成函数 ====================
def build_unified_autism_prompt(autism_profile):
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


def call_kimi_with_unified_profile(prompt, autism_profile):
    """调用API生成基于统一配置的孤独症儿童对话"""
    system_prompt = build_unified_autism_prompt(autism_profile)
    return call_kimi_api(prompt, system_prompt, temperature=0.7)


# ==================== 修改后的实验运行函数 ====================
def run_single_experiment(experiment_config):
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


def generate_experiment_batch(templates, scenes, num_experiments_per_combo=3, assessment_standard=None):
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


# ==================== ABC评估函数（保持不变） ====================
def evaluate_abc_behaviors(dialogue, autism_profile, scene_info):
    """基于ABC量表评估对话中的行为表现"""
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    all_lines = lines  # 包括所有角色的对话，用于分析互动
    
    # 初始化各领域得分
    domain_scores = {
        "感觉领域得分": 0,
        "交往领域得分": 0,
        "躯体运动领域得分": 0,
        "语言领域得分": 0,
        "社交与自理领域得分": 0
    }
    
    # 记录识别到的行为
    identified_behaviors = {
        "感觉领域": [],
        "交往领域": [],
        "躯体运动领域": [],
        "语言领域": [],
        "社交与自理领域": []
    }
    
    # 根据整体功能水平估算行为出现概率
    functioning_level = autism_profile.get('overall_functioning', 'need_support')
    behavior_probability = {
        'mainstream_with_support': 0.3,
        'need_support': 0.5,
        'need_substantial_support': 0.7,
        'need_very_substantial_support': 0.9,
        'variable_support_needs': 0.6
    }.get(functioning_level, 0.5)
    
    # 评估感觉领域行为
    sensory_score = evaluate_sensory_behaviors(
        autism_child_lines, all_lines, behavior_probability,
        identified_behaviors["感觉领域"]
    )
    domain_scores["感觉领域得分"] = sensory_score
    
    # 评估交往领域行为
    social_score = evaluate_social_behaviors(
        autism_child_lines, all_lines, behavior_probability,
        identified_behaviors["交往领域"]
    )
    domain_scores["交往领域得分"] = social_score
    
    # 评估躯体运动领域行为
    motor_score = evaluate_motor_behaviors(
        autism_child_lines, all_lines, behavior_probability,
        identified_behaviors["躯体运动领域"]
    )
    domain_scores["躯体运动领域得分"] = motor_score
    
    # 评估语言领域行为
    language_score = evaluate_language_behaviors(
        autism_child_lines, all_lines, behavior_probability,
        identified_behaviors["语言领域"]
    )
    domain_scores["语言领域得分"] = language_score
    
    # 评估社交与自理领域行为
    selfcare_score = evaluate_selfcare_behaviors(
        autism_child_lines, all_lines, behavior_probability,
        identified_behaviors["社交与自理领域"], scene_info
    )
    domain_scores["社交与自理领域得分"] = selfcare_score
    
    # 添加随机变异
    for domain in domain_scores:
        variation = np.random.normal(0, 0.1) * domain_scores[domain]
        domain_scores[domain] = max(0, min(domain_scores[domain] + variation, 
                                         get_max_score_for_domain(domain)))
        domain_scores[domain] = round(domain_scores[domain], 1)
    
    return domain_scores, identified_behaviors


def get_abc_severity_level(total_score):
    """根据ABC总分判断严重程度"""
    if total_score >= 101:
        return "重度孤独症"
    elif total_score >= 67:
        return "中度孤独症"
    elif total_score >= 53:
        return "轻度孤独症"
    elif total_score >= 40:
        return "边缘状态"
    else:
        return "非孤独症"


# ==================== DSM-5评估函数（保持不变） ====================
def evaluate_dsm5_dialogue(dialogue, autism_profile, scene_info):
    """基于DSM-5标准评估对话质量"""
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    
    if not autism_child_lines:
        return {metric: 0.0 for metric in DSM5_EVALUATION_METRICS.keys()}
    
    evaluation_scores = {}
    
    # 根据整体功能水平设置基础分数
    functioning_level = autism_profile.get('overall_functioning', 'need_support')
    base_severity = {
        'mainstream_with_support': 2,
        'need_support': 3,
        'need_substantial_support': 4,
        'need_very_substantial_support': 5,
        'variable_support_needs': 3
    }.get(functioning_level, 3)
    
    # 社交互动质量评估
    interaction_indicators = 0
    
    # 检查社交发起行为
    proactive_social = len([line for line in autism_child_lines if any(word in line for word in ['我想', '我们一起', '可以吗', '你好'])])
    if proactive_social > 0:
        interaction_indicators += 1
    
    # 检查社交反应
    responsive_social = len([line for line in autism_child_lines if any(word in line for word in ['好的', '是的', '不要', '谢谢'])])
    if responsive_social > len(autism_child_lines) * 0.3:
        interaction_indicators += 1
    
    social_score = base_severity - (interaction_indicators * 0.5)
    evaluation_scores["社交互动质量"] = max(1, min(5, social_score))
    
    # 沟通交流能力评估
    communication_quality = 0
    
    # 检查语言功能性
    functional_language = len([line for line in autism_child_lines if any(word in line for word in ['我要', '帮助', '不懂', '为什么'])])
    if functional_language > 0:
        communication_quality += 1
    
    # 检查回声式语言（重复他人话语）
    echolalia_signs = len([line for line in autism_child_lines if '?' in line and len(line.split()) < 5])
    if echolalia_signs > 0:
        communication_quality -= 0.5
    
    comm_score = base_severity - communication_quality + 0.5
    evaluation_scores["沟通交流能力"] = max(1, min(5, comm_score))
    
    # 刻板重复行为评估
    repetitive_indicators = 0
    
    # 检查重复表达
    repeated_phrases = len(set(autism_child_lines)) / len(autism_child_lines) if autism_child_lines else 1
    if repeated_phrases < 0.7:  # 如果重复率高
        repetitive_indicators += 1
    
    # 检查括号中的刻板动作描述
    stereotyped_actions = len([line for line in autism_child_lines if '（' in line and any(word in line for word in ['拍手', '摇', '转', '跳'])])
    if stereotyped_actions > 0:
        repetitive_indicators += 1
    
    repetitive_score = base_severity + (repetitive_indicators * 0.5)
    evaluation_scores["刻板重复行为"] = max(1, min(5, repetitive_score))
    
    # 感官处理能力评估  
    sensory_responses = 0
    
    # 检查感官相关反应
    sensory_words = ['太吵', '太亮', '不喜欢', '害怕', '疼', '舒服', '声音', '光']
    sensory_mentions = len([line for line in autism_child_lines 
                           if any(word in line for word in sensory_words)])
    if sensory_mentions > 0:
        sensory_responses = min(sensory_mentions * 0.3, 1.0)
    
    sensory_score = base_severity - (sensory_responses * 0.5) + 0.3
    evaluation_scores["感官处理能力"] = max(1, min(5, sensory_score))
    
    # 情绪行为调节评估
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
    
    emotion_score = base_severity - emotion_regulation + 0.3
    evaluation_scores["情绪行为调节"] = max(1, min(5, emotion_score))
    
    # 认知适应功能评估
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
    
    cognitive_score = base_severity - adaptation_quality + 0.2
    evaluation_scores["认知适应功能"] = max(1, min(5, cognitive_score))
    
    # 添加随机变异模拟真实评估的不确定性
    for metric in evaluation_scores:
        variation = np.random.normal(0, 0.2)  # 小幅随机变化
        evaluation_scores[metric] = max(1, min(5, evaluation_scores[metric] + variation))
        evaluation_scores[metric] = round(evaluation_scores[metric], 2)
    
    return evaluation_scores


def extract_dsm5_observations(dialogue):
    """从对话中提取DSM-5临床观察要点"""
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
        if '（' in line and '）' in line:
            action = line[line.find('（')+1:line.find('）')]
            if any(word in action for word in ['拍', '摇', '转', '跳']):
                observations["重复行为表现"].append(f"刻板动作：{action}")
        
        # 感官反应识别
        if any(word in line for word in ['太吵', '太亮', '疼', '痒']):
            observations["感官反应"].append("感官过敏反应")
        
        # 情绪识别
        if any(word in line for word in ['生气', '难过', '害怕', '开心']):
            observations["情绪调节"].append("情绪表达尝试")
    
    # 清理空列表
    observations = {k: v for k, v in observations.items() if v}
    
    return observations


# ==================== ABC评估辅助函数（保持不变） ====================
def get_max_score_for_domain(domain):
    """获取各领域的最高分"""
    max_scores = {
        "感觉领域得分": 22,
        "交往领域得分": 41,
        "躯体运动领域得分": 28,
        "语言领域得分": 42,
        "社交与自理领域得分": 25
    }
    return max_scores.get(domain, 0)


def evaluate_sensory_behaviors(child_lines, all_lines, probability, identified_list):
    """评估感觉领域行为"""
    score = 0
    sensory_items = ABC_BEHAVIOR_ITEMS["感觉领域"]["items"]
    
    # 检查各种感觉异常行为
    sensory_keywords = {
        "声音反应": ["太吵", "声音", "听不到", "捂耳朵", "害怕声音"],
        "视觉敏感": ["光", "亮", "看", "盯着", "转圈"],
        "触觉异常": ["不喜欢碰", "摸", "触摸", "碰我"],
        "疼痛反应": ["疼", "痛", "摔倒", "受伤"],
        "特殊感觉": ["闻", "舔", "尝", "转圈"]
    }
    
    for line in child_lines:
        for behavior_type, keywords in sensory_keywords.items():
            if any(keyword in line for keyword in keywords):
                # 根据概率决定是否记录该行为
                if np.random.random() < probability:
                    # 随机选择相关的行为项目
                    related_items = [item for item in sensory_items 
                                   if behavior_type.lower() in item["description"].lower()]
                    if related_items:
                        selected_item = np.random.choice(related_items)
                        score += selected_item["weight"]
                        identified_list.append(selected_item["description"])
    
    # 基于对话分析额外加分
    if len(child_lines) > 0:
        # 如果很少回应他人，可能有听觉异常
        response_rate = len([line for line in child_lines if "?" not in line]) / len(child_lines)
        if response_rate < 0.3 and np.random.random() < probability:
            score += sensory_items[0]["weight"]  # S1: 对声音的反应异常
            identified_list.append(sensory_items[0]["description"])
    
    return min(score, 22)  # 感觉领域最高分22


def evaluate_social_behaviors(child_lines, all_lines, probability, identified_list):
    """评估交往领域行为"""
    score = 0
    social_items = ABC_BEHAVIOR_ITEMS["交往领域"]["items"]
    
    # 检查社交障碍行为
    social_keywords = {
        "回避交流": ["不要", "走开", "别碰我", "自己玩"],
        "缺乏回应": ["...", "不说话", "沉默"],
        "目光问题": ["不看", "眼睛", "看别处"],
        "情感冷漠": ["不在乎", "无所谓", "不关心"],
        "独处倾向": ["一个人", "自己", "不跟你玩"]
    }
    
    # 分析整体对话模式
    total_interactions = len([line for line in all_lines if "老师" in line or "同学" in line])
    child_responses = len([line for line in child_lines if any(word in line for word in ["好", "嗯", "是"])])
    
    # 低回应率表明社交障碍
    if total_interactions > 0:
        response_rate = child_responses / total_interactions
        if response_rate < 0.3 and np.random.random() < probability:
            score += social_items[1]["weight"]  # R2: 对别人的呼唤没有反应
            identified_list.append(social_items[1]["description"])
    
    # 检查具体行为
    for line in child_lines:
        for behavior_type, keywords in social_keywords.items():
            if any(keyword in line for keyword in keywords):
                if np.random.random() < probability:
                    related_items = [item for item in social_items 
                                   if any(k in item["description"] for k in keywords)]
                    if related_items:
                        selected_item = np.random.choice(related_items)
                        if selected_item["description"] not in identified_list:
                            score += selected_item["weight"]
                            identified_list.append(selected_item["description"])
    
    # 基于严重程度添加核心症状
    if probability > 0.6:  # 中重度
        core_behaviors = ["很少主动与人交往", "不能与小朋友玩耍", "对亲人没有依恋"]
        for behavior in core_behaviors:
            if np.random.random() < probability * 0.8:
                item = next((item for item in social_items if item["description"] == behavior), None)
                if item and item["description"] not in identified_list:
                    score += item["weight"]
                    identified_list.append(item["description"])
    
    return min(score, 41)  # 交往领域最高分41


def evaluate_motor_behaviors(child_lines, all_lines, probability, identified_list):
    """评估躯体运动领域行为"""
    score = 0
    motor_items = ABC_BEHAVIOR_ITEMS["躯体运动领域"]["items"]
    
    # 检查刻板动作
    motor_keywords = {
        "重复动作": ["拍手", "摇", "晃", "重复", "一直"],
        "特殊动作": ["转圈", "踮脚", "跳", "特殊姿势"],
        "自我刺激": ["摸自己", "抓", "咬", "打自己"],
        "运动异常": ["走来走去", "跑来跑去", "停不下来"]
    }
    
    for line in child_lines:
        # 检查括号内的动作描述
        if "（" in line and "）" in line:
            action_desc = line[line.find("（")+1:line.find("）")]
            for behavior_type, keywords in motor_keywords.items():
                if any(keyword in action_desc for keyword in keywords):
                    if np.random.random() < probability:
                        related_items = [item for item in motor_items 
                                       if any(k in item["description"] for k in keywords)]
                        if related_items:
                            selected_item = np.random.choice(related_items)
                            if selected_item["description"] not in identified_list:
                                score += selected_item["weight"]
                                identified_list.append(selected_item["description"])
    
    # 对话内容中的刻板表现
    for line in child_lines:
        if any(word in line for word in ["转", "摇", "拍", "跳"]):
            if np.random.random() < probability * 0.7:
                relevant_item = motor_items[0]  # M1: 重复性的手部动作
                if relevant_item["description"] not in identified_list:
                    score += relevant_item["weight"]
                    identified_list.append(relevant_item["description"])
    
    return min(score, 28)  # 躯体运动领域最高分28


def evaluate_language_behaviors(child_lines, all_lines, probability, identified_list):
    """评估语言领域行为"""
    score = 0
    language_items = ABC_BEHAVIOR_ITEMS["语言领域"]["items"]
    
    # 基础语言分析
    if not child_lines:
        # 完全无语言
        score += language_items[0]["weight"]  # L1: 无语言或语言发育迟缓
        identified_list.append(language_items[0]["description"])
        return score
    
    # 检查语言异常模式
    language_patterns = {
        "重复语言": check_echolalia(child_lines, all_lines),
        "自言自语": check_self_talk(child_lines),
        "答非所问": check_irrelevant_responses(child_lines, all_lines),
        "代词混用": check_pronoun_confusion(child_lines),
        "语言刻板": check_stereotyped_language(child_lines)
    }
    
    for pattern_type, is_present in language_patterns.items():
        if is_present and np.random.random() < probability:
            # 找到对应的行为项目
            if pattern_type == "重复语言":
                score += language_items[1]["weight"]  # L2: 重复他人的话
                identified_list.append(language_items[1]["description"])
            elif pattern_type == "自言自语":
                score += language_items[3]["weight"]  # L4: 自言自语
                identified_list.append(language_items[3]["description"])
            elif pattern_type == "答非所问":
                score += language_items[11]["weight"]  # L12: 答非所问
                identified_list.append(language_items[11]["description"])
    
    # 语言功能分析
    functional_language = len([line for line in child_lines 
                             if any(word in line for word in ["我要", "帮我", "给我", "可以吗"])])
    
    if functional_language < len(child_lines) * 0.2 and np.random.random() < probability:
        score += language_items[4]["weight"]  # L5: 不能进行对话
        identified_list.append(language_items[4]["description"])
    
    # 基于严重程度添加额外语言问题
    if probability > 0.7:  # 重度
        if np.random.random() < 0.8:
            score += language_items[7]["weight"]  # L8: 不能理解简单指令
            identified_list.append(language_items[7]["description"])
    
    return min(score, 42)  # 语言领域最高分42


def evaluate_selfcare_behaviors(child_lines, all_lines, probability, identified_list, scene_info):
    """评估社交与自理领域行为"""
    score = 0
    selfcare_items = ABC_BEHAVIOR_ITEMS["社交与自理领域"]["items"]
    
    # 检查自理和适应问题
    selfcare_keywords = {
        "依赖性强": ["帮我", "不会", "不能", "妈妈"],
        "情绪问题": ["生气", "哭", "发脾气", "不高兴"],
        "特殊依恋": ["我的", "不给", "一定要", "必须"],
        "刻板行为": ["必须", "一定", "不能变", "就要这样"]
    }
    
    for line in child_lines:
        for behavior_type, keywords in selfcare_keywords.items():
            if any(keyword in line for keyword in keywords):
                if np.random.random() < probability:
                    # 选择相关行为项目
                    if behavior_type == "情绪问题":
                        score += selfcare_items[10]["weight"]  # A11: 情绪不稳定
                        identified_list.append(selfcare_items[10]["description"])
                    elif behavior_type == "特殊依恋":
                        score += selfcare_items[5]["weight"]  # A6: 对物体的特殊依恋
                        identified_list.append(selfcare_items[5]["description"])
    
    # 基于场景添加相关行为
    if "日常生活" in scene_info.get("desc", ""):
        if np.random.random() < probability * 0.8:
            score += selfcare_items[7]["weight"]  # A8: 不能独立穿衣
            identified_list.append(selfcare_items[7]["description"])
    
    # 玩耍能力评估
    play_related = [line for line in child_lines if "玩" in line or "玩具" in line]
    if play_related and np.random.random() < probability:
        score += selfcare_items[4]["weight"]  # A5: 不会玩玩具
        identified_list.append(selfcare_items[4]["description"])
    
    return min(score, 25)  # 社交与自理领域最高分25


# 辅助函数
def check_echolalia(child_lines, all_lines):
    """检查是否有鹦鹉学舌现象"""
    for i, line in enumerate(all_lines):
        if "孤独症儿童" not in line and i < len(all_lines) - 1:
            next_line = all_lines[i + 1]
            if "孤独症儿童" in next_line:
                # 检查是否重复前面的话
                prev_content = line.split(":")[-1] if ":" in line else line
                child_content = next_line.split(":")[-1] if ":" in next_line else next_line
                if len(prev_content) > 5 and prev_content in child_content:
                    return True
    return False


def check_self_talk(child_lines):
    """检查是否有自言自语"""
    for line in child_lines:
        if not any(word in line for word in ["你", "老师", "同学", "妈妈", "爸爸"]):
            if len(line.split(":")[-1]) > 10:  # 较长的独白
                return True
    return False


def check_irrelevant_responses(child_lines, all_lines):
    """检查是否答非所问"""
    question_words = ["什么", "为什么", "怎么", "吗", "呢", "？"]
    for i, line in enumerate(all_lines):
        if any(word in line for word in question_words) and "孤独症儿童" not in line:
            # 找下一个儿童的回答
            for j in range(i+1, min(i+5, len(all_lines))):
                if "孤独症儿童" in all_lines[j]:
                    response = all_lines[j].split(":")[-1] if ":" in all_lines[j] else all_lines[j]
                    # 简单判断是否相关
                    if len(response) < 5 or not any(word in response for word in ["好", "不", "要", "是"]):
                        return True
                    break
    return False


def check_pronoun_confusion(child_lines):
    """检查代词混用"""
    for line in child_lines:
        # 如果用"你"指代自己
        if "你要" in line or "你想" in line:
            context = line.split(":")[-1] if ":" in line else line
            if "我" not in context:  # 可能是代词混用
                return True
    return False


def check_stereotyped_language(child_lines):
    """检查语言刻板重复"""
    if len(child_lines) < 3:
        return False
    
    # 检查是否有重复的句式
    phrases = [line.split(":")[-1] if ":" in line else line for line in child_lines]
    for i in range(len(phrases) - 2):
        if phrases[i] == phrases[i+2]:  # 隔句重复
            return True
    
    return False