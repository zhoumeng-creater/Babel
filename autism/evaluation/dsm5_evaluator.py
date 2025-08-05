"""DSM-5标准评估逻辑模块"""
import numpy as np
from typing import Dict, List, Any

from autism.configs import DSM5_EVALUATION_METRICS


def evaluate_dsm5_dialogue(
    dialogue: str, 
    autism_profile: Dict[str, Any], 
    scene_info: Dict[str, Any]
) -> Dict[str, float]:
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
    proactive_social = len([line for line in autism_child_lines 
                           if any(word in line for word in ['我想', '我们一起', '可以吗', '你好'])])
    if proactive_social > 0:
        interaction_indicators += 1
    
    # 检查社交反应
    responsive_social = len([line for line in autism_child_lines 
                           if any(word in line for word in ['好的', '是的', '不要', '谢谢'])])
    if responsive_social > len(autism_child_lines) * 0.3:
        interaction_indicators += 1
    
    social_score = base_severity - (interaction_indicators * 0.5)
    evaluation_scores["社交互动质量"] = max(1, min(5, social_score))
    
    # 沟通交流能力评估
    communication_quality = 0
    
    # 检查语言功能性
    functional_language = len([line for line in autism_child_lines 
                             if any(word in line for word in ['我要', '帮助', '不懂', '为什么'])])
    if functional_language > 0:
        communication_quality += 1
    
    # 检查回声式语言（重复他人话语）
    echolalia_signs = len([line for line in autism_child_lines 
                          if '?' in line and len(line.split()) < 5])
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
    stereotyped_actions = len([line for line in autism_child_lines 
                              if '（' in line and any(word in line for word in ['拍手', '摇', '转', '跳'])])
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


def extract_dsm5_observations(dialogue: str) -> Dict[str, List[str]]:
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