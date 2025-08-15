"""孤独症评估系统页面模块"""

from .quick_assessment_page import page_quick_assessment
from .batch_research_page import page_batch_research
from .custom_assessment_page import page_custom_assessment
from .data_analysis_page import page_data_analysis
from .records_management_page import page_records_management
from .data_import_page import page_data_import
from .records_management_page import page_records_management
# 新增页面
from .multi_scale_assessment_page import page_multi_scale_assessment  # 多量表评估
from .intervention_assessment_page import page_intervention_assessment  # 干预评估
from .score_based_generation_page import page_score_based_generation  # 分数生成

__all__ = [
    # 基础功能页面
    'page_quick_assessment',
    'page_batch_research',
    'page_custom_assessment',
    'page_data_analysis',
    'page_records_management',
    
    # 增强功能页面
    'page_multi_scale_assessment',
    'page_intervention_assessment',
    'page_score_based_generation'
]