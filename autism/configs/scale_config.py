"""量表配置文件"""

# 量表描述信息
SCALE_DESCRIPTIONS = {
    'ABC': {
        'full_name': '孤独症行为量表 (Autism Behavior Checklist)',
        'description': '57项行为评估，5个领域，总分≥67为孤独症',
        'age_range': '18个月以上',
        'time_required': '10-15分钟',
        'cutoff_scores': {
            '非孤独症': (0, 52),
            '轻度': (53, 66),
            '中度': (67, 100),
            '重度': (101, 158)
        }
    },
    'DSM5': {
        'full_name': 'DSM-5诊断标准',
        'description': '美国精神疾病诊断与统计手册第五版标准',
        'age_range': '所有年龄',
        'time_required': '20-30分钟',
        'severity_levels': ['需要支持', '需要大量支持', '需要非常大量支持']
    },
    'CARS': {
        'full_name': '儿童孤独症评定量表',
        'description': '15个项目，每项1-4分，总分≥30为孤独症',
        'age_range': '2岁以上',
        'time_required': '20-30分钟',
        'cutoff_scores': {
            '非孤独症': (15, 29.5),
            '轻-中度': (30, 36.5),
            '重度': (37, 60)
        }
    },
    'ASSQ': {
        'full_name': '孤独症谱系筛查问卷',
        'description': '27项筛查项目，≥13分为筛查阳性',
        'age_range': '6-17岁',
        'time_required': '10分钟',
        'cutoff_scores': {
            '低风险': (0, 7),
            '边缘': (8, 12),
            '阳性': (13, 54)
        }
    }
}

# 推荐的量表组合
RECOMMENDED_SCALE_COMBINATIONS = {
    '快速筛查': {
        'scales': ['ASSQ'],
        'description': '适用于快速初筛',
        'time': '10分钟'
    },
    '标准评估': {
        'scales': ['ABC', 'DSM5'],
        'description': '临床常用组合，覆盖行为和诊断标准',
        'time': '30-40分钟'
    },
    '全面评估': {
        'scales': ['ABC', 'DSM5', 'CARS'],
        'description': '综合评估，适用于诊断确认',
        'time': '50-60分钟'
    },
    '研究评估': {
        'scales': ['ABC', 'DSM5', 'CARS', 'ASSQ'],
        'description': '全量表评估，适用于研究目的',
        'time': '60-80分钟'
    }
}