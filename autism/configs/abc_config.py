"""ABC孤独症行为量表配置

包含ABC量表的五大领域、57个行为项目和评估指标
"""

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

# ABC量表诊断标准
ABC_DIAGNOSTIC_CRITERIA = {
    "total_score_interpretation": {
        "autism": {"min": 67, "max": 158, "label": "孤独症"},
        "suspected": {"min": 53, "max": 66, "label": "可疑孤独症"},
        "borderline": {"min": 40, "max": 52, "label": "边缘状态"},
        "non_autism": {"min": 0, "max": 39, "label": "非孤独症"}
    },
    "severity_levels": {
        "severe": {"min": 101, "max": 158, "label": "重度孤独症"},
        "moderate": {"min": 67, "max": 100, "label": "中度孤独症"},
        "mild": {"min": 53, "max": 66, "label": "轻度孤独症"},
        "borderline": {"min": 40, "max": 52, "label": "边缘状态"},
        "normal": {"min": 0, "max": 39, "label": "正常范围"}
    }
}