"""JSON导出模块"""
import json
import datetime


def datetime_handler(obj):
    """处理datetime对象的JSON序列化"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def export_to_json(data, indent=2):
    """
    将数据导出为JSON格式
    
    Args:
        data: 要导出的数据
        indent: 缩进空格数
    
    Returns:
        str: JSON格式的字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=indent, default=datetime_handler)