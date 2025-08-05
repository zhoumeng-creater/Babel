"""评估辅助函数模块"""
import datetime
import numpy as np
from typing import List, Dict, Any


def generate_unique_id(prefix: str, template_name: str, scene_name: str, counter: int) -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        template_name: 模板名称
        scene_name: 场景名称
        counter: 计数器
    
    Returns:
        str: 唯一ID
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    return f"{prefix}_{counter:03d}_{template_name[:4]}_{scene_name[:4]}_{timestamp}"


def add_random_variation(profile: Dict[str, Any], keys: List[str], min_val: int = 1, max_val: int = 5) -> Dict[str, Any]:
    """
    为配置文件添加随机变异
    
    Args:
        profile: 原始配置字典
        keys: 要变异的键列表
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        dict: 变异后的配置
    """
    varied_profile = profile.copy()
    for key in keys:
        if key in varied_profile:
            variation = np.random.randint(-1, 2)
            varied_profile[key] = max(min_val, min(max_val, varied_profile[key] + variation))
    return varied_profile


# ABC评估相关的辅助函数
def check_echolalia(child_lines: List[str], all_lines: List[str]) -> bool:
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


def check_self_talk(child_lines: List[str]) -> bool:
    """检查是否有自言自语"""
    for line in child_lines:
        if not any(word in line for word in ["你", "老师", "同学", "妈妈", "爸爸"]):
            if len(line.split(":")[-1]) > 10:  # 较长的独白
                return True
    return False


def check_irrelevant_responses(child_lines: List[str], all_lines: List[str]) -> bool:
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


def check_pronoun_confusion(child_lines: List[str]) -> bool:
    """检查代词混用"""
    for line in child_lines:
        # 如果用"你"指代自己
        if "你要" in line or "你想" in line:
            context = line.split(":")[-1] if ":" in line else line
            if "我" not in context:  # 可能是代词混用
                return True
    return False


def check_stereotyped_language(child_lines: List[str]) -> bool:
    """检查语言刻板重复"""
    if len(child_lines) < 3:
        return False
    
    # 检查是否有重复的句式
    phrases = [line.split(":")[-1] if ":" in line else line for line in child_lines]
    for i in range(len(phrases) - 2):
        if phrases[i] == phrases[i+2]:  # 隔句重复
            return True
    
    return False


# 数据处理辅助函数
def normalize_scores(scores: Dict[str, float], max_scores: Dict[str, float]) -> Dict[str, float]:
    """
    归一化评分
    
    Args:
        scores: 原始评分字典
        max_scores: 各项最高分字典
    
    Returns:
        dict: 归一化后的评分（0-1范围）
    """
    normalized = {}
    for key, score in scores.items():
        if key in max_scores and max_scores[key] > 0:
            normalized[key] = score / max_scores[key]
        else:
            normalized[key] = score
    return normalized


def calculate_weighted_average(scores: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """
    计算加权平均分
    
    Args:
        scores: 评分字典
        weights: 权重字典，如果为None则使用等权重
    
    Returns:
        float: 加权平均分
    """
    if not scores:
        return 0.0
    
    if weights is None:
        return sum(scores.values()) / len(scores)
    
    total_weight = 0
    weighted_sum = 0
    
    for key, score in scores.items():
        weight = weights.get(key, 1.0)
        weighted_sum += score * weight
        total_weight += weight
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def format_experiment_id(prefix: str, counter: int, template: str, scene: str) -> str:
    """
    格式化实验ID
    
    Args:
        prefix: 前缀（如 UNI, ABC, DSM5）
        counter: 实验计数器
        template: 模板名称
        scene: 场景名称
    
    Returns:
        str: 格式化的实验ID
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    template_short = template[:4] if len(template) > 4 else template
    scene_short = scene[:4] if len(scene) > 4 else scene
    
    return f"{prefix}_{counter:03d}_{template_short}_{scene_short}_{timestamp}"


def extract_dialogue_statistics(dialogue: str) -> Dict[str, Any]:
    """
    提取对话统计信息
    
    Args:
        dialogue: 对话文本
    
    Returns:
        dict: 包含各种统计信息的字典
    """
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    other_lines = [line for line in lines if '孤独症儿童' not in line and ':' in line]
    
    # 提取基本统计
    stats = {
        'total_lines': len(lines),
        'child_lines': len(autism_child_lines),
        'other_lines': len(other_lines),
        'child_ratio': len(autism_child_lines) / len(lines) if lines else 0,
        
        # 计算平均句长
        'avg_child_sentence_length': np.mean([len(line.split()) for line in autism_child_lines]) if autism_child_lines else 0,
        
        # 计算独白比例（连续的儿童发言）
        'monologue_ratio': calculate_monologue_ratio(lines),
        
        # 计算回应率
        'response_rate': calculate_response_rate(lines)
    }
    
    return stats


def calculate_monologue_ratio(lines: List[str]) -> float:
    """计算独白比例（连续的儿童发言占比）"""
    if not lines:
        return 0.0
    
    consecutive_child = 0
    current_streak = 0
    
    for line in lines:
        if '孤独症儿童' in line:
            current_streak += 1
            consecutive_child = max(consecutive_child, current_streak)
        else:
            current_streak = 0
    
    return consecutive_child / len(lines) if lines else 0.0


def calculate_response_rate(lines: List[str]) -> float:
    """计算回应率（对他人发言的回应比例）"""
    if len(lines) < 2:
        return 0.0
    
    responses = 0
    opportunities = 0
    
    for i in range(len(lines) - 1):
        if '孤独症儿童' not in lines[i] and ':' in lines[i]:  # 他人发言
            opportunities += 1
            if '孤独症儿童' in lines[i + 1]:  # 儿童回应
                responses += 1
    
    return responses / opportunities if opportunities > 0 else 0.0