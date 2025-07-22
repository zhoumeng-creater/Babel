"""通用UI组件和辅助函数"""
import streamlit as st
import datetime
import numpy as np


def display_metric_with_color(metric_name, score, max_score=5, thresholds=None):
    """
    根据分数显示带颜色的指标
    
    Args:
        metric_name: 指标名称
        score: 分数
        max_score: 最高分
        thresholds: 阈值字典，例如 {'excellent': 4.5, 'good': 4.0, 'fair': 3.0}
    """
    if thresholds is None:
        thresholds = {'excellent': 4.5, 'good': 4.0, 'fair': 3.0}
    
    score_text = f"{metric_name}: {score}/{max_score}"
    
    if score >= thresholds.get('excellent', 4.5):
        st.success(score_text)
    elif score >= thresholds.get('good', 4.0):
        st.info(score_text)
    elif score >= thresholds.get('fair', 3.0):
        st.warning(score_text)
    else:
        st.error(score_text)


def create_download_button(label, data, filename, mime_type='text/plain'):
    """
    创建下载按钮
    
    Args:
        label: 按钮标签
        data: 要下载的数据
        filename: 文件名（包含时间戳）
        mime_type: MIME类型
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    full_filename = filename.replace('{timestamp}', timestamp)
    
    st.download_button(
        label=label,
        data=data,
        file_name=full_filename,
        mime=mime_type
    )


def display_sidebar_stats(records, record_type="评估"):
    """
    在侧边栏显示统计信息
    
    Args:
        records: 记录列表
        record_type: 记录类型名称
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📈 {record_type}统计")
    
    if records:
        st.sidebar.metric(f"{record_type}总数", len(records))
        recent_record = records[-1]
        st.sidebar.write(f"最近{record_type}: {recent_record['timestamp'].strftime('%m-%d %H:%M')}")
    else:
        st.sidebar.write(f"暂无{record_type}数据")


def generate_unique_id(prefix, template_name, scene_name, counter):
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        template_name: 模板名称
        scene_name: 场景名称
        counter: 计数器
    
    Returns:
        str: 唯一ID
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    return f"{prefix}_{counter:03d}_{template_name[:4]}_{scene_name[:4]}_{timestamp}"


def add_random_variation(profile, keys, min_val=1, max_val=5):
    """
    为配置文件添加随机变异
    
    Args:
        profile: 原始配置字典
        keys: 要变异的键列表
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        dict: 变异后的配置
    """
    varied_profile = profile.copy()
    for key in keys:
        if key in varied_profile:
            variation = np.random.randint(-1, 2)
            varied_profile[key] = max(min_val, min(max_val, varied_profile[key] + variation))
    return varied_profile