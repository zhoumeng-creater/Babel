"""孤独症数据分析模块包"""

# 为了保持向后兼容，从各子模块导入所有公开函数

# 核心分析函数
from .core_analyzer import (
    generate_clinical_analysis,
    detect_data_format,
    generate_unified_analysis,
    generate_legacy_analysis,
    generate_mixed_format_analysis,
    generate_unified_findings
)

# ABC分析函数
from .abc_analyzer import (
    analyze_abc_evaluations,
    analyze_abc_behavior_frequency,
    analyze_by_severity_abc,
    analyze_by_context_abc,
    generate_abc_analysis,
    generate_abc_findings,
    get_main_behaviors_in_context
)

# DSM-5分析函数
from .dsm5_analyzer import (
    analyze_dsm5_evaluations,
    analyze_by_severity_dsm5,
    analyze_by_context_dsm5,
    analyze_overall_dsm5,
    generate_dsm5_analysis,
    generate_dsm5_findings
)

# 对比分析函数
from .comparison_analyzer import (
    analyze_evaluation_consistency,
    compare_evaluation_methods,
    generate_comparison_report,
    analyze_evaluation_tendencies
)

# 行为分析函数
from .behavior_analyzer import (
    extract_behavior_specific_samples,
    analyze_behavior_associations,
    get_behavior_summary_stats
)

# 相似度计算函数
from .similarity_analyzer import (
    calculate_sample_similarity,
    find_similar_samples,
    calculate_abc_similarity_internal,
    calculate_dsm5_similarity_internal
)

# 导出处理函数
from .export_processor import (
    prepare_clinical_export_data
)

__all__ = [
    # 核心分析
    'generate_clinical_analysis',
    'detect_data_format',
    'generate_unified_analysis',
    'generate_legacy_analysis',
    'generate_mixed_format_analysis',
    'generate_unified_findings',
    
    # ABC分析
    'analyze_abc_evaluations',
    'analyze_abc_behavior_frequency',
    'analyze_by_severity_abc',
    'analyze_by_context_abc',
    'generate_abc_analysis',
    'generate_abc_findings',
    'get_main_behaviors_in_context',
    
    # DSM-5分析
    'analyze_dsm5_evaluations',
    'analyze_by_severity_dsm5',
    'analyze_by_context_dsm5',
    'analyze_overall_dsm5',
    'generate_dsm5_analysis',
    'generate_dsm5_findings',
    
    # 对比分析
    'analyze_evaluation_consistency',
    'compare_evaluation_methods',
    'generate_comparison_report',
    'analyze_evaluation_tendencies',
    
    # 行为分析
    'extract_behavior_specific_samples',
    'analyze_behavior_associations',
    'get_behavior_summary_stats',
    
    # 相似度计算
    'calculate_sample_similarity',
    'find_similar_samples',
    'calculate_abc_similarity_internal',
    'calculate_dsm5_similarity_internal',
    
    # 导出处理
    'prepare_clinical_export_data'
]