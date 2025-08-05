"""筛选器组件"""
import streamlit as st


def create_record_filters(records):
    """创建记录筛选器"""
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    filters = {}
    
    with col_filter1:
        filters['severity'] = st.selectbox(
            "按严重程度筛选",
            ["全部"] + list(set([r.get('template', '自定义') for r in records]))
        )
    
    with col_filter2:
        filters['context'] = st.selectbox(
            "按评估情境筛选",
            ["全部"] + list(set([r['scene'] for r in records]))
        )
    
    with col_filter3:
        filters['score'] = st.selectbox(
            "按评分筛选",
            ["全部", "ABC高分(≥67)", "ABC低分(<53)", "DSM5重度(≥3.5)", "DSM5轻度(<2.5)"]
        )
    
    with col_filter4:
        filters['sort'] = st.selectbox(
            "排序方式", 
            ["时间倒序", "时间正序", "ABC总分", "DSM-5核心症状", "一致性"]
        )
    
    return filters


def apply_record_filters(records, filters):
    """应用筛选条件"""
    filtered_records = records.copy()
    
    # 应用严重程度筛选
    if filters['severity'] != "全部":
        filtered_records = [r for r in filtered_records if r.get('template', '自定义') == filters['severity']]
    
    # 应用情境筛选
    if filters['context'] != "全部":
        filtered_records = [r for r in filtered_records if r['scene'] == filters['context']]
    
    # 应用评分筛选
    if filters['score'] != "全部":
        if filters['score'] == "ABC高分(≥67)":
            filtered_records = [r for r in filtered_records if r['abc_evaluation']['total_score'] >= 67]
        elif filters['score'] == "ABC低分(<53)":
            filtered_records = [r for r in filtered_records if r['abc_evaluation']['total_score'] < 53]
        elif filters['score'] == "DSM5重度(≥3.5)":
            filtered_records = [r for r in filtered_records if r['dsm5_evaluation']['core_symptom_average'] >= 3.5]
        elif filters['score'] == "DSM5轻度(<2.5)":
            filtered_records = [r for r in filtered_records if r['dsm5_evaluation']['core_symptom_average'] < 2.5]
    
    # 应用排序
    if filters['sort'] == "时间正序":
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'])
    elif filters['sort'] == "ABC总分":
        filtered_records = sorted(filtered_records, key=lambda x: x['abc_evaluation']['total_score'], reverse=True)
    elif filters['sort'] == "DSM-5核心症状":
        filtered_records = sorted(filtered_records, key=lambda x: x['dsm5_evaluation']['core_symptom_average'], reverse=True)
    elif filters['sort'] == "一致性":
        # 按ABC和DSM-5评估的一致性排序
        def get_consistency(record):
            abc_severe = record['abc_evaluation']['total_score'] >= 67
            dsm5_severe = record['dsm5_evaluation']['core_symptom_average'] >= 3.5
            return 1 if abc_severe == dsm5_severe else 0
        filtered_records = sorted(filtered_records, key=get_consistency, reverse=True)
    else:  # 时间倒序
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
    
    return filtered_records