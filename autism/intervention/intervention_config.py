"""干预策略配置模块

包含基于循证医学的各种孤独症干预策略配置
"""

# 行为干预策略（基于ABA原理）
BEHAVIORAL_INTERVENTIONS = {
    "正向强化": {
        "name": "Positive Reinforcement",
        "description": "通过奖励强化目标行为",
        "target_behaviors": ["社交主动性", "语言表达", "合作行为"],
        "implementation": {
            "immediate_reward": "立即给予表扬或奖励",
            "token_system": "使用代币系统累积奖励",
            "social_praise": "社交性赞美和认可"
        },
        "expected_improvements": {
            "social_interaction": 0.3,  # 预期改善程度
            "communication": 0.25,
            "behavioral_compliance": 0.35,
            "repetitive_behaviors": -0.1  # 负值表示减少
        },
        "evidence_base": "Cooper et al., 2020 - Applied Behavior Analysis"
    },
    
    "行为消退": {
        "name": "Extinction",
        "description": "通过忽略来减少问题行为",
        "target_behaviors": ["注意力寻求行为", "轻微破坏行为", "重复要求"],
        "implementation": {
            "planned_ignoring": "有计划地忽略问题行为",
            "redirect_attention": "将注意力转向适当行为",
            "consistency": "保持一致的反应模式"
        },
        "expected_improvements": {
            "problem_behaviors": -0.4,
            "emotional_regulation": 0.2,
            "adaptive_behaviors": 0.15
        },
        "evidence_base": "Iwata et al., 2018 - Behavior Modification"
    },
    
    "功能性沟通训练": {
        "name": "Functional Communication Training",
        "description": "教授功能性沟通替代问题行为",
        "target_behaviors": ["自伤行为", "攻击行为", "破坏行为"],
        "implementation": {
            "identify_function": "识别行为功能",
            "teach_alternative": "教授替代沟通方式",
            "reinforce_communication": "强化适当沟通"
        },
        "expected_improvements": {
            "communication": 0.4,
            "problem_behaviors": -0.5,
            "social_interaction": 0.2,
            "self_injury": -0.6
        },
        "evidence_base": "Tiger et al., 2019 - JABA"
    }
}

# 社交干预策略
SOCIAL_INTERVENTIONS = {
    "同伴介入": {
        "name": "Peer-Mediated Intervention",
        "description": "通过同伴互动促进社交技能",
        "target_skills": ["互动启动", "回应技能", "游戏技能"],
        "implementation": {
            "peer_training": "培训同伴如何互动",
            "structured_activities": "结构化的互动活动",
            "adult_facilitation": "成人促进和淡出"
        },
        "expected_improvements": {
            "social_initiation": 0.35,
            "social_response": 0.4,
            "peer_interaction": 0.45,
            "play_skills": 0.3
        },
        "evidence_base": "Chang & Locke, 2016 - Autism Research"
    },
    
    "社交故事": {
        "name": "Social Stories",
        "description": "通过故事教授社交规则和期望",
        "target_skills": ["社交理解", "情境行为", "社交规则"],
        "implementation": {
            "personalized_stories": "个性化的社交故事",
            "visual_supports": "配合视觉支持",
            "regular_review": "定期复习和练习"
        },
        "expected_improvements": {
            "social_understanding": 0.3,
            "appropriate_behavior": 0.25,
            "anxiety_reduction": 0.2,
            "routine_compliance": 0.3
        },
        "evidence_base": "Gray & Garand, 2017 - Focus on Autism"
    },
    
    "视频示范": {
        "name": "Video Modeling",
        "description": "通过视频示范目标行为",
        "target_skills": ["社交技能", "日常技能", "游戏技能"],
        "implementation": {
            "video_examples": "录制示范视频",
            "repeated_viewing": "重复观看",
            "practice_opportunities": "练习机会"
        },
        "expected_improvements": {
            "imitation_skills": 0.35,
            "social_skills": 0.3,
            "daily_living": 0.25,
            "generalization": 0.2
        },
        "evidence_base": "Bellini & Akullian, 2019 - JAD"
    }
}

# 沟通干预策略
COMMUNICATION_INTERVENTIONS = {
    "图片交换系统": {
        "name": "PECS",
        "description": "使用图片进行功能性沟通",
        "target_skills": ["请求", "评论", "社交沟通"],
        "implementation": {
            "picture_cards": "使用图片卡片",
            "exchange_training": "训练交换行为",
            "sentence_building": "构建句子"
        },
        "expected_improvements": {
            "functional_communication": 0.5,
            "requesting": 0.6,
            "vocabulary": 0.3,
            "social_communication": 0.25
        },
        "evidence_base": "Bondy & Frost, 2018 - Pyramid Educational"
    },
    
    "增强性替代沟通": {
        "name": "AAC",
        "description": "使用辅助工具支持沟通",
        "target_skills": ["表达需求", "社交互动", "学业参与"],
        "implementation": {
            "device_selection": "选择合适的AAC设备",
            "vocabulary_programming": "编程核心词汇",
            "naturalistic_teaching": "自然情境教学"
        },
        "expected_improvements": {
            "expressive_language": 0.4,
            "receptive_language": 0.2,
            "communication_initiation": 0.35,
            "frustration_reduction": 0.3
        },
        "evidence_base": "Light & McNaughton, 2020 - AAC Journal"
    },
    
    "关键反应训练": {
        "name": "Pivotal Response Training",
        "description": "针对关键领域的自然化干预",
        "target_skills": ["动机", "自我管理", "社交启动"],
        "implementation": {
            "child_choice": "儿童选择活动",
            "natural_reinforcement": "自然强化",
            "task_variation": "任务变化"
        },
        "expected_improvements": {
            "motivation": 0.4,
            "language_development": 0.35,
            "play_skills": 0.3,
            "social_engagement": 0.35
        },
        "evidence_base": "Koegel & Koegel, 2019 - PRT Manual"
    }
}

# 感觉统合干预
SENSORY_INTERVENTIONS = {
    "感觉调节策略": {
        "name": "Sensory Modulation",
        "description": "调节感觉输入改善行为表现",
        "target_areas": ["感觉寻求", "感觉回避", "感觉调节"],
        "implementation": {
            "sensory_diet": "感觉餐单",
            "environmental_modifications": "环境调整",
            "self_regulation_tools": "自我调节工具"
        },
        "expected_improvements": {
            "sensory_processing": 0.3,
            "attention": 0.25,
            "behavioral_regulation": 0.2,
            "anxiety": -0.25
        },
        "evidence_base": "Schaaf et al., 2018 - AJOT"
    },
    
    "深压觉输入": {
        "name": "Deep Pressure Input",
        "description": "提供深压觉刺激促进平静",
        "target_areas": ["焦虑", "多动", "感觉寻求"],
        "implementation": {
            "weighted_items": "使用加重物品",
            "compression_activities": "压缩活动",
            "proprioceptive_input": "本体觉输入"
        },
        "expected_improvements": {
            "calming": 0.35,
            "attention": 0.2,
            "sleep": 0.25,
            "self_soothing": 0.3
        },
        "evidence_base": "Reynolds et al., 2019 - Sensory Integration"
    }
}

# 认知行为干预
COGNITIVE_INTERVENTIONS = {
    "结构化教学": {
        "name": "Structured Teaching (TEACCH)",
        "description": "使用视觉结构支持学习",
        "target_skills": ["独立性", "任务完成", "过渡技能"],
        "implementation": {
            "visual_schedules": "视觉时间表",
            "work_systems": "工作系统",
            "physical_structure": "物理环境结构"
        },
        "expected_improvements": {
            "independence": 0.4,
            "task_completion": 0.45,
            "transitions": 0.35,
            "anxiety": -0.3
        },
        "evidence_base": "Mesibov et al., 2019 - TEACCH Approach"
    },
    
    "认知行为治疗": {
        "name": "CBT for Autism",
        "description": "适应性认知行为治疗",
        "target_areas": ["焦虑", "情绪调节", "社交理解"],
        "implementation": {
            "thought_identification": "识别想法",
            "coping_strategies": "应对策略",
            "behavioral_experiments": "行为实验"
        },
        "expected_improvements": {
            "anxiety": -0.4,
            "emotional_regulation": 0.35,
            "social_cognition": 0.25,
            "problem_solving": 0.2
        },
        "evidence_base": "Wood et al., 2020 - Clinical Psychology Review"
    }
}

# 综合干预包
COMPREHENSIVE_PACKAGES = {
    "早期丹佛模式": {
        "name": "Early Start Denver Model",
        "description": "综合性早期干预模式",
        "components": ["行为干预", "发展取向", "关系基础"],
        "age_range": "12-48个月",
        "intensity": "每周20-25小时",
        "expected_improvements": {
            "overall_development": 0.4,
            "language": 0.45,
            "social_skills": 0.4,
            "adaptive_behavior": 0.35,
            "cognitive_skills": 0.3
        },
        "evidence_base": "Dawson et al., 2020 - Pediatrics"
    },
    
    "SCERTS模式": {
        "name": "SCERTS Model",
        "description": "社交沟通-情绪调节-交互支持",
        "components": ["社交沟通", "情绪调节", "交互支持"],
        "age_range": "所有年龄",
        "intensity": "嵌入日常活动",
        "expected_improvements": {
            "social_communication": 0.4,
            "emotional_regulation": 0.35,
            "family_engagement": 0.3,
            "peer_relationships": 0.3
        },
        "evidence_base": "Prizant et al., 2019 - SCERTS Manual"
    }
}

# 干预组合推荐
INTERVENTION_COMBINATIONS = {
    "轻度孤独症": {
        "primary": ["社交故事", "同伴介入"],
        "secondary": ["认知行为治疗", "感觉调节策略"],
        "intensity": "每周10-15小时",
        "duration": "6-12个月",
        "expected_outcome": "主流环境适应"
    },
    
    "中度孤独症": {
        "primary": ["功能性沟通训练", "结构化教学"],
        "secondary": ["视频示范", "感觉统合"],
        "intensity": "每周20-25小时",
        "duration": "12-24个月",
        "expected_outcome": "支持下的融合"
    },
    
    "重度孤独症": {
        "primary": ["图片交换系统", "正向强化"],
        "secondary": ["深压觉输入", "结构化教学"],
        "intensity": "每周30-40小时",
        "duration": "持续性支持",
        "expected_outcome": "功能性技能发展"
    }
}

# 干预效果评估指标
INTERVENTION_METRICS = {
    "目标行为达成率": {
        "description": "达到预设目标的百分比",
        "measurement": "percentage",
        "success_threshold": 0.7
    },
    
    "泛化程度": {
        "description": "技能在不同情境的应用",
        "measurement": "scale_1_5",
        "success_threshold": 3
    },
    
    "维持效果": {
        "description": "干预结束后的保持情况",
        "measurement": "months",
        "success_threshold": 6
    },
    
    "家长满意度": {
        "description": "家长对干预效果的满意程度",
        "measurement": "scale_1_10",
        "success_threshold": 7
    }
}