"""ABC量表评估逻辑模块"""
import numpy as np
from typing import Dict, List, Tuple, Any

from autism.configs import ABC_BEHAVIOR_ITEMS, ABC_EVALUATION_METRICS


def evaluate_abc_behaviors(
    dialogue: str, 
    autism_profile: Dict[str, Any], 
    scene_info: Dict[str, Any]
) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
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


def get_abc_severity_level(total_score: float) -> str:
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


def get_max_score_for_domain(domain: str) -> int:
    """获取各领域的最高分"""
    max_scores = {
        "感觉领域得分": 22,
        "交往领域得分": 41,
        "躯体运动领域得分": 28,
        "语言领域得分": 42,
        "社交与自理领域得分": 25
    }
    return max_scores.get(domain, 0)


def evaluate_sensory_behaviors(
    child_lines: List[str], 
    all_lines: List[str], 
    probability: float, 
    identified_list: List[str]
) -> float:
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


def evaluate_social_behaviors(
    child_lines: List[str], 
    all_lines: List[str], 
    probability: float, 
    identified_list: List[str]
) -> float:
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


def evaluate_motor_behaviors(
    child_lines: List[str], 
    all_lines: List[str], 
    probability: float, 
    identified_list: List[str]
) -> float:
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


def evaluate_language_behaviors(
    child_lines: List[str], 
    all_lines: List[str], 
    probability: float, 
    identified_list: List[str]
) -> float:
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
    from .evaluation_helpers import (
        check_echolalia, check_self_talk, check_irrelevant_responses,
        check_pronoun_confusion, check_stereotyped_language
    )
    
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


def evaluate_selfcare_behaviors(
    child_lines: List[str], 
    all_lines: List[str], 
    probability: float, 
    identified_list: List[str], 
    scene_info: Dict[str, Any]
) -> float:
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