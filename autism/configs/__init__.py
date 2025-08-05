"""孤独症评估配置模块

将所有配置导出以保持向后兼容
"""

# 从各个子模块导入所有配置
from .scene_config import CLINICAL_SCENE_CONFIG

from .profile_config import (
    UNIFIED_AUTISM_PROFILES,
    # 旧版配置（已废弃但保留兼容）
    ABC_SEVERITY_PROFILES,
    DSM5_SEVERITY_PROFILES
)

from .abc_config import (
    ABC_BEHAVIOR_ITEMS,
    ABC_EVALUATION_METRICS
)

from .dsm5_config import DSM5_EVALUATION_METRICS

# 导出所有配置
__all__ = [
    # 场景配置
    'CLINICAL_SCENE_CONFIG',
    
    # 特征配置
    'UNIFIED_AUTISM_PROFILES',
    'ABC_SEVERITY_PROFILES',
    'DSM5_SEVERITY_PROFILES',
    
    # ABC配置
    'ABC_BEHAVIOR_ITEMS',
    'ABC_EVALUATION_METRICS',
    
    # DSM-5配置
    'DSM5_EVALUATION_METRICS'
]