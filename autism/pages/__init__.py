"""孤独症评估系统页面模块"""

from .quick_assessment_page import page_quick_assessment
from .batch_research_page import page_batch_research
from .custom_assessment_page import page_custom_assessment
from .data_analysis_page import page_data_analysis
from .records_management_page import page_records_management

__all__ = [
    'page_quick_assessment',
    'page_batch_research', 
    'page_custom_assessment',
    'page_data_analysis',
    'page_records_management'
]