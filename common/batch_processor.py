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
    
    # 创建进度容器
    if 'st' in globals():
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            eta_text = st.empty()
    
    total_items = len(items)
    start_time = time.time()
    
    for i, item in enumerate(items):
        if progress_callback:
            progress_callback(i + 1, total_items)
        
        # 更新进度显示
        if 'st' in globals():
            progress = (i + 1) / total_items
            progress_bar.progress(progress)
            
            # 计算剩余时间
            elapsed_time = time.time() - start_time
            if i > 0:
                avg_time_per_item = elapsed_time / i
                remaining_items = total_items - i - 1
                eta_seconds = remaining_items * avg_time_per_item
                eta_minutes = eta_seconds / 60
                
                status_text.text(f"⏳ 处理进度: {i+1}/{total_items} ({progress:.1%})")
                eta_text.text(f"预计剩余时间: {eta_minutes:.1f} 分钟")
        
        # 处理项目
        try:
            result = process_function(item)
            results.append(result)
        except Exception as e:
            error_result = {
                'error': f'处理失败: {str(e)}',
                'item': item.get('experiment_id', 'unknown')
            }
            results.append(error_result)
        
        # API限制延迟
        if i < total_items - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # 清理进度显示
    if 'st' in globals():
        progress_bar.empty()
        status_text.empty()
        eta_text.empty()
        st.success(f"✅ 批量处理完成！共处理 {total_items} 个{item_name}")
    
    return results