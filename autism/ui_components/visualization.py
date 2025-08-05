"""可视化组件"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

from autism.config import ABC_EVALUATION_METRICS, DSM5_EVALUATION_METRICS
from autism.analyzer import get_behavior_summary_stats


def create_assessment_comparison_plot(results):
    """创建评估对比可视化"""
    # 准备数据
    data = []
    for record in results:
        data.append({
            '严重程度': record.get('template', '自定义'),
            'ABC总分': record['abc_evaluation']['total_score'],
            'DSM-5核心症状': record['dsm5_evaluation']['core_symptom_average'] * 30  # 缩放到相似范围
        })
    
    df = pd.DataFrame(data)
    
    # 创建分组条形图
    fig = px.bar(
        df.groupby('严重程度').mean().reset_index(),
        x='严重程度',
        y=['ABC总分', 'DSM-5核心症状'],
        title='不同严重程度的ABC与DSM-5评分对比',
        labels={'value': '评分', 'variable': '评估标准'},
        barmode='group'
    )
    
    return fig


def create_correlation_scatter(records):
    """创建ABC与DSM-5相关性散点图"""
    abc_scores = []
    dsm5_scores = []
    severities = []
    
    for record in records:
        abc_scores.append(record['abc_evaluation']['total_score'])
        dsm5_scores.append(record['dsm5_evaluation']['core_symptom_average'])
        severities.append(record.get('template', '自定义'))
    
    df = pd.DataFrame({
        'ABC总分': abc_scores,
        'DSM-5核心症状': dsm5_scores,
        '严重程度': severities
    })
    
    fig = px.scatter(
        df,
        x='ABC总分',
        y='DSM-5核心症状',
        color='严重程度',
        title='ABC总分与DSM-5核心症状相关性',
        labels={'ABC总分': 'ABC总分', 'DSM-5核心症状': 'DSM-5核心症状均分'},
        trendline="ols"
    )
    
    # 添加诊断阈值线
    fig.add_hline(y=3.5, line_dash="dash", line_color="red", annotation_text="DSM-5重度阈值")
    fig.add_vline(x=67, line_dash="dash", line_color="red", annotation_text="ABC孤独症阈值")
    
    return fig


def display_abc_analysis(records, analysis):
    """显示ABC量表分析结果"""
    st.write("### 📊 ABC量表评估分析")
    
    # ABC总分分布
    abc_scores = [r['abc_evaluation']['total_score'] for r in records]
    
    fig_hist = px.histogram(
        x=abc_scores,
        nbins=20,
        title="ABC总分分布",
        labels={'x': 'ABC总分', 'y': '频次'}
    )
    fig_hist.add_vline(x=67, line_dash="dash", line_color="red", annotation_text="孤独症阈值")
    fig_hist.add_vline(x=53, line_dash="dash", line_color="orange", annotation_text="轻度阈值")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # 各领域得分分析
    domain_data = {domain: [] for domain in ABC_EVALUATION_METRICS.keys()}
    for record in records:
        for domain, score in record['abc_evaluation']['domain_scores'].items():
            domain_data[domain].append(score)
    
    # 箱线图
    fig_box = go.Figure()
    for domain, scores in domain_data.items():
        fig_box.add_trace(go.Box(
            y=scores,
            name=domain.replace("得分", ""),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
    fig_box.update_layout(
        title="ABC各领域得分分布",
        yaxis_title="得分"
    )
    st.plotly_chart(fig_box, use_container_width=True)
    
    # 高频行为分析
    if st.checkbox("查看高频行为分析"):
        behavior_stats = get_behavior_summary_stats(records)
        if behavior_stats['total_records'] > 0:
            st.write(f"**总评估记录**: {behavior_stats['total_records']}")
            st.write(f"**识别的行为种类**: {behavior_stats['unique_behaviors_count']}")
            
            if behavior_stats['most_common']:
                st.write("**最常见的行为**:")
                for behavior, stats_item in behavior_stats['most_common'][:10]:
                    st.write(f"• {behavior}: {stats_item['count']}次 ({stats_item['percentage']:.1f}%)")


def display_dsm5_analysis(records, analysis):
    """显示DSM-5标准分析结果"""
    st.write("### 🧠 DSM-5标准评估分析")
    
    # 核心症状分布
    core_scores = [r['dsm5_evaluation']['core_symptom_average'] for r in records]
    
    fig_hist = px.histogram(
        x=core_scores,
        nbins=20,
        title="DSM-5核心症状分布",
        labels={'x': '核心症状均分', 'y': '频次'}
    )
    fig_hist.add_vline(x=3.5, line_dash="dash", line_color="red", annotation_text="重度阈值")
    fig_hist.add_vline(x=2.5, line_dash="dash", line_color="orange", annotation_text="中度阈值")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # 各维度雷达图
    avg_scores = {}
    for metric in DSM5_EVALUATION_METRICS.keys():
        scores = [r['dsm5_evaluation']['scores'][metric] for r in records]
        avg_scores[metric] = np.mean(scores)
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=list(avg_scores.values()),
        theta=list(avg_scores.keys()),
        fill='toself',
        name='平均严重程度'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 5]
            )),
        showlegend=False,
        title="DSM-5各维度平均评分"
    )
    st.plotly_chart(fig_radar, use_container_width=True)


def display_comprehensive_comparison(records, analysis):
    """显示综合对比分析"""
    st.write("### 🔄 ABC与DSM-5综合对比")
    
    # 准备对比数据
    comparison_data = []
    for record in records:
        comparison_data.append({
            '评估ID': record['experiment_id'][:20] + '...',
            'ABC总分': record['abc_evaluation']['total_score'],
            'ABC判定': record['abc_evaluation']['severity'],
            'DSM5核心': f"{record['dsm5_evaluation']['core_symptom_average']:.2f}",
            '一致性': '✅' if (record['abc_evaluation']['total_score'] >= 67) == (record['dsm5_evaluation']['core_symptom_average'] >= 3.5) else '❌'
        })
    
    df_comp = pd.DataFrame(comparison_data[:20])  # 显示前20条
    st.dataframe(df_comp, use_container_width=True)
    
    if len(records) > 20:
        st.info(f"显示前20条记录，共{len(records)}条")
    
    # 一致性统计
    consistent = sum(1 for d in comparison_data if d['一致性'] == '✅')
    inconsistent = len(comparison_data) - consistent
    
    fig_pie = px.pie(
        values=[consistent, inconsistent],
        names=['一致', '不一致'],
        title='ABC与DSM-5评估一致性',
        color_discrete_map={'一致': 'green', '不一致': 'red'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)


def display_statistical_analysis(records):
    """显示统计学分析"""
    try:
        # 准备数据
        severity_groups = {}
        for record in records:
            severity = record.get('template', '自定义')
            if severity not in severity_groups:
                severity_groups[severity] = {
                    'abc_scores': [],
                    'dsm5_scores': []
                }
            severity_groups[severity]['abc_scores'].append(record['abc_evaluation']['total_score'])
            severity_groups[severity]['dsm5_scores'].append(record['dsm5_evaluation']['core_symptom_average'])
        
        if len(severity_groups) >= 2:
            # ABC方差分析
            abc_groups = [scores['abc_scores'] for scores in severity_groups.values() if len(scores['abc_scores']) > 0]
            if len(abc_groups) >= 2:
                f_stat_abc, p_value_abc = stats.f_oneway(*abc_groups)
                
                st.write("**ABC总分的单因素方差分析**:")
                st.write(f"- F统计量: {f_stat_abc:.3f}")
                st.write(f"- p值: {p_value_abc:.4f}")
                
                if p_value_abc < 0.05:
                    st.success("✅ 不同严重程度组间ABC总分差异具有统计学意义 (p < 0.05)")
                else:
                    st.info("ℹ️ 不同严重程度组间ABC总分差异无统计学意义 (p ≥ 0.05)")
            
            # DSM-5方差分析
            dsm5_groups = [scores['dsm5_scores'] for scores in severity_groups.values() if len(scores['dsm5_scores']) > 0]
            if len(dsm5_groups) >= 2:
                f_stat_dsm5, p_value_dsm5 = stats.f_oneway(*dsm5_groups)
                
                st.write("\n**DSM-5核心症状的单因素方差分析**:")
                st.write(f"- F统计量: {f_stat_dsm5:.3f}")
                st.write(f"- p值: {p_value_dsm5:.4f}")
                
                if p_value_dsm5 < 0.05:
                    st.success("✅ 不同严重程度组间DSM-5核心症状差异具有统计学意义 (p < 0.05)")
                else:
                    st.info("ℹ️ 不同严重程度组间DSM-5核心症状差异无统计学意义 (p ≥ 0.05)")
                
    except ImportError:
        st.info("💡 安装scipy模块可启用统计学分析功能")