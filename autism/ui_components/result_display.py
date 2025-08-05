"""结果显示组件"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from autism.config import ABC_EVALUATION_METRICS, DSM5_EVALUATION_METRICS


def display_dual_assessment_results(result):
    """显示双重评估结果"""
    st.subheader("📊 双重评估结果对比")
    
    # 创建两列显示两种评估结果
    col_abc, col_dsm5 = st.columns(2)
    
    with col_abc:
        st.markdown("### 📋 ABC量表评估")
        
        # ABC评估结果
        abc_eval = result['abc_evaluation']
        total_score = abc_eval['total_score']
        severity = abc_eval['severity']
        
        if total_score >= 67:
            st.error(f"**ABC总分: {total_score}**")
            st.error(f"**判定: {severity}**")
        elif total_score >= 53:
            st.warning(f"**ABC总分: {total_score}**")
            st.warning(f"**判定: {severity}**")
        else:
            st.info(f"**ABC总分: {total_score}**")
            st.info(f"**判定: {severity}**")
        
        st.write("**各领域得分**:")
        for domain, score in abc_eval['domain_scores'].items():
            max_score = ABC_EVALUATION_METRICS[domain]['max_score']
            percentage = score / max_score * 100
            st.write(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
        
        # 显示识别到的主要行为
        if abc_eval['identified_behaviors']:
            st.write("**识别到的主要行为**:")
            behavior_count = 0
            for domain, behaviors in abc_eval['identified_behaviors'].items():
                if behaviors and behavior_count < 5:
                    for behavior in behaviors[:2]:
                        st.write(f"• {behavior}")
                        behavior_count += 1
                        if behavior_count >= 5:
                            break
    
    with col_dsm5:
        st.markdown("### 🧠 DSM-5标准评估")
        
        # DSM-5评估结果
        dsm5_eval = result['dsm5_evaluation']
        core_avg = dsm5_eval['core_symptom_average']
        
        if core_avg >= 4.0:
            st.error(f"**核心症状均值: {core_avg:.2f}/5**")
            st.error("**需要非常大量支持**")
        elif core_avg >= 3.0:
            st.warning(f"**核心症状均值: {core_avg:.2f}/5**")
            st.warning("**需要大量支持**")
        else:
            st.info(f"**核心症状均值: {core_avg:.2f}/5**")
            st.info("**需要支持**")
        
        st.write("**各维度评分**:")
        for metric, score in dsm5_eval['scores'].items():
            severity_label = "轻度" if score < 2.5 else "中度" if score < 3.5 else "重度"
            st.write(f"• {metric}: {score:.2f}/5 ({severity_label})")
        
        # 显示临床观察
        if dsm5_eval['clinical_observations']:
            st.write("**临床观察要点**:")
            obs_count = 0
            for category, observations in dsm5_eval['clinical_observations'].items():
                if observations and obs_count < 5:
                    for obs in observations[:1]:
                        st.write(f"• [{category}] {obs}")
                        obs_count += 1
                        if obs_count >= 5:
                            break
    
    # 评估一致性分析
    st.subheader("🔄 评估一致性分析")
    
    # 简单的一致性判断
    abc_severe = total_score >= 67
    dsm5_severe = core_avg >= 3.5
    
    if abc_severe == dsm5_severe:
        st.success("✅ 两种评估标准的严重程度判断基本一致")
    else:
        st.warning("⚠️ 两种评估标准的严重程度判断存在差异")
        if abc_severe and not dsm5_severe:
            st.info("ABC量表显示较严重，但DSM-5评估相对较轻")
        else:
            st.info("DSM-5评估显示较严重，但ABC量表得分相对较低")


def analyze_batch_consistency(results):
    """分析批量结果的评估一致性"""
    consistent_count = 0
    abc_scores = []
    dsm5_scores = []
    
    for record in results:
        abc_severe = record['abc_evaluation']['total_score'] >= 67
        dsm5_severe = record['dsm5_evaluation']['core_symptom_average'] >= 3.5
        
        if abc_severe == dsm5_severe:
            consistent_count += 1
        
        # 标准化分数以便计算相关性
        abc_normalized = record['abc_evaluation']['total_score'] / 158  # ABC最高分158
        dsm5_normalized = record['dsm5_evaluation']['core_symptom_average'] / 5  # DSM-5最高5分
        
        abc_scores.append(abc_normalized)
        dsm5_scores.append(dsm5_normalized)
    
    # 计算相关系数
    if len(results) > 1:
        correlation = np.corrcoef(abc_scores, dsm5_scores)[0, 1]
    else:
        correlation = 0
    
    return {
        'consistency_rate': (consistent_count / len(results)) * 100 if results else 0,
        'correlation': correlation,
        'abc_scores': abc_scores,
        'dsm5_scores': dsm5_scores
    }


def create_severity_comparison_df(results):
    """创建严重程度对比数据框"""
    comparison_data = []
    
    # 按严重程度分组
    severity_groups = {}
    for record in results:
        severity = record.get('template', '自定义')
        if severity not in severity_groups:
            severity_groups[severity] = {
                'abc_scores': [],
                'dsm5_scores': []
            }
        
        severity_groups[severity]['abc_scores'].append(record['abc_evaluation']['total_score'])
        severity_groups[severity]['dsm5_scores'].append(record['dsm5_evaluation']['core_symptom_average'])
    
    # 计算每组的统计数据
    for severity, data in severity_groups.items():
        comparison_data.append({
            '严重程度': severity,
            '样本数': len(data['abc_scores']),
            'ABC平均分': f"{np.mean(data['abc_scores']):.1f}",
            'ABC标准差': f"{np.std(data['abc_scores']):.1f}",
            'DSM5平均分': f"{np.mean(data['dsm5_scores']):.2f}",
            'DSM5标准差': f"{np.std(data['dsm5_scores']):.2f}"
        })
    
    return pd.DataFrame(comparison_data)


def display_abc_detailed_results(abc_eval):
    """显示ABC评估详细结果"""
    st.write(f"### ABC总分: {abc_eval['total_score']}")
    st.write(f"### 严重程度: {abc_eval['severity']}")
    
    # 各领域得分雷达图
    domain_scores = abc_eval['domain_scores']
    domain_names = list(domain_scores.keys())
    domain_values = list(domain_scores.values())
    domain_max_values = [ABC_EVALUATION_METRICS[d]['max_score'] for d in domain_names]
    domain_percentages = [v/m*100 for v, m in zip(domain_values, domain_max_values)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=domain_percentages,
        theta=[d.replace("得分", "") for d in domain_names],
        fill='toself',
        name='得分百分比'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="ABC各领域得分百分比"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 识别到的行为
    if abc_eval['identified_behaviors']:
        st.write("### 识别到的行为")
        for domain, behaviors in abc_eval['identified_behaviors'].items():
            if behaviors:
                st.write(f"**{domain}**:")
                for behavior in behaviors:
                    st.write(f"• {behavior}")


def display_dsm5_detailed_results(dsm5_eval):
    """显示DSM-5评估详细结果"""
    st.write(f"### 核心症状平均分: {dsm5_eval['core_symptom_average']:.2f}/5")
    
    # 各维度评分条形图
    scores = dsm5_eval['scores']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(scores.keys()),
        y=list(scores.values()),
        marker_color=['red' if v >= 4 else 'orange' if v >= 3 else 'green' for v in scores.values()]
    ))
    fig.update_layout(
        title="DSM-5各维度评分",
        yaxis_range=[0, 5],
        yaxis_title="严重程度 (1-5分)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 临床观察
    if dsm5_eval['clinical_observations']:
        st.write("### 临床观察要点")
        for category, observations in dsm5_eval['clinical_observations'].items():
            if observations:
                st.write(f"**{category}**:")
                for obs in observations:
                    st.write(f"• {obs}")


def display_assessment_comparison(record):
    """显示单个记录的评估对比"""
    abc_eval = record['abc_evaluation']
    dsm5_eval = record['dsm5_evaluation']
    
    # 严重程度对比
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ABC总分", abc_eval['total_score'])
        st.write(f"判定: {abc_eval['severity']}")
    
    with col2:
        st.metric("DSM-5核心症状", f"{dsm5_eval['core_symptom_average']:.2f}")
        severity_label = "重度" if dsm5_eval['core_symptom_average'] >= 3.5 else "中度" if dsm5_eval['core_symptom_average'] >= 2.5 else "轻度"
        st.write(f"判定: {severity_label}")
    
    # 一致性判断
    abc_severe = abc_eval['total_score'] >= 67
    dsm5_severe = dsm5_eval['core_symptom_average'] >= 3.5
    
    if abc_severe == dsm5_severe:
        st.success("✅ 两种评估标准的严重程度判断一致")
    else:
        st.warning("⚠️ 两种评估标准的严重程度判断存在差异")
    
    # 详细对比
    st.write("### 评估特点对比")
    
    comparison_text = []
    
    # ABC特点
    if 'identified_behaviors' in abc_eval:
        total_behaviors = sum(len(behaviors) for behaviors in abc_eval['identified_behaviors'].values())
        comparison_text.append(f"• ABC识别了 {total_behaviors} 个具体行为")
    
    # DSM-5特点
    if 'clinical_observations' in dsm5_eval:
        total_observations = sum(len(obs) for obs in dsm5_eval['clinical_observations'].values())
        comparison_text.append(f"• DSM-5记录了 {total_observations} 类临床观察")
    
    # 主要差异
    if abc_eval['domain_scores'].get('语言领域得分', 0) > 30 and dsm5_eval['scores'].get('沟通交流能力', 0) < 3:
        comparison_text.append("• ABC显示语言问题严重，但DSM-5评估相对较轻")
    
    if abc_eval['domain_scores'].get('交往领域得分', 0) > 30 and dsm5_eval['scores'].get('社交互动质量', 0) < 3:
        comparison_text.append("• ABC显示社交障碍严重，但DSM-5评估相对较轻")
    
    for text in comparison_text:
        st.write(text)


def display_single_record_analysis(record):
    """显示单个记录的详细分析"""
    st.write("### 📊 详细评估分析")
    
    # 创建两列
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**ABC量表分析**")
        # 饼图显示各领域贡献
        domain_scores = record['abc_evaluation']['domain_scores']
        fig = px.pie(
            values=list(domain_scores.values()),
            names=[d.replace("得分", "") for d in domain_scores.keys()],
            title="ABC各领域得分占比"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**DSM-5标准分析**")
        # 雷达图显示各维度
        scores = record['dsm5_evaluation']['scores']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
            title="DSM-5各维度评分"
        )
        st.plotly_chart(fig, use_container_width=True)