"""文本导出模块"""


def export_to_text(content_lines):
    """
    将内容行列表导出为文本
    
    Args:
        content_lines: 字符串列表
    
    Returns:
        bytes: UTF-8编码的文本数据
    """
    text_content = '\n'.join(content_lines)
    return text_content.encode('utf-8')