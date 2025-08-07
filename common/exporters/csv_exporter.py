"""CSV导出模块"""
import pandas as pd


def export_to_csv(data_list, encoding='utf-8-sig'):
    """
    将数据列表导出为CSV格式
    
    Args:
        data_list: 字典列表，每个字典代表一行数据
        encoding: 编码格式
    
    Returns:
        bytes: CSV格式的字节数据（而不是字符串）
    """
    if not data_list:
        return b""
    
    df = pd.DataFrame(data_list)
    # 直接返回编码后的字节流
    return df.to_csv(index=False, encoding=encoding).encode(encoding)