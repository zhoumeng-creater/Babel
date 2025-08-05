"""孤独症儿童特征配置

包含统一的孤独症特征配置和旧版严重程度配置
"""

# ==================== 统一的孤独症特征配置 ====================
# 用于生成中立的行为表现，不偏向任何特定评估标准
UNIFIED_AUTISM_PROFILES = {
    "极轻度表现": {
        "name": "极轻度孤独症表现",
        "social_characteristics": "社交主动性偏低，能够回应他人；偶尔主动发起互动；目光接触存在但不稳定",
        "communication_characteristics": "有功能性语言，词汇量接近年龄水平；语用技能弱，难以理解暗示和比喻；对话时可能过于关注细节",
        "behavioral_characteristics": "有1-2个特别感兴趣的主题；偶有手部小动作；对变化敏感但能适应；轻微的感觉敏感",
        "cognitive_characteristics": "智力正常或超常；可能在某些领域有特殊才能；学习能力良好但可能偏科",
        "emotional_characteristics": "情绪基本稳定；焦虑程度略高；能识别基本情绪但难以理解复杂情绪",
        "daily_living": "生活基本自理；需要提醒和引导；在新环境中需要额外支持",
        "overall_functioning": "mainstream_with_support",
        "behavioral_examples": [
            "在课堂上可能过度关注某个细节而忽略整体",
            "休息时间倾向于独自活动或反复玩同一个游戏",
            "对突然的计划改变表现出明显的不适但能够调整",
            "与同龄人交流时可能显得过于正式或学究"
        ]
    },
    
    "轻度表现": {
        "name": "轻度孤独症表现",
        "social_characteristics": "很少主动社交，但能被动参与；目光接触少；难以理解社交暗示；朋友很少或没有",
        "communication_characteristics": "有语言但可能起步晚；语调平板或特殊；理解字面意思；难以进行来回对话；可能有鹦鹉学舌",
        "behavioral_characteristics": "明显的重复行为如摇摆、转圈；强烈的常规需求；兴趣狭窄且强烈；感觉问题明显",
        "cognitive_characteristics": "认知能力可能不均衡；部分领域可能超常；学习方式特殊；视觉学习能力强",
        "emotional_characteristics": "情绪调节困难；容易崩溃；难以识别和表达情绪；对压力反应强烈",
        "daily_living": "需要日常生活的持续提醒；自理能力发展缓慢；依赖固定程序",
        "overall_functioning": "need_support",
        "behavioral_examples": [
            "看到喜欢的东西会重复拍手或跳跃",
            "每天必须走同一条路线否则会哭闹",
            "可能突然重复电视广告词或他人说过的话",
            "对某些声音极度敏感需要捂住耳朵",
            "吃饭只吃特定质地或颜色的食物"
        ]
    },
    
    "中度表现": {
        "name": "中度孤独症表现",
        "social_characteristics": "社交意识极其有限；基本不主动互动；对他人存在的觉察很少；难以参与集体活动",
        "communication_characteristics": "语言有限或无语言；可能只有几个词；大量使用手势或拉人；理解能力有限；回声式语言明显",
        "behavioral_characteristics": "频繁的刻板动作；自我刺激行为明显；对变化极度抗拒；可能有自伤行为；感觉寻求或回避极端",
        "cognitive_characteristics": "认知发展明显迟缓；学习困难；需要大量重复；具体思维为主",
        "emotional_characteristics": "情绪波动大；频繁崩溃；用行为表达需求；共情能力极其有限",
        "daily_living": "大部分生活技能需要协助；依赖他人照顾；安全意识差",
        "overall_functioning": "need_substantial_support",
        "behavioral_examples": [
            "长时间盯着旋转的风扇或车轮",
            "不停地摇摆身体或原地转圈",
            "用拉扯他人的方式表达需求",
            "对日常程序的微小改变都会导致严重情绪崩溃",
            "可能出现撞头、咬手等自伤行为",
            "完全不能忍受某些质地的衣物"
        ]
    },
    
    "重度表现": {
        "name": "重度孤独症表现", 
        "social_characteristics": "几乎完全没有社交意识；不认识熟悉的人；对他人没有反应；活在自己的世界里",
        "communication_characteristics": "无功能性语言；可能有声音但无意义；不理解简单指令；无法用任何方式表达需求",
        "behavioral_characteristics": "持续的重复刻板行为；严重的自伤行为；完全不能接受任何变化；感觉异常极其严重",
        "cognitive_characteristics": "严重认知障碍；无法学习基本技能；注意力极其短暂；无法理解因果关系",
        "emotional_characteristics": "情绪极不稳定；频繁的严重崩溃；无法安抚；可能有攻击行为",
        "daily_living": "完全依赖他人；无任何自理能力；需要24小时监护；安全意识完全缺失",
        "overall_functioning": "need_very_substantial_support",
        "behavioral_examples": [
            "持续数小时的摇摆或自我刺激",
            "严重的头部撞击或其他自伤行为",
            "完全沉浸在手指晃动等刻板行为中",
            "对疼痛或危险没有反应",
            "可能有严重的睡眠问题",
            "进食极其有限可能需要特殊干预",
            "对环境中的人完全没有觉察"
        ]
    },
    
    "不均衡型表现": {
        "name": "能力发展不均衡型",
        "social_characteristics": "社交能力与其他能力相比明显落后；可能在熟悉环境表现较好；陌生环境退缩明显",
        "communication_characteristics": "表达能力和理解能力差距大；可能词汇量大但不会对话；书面语言可能优于口语",
        "behavioral_characteristics": "行为表现起伏大；好时很好，差时很差；特定触发因素导致行为问题",
        "cognitive_characteristics": "能力极不均衡；可能某方面天才，某方面严重落后；学习能力因领域差异极大",
        "emotional_characteristics": "情绪反应不可预测；同样情况可能反应完全不同；对特定刺激过度反应",
        "daily_living": "自理能力参差不齐；某些方面独立，某些方面完全依赖；技能泛化困难",
        "overall_functioning": "variable_support_needs",
        "behavioral_examples": [
            "能背诵整本书但不会系鞋带",
            "在家里表现很好但在学校完全不同",
            "对数字或日期有惊人记忆但不会简单对话",
            "某些日子能正常交流，某些日子完全沉默",
            "能完成复杂拼图但不会用勺子吃饭"
        ]
    }
}

# ==================== 旧版严重程度配置（已废弃，但保留以兼容旧数据） ====================
# 基于ABC量表的孤独症严重程度分级
ABC_SEVERITY_PROFILES = {
    "孤独症（ABC≥67分）": {
        "sensory_abnormal": 0.7,
        "social_impairment": 0.8,
        "motor_stereotypy": 0.7,
        "language_deficit": 0.8,
        "self_care_deficit": 0.7,
        "total_score_range": [67, 158],
        "behavior_frequency": 0.8,
        "description": "孤独症"
    },
    "可疑孤独症（ABC 53-66分）": {
        "sensory_abnormal": 0.4,
        "social_impairment": 0.5,
        "motor_stereotypy": 0.4,
        "language_deficit": 0.5,
        "self_care_deficit": 0.4,
        "total_score_range": [53, 66],
        "behavior_frequency": 0.5,
        "description": "可疑孤独症"
    },
    "非孤独症（ABC<53分）": {
        "sensory_abnormal": 0.1,
        "social_impairment": 0.2,
        "motor_stereotypy": 0.1,
        "language_deficit": 0.2,
        "self_care_deficit": 0.1,
        "total_score_range": [0, 52],
        "behavior_frequency": 0.2,
        "description": "非孤独症"
    }
}

# 基于医学标准的孤独症严重程度分级
DSM5_SEVERITY_PROFILES = {
    "需要支持（轻度）": {
        "social_communication": 3,
        "restricted_repetitive": 2,
        "sensory_processing": 3,
        "cognitive_function": 4,
        "adaptive_behavior": 3,
        "language_level": 4,
        "special_interests": "数学计算、交通工具、地图",
        "support_needs": "最小支持",
        "dsm5_severity": "需要支持"
    },
    "需要大量支持（中度）": {
        "social_communication": 4,
        "restricted_repetitive": 4,
        "sensory_processing": 4,
        "cognitive_function": 2,
        "adaptive_behavior": 2,
        "language_level": 2,
        "special_interests": "旋转物体、特定音乐、重复动作",
        "support_needs": "大量支持",
        "dsm5_severity": "需要大量支持"
    },
    "需要非常大量支持（重度）": {
        "social_communication": 5,
        "restricted_repetitive": 5,
        "sensory_processing": 5,
        "cognitive_function": 1,
        "adaptive_behavior": 1,
        "language_level": 1,
        "special_interests": "光影变化、自我刺激行为、重复发声",
        "support_needs": "非常大量支持",
        "dsm5_severity": "需要非常大量支持"
    },
    "阿斯伯格样表现": {
        "social_communication": 3,
        "restricted_repetitive": 3,
        "sensory_processing": 4,
        "cognitive_function": 5,
        "adaptive_behavior": 3,
        "language_level": 4,
        "special_interests": "科学、历史、编程、收集",
        "support_needs": "部分支持",
        "dsm5_severity": "需要支持（高功能）"
    },
    "共患ADHD": {
        "social_communication": 3,
        "restricted_repetitive": 3,
        "sensory_processing": 4,
        "cognitive_function": 3,
        "adaptive_behavior": 2,
        "language_level": 3,
        "special_interests": "运动、游戏、动态活动",
        "support_needs": "中等支持",
        "dsm5_severity": "需要支持+注意缺陷多动障碍"
    }
}