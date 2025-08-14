"""可视化组件 - 修复版本，支持不同格式的领域名称"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

from autism.configs import ABC_EVALUATION_METRICS, DSM5_EVALUATION_METRICS
from autism.analysis import get_behavior_summary_stats


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
    """创建ABC与DSM-5相关性散点图 - 支持新旧格式"""
    abc_scores = []
    dsm5_scores = []
    severities = []
    
    for record in records:
        # 获取ABC总分
        if 'abc_evaluation' in record:
            abc_scores.append(record['abc_evaluation']['total_score'])
        elif 'abc_total_score' in record:
            abc_scores.append(record['abc_total_score'])
        else:
            continue
            
        # 获取DSM5核心症状
        if 'dsm5_evaluation' in record:
            dsm5_scores.append(record['dsm5_evaluation']['core_symptom_average'])
        elif 'dsm5_core_symptom_average' in record:
            dsm5_scores.append(record['dsm5_core_symptom_average'])
        else:
            continue
            
        severities.append(record.get('template', '自定义'))
    
    if not abc_scores:
        # 返回空图表
        fig = go.Figure()
        fig.add_annotation(
            text="没有足够的数据来创建相关性图表",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
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
        trendline="ols" if len(abc_scores) > 2 else None
    )
    
    # 添加诊断阈值线
    fig.add_hline(y=3.5, line_dash="dash", line_color="red", annotation_text="DSM-5重度阈值")
    fig.add_vline(x=67, line_dash="dash", line_color="red", annotation_text="ABC孤独症阈值")
    
    return fig


def normalize_domain_name(domain_name):
    """标准化领域名称，处理不同格式的兼容性"""
    # 创建映射表
    domain_mapping = {
        '感觉': '感觉领域得分',
        '交往': '交往领域得分',
        '躯体运动': '躯体运动领域得分',
        '运动': '躯体运动领域得分',
        '语言': '语言领域得分',
        '社交与自理': '社交与自理领域得分',
        '自理': '社交与自理领域得分',
        # 已经是完整名称的保持不变
        '感觉领域得分': '感觉领域得分',
        '交往领域得分': '交往领域得分',
        '躯体运动领域得分': '躯体运动领域得分',
        '语言领域得分': '语言领域得分',
        '社交与自理领域得分': '社交与自理领域得分'
    }
    
    return domain_mapping.get(domain_name, domain_name)


def display_abc_analysis(records, analysis):
    """显示ABC量表分析结果 - 增强兼容性"""
    st.write("### 📊 ABC量表评估分析")
    
    # 收集所有包含ABC评估的记录
    abc_records = []
    for r in records:
        if 'abc_evaluation' in r:
            abc_records.append(r)
        elif 'abc_total_score' in r:
            # 转换旧格式为新格式结构
            abc_eval = {
                'total_score': r.get('abc_total_score', 0),
                'severity': r.get('abc_severity', '未知'),
                'domain_scores': {}
            }
            # 尝试从其他字段提取领域分数
            if 'evaluation_scores' in r:
                for key, value in r['evaluation_scores'].items():
                    normalized_key = normalize_domain_name(key)
                    if normalized_key in ABC_EVALUATION_METRICS:
                        abc_eval['domain_scores'][normalized_key] = value
            
            abc_records.append({
                'abc_evaluation': abc_eval,
                'template': r.get('template', '自定义')
            })
    
    if not abc_records:
        st.info("📊 没有ABC评估数据")
        return
    
    # ABC总分分布
    abc_scores = [r['abc_evaluation']['total_score'] for r in abc_records]
    
    fig_hist = px.histogram(
        x=abc_scores,
        nbins=20,
        title="ABC总分分布",
        labels={'x': 'ABC总分', 'y': '频次'}
    )
    fig_hist.add_vline(x=67, line_dash="dash", line_color="red", annotation_text="孤独症阈值")
    fig_hist.add_vline(x=53, line_dash="dash", line_color="orange", annotation_text="轻度阈值")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # 各领域得分分析 - 使用灵活的数据收集方式
    domain_data = {domain: [] for domain in ABC_EVALUATION_METRICS.keys()}
    
    for record in abc_records:
        domain_scores = record['abc_evaluation'].get('domain_scores', {})
        
        # 遍历记录中的领域分数
        for domain, score in domain_scores.items():
            # 标准化领域名称
            normalized_domain = normalize_domain_name(domain)
            
            # 如果标准化后的名称在我们的指标中，添加分数
            if normalized_domain in domain_data:
                domain_data[normalized_domain].append(score)
    
    # 过滤掉没有数据的领域
    valid_domain_data = {domain: scores for domain, scores in domain_data.items() if scores}
    
    if valid_domain_data:
        # 箱线图
        fig_box = go.Figure()
        for domain, scores in valid_domain_data.items():
            fig_box.add_trace(go.Box(
                y=scores,
                name=domain.replace("领域得分", "").replace("得分", ""),
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ))
        fig_box.update_layout(
            title="ABC各领域得分分布",
            yaxis_title="得分"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("没有足够的领域得分数据来创建箱线图")
    
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
    """显示DSM-5标准分析结果 - 增强兼容性"""
    st.write("### 🧠 DSM-5标准评估分析")
    
    # 收集所有包含DSM5评估的记录
    dsm5_records = []
    for r in records:
        if 'dsm5_evaluation' in r:
            dsm5_records.append(r)
        elif 'dsm5_core_symptom_average' in r:
            # 转换旧格式
            dsm5_eval = {
                'core_symptom_average': r.get('dsm5_core_symptom_average', 0),
                'scores': r.get('evaluation_scores', {})
            }
            dsm5_records.append({
                'dsm5_evaluation': dsm5_eval,
                'template': r.get('template', '自定义')
            })
    
    if not dsm5_records:
        st.info("📊 没有DSM-5评估数据")
        return
    
    # 核心症状分布
    core_scores = [r['dsm5_evaluation']['core_symptom_average'] for r in dsm5_records]
    
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
    
    # 收集各维度分数
    for metric in DSM5_EVALUATION_METRICS.keys():
        scores = []
        for r in dsm5_records:
            dsm5_scores = r['dsm5_evaluation'].get('scores', {})
            if metric in dsm5_scores:
                scores.append(dsm5_scores[metric])
        if scores:
            avg_scores[metric] = np.mean(scores)
    
    if avg_scores:
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
    else:
        st.info("没有足够的DSM-5维度数据来创建雷达图")


def display_comprehensive_comparison(records, analysis):
    """显示综合对比分析"""
    st.write("### 🔄 ABC与DSM-5综合对比")
    
    # 准备对比数据 - 只处理包含两种评估的记录
    comparison_data = []
    for record in records:
        # 检查是否同时包含两种评估
        has_abc = 'abc_evaluation' in record or 'abc_total_score' in record
        has_dsm5 = 'dsm5_evaluation' in record or 'dsm5_core_symptom_average' in record
        
        if has_abc and has_dsm5:
            # 获取ABC数据
            if 'abc_evaluation' in record:
                abc_total = record['abc_evaluation']['total_score']
                abc_severity = record['abc_evaluation']['severity']
            else:
                abc_total = record.get('abc_total_score', 0)
                abc_severity = record.get('abc_severity', '未知')
            
            # 获取DSM5数据
            if 'dsm5_evaluation' in record:
                dsm5_core = record['dsm5_evaluation']['core_symptom_average']
            else:
                dsm5_core = record.get('dsm5_core_symptom_average', 0)
            
            comparison_data.append({
                '评估ID': record.get('experiment_id', 'ID')[:20] + '...',
                'ABC总分': abc_total,
                'ABC判定': abc_severity,
                'DSM5核心': f"{dsm5_core:.2f}",
                '一致性': '✅' if (abc_total >= 67) == (dsm5_core >= 3.5) else '❌'
            })
    
    if not comparison_data:
        st.info("📊 没有同时包含两种评估的记录")
        return
    
    df_comp = pd.DataFrame(comparison_data[:20])  # 显示前20条
    st.dataframe(df_comp, use_container_width=True)
    
    if len(comparison_data) > 20:
        st.info(f"显示前20条记录，共{len(comparison_data)}条")
    
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
        # 准备数据 - 支持新旧格式
        severity_groups = {}
        for record in records:
            severity = record.get('template', '自定义')
            if severity not in severity_groups:
                severity_groups[severity] = {
                    'abc_scores': [],
                    'dsm5_scores': []
                }
            
            # 获取ABC分数
            if 'abc_evaluation' in record:
                severity_groups[severity]['abc_scores'].append(record['abc_evaluation']['total_score'])
            elif 'abc_total_score' in record:
                severity_groups[severity]['abc_scores'].append(record['abc_total_score'])
            
            # 获取DSM5分数
            if 'dsm5_evaluation' in record:
                severity_groups[severity]['dsm5_scores'].append(record['dsm5_evaluation']['core_symptom_average'])
            elif 'dsm5_core_symptom_average' in record:
                severity_groups[severity]['dsm5_scores'].append(record['dsm5_core_symptom_average'])
        
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