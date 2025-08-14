"""
CARS (Childhood Autism Rating Scale) 儿童孤独症评定量表评估器
基于 Schopler et al. (1980, 1988, 2010) 的标准版本
"""
import numpy as np
from typing import Dict, List, Tuple, Any

# CARS量表15个评估项目（基于CARS-2标准版本）
CARS_EVALUATION_ITEMS = {
    "人际关系": {
        "id": "I",
        "description": "与人的情感接触和社交互动",
        "behaviors": [
            "目光接触异常或回避",
            "对他人缺乏兴趣",
            "难以建立同伴关系",
            "社交互动被动或异常"
        ],
        "scoring_guide": {
            1: "与年龄相当：儿童的行为与同龄儿童相符",
            1.5: "介于1和2之间",
            2: "轻度异常：儿童有些回避目光接触，或在成人主动时才有反应",
            2.5: "介于2和3之间",
            3: "中度异常：儿童对成人有时会有所察觉，但接触很少",
            3.5: "介于3和4之间",
            4: "严重异常：儿童极少察觉或反应他人的存在"
        }
    },
    "模仿": {
        "id": "II",
        "description": "模仿语言、动作和行为的能力",
        "behaviors": [
            "不能模仿声音或动作",
            "只能部分模仿",
            "延迟模仿",
            "机械性模仿"
        ],
        "scoring_guide": {
            1: "适当的模仿：能够模仿与年龄相符的声音、词语和动作",
            2: "轻度异常：大部分时间能模仿简单行为",
            3: "中度异常：只能偶尔模仿，需要大量帮助和反复示范",
            4: "严重异常：很少或从不模仿声音、词语或动作"
        }
    },
    "情感反应": {
        "id": "III",
        "description": "情感表达的适当性和强度",
        "behaviors": [
            "情感反应不当",
            "情感平淡或过度",
            "无明显原因的情绪变化",
            "对情境的情感反应异常"
        ],
        "scoring_guide": {
            1: "年龄相当的情感反应",
            2: "轻度异常：偶尔表现出不适当的情感反应",
            3: "中度异常：情感反应明显受限或过度",
            4: "严重异常：极少有适当的情感反应"
        }
    },
    "身体运用": {
        "id": "IV",
        "description": "身体协调性和运动能力",
        "behaviors": [
            "笨拙的步态",
            "异常的身体姿势",
            "精细动作困难",
            "重复性身体动作"
        ],
        "scoring_guide": {
            1: "年龄相当：运动能力正常",
            2: "轻度异常：有些轻微的笨拙",
            3: "中度异常：明显的运动协调问题",
            4: "严重异常：严重的运动异常或大量刻板动作"
        }
    },
    "物体运用": {
        "id": "V",
        "description": "对玩具和其他物体的使用",
        "behaviors": [
            "不当使用玩具",
            "对物体部分的过度关注",
            "重复性地操作物体",
            "对物体的异常兴趣"
        ],
        "scoring_guide": {
            1: "适当的兴趣和使用",
            2: "轻度异常：对玩具有些异常兴趣",
            3: "中度异常：对物体的使用明显异常",
            4: "严重异常：严重不当使用物体"
        }
    },
    "环境适应": {
        "id": "VI",
        "description": "对变化的适应能力",
        "behaviors": [
            "抗拒环境变化",
            "对常规的过度依赖",
            "对新环境的异常反应",
            "转换困难"
        ],
        "scoring_guide": {
            1: "年龄相当的反应",
            2: "轻度异常：对变化有些抗拒",
            3: "中度异常：对变化反应强烈",
            4: "严重异常：对变化极度抗拒"
        }
    },
    "视觉反应": {
        "id": "VII",
        "description": "视觉注意和目光使用",
        "behaviors": [
            "避免目光接触",
            "凝视空间",
            "异常的视觉探索",
            "对光线的异常反应"
        ],
        "scoring_guide": {
            1: "年龄相当的视觉反应",
            2: "轻度异常：偶尔需要提醒进行目光接触",
            3: "中度异常：经常避免目光接触",
            4: "严重异常：持续避免目光接触"
        }
    },
    "听觉反应": {
        "id": "VIII",
        "description": "对声音的反应",
        "behaviors": [
            "对声音过度敏感或迟钝",
            "对特定声音的异常反应",
            "忽视语言指令",
            "对声音的选择性注意"
        ],
        "scoring_guide": {
            1: "年龄相当的听觉反应",
            2: "轻度异常：对某些声音有轻微异常反应",
            3: "中度异常：对声音的反应明显异常",
            4: "严重异常：对声音极度敏感或无反应"
        }
    },
    "味觉嗅觉触觉反应": {
        "id": "IX",
        "description": "对感觉刺激的反应",
        "behaviors": [
            "异常的感觉寻求",
            "对触摸的过度反应",
            "对疼痛的反应异常",
            "异常的口腔探索"
        ],
        "scoring_guide": {
            1: "正常的感觉使用和反应",
            2: "轻度异常：轻微的感觉异常",
            3: "中度异常：中度的感觉反应异常",
            4: "严重异常：严重的感觉异常"
        }
    },
    "焦虑反应": {
        "id": "X",
        "description": "恐惧和焦虑的表现",
        "behaviors": [
            "不合理的恐惧",
            "缺乏适当的恐惧",
            "过度的焦虑反应",
            "对常规事物的恐惧"
        ],
        "scoring_guide": {
            1: "正常的恐惧或焦虑",
            2: "轻度异常：偶尔表现异常的恐惧",
            3: "中度异常：明显的恐惧或焦虑问题",
            4: "严重异常：严重的恐惧反应异常"
        }
    },
    "语言交流": {
        "id": "XI",
        "description": "语言能力和使用",
        "behaviors": [
            "语言发展延迟",
            "鹦鹉学舌",
            "代词混用",
            "异常的语音语调"
        ],
        "scoring_guide": {
            1: "正常的语言交流",
            2: "轻度异常：语言发展轻微延迟",
            3: "中度异常：明显的语言问题",
            4: "严重异常：无意义语言或无语言"
        }
    },
    "非语言交流": {
        "id": "XII",
        "description": "手势和身体语言的使用",
        "behaviors": [
            "缺乏手势",
            "不理解非语言暗示",
            "异常的面部表情",
            "身体语言使用异常"
        ],
        "scoring_guide": {
            1: "正常的非语言交流",
            2: "轻度异常：非语言交流轻微不成熟",
            3: "中度异常：很少使用或理解非语言交流",
            4: "严重异常：无非语言交流"
        }
    },
    "活动水平": {
        "id": "XIII",
        "description": "活动量和能量水平",
        "behaviors": [
            "过度活跃",
            "活动不足",
            "难以静坐",
            "精力分配异常"
        ],
        "scoring_guide": {
            1: "正常的活动水平",
            2: "轻度异常：轻微的活动过度或不足",
            3: "中度异常：明显的活动水平问题",
            4: "严重异常：极端的活动过度或不足"
        }
    },
    "智力功能": {
        "id": "XIV",
        "description": "认知能力和智力表现",
        "behaviors": [
            "技能发展不均衡",
            "特殊才能与缺陷并存",
            "认知功能异常",
            "学习能力受限"
        ],
        "scoring_guide": {
            1: "智力功能正常且均衡",
            2: "轻度异常：轻微的不均衡",
            3: "中度异常：明显的智力功能问题",
            4: "严重异常：严重的智力功能异常"
        }
    },
    "总体印象": {
        "id": "XV",
        "description": "总体孤独症表现",
        "behaviors": [
            "综合所有观察",
            "整体严重程度",
            "症状的广泛性",
            "对日常功能的影响"
        ],
        "scoring_guide": {
            1: "无孤独症表现",
            2: "轻度孤独症表现",
            3: "中度孤独症表现",
            4: "严重孤独症表现"
        }
    }
}


def evaluate_cars_behaviors(
    dialogue: str,
    autism_profile: Dict[str, Any],
    scene_info: Dict[str, Any]
) -> Tuple[Dict[str, float], Dict[str, List[str]], float]:
    """
    基于CARS量表评估行为表现
    
    Args:
        dialogue: 观察对话内容
        autism_profile: 孤独症儿童特征配置
        scene_info: 场景信息
    
    Returns:
        (各项得分字典, 识别的行为字典, 总分)
    """
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    all_lines = lines
    
    # 初始化得分
    item_scores = {}
    identified_behaviors = {}
    
    # 根据功能水平设置基础严重度
    functioning_level = autism_profile.get('overall_functioning', 'need_support')
    base_severity = {
        'mainstream_with_support': 1.5,
        'need_support': 2.0,
        'need_substantial_support': 2.5,
        'need_very_substantial_support': 3.0,
        'variable_support_needs': 2.0
    }.get(functioning_level, 2.0)
    
    # 评估人际关系
    score, behaviors = evaluate_social_relating(autism_child_lines, all_lines, base_severity)
    item_scores["人际关系"] = score
    identified_behaviors["人际关系"] = behaviors
    
    # 评估模仿能力
    score, behaviors = evaluate_imitation(autism_child_lines, all_lines, base_severity)
    item_scores["模仿"] = score
    identified_behaviors["模仿"] = behaviors
    
    # 评估情感反应
    score, behaviors = evaluate_emotional_response(autism_child_lines, all_lines, base_severity)
    item_scores["情感反应"] = score
    identified_behaviors["情感反应"] = behaviors
    
    # 评估身体运用
    score, behaviors = evaluate_body_use(autism_child_lines, base_severity)
    item_scores["身体运用"] = score
    identified_behaviors["身体运用"] = behaviors
    
    # 评估物体运用
    score, behaviors = evaluate_object_use(autism_child_lines, base_severity)
    item_scores["物体运用"] = score
    identified_behaviors["物体运用"] = behaviors
    
    # 评估环境适应
    score, behaviors = evaluate_adaptation(autism_child_lines, scene_info, base_severity)
    item_scores["环境适应"] = score
    identified_behaviors["环境适应"] = behaviors
    
    # 评估视觉反应
    score, behaviors = evaluate_visual_response(autism_child_lines, base_severity)
    item_scores["视觉反应"] = score
    identified_behaviors["视觉反应"] = behaviors
    
    # 评估听觉反应
    score, behaviors = evaluate_listening_response(autism_child_lines, all_lines, base_severity)
    item_scores["听觉反应"] = score
    identified_behaviors["听觉反应"] = behaviors
    
    # 评估感觉反应
    score, behaviors = evaluate_sensory_response(autism_child_lines, base_severity)
    item_scores["味觉嗅觉触觉反应"] = score
    identified_behaviors["味觉嗅觉触觉反应"] = behaviors
    
    # 评估焦虑反应
    score, behaviors = evaluate_fear_nervousness(autism_child_lines, all_lines, base_severity)
    item_scores["焦虑反应"] = score
    identified_behaviors["焦虑反应"] = behaviors
    
    # 评估语言交流
    score, behaviors = evaluate_verbal_communication(autism_child_lines, base_severity)
    item_scores["语言交流"] = score
    identified_behaviors["语言交流"] = behaviors
    
    # 评估非语言交流
    score, behaviors = evaluate_nonverbal_communication(autism_child_lines, base_severity)
    item_scores["非语言交流"] = score
    identified_behaviors["非语言交流"] = behaviors
    
    # 评估活动水平
    score, behaviors = evaluate_activity_level(autism_child_lines, base_severity)
    item_scores["活动水平"] = score
    identified_behaviors["活动水平"] = behaviors
    
    # 评估智力功能
    score, behaviors = evaluate_intellectual_response(autism_child_lines, autism_profile, base_severity)
    item_scores["智力功能"] = score
    identified_behaviors["智力功能"] = behaviors
    
    # 总体印象（基于其他所有项目的平均）
    avg_score = np.mean(list(item_scores.values()))
    item_scores["总体印象"] = round(avg_score, 1)
    identified_behaviors["总体印象"] = ["基于所有观察的综合评估"]
    
    # 计算总分
    total_score = sum(item_scores.values())
    
    return item_scores, identified_behaviors, total_score


def evaluate_social_relating(child_lines, all_lines, base_severity):
    """评估人际关系"""
    behaviors = []
    score = base_severity
    
    # 检查目光接触
    if any('看着' in line or '目光' in line for line in child_lines):
        score -= 0.5
    elif any('看向别处' in line or '避开' in line for line in child_lines):
        behaviors.append("避免目光接触")
        score += 0.5
    
    # 检查社交主动性
    social_initiation = len([line for line in child_lines if any(word in line for word in ['你好', '一起', '玩'])])
    if social_initiation > 1:
        score -= 0.5
    elif social_initiation == 0:
        behaviors.append("缺乏社交主动性")
        score += 0.5
    
    # 检查对他人的反应
    if len(child_lines) < len(all_lines) * 0.2:
        behaviors.append("对他人反应少")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_imitation(child_lines, all_lines, base_severity):
    """评估模仿能力"""
    behaviors = []
    score = base_severity
    
    # 检查是否有模仿行为
    imitation_words = ['也', '一样', '跟着', '学']
    if any(word in ''.join(child_lines) for word in imitation_words):
        score -= 0.5
    else:
        behaviors.append("缺乏模仿行为")
        score += 0.5
    
    # 检查鹦鹉学舌
    for i, line in enumerate(all_lines[:-1]):
        if '孤独症儿童' not in line and i < len(all_lines) - 1:
            next_line = all_lines[i + 1]
            if '孤独症儿童' in next_line:
                prev_content = line.split(':')[-1] if ':' in line else line
                child_content = next_line.split(':')[-1] if ':' in next_line else next_line
                if len(prev_content) > 3 and prev_content.strip() in child_content:
                    behaviors.append("鹦鹉学舌")
                    score += 0.5
                    break
    
    return min(4, max(1, score)), behaviors


def evaluate_emotional_response(child_lines, all_lines, base_severity):
    """评估情感反应"""
    behaviors = []
    score = base_severity
    
    # 检查情感词汇
    emotion_words = ['高兴', '开心', '难过', '生气', '害怕', '喜欢', '不喜欢']
    emotion_count = sum(1 for line in child_lines if any(word in line for word in emotion_words))
    
    if emotion_count > 2:
        score -= 0.5
    elif emotion_count == 0:
        behaviors.append("情感表达缺乏")
        score += 0.5
    
    # 检查笑或哭的描述
    if any('笑' in line or '哭' in line for line in child_lines):
        if '突然' in ''.join(child_lines) or '莫名' in ''.join(child_lines):
            behaviors.append("情绪变化无明显原因")
            score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_body_use(child_lines, base_severity):
    """评估身体运用"""
    behaviors = []
    score = base_severity
    
    # 检查重复性动作
    repetitive_actions = ['拍手', '摇晃', '转圈', '踮脚', '扭动']
    for action in repetitive_actions:
        if any(action in line for line in child_lines):
            behaviors.append(f"重复性{action}")
            score += 0.5
            break
    
    # 检查运动描述
    if any('笨拙' in line or '摔' in line or '撞' in line for line in child_lines):
        behaviors.append("运动协调问题")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_object_use(child_lines, base_severity):
    """评估物体运用"""
    behaviors = []
    score = base_severity
    
    # 检查异常的物体使用
    unusual_use = ['排列', '旋转', '反复', '固定']
    for pattern in unusual_use:
        if any(pattern in line for line in child_lines):
            behaviors.append(f"{pattern}物体")
            score += 0.5
            break
    
    # 检查对物体部分的关注
    if any('轮子' in line or '部分' in line or '细节' in line for line in child_lines):
        behaviors.append("过度关注物体部分")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_adaptation(child_lines, scene_info, base_severity):
    """评估环境适应"""
    behaviors = []
    score = base_severity
    
    # 检查对变化的反应
    change_reactions = ['不要', '还是', '一定要', '必须', '不行']
    resistance_count = sum(1 for line in child_lines if any(word in line for word in change_reactions))
    
    if resistance_count > 2:
        behaviors.append("抗拒变化")
        score += 0.5
    
    # 检查对常规的坚持
    if any('一样' in line or '总是' in line or '每次' in line for line in child_lines):
        behaviors.append("坚持常规")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_visual_response(child_lines, base_severity):
    """评估视觉反应"""
    behaviors = []
    score = base_severity
    
    # 检查视觉相关描述
    if any('盯着' in line or '凝视' in line for line in child_lines):
        behaviors.append("异常凝视")
        score += 0.5
    
    if any('斜眼' in line or '余光' in line for line in child_lines):
        behaviors.append("异常的视觉角度")
        score += 0.5
    
    if any('不看' in line or '避开眼神' in line for line in child_lines):
        behaviors.append("避免目光接触")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_listening_response(child_lines, all_lines, base_severity):
    """评估听觉反应"""
    behaviors = []
    score = base_severity
    
    # 检查对声音的反应
    if any('捂耳' in line or '耳朵' in line for line in child_lines):
        behaviors.append("对声音过度敏感")
        score += 0.5
    
    # 检查是否忽视呼唤
    if '没有反应' in ''.join(all_lines) or '不理' in ''.join(all_lines):
        behaviors.append("忽视语言指令")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_sensory_response(child_lines, base_severity):
    """评估感觉反应"""
    behaviors = []
    score = base_severity
    
    # 检查感觉寻求行为
    sensory_seeking = ['闻', '舔', '摸', '咬']
    for behavior in sensory_seeking:
        if any(behavior in line for line in child_lines):
            behaviors.append(f"异常的{behavior}行为")
            score += 0.5
            break
    
    # 检查对触摸的反应
    if any('不让碰' in line or '推开' in line for line in child_lines):
        behaviors.append("触觉防御")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_fear_nervousness(child_lines,  all_lines, base_severity):
    """评估焦虑反应"""
    behaviors = []
    score = base_severity
    
    # 检查恐惧相关表现
    fear_words = ['怕', '害怕', '恐惧', '紧张', '焦虑']
    fear_count = sum(1 for line in child_lines if any(word in line for word in fear_words))
    
    if fear_count > 2:
        behaviors.append("过度焦虑")
        score += 0.5
    elif fear_count == 0 and len(child_lines) > 5:
        # 在应该有恐惧的情况下没有恐惧
        if any('危险' in line or '小心' in line for line in all_lines):
            behaviors.append("缺乏适当的恐惧")
            score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_verbal_communication(child_lines, base_severity):
    """评估语言交流"""
    behaviors = []
    score = base_severity
    
    # 统计语言使用
    verbal_lines = [line for line in child_lines if not line.strip().startswith('（') and len(line.strip()) > 2]
    
    if len(verbal_lines) == 0:
        behaviors.append("无语言")
        score = 4
    elif len(verbal_lines) < 3:
        behaviors.append("语言极少")
        score += 1
    
    # 检查语言质量
    if verbal_lines:
        # 检查鹦鹉学舌
        if any(line.count('？') > 1 or '...' in line for line in verbal_lines):
            behaviors.append("语言重复或刻板")
            score += 0.5
        
        # 检查代词使用
        if any('我' not in line and '你' in line for line in verbal_lines):
            behaviors.append("代词混用")
            score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_nonverbal_communication(child_lines, base_severity):
    """评估非语言交流"""
    behaviors = []
    score = base_severity
    
    # 检查手势使用（通过括号中的描述）
    gesture_lines = [line for line in child_lines if '（' in line and '）' in line]
    
    if len(gesture_lines) == 0:
        behaviors.append("缺乏手势")
        score += 0.5
    elif any('指' in line or '挥手' in line for line in gesture_lines):
        score -= 0.5
    
    # 检查面部表情
    if any('面无表情' in line or '表情' in line for line in child_lines):
        behaviors.append("面部表情异常")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_activity_level(child_lines, base_severity):
    """评估活动水平"""
    behaviors = []
    score = base_severity
    
    # 检查活动描述
    hyperactive = ['跑来跑去', '不停', '一直', '转圈']
    hypoactive = ['不动', '呆坐', '静止']
    
    if any(word in ''.join(child_lines) for word in hyperactive):
        behaviors.append("过度活跃")
        score += 0.5
    elif any(word in ''.join(child_lines) for word in hypoactive):
        behaviors.append("活动不足")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def evaluate_intellectual_response(child_lines, autism_profile, base_severity):
    """评估智力功能"""
    behaviors = []
    score = base_severity
    
    # 基于配置文件的认知特征
    cognitive = autism_profile.get('cognitive_characteristics', '')
    
    if '发展不均' in cognitive or '特殊才能' in cognitive:
        behaviors.append("技能发展不均衡")
        score += 0.5
    
    # 检查问题解决
    if any('不懂' in line or '不会' in line or '不明白' in line for line in child_lines):
        behaviors.append("理解困难")
        score += 0.5
    
    return min(4, max(1, score)), behaviors


def get_cars_severity_level(total_score: float) -> str:
    """
    根据CARS总分判断严重程度
    
    Args:
        total_score: CARS总分（15-60）
    
    Returns:
        严重程度描述
    """
    if total_score < 30:
        return "非孤独症范围"
    elif total_score <= 36.5:
        return "轻到中度孤独症"
    else:
        return "重度孤独症"


def get_cars_interpretation(total_score: float) -> Dict[str, Any]:
    """
    获取CARS评分的详细解释
    
    Args:
        total_score: CARS总分
    
    Returns:
        包含解释和建议的字典
    """
    interpretation = {
        'score': total_score,
        'severity': get_cars_severity_level(total_score),
        'percentile': None,
        'clinical_significance': '',
        'recommendations': []
    }
    
    if total_score < 30:
        interpretation['clinical_significance'] = "评分低于孤独症诊断阈值，但仍需关注个别领域的发展"
        interpretation['recommendations'] = [
            "继续监测发展情况",
            "针对薄弱领域提供支持",
            "定期复评"
        ]
    elif total_score <= 36.5:
        interpretation['clinical_significance'] = "符合轻到中度孤独症表现，需要系统性干预"
        interpretation['recommendations'] = [
            "寻求专业的孤独症干预服务",
            "制定个体化教育计划(IEP)",
            "考虑言语治疗和职能治疗",
            "家长培训和支持"
        ]
    else:
        interpretation['clinical_significance'] = "符合重度孤独症表现，需要密集和全面的支持"
        interpretation['recommendations'] = [
            "立即寻求综合性孤独症干预项目",
            "考虑密集行为干预(如ABA)",
            "多学科团队评估和支持",
            "家庭支持和喘息服务",
            "特殊教育安置"
        ]
    
    return interpretation