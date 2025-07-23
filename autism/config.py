"""孤独症儿童评估相关配置 - 基于ABC量表"""

# 基于ABC量表的场景配置
CLINICAL_SCENE_CONFIG = {
    "结构化教学环境": {
        "roles": ["孤独症儿童", "特殊教育老师", "同班同学", "教学助理", "评估师"],
        "target": "观察孤独症儿童在结构化教学环境中的行为表现",
        "desc": "🏫 结构化教学环境（适合观察语言、交往等行为）",
        "activities": [
            "个别化教学任务", "视觉提示学习", "社交故事训练", 
            "轮流活动练习", "日程表使用训练", "工作系统操作"
        ],
        "triggers": [
            "日程突然改变", "新任务引入", "社交要求增加", 
            "感官刺激过载", "规则变化", "时间压力"
        ],
        "observation_points": [
            "语言交流行为", "社交互动表现", "刻板重复动作",
            "感觉异常反应", "自理能力表现", "情绪行为问题"
        ]
    },
    "自然社交情境": {
        "roles": ["孤独症儿童", "典型发育同伴", "社交技能治疗师", "观察员", "家长"],
        "target": "评估孤独症儿童在自然社交环境中的交往能力",
        "desc": "👥 自然社交情境（重点观察交往领域行为）", 
        "activities": [
            "自由游戏时间", "合作游戏任务", "角色扮演游戏",
            "分享活动", "冲突解决情境", "集体讨论"
        ],
        "triggers": [
            "同伴拒绝", "游戏规则争议", "注意力竞争",
            "身体接触要求", "情绪表达需求", "帮助请求"
        ],
        "observation_points": [
            "目光对视", "社交主动性", "情感反应",
            "合作行为", "交流方式", "人际距离"
        ]
    },
    "感官调节环境": {
        "roles": ["孤独症儿童", "职业治疗师", "感统训练师", "护理人员", "评估专家"],
        "target": "观察孤独症儿童的感觉异常和躯体运动表现",
        "desc": "🌈 感官调节环境（重点观察感觉和躯体运动）",
        "activities": [
            "感官探索活动", "深压觉输入", "前庭刺激训练",
            "精细动作练习", "感官休息时间", "适应性行为训练"
        ],
        "triggers": [
            "噪音刺激", "光线变化", "质地变化",
            "运动要求", "拥挤环境", "多重感官输入"
        ],
        "observation_points": [
            "感觉过敏反应", "感觉寻求行为", "运动协调性",
            "姿势控制", "自我刺激行为", "感觉逃避表现"
        ]
    },
    "日常生活技能": {
        "roles": ["孤独症儿童", "生活技能训练师", "家庭成员", "康复师", "行为分析师"],
        "target": "评估孤独症儿童的自理能力和适应性行为",
        "desc": "🏠 日常生活技能训练（重点观察社交自理能力）",
        "activities": [
            "自理技能练习", "家务参与", "购物模拟",
            "时间管理", "安全意识训练", "社区适应"
        ],
        "triggers": [
            "程序被打断", "新环境适应", "选择要求",
            "时间限制", "独立要求", "问题解决需求"
        ],
        "observation_points": [
            "生活自理能力", "规则遵守", "安全意识",
            "独立性表现", "适应能力", "问题解决"
        ]
    },
    "语言沟通评估": {
        "roles": ["孤独症儿童", "语言治疗师", "沟通伙伴", "评估师", "技术支持"],
        "target": "专门评估孤独症儿童的语言沟通能力",
        "desc": "💬 语言沟通专项评估（重点观察语言领域）",
        "activities": [
            "语言表达训练", "理解能力测试", "非语言沟通",
            "AAC设备使用", "社交语言练习", "叙事能力评估"
        ],
        "triggers": [
            "复杂指令", "抽象概念", "情绪表达要求",
            "社交语言需求", "新词汇学习", "语用技能挑战"
        ],
        "observation_points": [
            "语言表达能力", "语言理解水平", "语调语速",
            "手势使用", "模仿能力", "交流功能性"
        ]
    }
}

# ABC量表的五大领域和57个行为项目
ABC_BEHAVIOR_ITEMS = {
    "感觉领域": {
        "items": [
            {"id": "S1", "description": "对声音的反应异常", "weight": 3},
            {"id": "S2", "description": "旋转而不觉得头晕", "weight": 2},
            {"id": "S3", "description": "对疼痛不敏感", "weight": 3},
            {"id": "S4", "description": "对某种特殊声音、光线特别敏感", "weight": 3},
            {"id": "S5", "description": "特别喜欢嗅、尝或触摸物体", "weight": 2},
            {"id": "S6", "description": "对温度变化不敏感", "weight": 2},
            {"id": "S7", "description": "视觉敏感，喜欢看亮光、旋转物", "weight": 2},
            {"id": "S8", "description": "喜欢长时间自身旋转", "weight": 3},
            {"id": "S9", "description": "有特殊的恐惧感", "weight": 2}
        ]
    },
    "交往领域": {
        "items": [
            {"id": "R1", "description": "很少主动与人交往", "weight": 4},
            {"id": "R2", "description": "对别人的呼唤没有反应", "weight": 3},
            {"id": "R3", "description": "很少与人目光对视", "weight": 3},
            {"id": "R4", "description": "不愿被人拥抱或触摸", "weight": 3},
            {"id": "R5", "description": "对别人的情感没有反应", "weight": 4},
            {"id": "R6", "description": "不能与小朋友玩耍", "weight": 4},
            {"id": "R7", "description": "不会向人求助", "weight": 3},
            {"id": "R8", "description": "难以接受环境的变化", "weight": 2},
            {"id": "R9", "description": "喜欢独自活动", "weight": 3},
            {"id": "R10", "description": "不能理解别人的感受", "weight": 3},
            {"id": "R11", "description": "缺乏社交性微笑", "weight": 3},
            {"id": "R12", "description": "对亲人没有依恋", "weight": 4}
        ]
    },
    "躯体运动领域": {
        "items": [
            {"id": "M1", "description": "重复性的手部动作（拍手、挥手等）", "weight": 3},
            {"id": "M2", "description": "来回踱步或跑动", "weight": 2},
            {"id": "M3", "description": "旋转物体", "weight": 2},
            {"id": "M4", "description": "摇摆身体", "weight": 2},
            {"id": "M5", "description": "踮脚尖走路", "weight": 2},
            {"id": "M6", "description": "特殊的手指动作", "weight": 3},
            {"id": "M7", "description": "怪异的身体姿势", "weight": 2},
            {"id": "M8", "description": "自伤行为", "weight": 4},
            {"id": "M9", "description": "过度活跃", "weight": 2},
            {"id": "M10", "description": "行走姿势异常", "weight": 2},
            {"id": "M11", "description": "重复跳跃", "weight": 2},
            {"id": "M12", "description": "紧张时的特殊动作", "weight": 2}
        ]
    },
    "语言领域": {
        "items": [
            {"id": "L1", "description": "无语言或语言发育迟缓", "weight": 4},
            {"id": "L2", "description": "重复他人的话（鹦鹉学舌）", "weight": 3},
            {"id": "L3", "description": "语调、语速异常", "weight": 2},
            {"id": "L4", "description": "自言自语", "weight": 2},
            {"id": "L5", "description": "不能进行对话", "weight": 4},
            {"id": "L6", "description": "代词混用（你、我不分）", "weight": 3},
            {"id": "L7", "description": "语言刻板重复", "weight": 3},
            {"id": "L8", "description": "不能理解简单指令", "weight": 3},
            {"id": "L9", "description": "不会用点头或摇头表示", "weight": 3},
            {"id": "L10", "description": "不能用手势表达需要", "weight": 3},
            {"id": "L11", "description": "语言退化现象", "weight": 4},
            {"id": "L12", "description": "答非所问", "weight": 3},
            {"id": "L13", "description": "特殊的语言形式", "weight": 2}
        ]
    },
    "社交与自理领域": {
        "items": [
            {"id": "A1", "description": "大小便不能自理", "weight": 3},
            {"id": "A2", "description": "睡眠障碍", "weight": 2},
            {"id": "A3", "description": "特殊的饮食习惯", "weight": 2},
            {"id": "A4", "description": "不会模仿", "weight": 3},
            {"id": "A5", "description": "不会玩玩具", "weight": 3},
            {"id": "A6", "description": "对物体的特殊依恋", "weight": 2},
            {"id": "A7", "description": "强迫行为或仪式", "weight": 3},
            {"id": "A8", "description": "不能独立穿衣", "weight": 2},
            {"id": "A9", "description": "破坏行为", "weight": 3},
            {"id": "A10", "description": "攻击行为", "weight": 3},
            {"id": "A11", "description": "情绪不稳定", "weight": 3}
        ]
    }
}

# 基于ABC量表的孤独症严重程度分级
ABC_SEVERITY_PROFILES = {
    "孤独症（ABC≥67分）": {
        "sensory_abnormal": 0.7,      # 感觉异常程度
        "social_impairment": 0.8,      # 交往障碍程度
        "motor_stereotypy": 0.7,       # 躯体运动刻板程度
        "language_deficit": 0.8,        # 语言缺陷程度
        "self_care_deficit": 0.7,       # 自理缺陷程度
        "total_score_range": [67, 158],
        "behavior_frequency": 0.8,      # 异常行为出现频率
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

# ABC量表评估指标说明
ABC_EVALUATION_METRICS = {
    "感觉领域得分": {
        "description": "感觉异常行为的严重程度",
        "max_score": 22,
        "behaviors": ["对声音反应异常", "感觉过敏或迟钝", "特殊感觉寻求"],
        "interpretation": {
            "low": "感觉功能基本正常",
            "medium": "存在明显感觉异常",
            "high": "严重感觉功能障碍"
        }
    },
    "交往领域得分": {
        "description": "社交互动和人际交往的障碍程度",
        "max_score": 41,
        "behaviors": ["目光回避", "社交冷漠", "缺乏依恋"],
        "interpretation": {
            "low": "社交功能轻度受损",
            "medium": "明显社交障碍",
            "high": "严重社交隔离"
        }
    },
    "躯体运动领域得分": {
        "description": "刻板重复动作和运动异常",
        "max_score": 28,
        "behaviors": ["重复动作", "自伤行为", "怪异姿势"],
        "interpretation": {
            "low": "偶有刻板行为",
            "medium": "频繁刻板动作",
            "high": "严重运动异常"
        }
    },
    "语言领域得分": {
        "description": "语言沟通能力的缺陷程度",
        "max_score": 42,
        "behaviors": ["语言缺失", "鹦鹉学舌", "交流障碍"],
        "interpretation": {
            "low": "语言发展迟缓",
            "medium": "明显语言障碍",
            "high": "无功能性语言"
        }
    },
    "社交与自理领域得分": {
        "description": "日常生活自理和适应能力",
        "max_score": 25,
        "behaviors": ["自理缺陷", "强迫行为", "情绪问题"],
        "interpretation": {
            "low": "基本自理能力",
            "medium": "自理能力受损",
            "high": "完全依赖他人"
        }
    }
}