"""通用配置文件"""

# API配置
API_KEY = "sk-DQY3QAIcPGWTMfqZN1itL0qwl3y7ejrqyQwyGLyPom6TGz2v"
API_URL = "https://api.moonshot.cn/v1/chat/completions"

# 批量处理配置
DELAY_BETWEEN_REQUESTS = 25  # API请求间隔秒数
API_TIMEOUT = 30  # API超时时间
MAX_RETRIES = 3  # 最大重试次数

# Excel功能检测
EXCEL_AVAILABLE = False
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import BarChart, Reference
    EXCEL_AVAILABLE = True
except ImportError:
    pass