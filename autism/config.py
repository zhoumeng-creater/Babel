"""孤独症儿童评估相关配置 - 支持DSM-5和ABC双标准统一评估"""

# ==================== 通用场景配置 ====================
CLINICAL_SCENE_CONFIG = {
    "结构化教学环境": {
        "roles": ["孤独症儿童", "特殊教育老师", "同班同学", "教学助理", "评估师"],
        "target": "观察孤独症儿童在结构化教学环境中的行为表现",
        "desc": "🏫 结构化教学环境",
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
        "desc": "👥 自然社交情境", 
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
        "desc": "🌈 感官调节环境",
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
        "desc": "🏠 日常生活技能训练",
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
        "desc": "💬 语言沟通专项评估",
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

# ==================== 统一的孤独症特征配置（新增） ====================
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

# ==================== ABC量表配置（保持不变） ====================
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

# ABC量表评估指标说明（保持不变）
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

# ==================== DSM-5标准配置（保持不变） ====================
# 基于医学标准的孤独症评估指标
DSM5_EVALUATION_METRICS = {
    "社交互动质量": {
        "description": "社会情感互惠性缺陷的程度",
        "subscales": {
            "社交发起": "主动发起社交互动的频率和质量",
            "社交反应": "对他人社交信号的反应性和适当性", 
            "社交维持": "维持社交互动的能力和持续性",
            "情感分享": "分享情感和兴趣的能力"
        },
        "scoring_criteria": {
            5: "严重缺陷 - 极少主动社交，不回应社交信号",
            4: "明显缺陷 - 社交发起有限，反应不当",
            3: "中度缺陷 - 可以社交但质量差，需要支持", 
            2: "轻度缺陷 - 基本社交能力，偶有困难",
            1: "无明显缺陷 - 社交互动基本正常"
        }
    },
    "沟通交流能力": {
        "description": "语言和非语言沟通的缺陷程度",
        "subscales": {
            "表达性沟通": "语言或替代方式表达需求和想法的能力",
            "接受性沟通": "理解他人语言和非语言信息的能力",
            "社交性沟通": "在社交情境中使用沟通的语用技能",
            "非语言沟通": "眼神、手势、表情等非语言沟通的使用"
        },
        "scoring_criteria": {
            5: "严重缺陷 - 无功能性沟通或仅有少量单词",
            4: "明显缺陷 - 有限的功能性语言，语用严重受损",
            3: "中度缺陷 - 基本沟通能力但语用技能差",
            2: "轻度缺陷 - 沟通基本流畅但有社交语用困难",
            1: "无明显缺陷 - 沟通能力年龄适宜"
        }
    },
    "刻板重复行为": {
        "description": "限制性重复行为模式的严重程度",
        "subscales": {
            "刻板动作": "重复的运动模式或动作的频率和强度",
            "仪式化行为": "坚持固定程序和仪式的程度",
            "狭隘兴趣": "异常强烈或限制性兴趣的程度",
            "感官行为": "异常感官兴趣或感官寻求/逃避行为"
        },
        "scoring_criteria": {
            5: "严重程度 - 重复行为严重干扰功能",
            4: "明显程度 - 重复行为明显且影响日常活动",
            3: "中度程度 - 有明显重复行为但可以中断",
            2: "轻度程度 - 偶有重复行为，影响轻微",
            1: "无或极轻微 - 很少重复行为"
        }
    },
    "感官处理能力": {
        "description": "感官信息处理的异常程度",
        "subscales": {
            "感官过敏": "对感官刺激过度敏感的程度",
            "感官寻求": "主动寻求感官刺激的行为",
            "感官调节": "调节感官输入的能力",
            "感官整合": "整合多种感官信息的能力"
        },
        "scoring_criteria": {
            5: "严重异常 - 感官问题严重影响日常功能",
            4: "明显异常 - 感官敏感性明显且经常出现",
            3: "中度异常 - 有感官处理困难需要策略支持",
            2: "轻度异常 - 偶有感官敏感但可以适应",
            1: "正常范围 - 感官处理基本正常"
        }
    },
    "情绪行为调节": {
        "description": "情绪识别、表达和调节的能力",
        "subscales": {
            "情绪识别": "识别自己和他人情绪的能力",
            "情绪表达": "适当表达情绪的能力",
            "情绪调节": "管理和调节情绪的策略和能力",
            "行为控制": "控制冲动和不当行为的能力"
        },
        "scoring_criteria": {
            5: "严重困难 - 情绪失调频繁，自伤或攻击行为",
            4: "明显困难 - 经常情绪爆发，调节能力差",
            3: "中度困难 - 情绪调节有困难但有改善空间",
            2: "轻度困难 - 大多数时候能调节情绪",
            1: "良好 - 情绪调节年龄适宜"
        }
    },
    "认知适应功能": {
        "description": "认知功能和适应性行为的水平",
        "subscales": {
            "学习能力": "学习新技能和概念的能力",
            "问题解决": "解决日常问题的能力",
            "执行功能": "计划、组织和灵活思维的能力",
            "适应性行为": "在日常环境中独立功能的能力"
        },
        "scoring_criteria": {
            5: "重度缺陷 - 明显智力障碍，适应能力极差",
            4: "中度缺陷 - 学习困难，需要大量支持",
            3: "轻度缺陷 - 学习能力有限但可训练",
            2: "边缘水平 - 认知能力基本正常但有弱项",
            1: "正常范围 - 认知和适应功能年龄适宜"
        }
    }
}

# ==================== 旧的严重程度配置（已废弃，但保留以兼容旧数据） ====================
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