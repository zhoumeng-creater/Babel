"""评估记录管理页面"""
import streamlit as st

from autism.analysis import find_similar_samples
from autism.ui_components.filters import create_record_filters, apply_record_filters
from autism.ui_components.result_display import display_single_record_analysis


def page_records_management():
    """评估记录管理页面 - 支持双重评估数据"""
    st.header("📚 评估记录管理")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.info("📝 暂无评估记录")
        st.stop()
    
    st.subheader(f"📊 共有 {len(records)} 条评估记录")
    
    # 创建筛选器
    filters = create_record_filters(records)
    
    # 应用筛选
    filtered_records = apply_record_filters(records, filters)
    
    st.write(f"筛选后记录数: {len(filtered_records)}")
    
    # 记录列表显示
    for i, record in enumerate(filtered_records):
        
        # 判断数据格式并获取评估结果
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            # 新格式：统一评估
            abc_total = record['abc_evaluation']['total_score']
            abc_severity = record['abc_evaluation']['severity']
            dsm5_core = record['dsm5_evaluation']['core_symptom_average']
            data_format = "统一评估"
        else:
            # 旧格式：兼容处理
            abc_total = record.get('abc_total_score', 0)
            abc_severity = record.get('abc_severity', '未知')
            dsm5_core = record.get('dsm5_core_symptom_average', 0)
            data_format = f"旧版{record.get('assessment_standard', 'ABC')}"
        
        # 判断一致性
        abc_severe = abc_total >= 67
        dsm5_severe = dsm5_core >= 3.5
        consistency = "✅" if abc_severe == dsm5_severe else "⚠️"
        
        # 显示标题
        display_title = (f"{consistency} [{data_format}] {record['experiment_id']} - "
                        f"ABC:{abc_total} | DSM5:{dsm5_core:.2f} - "
                        f"{record['timestamp'].strftime('%m-%d %H:%M')}")
        
        with st.expander(display_title):
            _display_record_details(record, i)


def _display_record_details(record, index):
    """显示记录详情 - 支持新旧格式"""
    # 基本信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**📋 评估基本信息:**")
        st.write(f"• 配置类型: {record.get('template', '自定义')}")
        st.write(f"• 评估情境: {record['scene']}")
        st.write(f"• 观察活动: {record.get('activity', '未指定')}")
        st.write(f"• 触发因素: {record.get('trigger', '未指定')}")
        st.write(f"• 评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.write("**📊 ABC量表评估:**")
        if 'abc_evaluation' in record:
            # 新格式
            st.write(f"• 总分: {record['abc_evaluation']['total_score']}")
            st.write(f"• 严重程度: {record['abc_evaluation']['severity']}")
            st.write("• 各领域得分:")
            for domain, score in record['abc_evaluation']['domain_scores'].items():
                st.write(f"  - {domain}: {score}")
        else:
            # 旧格式
            st.write(f"• 总分: {record.get('abc_total_score', 'N/A')}")
            st.write(f"• 严重程度: {record.get('abc_severity', 'N/A')}")
            if 'evaluation_scores' in record:
                st.write("• 各领域得分:")
                for domain, score in record['evaluation_scores'].items():
                    st.write(f"  - {domain}: {score}")
    
    with col3:
        st.write("**🧠 DSM-5标准评估:**")
        if 'dsm5_evaluation' in record:
            # 新格式
            st.write(f"• 核心症状均值: {record['dsm5_evaluation']['core_symptom_average']:.2f}")
            st.write("• 各维度评分:")
            for metric, score in record['dsm5_evaluation']['scores'].items():
                if metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']:
                    st.write(f"  - {metric}: {score:.2f} ⭐")
                else:
                    st.write(f"  - {metric}: {score:.2f}")
        else:
            # 旧格式（仅DSM5评估）
            if record.get('assessment_standard') == 'DSM5':
                st.write(f"• 核心症状均值: {record.get('dsm5_core_symptom_average', 'N/A')}")
                if 'evaluation_scores' in record:
                    st.write("• 各维度评分:")
                    for metric, score in record['evaluation_scores'].items():
                        st.write(f"  - {metric}: {score}")
            else:
                st.write("• DSM-5评估数据不可用")
    
    # 对话记录
    st.write("**💬 行为观察对话记录:**")
    dialogue_text = record.get('dialogue', '无对话记录')
    
    unique_key = f"dialogue_{index}_{record['experiment_id']}_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}"
    st.text_area("", dialogue_text, height=200, key=unique_key)
    
    # 快速操作按钮
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)  
    
    with col_btn1:
        if st.button(f"📋 生成报告", key=f"report_{record['experiment_id']}"):
            st.info("双重评估报告生成功能开发中...")
    
    with col_btn2:
        if st.button(f"📈 详细分析", key=f"analysis_{record['experiment_id']}"):
            display_single_record_analysis(record)
    
    with col_btn3:
        if st.button(f"🔄 重复评估", key=f"repeat_{record['experiment_id']}"):
            st.info("重复评估功能开发中...")
    
    with col_btn4:
        if st.button(f"🔍 查找相似", key=f"similar_{record['experiment_id']}"):
            with st.spinner("正在查找相似样本..."):
                similar_samples = find_similar_samples(
                    record, 
                    st.session_state.experiment_records,
                    threshold=0.7,
                    max_results=5
                )
            
            if similar_samples:
                st.write("**相似样本：**")
                for idx, item in enumerate(similar_samples, 1):
                    similar_record = item['record']
                    st.write(f"{idx}. {similar_record['experiment_id']} - "
                           f"相似度: {item['similarity']:.2%}")
            else:
                st.info("未找到相似度超过70%的样本")