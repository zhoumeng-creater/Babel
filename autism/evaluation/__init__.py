"""孤独症评估模块 - 导出接口"""

# 从各子模块导入主要功能，保持向后兼容
from .unified_evaluator import (
    run_single_experiment,
    generate_experiment_batch
)

from .abc_evaluator import (
    evaluate_abc_behaviors,
    get_abc_severity_level
)

from .dsm5_evaluator import (
    evaluate_dsm5_dialogue,
    extract_dsm5_observations
)

from .evaluation_helpers import (
    generate_unique_id,
    add_random_variation
)

__all__ = [
    # 统一评估
    'run_single_experiment',
    'generate_experiment_batch',
    
    # ABC评估
    'evaluate_abc_behaviors',
    'get_abc_severity_level',
    
    # DSM-5评估
    'evaluate_dsm5_dialogue',
    'extract_dsm5_observations',
    
    # 辅助函数
    'generate_unique_id',
    'add_random_variation'
]