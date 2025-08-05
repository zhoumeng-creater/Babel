"""数据分析页面"""
import streamlit as st
import numpy as np

from autism.analysis import generate_clinical_analysis, get_behavior_summary_stats
from autism.ui_components.visualization import (
    create_correlation_scatter,
    display_abc_analysis,
    display_dsm5_analysis,
    display_comprehensive_comparison,
    display_statistical_analysis
)


def page_data_analysis():
    """数据分析页面 - 支持双重评估数据分析"""
    st.header("📈 临床数据分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行临床评估")
        st.stop()
    
    # 生成分析
    analysis = generate_clinical_analysis(records)
    
    # 数据概览
    st.subheader("🏥 评估数据概览")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("评估总数", len(records))
    with col2:
        st.metric("评估情境数", len(set(r['scene'] for r in records)))
    with col3:
        # 计算平均ABC总分
        avg_abc = np.mean([r['abc_evaluation']['total_score'] for r in records])
        st.metric("平均ABC总分", f"{avg_abc:.1f}")
    with col4:
        # 计算平均DSM-5核心症状
        avg_dsm5 = np.mean([r['dsm5_evaluation']['core_symptom_average'] for r in records])
        st.metric("平均DSM-5核心", f"{avg_dsm5:.2f}")
    
    # 评估一致性分析
    st.subheader("🔄 ABC与DSM-5评估一致性分析")
    
    consistency_results = _analyze_consistency(records)
    
    col_cons1, col_cons2, col_cons3 = st.columns(3)
    with col_cons1:
        st.metric("Pearson相关系数", f"{consistency_results['correlation']:.3f}")
        st.write(f"p值: {consistency_results['p_value']:.4f}")
    with col_cons2:
        st.metric("一致性比例", f"{consistency_results['agreement_rate']:.1f}%")
        st.write("(严重程度判断一致)")
    with col_cons3:
        st.metric("评分差异", f"{consistency_results['mean_difference']:.2f}")
        st.write("(标准化后)")
    
    # 散点图显示相关性
    fig_scatter = create_correlation_scatter(records)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 分别显示两种评估的结果
    tab1, tab2, tab3 = st.tabs(["ABC量表分析", "DSM-5标准分析", "综合对比"])
    
    with tab1:
        display_abc_analysis(records, analysis)
    
    with tab2:
        display_dsm5_analysis(records, analysis)
    
    with tab3:
        display_comprehensive_comparison(records, analysis)
    
    # 统计显著性检验
    if len(records) > 10:
        st.subheader("📐 统计学分析")
        display_statistical_analysis(records)


def _analyze_consistency(records):
    """分析ABC和DSM-5评估的一致性"""
    from scipy import stats
    
    abc_scores = []
    dsm5_scores = []
    agreements = 0
    
    for record in records:
        abc_total = record['abc_evaluation']['total_score']
        dsm5_core = record['dsm5_evaluation']['core_symptom_average']
        
        # 标准化分数
        abc_normalized = abc_total / 158
        dsm5_normalized = dsm5_core / 5
        
        abc_scores.append(abc_normalized)
        dsm5_scores.append(dsm5_normalized)
        
        # 判断一致性
        abc_severe = abc_total >= 67
        dsm5_severe = dsm5_core >= 3.5
        if abc_severe == dsm5_severe:
            agreements += 1
    
    # 计算相关性和p值
    if len(records) > 1:
        correlation, p_value = stats.pearsonr(abc_scores, dsm5_scores)
    else:
        correlation, p_value = 0, 1
    
    return {
        'correlation': correlation,
        'p_value': p_value,
        'agreement_rate': (agreements / len(records)) * 100 if records else 0,
        'mean_difference': np.mean([abs(a - d) for a, d in zip(abc_scores, dsm5_scores)])
    }