"""批量处理模块"""
import time
import streamlit as st
from .config import DELAY_BETWEEN_REQUESTS


def run_batch_processing(items, process_function, progress_callback=None, item_name="实验"):
    """
    运行批量处理
    
    Args:
        items: 要处理的项目列表
        process_function: 处理单个项目的函数
        progress_callback: 进度回调函数
        item_name: 项目名称（用于显示）
    
    Returns:
        list: 处理结果列表
    """
    results = []
    
    for i, item in enumerate(items):
        if progress_callback:
            progress_callback(i + 1, len(items))
        
        if 'st' in globals():
            remaining_items = len(items) - i - 1
            estimated_time = remaining_items * DELAY_BETWEEN_REQUESTS / 60
            st.info(f"⏳ 正在处理第 {i+1}/{len(items)} 个{item_name}，预计还需 {estimated_time:.1f} 分钟")
        
        result = process_function(item)
        results.append(result)
        
        if i < len(items) - 1:
            print(f"等待{DELAY_BETWEEN_REQUESTS}秒避免API限制...")
            if 'st' in globals():
                progress_bar = st.progress(0)
                for wait_second in range(DELAY_BETWEEN_REQUESTS):
                    progress_bar.progress((wait_second + 1) / DELAY_BETWEEN_REQUESTS)
                    time.sleep(1)
                progress_bar.empty()
            else:
                time.sleep(DELAY_BETWEEN_REQUESTS)
    
    return results