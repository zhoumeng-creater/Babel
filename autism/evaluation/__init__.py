"""孤独症评估模块 - 增强版导出接口"""

# ============================================
# 统一使用增强版函数，旧函数作为兼容性封装
# ============================================

# 导入增强版核心功能
from .enhanced_unified_evaluator import (
    run_enhanced_experiment,
    AVAILABLE_SCALES,
    DEFAULT_SCALES,
    COMPREHENSIVE_SCALES,
    get_scale_selection_recommendations,
    validate_scale_selection,
    perform_abc_evaluation,
    perform_dsm5_evaluation,
    perform_cars_evaluation,
    perform_assq_evaluation,
    compare_scale_results,
    generate_evaluation_summary
)

# 导入各量表评估器
from .abc_evaluator import (
    evaluate_abc_behaviors,
    get_abc_severity_level
)

from .dsm5_evaluator import (
    evaluate_dsm5_dialogue,
    extract_dsm5_observations
)

from .cars_evaluator import (
    evaluate_cars_behaviors,
    get_cars_severity_level,
    get_cars_interpretation
)

from .assq_evaluator import (
    evaluate_assq_behaviors,
    get_assq_screening_result,
    get_assq_category_interpretation
)

# 导入原始unified_evaluator中的辅助函数
from .unified_evaluator import (
    build_unified_autism_prompt,
    call_kimi_with_unified_profile,
    generate_experiment_batch as generate_experiment_batch_legacy
)

from .evaluation_helpers import (
    generate_unique_id,
    add_random_variation
)

# ============================================
# 兼容性封装：将旧函数名映射到新函数
# ============================================

def run_single_experiment(experiment_config):
    """
    兼容性封装：将旧的 run_single_experiment 调用重定向到增强版
    自动使用默认的 ABC 和 DSM-5 双量表评估
    """
    # 确保配置中包含量表选择（如果没有，使用默认）
    if 'selected_scales' not in experiment_config:
        experiment_config['selected_scales'] = DEFAULT_SCALES
    
    # 调用增强版函数
    return run_enhanced_experiment(experiment_config)


def run_single_experiment_with_scales(experiment_config):
    """
    干预模块需要的函数（修复函数名问题）
    直接映射到增强版函数
    """
    return run_enhanced_experiment(experiment_config)


def generate_experiment_batch(templates, scenes, num_experiments_per_combo=3, assessment_standard=None):
    """
    兼容性封装：生成批量实验配置
    自动为每个实验添加默认量表配置
    """
    # 调用原始批量生成函数
    experiments = generate_experiment_batch_legacy(
        templates, 
        scenes, 
        num_experiments_per_combo,
        assessment_standard
    )
    
    # 为每个实验添加量表配置
    for exp in experiments:
        if 'selected_scales' not in exp:
            exp['selected_scales'] = DEFAULT_SCALES
    
    return experiments


# ============================================
# 新增的增强版批量生成函数
# ============================================

def generate_enhanced_batch(templates, scenes, num_experiments_per_combo=3, selected_scales=None):
    """
    增强版批量生成函数，支持自定义量表选择
    """
    if selected_scales is None:
        selected_scales = DEFAULT_SCALES
    
    experiments = []
    experiment_counter = 0
    
    import datetime
    import numpy as np
    
    for template_name, profile in templates.items():
        for scene_name, scene_data in scenes.items():
            for activity in scene_data['activities'][:2]:
                for trigger in scene_data['triggers'][:2]:
                    for i in range(num_experiments_per_combo):
                        experiment_counter += 1
                        
                        # 添加轻微的随机变异
                        varied_profile = profile.copy()
                        
                        # 对行为示例进行轻微变化
                        if 'behavioral_examples' in varied_profile:
                            examples = varied_profile['behavioral_examples']
                            if len(examples) > 3:
                                num_examples = np.random.randint(3, min(6, len(examples) + 1))
                                selected_examples = np.random.choice(examples, num_examples, replace=False)
                                varied_profile['behavioral_examples'] = list(selected_examples)
                        
                        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                        unique_id = f"ENH_{experiment_counter:03d}_{template_name[:4]}_{scene_name[:4]}_{timestamp}"
                        
                        experiments.append({
                            'template': template_name,
                            'scene': scene_name,
                            'activity': activity,
                            'trigger': trigger,
                            'autism_profile': varied_profile,
                            'experiment_id': unique_id,
                            'batch_index': experiment_counter,
                            'selected_scales': selected_scales  # 添加量表选择
                        })
    
    return experiments


# ============================================
# 导出所有公开接口
# ============================================

__all__ = [
    # 核心评估函数（统一使用增强版）
    'run_single_experiment',  # 兼容性封装
    'run_single_experiment_with_scales',  # 干预模块需要
    'run_enhanced_experiment',  # 增强版本体
    'generate_experiment_batch',  # 兼容性封装
    'generate_enhanced_batch',  # 增强版批量生成
    
    # 量表配置
    'AVAILABLE_SCALES',
    'DEFAULT_SCALES', 
    'COMPREHENSIVE_SCALES',
    'get_scale_selection_recommendations',
    'validate_scale_selection',
    
    # 各量表评估函数
    'perform_abc_evaluation',
    'perform_dsm5_evaluation',
    'perform_cars_evaluation',
    'perform_assq_evaluation',
    
    # ABC评估
    'evaluate_abc_behaviors',
    'get_abc_severity_level',
    
    # DSM-5评估
    'evaluate_dsm5_dialogue',
    'extract_dsm5_observations',
    
    # CARS评估
    'evaluate_cars_behaviors',
    'get_cars_severity_level',
    'get_cars_interpretation',
    
    # ASSQ评估
    'evaluate_assq_behaviors',
    'get_assq_screening_result',
    'get_assq_category_interpretation',
    
    # 对比和汇总
    'compare_scale_results',
    'generate_evaluation_summary',
    
    # 辅助函数
    'build_unified_autism_prompt',
    'call_kimi_with_unified_profile',
    'generate_unique_id',
    'add_random_variation'
]