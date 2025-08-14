"""
增强版批量研究页面 - 支持多量表选择的批量评估
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime

from common.batch_processor import run_batch_processing
from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation.enhanced_unified_evaluator import (
    run_enhanced_experiment,
    AVAILABLE_SCALES,
    DEFAULT_SCALES,
    COMPREHENSIVE_SCALES
)
from autism.ui_components.visualization import create_assessment_comparison_plot
from autism.ui_components.result_display import analyze_batch_consistency


def generate_enhanced_experiment_batch(
    severity_profiles: dict,
    scene_configs: dict,
    repeats: int,
    selected_scales: list
) -> list:
    """
    生成增强版实验批次配置
    
    Args:
        severity_profiles: 严重程度配置字典
        scene_configs: 场景配置字典
        repeats: 每个组合的重复次数
        selected_scales: 选择的评估量表
    
    Returns:
        实验配置列表
    """
    experiments = []
    counter = 0
    
    for severity_name, profile in severity_profiles.items():
        for scene_name, scene_data in scene_configs.items():
            for repeat in range(repeats):
                for activity in scene_data['activities'][:2]:  # 每个场景选2个活动
                    for trigger in scene_data['triggers'][:2]:  # 每个活动选2个触发因素
                        counter += 1
                        
                        experiment_config = {
                            'experiment_id': f"BATCH_{counter:04d}_{severity_name[:4]}_{scene_name[:4]}",
                            'template': severity_name,
                            'scene': scene_name,
                            'activity': activity,
                            'trigger': trigger,
                            'autism_profile': profile.copy(),
                            'selected_scales': selected_scales,
                            'batch_number': counter,
                            'repeat_number': repeat + 1
                        }
                        experiments.append(experiment_config)
    
    return experiments


def page_batch_research_enhanced():
    """增强版批量研究页面 - 支持多量表选择"""
    st.header("🔬 批量临床研究（多量表版）")
    st.markdown("批量生成行为样本，使用多个量表进行综合评估和对比分析")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        # 量表选择
        st.write("### 1️⃣ 选择评估量表")
        
        scale_preset = st.radio(
            "量表组合方案",
            ["双量表对比（ABC+DSM5）", "三量表验证（ABC+DSM5+CARS）", 
             "全量表综合（所有4个）", "自定义选择"],
            help="选择批量研究使用的量表组合"
        )
        
        if scale_preset == "双量表对比（ABC+DSM5）":
            selected_scales = ['ABC', 'DSM5']
            st.info("✅ 经典双量表对比研究")
        elif scale_preset == "三量表验证（ABC+DSM5+CARS）":
            selected_scales = ['ABC', 'DSM5', 'CARS']
            st.info("✅ 三量表交叉验证研究")
        elif scale_preset == "全量表综合（所有4个）":
            selected_scales = COMPREHENSIVE_SCALES
            st.warning("⚠️ 全量表评估，处理时间较长")
        else:
            selected_scales = []
            cols = st.columns(4)
            for idx, (scale_key, scale_info) in enumerate(AVAILABLE_SCALES.items()):
                with cols[idx]:
                    if st.checkbox(scale_info['name'], value=(scale_key in DEFAULT_SCALES)):
                        selected_scales.append(scale_key)
        
        # 研究规模
        st.write("### 2️⃣ 选择研究规模")
        
        research_scale = st.radio(
            "研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究", "自定义"],
            help="根据研究需要选择合适的样本规模"
        )
        
        if research_scale == "试点研究（推荐）":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())[:2]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            estimated_samples = len(default_severities) * len(default_contexts) * 4 * default_repeats
            st.info(f"🚀 预计生成 {estimated_samples} 个样本，约需 {estimated_samples * len(selected_scales) * 0.5:.0f} 分钟")
        elif research_scale == "标准研究":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())[:3]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            estimated_samples = len(default_severities) * len(default_contexts) * 4 * default_repeats
            st.info(f"⏳ 预计生成 {estimated_samples} 个样本，约需 {estimated_samples * len(selected_scales) * 0.5:.0f} 分钟")
        elif research_scale == "大样本研究":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())
            default_repeats = 2
            estimated_samples = len(default_severities) * len(default_contexts) * 4 * default_repeats
            st.warning(f"⏰ 预计生成 {estimated_samples} 个样本，约需 {estimated_samples * len(selected_scales) * 0.5:.0f} 分钟")
        else:
            # 自定义选择
            default_severities = []
            default_contexts = []
            default_repeats = 1
            
            st.write("**选择严重程度组：**")
            severity_cols = st.columns(3)
            for idx, severity in enumerate(UNIFIED_AUTISM_PROFILES.keys()):
                with severity_cols[idx % 3]:
                    if st.checkbox(severity, key=f"sev_{severity}"):
                        default_severities.append(severity)
            
            st.write("**选择评估情境：**")
            context_cols = st.columns(3)
            for idx, context in enumerate(CLINICAL_SCENE_CONFIG.keys()):
                with context_cols[idx % 3]:
                    if st.checkbox(context, key=f"ctx_{context}"):
                        default_contexts.append(context)
            
            default_repeats = st.slider("每组合重复次数", 1, 5, 1)
            
            if default_severities and default_contexts:
                estimated_samples = len(default_severities) * len(default_contexts) * 4 * default_repeats
                st.info(f"预计生成 {estimated_samples} 个样本")
        
        # 最终选择确认
        if research_scale != "自定义":
            selected_severities = st.multiselect(
                "确认严重程度组", 
                list(UNIFIED_AUTISM_PROFILES.keys()),
                default=default_severities
            )
            
            selected_contexts = st.multiselect(
                "确认评估情境",
                list(CLINICAL_SCENE_CONFIG.keys()),
                default=default_contexts
            )
            
            repeats_per_combo = st.slider(
                "每组合重复次数", 
                1, 5, 
                default_repeats,
                help="增加重复次数提高统计可靠性"
            )
        else:
            selected_severities = default_severities
            selected_contexts = default_contexts
            repeats_per_combo = default_repeats
        
        # 研究选项
        st.write("### 3️⃣ 研究选项")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            compare_scales = st.checkbox("生成量表间对比分析", value=True)
            calculate_reliability = st.checkbox("计算评估信度", value=True)
        with col_opt2:
            export_raw_data = st.checkbox("导出原始数据", value=True)
            generate_report = st.checkbox("生成研究报告", value=True)
    
    with col2:
        st.subheader("📊 研究信息")
        
        if selected_severities and selected_contexts and selected_scales:
            # 显示研究设计矩阵
            st.write("**研究设计矩阵：**")
            
            design_matrix = pd.DataFrame(
                index=selected_severities,
                columns=selected_contexts,
                data=[[repeats_per_combo] * len(selected_contexts)] * len(selected_severities)
            )
            st.dataframe(design_matrix, use_container_width=True)
            
            # 计算总样本数
            total_samples = (
                len(selected_severities) * 
                len(selected_contexts) * 
                4 * repeats_per_combo  # 4是活动和触发因素的组合
            )
            
            # 显示统计信息
            st.metric("总样本数", total_samples)
            st.metric("评估量表数", len(selected_scales))
            st.metric("总评估次数", total_samples * len(selected_scales))
            
            # 预计时间
            estimated_time = total_samples * len(selected_scales) * 0.5  # 假设每个评估0.5分钟
            st.metric("预计时间", f"{estimated_time:.0f} 分钟")
            
            # 显示选中的量表
            st.write("**使用的量表：**")
            for scale in selected_scales:
                st.write(f"• {AVAILABLE_SCALES[scale]['name']}")
        else:
            st.warning("请完成研究设计")
        
        # 开始批量研究按钮
        st.write("---")
        
        if st.button("🚀 开始批量研究", type="primary", use_container_width=True):
            if not selected_severities:
                st.error("请选择至少一个严重程度组")
            elif not selected_contexts:
                st.error("请选择至少一个评估情境")
            elif not selected_scales:
                st.error("请选择至少一个评估量表")
            else:
                run_batch_research(
                    selected_severities,
                    selected_contexts,
                    repeats_per_combo,
                    selected_scales,
                    compare_scales,
                    calculate_reliability,
                    export_raw_data,
                    generate_report
                )


def run_batch_research(
    severities: list,
    contexts: list,
    repeats: int,
    scales: list,
    compare: bool,
    reliability: bool,
    export_data: bool,
    report: bool
):
    """执行批量研究"""
    
    # 准备配置
    severity_dict = {k: UNIFIED_AUTISM_PROFILES[k] for k in severities}
    context_dict = {k: CLINICAL_SCENE_CONFIG[k] for k in contexts}
    
    # 生成实验批次
    experiments = generate_enhanced_experiment_batch(
        severity_dict,
        context_dict,
        repeats,
        scales
    )
    
    st.info(f"📊 将生成 {len(experiments)} 个实验")
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    # 执行批量处理
    successful = 0
    failed = 0
    results = []
    
    for idx, experiment_config in enumerate(experiments):
        # 更新进度
        progress = (idx + 1) / len(experiments)
        progress_bar.progress(progress)
        status_text.text(f"处理中... ({idx + 1}/{len(experiments)})")
        
        try:
            # 执行实验
            result = run_enhanced_experiment(experiment_config)
            
            if 'error' not in result:
                results.append(result)
                successful += 1
                st.session_state.experiment_records.append(result)
            else:
                failed += 1
                
        except Exception as e:
            failed += 1
            print(f"实验失败: {e}")
        
        # 添加延迟避免API限制
        time.sleep(0.5)
    
    # 完成处理
    progress_bar.progress(1.0)
    status_text.text("处理完成！")
    
    # 显示结果
    with results_container:
        st.success(f"✅ 批量研究完成！成功: {successful}, 失败: {failed}")
        
        if results:
            # 分析结果
            st.subheader("📊 研究结果分析")
            
            # 量表间对比
            if compare and len(scales) > 1:
                display_scale_comparison_analysis(results, scales)
            
            # 信度分析
            if reliability:
                display_reliability_analysis(results, scales)
            
            # 数据导出
            if export_data:
                export_research_data(results, scales)
            
            # 生成报告
            if report:
                generate_research_report(results, scales, severities, contexts)


def display_scale_comparison_analysis(results: list, scales: list):
    """显示量表间对比分析"""
    st.write("### 量表间一致性分析")
    
    # 收集对比数据
    comparison_data = []
    
    for result in results:
        if 'scale_comparison' in result:
            comp = result['scale_comparison']
            if 'consistency' in comp:
                comparison_data.append({
                    'ID': result['experiment_id'][:10],
                    '一致性': comp['consistency'].get('overall', 'N/A'),
                    '严重程度': result['template'],
                    '场景': result['scene']
                })
    
    if comparison_data:
        comp_df = pd.DataFrame(comparison_data)
        
        # 统计一致性
        consistency_stats = comp_df['一致性'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**一致性分布：**")
            st.bar_chart(consistency_stats)
        
        with col2:
            st.write("**一致性百分比：**")
            for level, count in consistency_stats.items():
                percentage = (count / len(comparison_data)) * 100
                st.write(f"• {level}: {percentage:.1f}%")


def display_reliability_analysis(results: list, scales: list):
    """显示信度分析"""
    st.write("### 评估信度分析")
    
    # 按量表计算信度指标
    for scale in scales:
        scale_scores = []
        
        for result in results:
            if scale == 'ABC' and 'abc_evaluation' in result:
                scale_scores.append(result['abc_evaluation']['total_score'])
            elif scale == 'DSM5' and 'dsm5_evaluation' in result:
                scale_scores.append(result['dsm5_evaluation']['core_symptom_average'])
            elif scale == 'CARS' and 'cars_evaluation' in result:
                scale_scores.append(result['cars_evaluation']['total_score'])
            elif scale == 'ASSQ' and 'assq_evaluation' in result:
                scale_scores.append(result['assq_evaluation']['total_score'])
        
        if scale_scores:
            # 计算基本统计
            mean_score = np.mean(scale_scores)
            std_score = np.std(scale_scores)
            cv = (std_score / mean_score) * 100 if mean_score > 0 else 0
            
            st.write(f"**{AVAILABLE_SCALES[scale]['name']}：**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("均值", f"{mean_score:.2f}")
            with col2:
                st.metric("标准差", f"{std_score:.2f}")
            with col3:
                st.metric("变异系数", f"{cv:.1f}%")


def export_research_data(results: list, scales: list):
    """导出研究数据"""
    st.write("### 数据导出")
    
    # 准备导出数据
    export_data = []
    
    for result in results:
        row = {
            'ID': result['experiment_id'],
            '时间': result['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '严重程度': result['template'],
            '场景': result['scene'],
            '活动': result['activity']
        }
        
        # 添加各量表得分
        if 'ABC' in scales and 'abc_evaluation' in result:
            row['ABC总分'] = result['abc_evaluation']['total_score']
            row['ABC严重度'] = result['abc_evaluation']['severity']
        
        if 'DSM5' in scales and 'dsm5_evaluation' in result:
            row['DSM5核心'] = result['dsm5_evaluation']['core_symptom_average']
            row['DSM5程度'] = result['dsm5_evaluation']['severity_level']
        
        if 'CARS' in scales and 'cars_evaluation' in result:
            row['CARS总分'] = result['cars_evaluation']['total_score']
            row['CARS严重度'] = result['cars_evaluation']['severity']
        
        if 'ASSQ' in scales and 'assq_evaluation' in result:
            row['ASSQ总分'] = result['assq_evaluation']['total_score']
            row['ASSQ风险'] = result['assq_evaluation']['risk_level']
        
        export_data.append(row)
    
    # 创建DataFrame
    df = pd.DataFrame(export_data)
    
    # 提供下载
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载CSV数据",
        data=csv,
        file_name=f"batch_research_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv'
    )


def generate_research_report(results: list, scales: list, severities: list, contexts: list):
    """生成研究报告"""
    st.write("### 研究报告")
    
    report = []
    report.append("# 批量临床研究报告")
    report.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("## 研究设计")
    report.append(f"- 样本数: {len(results)}")
    report.append(f"- 严重程度组: {', '.join(severities)}")
    report.append(f"- 评估情境: {', '.join(contexts)}")
    report.append(f"- 使用量表: {', '.join([AVAILABLE_SCALES[s]['name'] for s in scales])}")
    report.append("")
    
    # 添加更多报告内容...
    
    report_text = "\n".join(report)
    
    st.download_button(
        label="📄 下载研究报告",
        data=report_text,
        file_name=f"research_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime='text/markdown'
    )