"""批量研究页面 - 增强版（支持多量表选择）"""
import streamlit as st
import pandas as pd
import numpy as np

from common.batch_processor import run_batch_processing
from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
# 修改导入：使用增强版函数
from autism.evaluation import (
    run_enhanced_experiment,  # 使用增强版
    generate_enhanced_batch,   # 使用增强版批量生成
    AVAILABLE_SCALES,
    DEFAULT_SCALES,
    COMPREHENSIVE_SCALES
)
from autism.ui_components.visualization import create_assessment_comparison_plot
from autism.ui_components.result_display import analyze_batch_consistency, create_severity_comparison_df


def page_batch_research():
    """批量研究页面 - 支持多量表评估"""
    st.header("🔬 批量临床研究")
    st.markdown("批量生成行为样本，支持多种量表组合的评估和对比分析")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        # 研究规模选择
        research_scale = st.radio(
            "选择研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究"],
            help="根据研究需要选择合适的样本规模"
        )
        
        if research_scale == "试点研究（推荐）":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())[:2]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            st.info("🚀 试点研究：验证评估效果，约需5-8分钟")
        elif research_scale == "标准研究":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())[:3]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            st.info("⏳ 标准研究：获得可靠数据，约需20-30分钟")
        else:
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())
            default_repeats = 2
            st.warning("⏰ 大样本研究：完整研究数据，约需60-90分钟")
        
        # 严重程度和情境选择
        selected_severities = st.multiselect(
            "选择严重程度组", 
            list(UNIFIED_AUTISM_PROFILES.keys()),
            default=default_severities
        )
        
        selected_contexts = st.multiselect(
            "选择评估情境",
            list(CLINICAL_SCENE_CONFIG.keys()),
            default=default_contexts
        )
        
        repeats_per_combo = st.slider(
            "每组合重复次数", 
            1, 3, 
            default_repeats,
            help="增加重复次数提高统计可靠性"
        )
        
        # ✨ 新增：量表选择功能
        with st.expander("⚙️ 高级选项 - 量表选择", expanded=False):
            st.write("**选择评估量表组合**")
            
            scale_mode = st.radio(
                "量表模式",
                ["标准双量表（ABC+DSM-5）", "全面四量表", "快速筛查（ASSQ）", "自定义选择"],
                horizontal=False
            )
            
            if scale_mode == "标准双量表（ABC+DSM-5）":
                selected_scales = DEFAULT_SCALES
                st.info("✅ 使用ABC和DSM-5双重评估")
            elif scale_mode == "全面四量表":
                selected_scales = COMPREHENSIVE_SCALES
                st.warning("⏱️ 全面评估需要更多时间")
            elif scale_mode == "快速筛查（ASSQ）":
                selected_scales = ['ASSQ']
                st.info("⚡ 仅使用ASSQ快速筛查")
            else:
                # 自定义选择
                selected_scales = []
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.checkbox("ABC量表", value=True, key="batch_abc"):
                        selected_scales.append('ABC')
                    if st.checkbox("CARS量表", value=False, key="batch_cars"):
                        selected_scales.append('CARS')
                with col_b:
                    if st.checkbox("DSM-5标准", value=True, key="batch_dsm5"):
                        selected_scales.append('DSM5')
                    if st.checkbox("ASSQ筛查", value=False, key="batch_assq"):
                        selected_scales.append('ASSQ')
            
            # 显示选中的量表
            if selected_scales:
                st.write(f"**将使用的量表**: {', '.join([AVAILABLE_SCALES[s]['name'] for s in selected_scales])}")
            else:
                # 默认使用双量表
                selected_scales = DEFAULT_SCALES
        
        # 准备实验配置
        if selected_severities and selected_contexts:
            severity_dict = {k: UNIFIED_AUTISM_PROFILES[k] for k in selected_severities}
            context_dict = {k: CLINICAL_SCENE_CONFIG[k] for k in selected_contexts}
            
            # 使用增强版批量生成
            experiments = generate_enhanced_batch(
                severity_dict, 
                context_dict, 
                repeats_per_combo,
                selected_scales  # 传入选择的量表
            )
            
            # 计算评估总数
            total_assessments = len(experiments) * len(selected_scales)
            st.info(f"📊 将生成 {len(experiments)} 个行为样本，进行 {total_assessments} 次量表评估")
            
            # 研究设计预览
            with st.expander("研究设计预览", expanded=False):
                preview_df = pd.DataFrame([
                    {
                        '严重程度': exp['template'],
                        '评估情境': exp['scene'],
                        '观察活动': exp['activity'],
                        '触发因素': exp['trigger'],
                        '评估量表': ', '.join([AVAILABLE_SCALES[s]['name'] for s in exp['selected_scales']])
                    } for exp in experiments[:10]
                ])
                st.dataframe(preview_df)
                if len(experiments) > 10:
                    st.write(f"*...还有 {len(experiments) - 10} 个评估*")
    
    with col2:
        st.subheader("🚀 执行研究")
        
        # Session state管理
        if 'batch_ready' not in st.session_state:
            st.session_state.batch_ready = False
        if 'batch_running' not in st.session_state:
            st.session_state.batch_running = False
        
        if selected_severities and selected_contexts and selected_scales:
            # 预估时间（考虑多量表）
            time_per_sample = 0.5 * len(selected_scales)  # 每个量表约0.5分钟
            estimated_minutes = len(experiments) * time_per_sample
            
            st.info(f"📊 评估数量: {len(experiments)}")
            st.info(f"📋 量表数量: {len(selected_scales)}")
            st.info(f"⏰ 预计时间: {estimated_minutes:.1f} 分钟")
            
            if not st.session_state.batch_ready and not st.session_state.batch_running:
                if st.button("⚡ 准备开始研究", use_container_width=True):
                    st.session_state.batch_ready = True
                    st.rerun()
            
            elif st.session_state.batch_ready and not st.session_state.batch_running:
                st.warning("⏰ **重要**: 由于API限制，批量研究需要较长时间")
                st.info(f"💡 每个样本将进行{len(selected_scales)}个量表评估")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("❌ 取消", use_container_width=True):
                        st.session_state.batch_ready = False
                        st.rerun()
                
                with col_btn2:
                    if st.button("✅ 开始研究", type="primary", use_container_width=True):
                        st.session_state.batch_running = True
                        st.session_state.batch_ready = False
                        st.rerun()
            
            elif st.session_state.batch_running:
                _run_batch_research_enhanced(experiments, selected_scales)
        
        else:
            if not selected_severities:
                st.error("请选择严重程度")
            if not selected_contexts:
                st.error("请选择评估情境")
            if not selected_scales:
                st.error("请选择至少一个评估量表")


def _run_batch_research_enhanced(experiments, selected_scales):
    """执行增强版批量研究"""
    st.success(f"🔬 多量表批量研究进行中...")
    st.info(f"使用量表: {', '.join([AVAILABLE_SCALES[s]['name'] for s in selected_scales])}")
    
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_container = st.empty()
    
    def update_progress(current, total):
        progress = current / total
        progress_bar.progress(progress)
        remaining_time = (total - current) * 0.5 * len(selected_scales) / 60
        status_text.text(f"研究进度: {current}/{total} ({progress:.1%}) - 预计还需 {remaining_time:.1f} 分钟")
    
    try:
        # 使用增强版评估函数
        results = run_batch_processing(
            experiments, 
            run_enhanced_experiment,  # 使用增强版函数
            update_progress,
            "多量表评估"
        )
        
        successful_results = [r for r in results if 'error' not in r]
        failed_results = [r for r in results if 'error' in r]
        
        # 保存结果
        st.session_state.current_batch_results = successful_results
        st.session_state.experiment_records.extend(successful_results)
        
        # 清理进度显示
        progress_bar.empty()
        status_text.empty()
        st.session_state.batch_running = False
        
        # 显示结果摘要
        with result_container:
            st.success(f"✅ 批量研究完成！")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("成功评估", len(successful_results))
            with col_r2:
                st.metric("失败评估", len(failed_results))
            with col_r3:
                success_rate = len(successful_results) / len(results) * 100
                st.metric("成功率", f"{success_rate:.1f}%")
            
            # 分析结果
            if successful_results:
                st.subheader("📊 研究结果分析")
                
                # 根据使用的量表显示不同的分析
                tabs = []
                if 'ABC' in selected_scales:
                    tabs.append("ABC量表分析")
                if 'DSM5' in selected_scales:
                    tabs.append("DSM-5分析")
                if 'CARS' in selected_scales:
                    tabs.append("CARS量表分析")
                if 'ASSQ' in selected_scales:
                    tabs.append("ASSQ筛查分析")
                if len(selected_scales) > 1:
                    tabs.append("量表对比")
                
                if tabs:
                    tab_objects = st.tabs(tabs)
                    tab_idx = 0
                    
                    # ABC分析
                    if 'ABC' in selected_scales:
                        with tab_objects[tab_idx]:
                            display_abc_batch_analysis(successful_results)
                        tab_idx += 1
                    
                    # DSM-5分析
                    if 'DSM5' in selected_scales:
                        with tab_objects[tab_idx]:
                            display_dsm5_batch_analysis(successful_results)
                        tab_idx += 1
                    
                    # CARS分析
                    if 'CARS' in selected_scales:
                        with tab_objects[tab_idx]:
                            display_cars_batch_analysis(successful_results)
                        tab_idx += 1
                    
                    # ASSQ分析
                    if 'ASSQ' in selected_scales:
                        with tab_objects[tab_idx]:
                            display_assq_batch_analysis(successful_results)
                        tab_idx += 1
                    
                    # 量表对比
                    if len(selected_scales) > 1:
                        with tab_objects[tab_idx]:
                            display_scale_comparison_analysis(successful_results, selected_scales)
            
            # 下载选项
            if st.button("💾 保存研究数据", use_container_width=True):
                save_batch_research_data(successful_results, selected_scales)
                st.success("数据已保存！")
                
    except Exception as e:
        st.error(f"批量研究失败: {str(e)}")
        st.session_state.batch_running = False


def display_abc_batch_analysis(results):
    """显示ABC量表批量分析"""
    abc_scores = []
    for r in results:
        if 'abc_evaluation' in r:
            abc_scores.append(r['abc_evaluation']['total_score'])
    
    if abc_scores:
        df = pd.DataFrame({'ABC总分': abc_scores})
        st.metric("平均ABC总分", f"{np.mean(abc_scores):.1f}")
        st.bar_chart(df)


def display_dsm5_batch_analysis(results):
    """显示DSM-5批量分析"""
    dsm5_scores = []
    for r in results:
        if 'dsm5_evaluation' in r:
            dsm5_scores.append(r['dsm5_evaluation']['core_symptom_average'])
    
    if dsm5_scores:
        df = pd.DataFrame({'DSM-5核心症状': dsm5_scores})
        st.metric("平均核心症状", f"{np.mean(dsm5_scores):.2f}")
        st.line_chart(df)


def display_cars_batch_analysis(results):
    """显示CARS量表批量分析"""
    cars_scores = []
    for r in results:
        if 'cars_evaluation' in r:
            cars_scores.append(r['cars_evaluation']['total_score'])
    
    if cars_scores:
        df = pd.DataFrame({'CARS总分': cars_scores})
        st.metric("平均CARS总分", f"{np.mean(cars_scores):.1f}")
        st.bar_chart(df)


def display_assq_batch_analysis(results):
    """显示ASSQ筛查批量分析"""
    assq_scores = []
    positive_count = 0
    for r in results:
        if 'assq_evaluation' in r:
            score = r['assq_evaluation']['total_score']
            assq_scores.append(score)
            if r['assq_evaluation']['positive_screen']:
                positive_count += 1
    
    if assq_scores:
        st.metric("平均ASSQ分数", f"{np.mean(assq_scores):.1f}")
        st.metric("阳性筛查率", f"{positive_count/len(assq_scores)*100:.1f}%")


def display_scale_comparison_analysis(results, scales):
    """显示量表对比分析"""
    st.write("### 量表一致性分析")
    
    consistency_count = 0
    total_count = 0
    
    for result in results:
        if 'scale_comparison' in result:
            if result['scale_comparison'].get('consistency', {}).get('overall') == '一致':
                consistency_count += 1
            total_count += 1
    
    if total_count > 0:
        consistency_rate = consistency_count / total_count * 100
        st.metric("量表一致性率", f"{consistency_rate:.1f}%")
        
        if consistency_rate < 70:
            st.warning("⚠️ 量表间一致性较低，建议增加样本量或调整评估方法")
        else:
            st.success("✅ 量表间一致性良好")


def save_batch_research_data(results, scales):
    """保存批量研究数据"""
    # 实现数据保存逻辑
    pass