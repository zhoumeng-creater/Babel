"""
ASSQ (Autism Spectrum Screening Questionnaire) 孤独症谱系筛查问卷评估器
基于 Ehlers, Gillberg & Wing (1999) 的标准版本
"""
import numpy as np
from typing import Dict, List, Tuple, Any
import datetime

# ASSQ量表27个评估项目
ASSQ_SCREENING_ITEMS = {
    "社交互动": [
        {
            "id": 1,
            "item": "看起来老成或早熟",
            "description": "言谈举止超出年龄，过于正式或成熟",
            "keywords": ["老成", "成熟", "正式", "古板"]
        },
        {
            "id": 2,
            "item": "被同龄人视为'古怪教授'",
            "description": "因知识渊博但社交笨拙而被认为古怪",
            "keywords": ["古怪", "书呆子", "教授", "与众不同"]
        },
        {
            "id": 3,
            "item": "生活在自己的世界里",
            "description": "沉浸在自己的思想和兴趣中，与外界脱节",
            "keywords": ["自己的世界", "沉浸", "脱节", "封闭"]
        },
        {
            "id": 4,
            "item": "社交时缺乏理解",
            "description": "不理解社交暗示和潜规则",
            "keywords": ["不理解", "社交困难", "误解", "不懂暗示"]
        },
        {
            "id": 5,
            "item": "缺乏最好的朋友",
            "description": "没有亲密的友谊关系",
            "keywords": ["没有朋友", "孤独", "独处", "缺乏友谊"]
        },
        {
            "id": 6,
            "item": "缺乏常识",
            "description": "在日常生活判断上显得幼稚或不切实际",
            "keywords": ["缺乏常识", "判断差", "不切实际", "幼稚"]
        },
        {
            "id": 7,
            "item": "与同龄人合作游戏困难",
            "description": "难以参与需要合作的集体活动",
            "keywords": ["不合作", "游戏困难", "集体活动差", "独自玩"]
        }
    ],
    "沟通问题": [
        {
            "id": 8,
            "item": "特殊的声音使用",
            "description": "音调、音量或节奏异常",
            "keywords": ["音调异常", "声音特殊", "单调", "音量不当"]
        },
        {
            "id": 9,
            "item": "特殊的语言使用",
            "description": "过于正式、学究或重复的语言",
            "keywords": ["语言正式", "学究", "重复语言", "刻板用语"]
        },
        {
            "id": 10,
            "item": "谈话内容有限",
            "description": "只谈论特定主题，缺乏话题多样性",
            "keywords": ["话题单一", "重复话题", "兴趣狭窄", "固定话题"]
        },
        {
            "id": 11,
            "item": "语言理解问题",
            "description": "字面理解，不懂比喻或双关",
            "keywords": ["字面理解", "不懂比喻", "理解困难", "误解含义"]
        },
        {
            "id": 12,
            "item": "隐喻性语言理解困难",
            "description": "不理解暗示、讽刺或幽默",
            "keywords": ["不懂暗示", "不懂幽默", "不懂讽刺", "理解字面"]
        },
        {
            "id": 13,
            "item": "异常的面部表情",
            "description": "表情与情境不符或缺乏表情",
            "keywords": ["表情异常", "面无表情", "表情不当", "表情僵硬"]
        },
        {
            "id": 14,
            "item": "异常的身体姿势",
            "description": "姿势僵硬、不自然或异常",
            "keywords": ["姿势异常", "僵硬", "不自然", "身体语言差"]
        }
    ],
    "限制性兴趣": [
        {
            "id": 15,
            "item": "特殊兴趣模式",
            "description": "对特定主题有强烈而狭窄的兴趣",
            "keywords": ["特殊兴趣", "狭窄兴趣", "执着", "单一兴趣"]
        },
        {
            "id": 16,
            "item": "重复性行为",
            "description": "刻板或仪式化的行为模式",
            "keywords": ["重复", "刻板", "仪式", "固定模式"]
        },
        {
            "id": 17,
            "item": "常规和仪式",
            "description": "坚持特定的日常程序或仪式",
            "keywords": ["坚持常规", "仪式行为", "固定程序", "抗拒改变"]
        }
    ],
    "运动协调": [
        {
            "id": 18,
            "item": "动作笨拙",
            "description": "运动协调性差，动作不灵活",
            "keywords": ["笨拙", "协调差", "运动困难", "不灵活"]
        },
        {
            "id": 19,
            "item": "异常的步态",
            "description": "走路姿势异常或不协调",
            "keywords": ["步态异常", "走路怪异", "姿势不当", "踮脚走"]
        }
    ],
    "其他特征": [
        {
            "id": 20,
            "item": "特殊面部表情或抽搐",
            "description": "不自主的面部动作或表情",
            "keywords": ["抽搐", "怪表情", "不自主动作", "面部动作"]
        },
        {
            "id": 21,
            "item": "特殊的依恋",
            "description": "对特定物品或人的异常依恋",
            "keywords": ["依恋物品", "执着", "不寻常依恋", "固定依恋"]
        },
        {
            "id": 22,
            "item": "被其他孩子欺负",
            "description": "容易成为欺凌的目标",
            "keywords": ["被欺负", "受害者", "被排斥", "被嘲笑"]
        },
        {
            "id": 23,
            "item": "特殊的眼神接触",
            "description": "避免或异常的目光接触",
            "keywords": ["避免眼神", "目光异常", "不看人", "凝视"]
        },
        {
            "id": 24,
            "item": "不喜欢身体接触",
            "description": "回避或对触摸过度敏感",
            "keywords": ["回避接触", "触觉敏感", "不喜欢碰触", "推开"]
        },
        {
            "id": 25,
            "item": "言语重复",
            "description": "重复自己或他人的话语",
            "keywords": ["重复", "鹦鹉学舌", "回声语言", "反复说"]
        },
        {
            "id": 26,
            "item": "奇特的恐惧",
            "description": "对普通事物的不寻常恐惧",
            "keywords": ["异常恐惧", "特殊害怕", "不合理恐惧", "过度恐惧"]
        },
        {
            "id": 27,
            "item": "缺乏想象力游戏",
            "description": "游戏缺乏创造性和想象力",
            "keywords": ["缺乏想象", "游戏单调", "不会假装", "机械游戏"]
        }
    ]
}


def evaluate_assq_behaviors(
    dialogue: str,
    autism_profile: Dict[str, Any],
    scene_info: Dict[str, Any]
) -> Tuple[Dict[str, int], List[str], int]:
    """
    基于ASSQ筛查问卷评估行为表现
    
    Args:
        dialogue: 观察对话内容
        autism_profile: 孤独症儿童特征配置
        scene_info: 场景信息
    
    Returns:
        (各项得分字典, 识别的特征列表, 总分)
    """
    lines = dialogue.split('\n')
    autism_child_lines = [line for line in lines if '孤独症儿童' in line]
    all_lines = lines
    
    # 初始化
    item_scores = {}
    identified_traits = []
    
    # 根据功能水平设置基础概率
    functioning_level = autism_profile.get('overall_functioning', 'need_support')
    trait_probability = {
        'mainstream_with_support': 0.3,
        'need_support': 0.5,
        'need_substantial_support': 0.7,
        'need_very_substantial_support': 0.85,
        'variable_support_needs': 0.6
    }.get(functioning_level, 0.5)
    
    # 遍历所有ASSQ项目进行评分
    for category, items in ASSQ_SCREENING_ITEMS.items():
        for item_data in items:
            score = evaluate_single_assq_item(
                item_data,
                autism_child_lines,
                all_lines,
                autism_profile,
                trait_probability
            )
            
            item_key = f"项目{item_data['id']}"
            item_scores[item_key] = score
            
            if score > 0:
                identified_traits.append(f"{item_data['item']} (得分:{score})")
    
    # 计算总分
    total_score = sum(item_scores.values())
    
    # 添加分类得分汇总
    category_scores = {
        "社交互动": sum(item_scores[f"项目{i}"] for i in range(1, 8)),
        "沟通问题": sum(item_scores[f"项目{i}"] for i in range(8, 15)),
        "限制性兴趣": sum(item_scores[f"项目{i}"] for i in range(15, 18)),
        "运动协调": sum(item_scores[f"项目{i}"] for i in range(18, 20)),
        "其他特征": sum(item_scores[f"项目{i}"] for i in range(20, 28))
    }
    
    return item_scores, identified_traits, total_score, category_scores


def evaluate_single_assq_item(
    item_data: Dict,
    child_lines: List[str],
    all_lines: List[str],
    autism_profile: Dict[str, Any],
    base_probability: float
) -> int:
    """
    评估单个ASSQ项目
    
    Returns:
        0: 不符合
        1: 有点符合
        2: 完全符合
    """
    score = 0
    dialogue_text = ' '.join(child_lines).lower()
    all_text = ' '.join(all_lines).lower()
    
    # 检查关键词
    keyword_matches = sum(1 for keyword in item_data['keywords'] 
                          if keyword.lower() in dialogue_text or keyword.lower() in all_text)
    
    # 基于项目ID的特定评估逻辑
    item_id = item_data['id']
    
    # 社交互动项目 (1-7)
    if item_id == 1:  # 老成或早熟
        if any(word in dialogue_text for word in ['规则', '必须', '应该', '原则']):
            score = 1 if base_probability < 0.6 else 2
    
    elif item_id == 3:  # 生活在自己的世界里
        if len(child_lines) < len(all_lines) * 0.2:  # 互动很少
            score = 2
        elif len(child_lines) < len(all_lines) * 0.3:
            score = 1
    
    elif item_id == 4:  # 社交时缺乏理解
        if '不懂' in dialogue_text or '不明白' in dialogue_text:
            score = 1
        if keyword_matches >= 2:
            score = 2
    
    elif item_id == 5:  # 缺乏最好的朋友
        if '朋友' not in dialogue_text and '一起玩' not in dialogue_text:
            score = 1 if base_probability < 0.7 else 2
    
    # 沟通问题项目 (8-14)
    elif item_id == 8:  # 特殊的声音使用
        if any(pattern in all_text for pattern in ['单调', '平淡', '机械']):
            score = 2
        elif '声音' in all_text and '异常' in all_text:
            score = 1
    
    elif item_id == 9:  # 特殊的语言使用
        repetitive_count = check_repetitive_language(child_lines)
        if repetitive_count > 3:
            score = 2
        elif repetitive_count > 1:
            score = 1
    
    elif item_id == 10:  # 谈话内容有限
        topics = identify_topics(child_lines)
        if len(topics) <= 1 and len(child_lines) > 3:
            score = 2
        elif len(topics) <= 2:
            score = 1
    
    elif item_id == 13:  # 异常的面部表情
        if '面无表情' in all_text or '表情' in all_text and '异常' in all_text:
            score = 2
        elif '表情' in all_text:
            score = 1
    
    # 限制性兴趣项目 (15-17)
    elif item_id == 15:  # 特殊兴趣模式
        special_interest = check_special_interest(child_lines)
        if special_interest:
            score = 2
    
    elif item_id == 16:  # 重复性行为
        if any(word in dialogue_text for word in ['重复', '反复', '一直', '不停']):
            score = 2
        elif any(word in dialogue_text for word in ['又', '再']):
            score = 1
    
    elif item_id == 17:  # 常规和仪式
        if any(word in dialogue_text for word in ['必须', '一定要', '总是', '每次']):
            score = 2
        elif '要' in dialogue_text and '样' in dialogue_text:
            score = 1
    
    # 运动协调项目 (18-19)
    elif item_id == 18:  # 动作笨拙
        if any(word in all_text for word in ['笨拙', '摔', '撞', '协调']):
            score = 2
    
    elif item_id == 19:  # 异常的步态
        if any(word in all_text for word in ['踮脚', '步态', '走路', '姿势']):
            score = 1 if base_probability < 0.6 else 2
    
    # 其他特征项目 (20-27)
    elif item_id == 22:  # 被其他孩子欺负
        if any(word in all_text for word in ['欺负', '嘲笑', '排斥', '孤立']):
            score = 2
    
    elif item_id == 23:  # 特殊的眼神接触
        if '不看' in dialogue_text or '避开' in dialogue_text or '眼神' in all_text:
            score = 2
        elif '看' in dialogue_text and '别处' in dialogue_text:
            score = 1
    
    elif item_id == 24:  # 不喜欢身体接触
        if any(word in dialogue_text for word in ['不要碰', '推开', '躲开']):
            score = 2
        elif '碰' in dialogue_text or '触' in dialogue_text:
            score = 1
    
    elif item_id == 25:  # 言语重复
        if check_echolalia(child_lines, all_lines):
            score = 2
    
    elif item_id == 27:  # 缺乏想象力游戏
        if '假装' not in dialogue_text and '扮演' not in dialogue_text:
            if '排列' in dialogue_text or '转' in dialogue_text:
                score = 2
            else:
                score = 1 if base_probability > 0.5 else 0
    
    # 如果没有特定逻辑，使用关键词匹配
    if score == 0 and keyword_matches > 0:
        if keyword_matches >= 2 or base_probability > 0.7:
            score = 2
        else:
            score = 1
    
    # 随机因素（基于概率）
    if score == 0 and np.random.random() < base_probability * 0.3:
        score = 1
    
    return min(2, score)


def check_repetitive_language(child_lines: List[str]) -> int:
    """检查重复性语言的次数"""
    repetitions = 0
    seen_phrases = []
    
    for line in child_lines:
        content = line.split(':')[-1].strip() if ':' in line else line.strip()
        if len(content) > 3:
            if content in seen_phrases:
                repetitions += 1
            else:
                seen_phrases.append(content)
    
    return repetitions


def check_echolalia(child_lines: List[str], all_lines: List[str]) -> bool:
    """检查是否有鹦鹉学舌现象"""
    for i, line in enumerate(all_lines[:-1]):
        if '孤独症儿童' not in line:
            next_line = all_lines[i + 1] if i + 1 < len(all_lines) else ''
            if '孤独症儿童' in next_line:
                prev_content = line.split(':')[-1].strip() if ':' in line else line.strip()
                child_content = next_line.split(':')[-1].strip() if ':' in next_line else next_line.strip()
                if len(prev_content) > 5 and prev_content in child_content:
                    return True
    return False


def identify_topics(lines: List[str]) -> set:
    """识别对话中的主题"""
    topics = set()
    topic_keywords = {
        '玩具': ['玩具', '积木', '车', '娃娃', '球'],
        '食物': ['吃', '饭', '饿', '喝', '水'],
        '游戏': ['游戏', '玩', '做', '一起'],
        '学习': ['学', '写', '读', '书', '作业'],
        '情感': ['高兴', '难过', '生气', '害怕', '喜欢']
    }
    
    text = ' '.join(lines)
    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            topics.add(topic)
    
    return topics


def check_special_interest(lines: List[str]) -> bool:
    """检查是否有特殊兴趣"""
    interest_indicators = ['喜欢', '一直', '总是', '只要', '特别']
    text = ' '.join(lines)
    
    for indicator in interest_indicators:
        if indicator in text:
            # 检查是否反复提到某个主题
            words = text.split()
            word_counts = {}
            for word in words:
                if len(word) > 2:  # 排除短词
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # 如果某个词出现超过3次，可能是特殊兴趣
            if any(count > 3 for count in word_counts.values()):
                return True
    
    return False


def get_assq_screening_result(total_score: int, informant: str = 'parent') -> Dict[str, Any]:
    """
    根据ASSQ总分获取筛查结果
    
    Args:
        total_score: ASSQ总分（0-54）
        informant: 评分者类型 ('parent'或'teacher')
    
    Returns:
        筛查结果和建议
    """
    # 基于研究的截断分数
    cutoff_scores = {
        'parent': {
            'clinical': 13,  # 临床样本截断分
            'population': 19  # 人群筛查截断分
        },
        'teacher': {
            'clinical': 11,
            'population': 22
        }
    }
    
    cutoff = cutoff_scores[informant]
    
    result = {
        'score': total_score,
        'screening_result': '',
        'risk_level': '',
        'clinical_significance': '',
        'recommendations': []
    }
    
    if total_score < cutoff['clinical']:
        result['screening_result'] = '阴性'
        result['risk_level'] = '低风险'
        result['clinical_significance'] = 'ASSQ筛查未达到临床关注阈值'
        result['recommendations'] = [
            '继续常规发展监测',
            '如有其他担忧，寻求专业评估'
        ]
    elif total_score < cutoff['population']:
        result['screening_result'] = '边缘'
        result['risk_level'] = '中等风险'
        result['clinical_significance'] = '达到临床筛查阈值，建议进一步评估'
        result['recommendations'] = [
            '建议进行全面的孤独症评估',
            '咨询发展儿科医生或心理学家',
            '考虑进行ADOS或ADI-R评估'
        ]
    else:
        result['screening_result'] = '阳性'
        result['risk_level'] = '高风险'
        result['clinical_significance'] = '明显超过筛查阈值，高度提示孤独症谱系障碍'
        result['recommendations'] = [
            '强烈建议立即进行综合诊断评估',
            '寻求孤独症专科评估',
            '尽早开始干预服务',
            '家长教育和支持'
        ]
    
    # 添加百分位数信息（基于Posserud et al., 2006的数据）
    if informant == 'parent':
        if total_score <= 3:
            result['percentile'] = '<50%'
        elif total_score <= 7:
            result['percentile'] = '50-84%'
        elif total_score <= 12:
            result['percentile'] = '85-95%'
        else:
            result['percentile'] = '>95%'
    
    return result


def get_assq_category_interpretation(category_scores: Dict[str, int]) -> Dict[str, str]:
    """
    获取ASSQ各类别得分的解释
    
    Args:
        category_scores: 各类别得分
    
    Returns:
        各类别的解释
    """
    interpretations = {}
    
    # 社交互动（7个项目，最高14分）
    social_score = category_scores.get('社交互动', 0)
    if social_score <= 3:
        interpretations['社交互动'] = '社交功能基本正常'
    elif social_score <= 7:
        interpretations['社交互动'] = '轻度社交困难'
    elif social_score <= 10:
        interpretations['社交互动'] = '中度社交障碍'
    else:
        interpretations['社交互动'] = '严重社交障碍'
    
    # 沟通问题（7个项目，最高14分）
    comm_score = category_scores.get('沟通问题', 0)
    if comm_score <= 3:
        interpretations['沟通问题'] = '沟通功能基本正常'
    elif comm_score <= 7:
        interpretations['沟通问题'] = '轻度沟通困难'
    elif comm_score <= 10:
        interpretations['沟通问题'] = '中度沟通障碍'
    else:
        interpretations['沟通问题'] = '严重沟通障碍'
    
    # 限制性兴趣（3个项目，最高6分）
    interest_score = category_scores.get('限制性兴趣', 0)
    if interest_score <= 1:
        interpretations['限制性兴趣'] = '兴趣模式正常'
    elif interest_score <= 3:
        interpretations['限制性兴趣'] = '轻度限制性兴趣'
    elif interest_score <= 4:
        interpretations['限制性兴趣'] = '中度限制性兴趣'
    else:
        interpretations['限制性兴趣'] = '严重限制性兴趣'
    
    # 运动协调（2个项目，最高4分）
    motor_score = category_scores.get('运动协调', 0)
    if motor_score == 0:
        interpretations['运动协调'] = '运动功能正常'
    elif motor_score <= 2:
        interpretations['运动协调'] = '轻度运动协调问题'
    else:
        interpretations['运动协调'] = '明显运动协调障碍'
    
    # 其他特征（8个项目，最高16分）
    other_score = category_scores.get('其他特征', 0)
    if other_score <= 4:
        interpretations['其他特征'] = '其他特征基本正常'
    elif other_score <= 8:
        interpretations['其他特征'] = '轻度其他孤独症特征'
    elif other_score <= 12:
        interpretations['其他特征'] = '中度其他孤独症特征'
    else:
        interpretations['其他特征'] = '严重其他孤独症特征'
    
    return interpretations