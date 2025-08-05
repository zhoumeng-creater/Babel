"""批量研究页面"""
import streamlit as st
import pandas as pd
import numpy as np

from common.batch_processor import run_batch_processing
from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation import run_single_experiment, generate_experiment_batch
from autism.ui_components.visualization import create_assessment_comparison_plot
from autism.ui_components.result_display import analyze_batch_consistency, create_severity_comparison_df


def page_batch_research():
    """批量研究页面 - 统一生成，双标准评估"""
    st.header("🔬 批量临床研究")
    st.markdown("批量生成行为样本，同时进行ABC和DSM-5双重评估对比")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        research_scale = st.radio(
            "选择研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究"],
            help="根据研究需要选择合适的样本规模"
        )
        
        if research_scale == "试点研究（推荐）":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())[:2]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            st.info("🚀 试点研究：验证双重评估效果，约需5-8分钟")
        elif research_scale == "标准研究":
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())[:3]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            st.info("⏳ 标准研究：获得可靠对比数据，约需20-30分钟")
        else:
            default_severities = list(UNIFIED_AUTISM_PROFILES.keys())
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())
            default_repeats = 2
            st.warning("⏰ 大样本研究：完整对比研究数据，约需60-90分钟")
        
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
        
        if selected_severities and selected_contexts:
            severity_dict = {k: UNIFIED_AUTISM_PROFILES[k] for k in selected_severities}
            context_dict = {k: CLINICAL_SCENE_CONFIG[k] for k in selected_contexts}
            
            experiments = generate_experiment_batch(
                severity_dict, 
                context_dict, 
                repeats_per_combo
            )
            
            st.info(f"📊 将生成 {len(experiments)} 个行为样本，每个进行双重评估")
            
            # 研究设计预览
            with st.expander("研究设计预览", expanded=False):
                preview_df = pd.DataFrame([
                    {
                        '严重程度': exp['template'],
                        '评估情境': exp['scene'],
                        '观察活动': exp['activity'],
                        '触发因素': exp['trigger']
                    } for exp in experiments[:10]
                ])
                st.dataframe(preview_df)
                if len(experiments) > 10:
                    st.write(f"*...还有 {len(experiments) - 10} 个评估*")
    
    with col2:
        st.subheader("🚀 执行研究")
        
        if 'batch_ready' not in st.session_state:
            st.session_state.batch_ready = False
        if 'batch_running' not in st.session_state:
            st.session_state.batch_running = False
        
        if selected_severities and selected_contexts:
            estimated_minutes = len(experiments) * 25 / 60
            st.info(f"📊 评估数量: {len(experiments)}")
            st.info(f"⏰ 预计时间: {estimated_minutes:.1f} 分钟")
            st.info(f"📈 将产生: {len(experiments)*2} 个评估结果")
            
            if not st.session_state.batch_ready and not st.session_state.batch_running:
                if st.button("⚡ 准备开始研究", use_container_width=True):
                    st.session_state.batch_ready = True
                    st.rerun()
            
            elif st.session_state.batch_ready and not st.session_state.batch_running:
                st.warning("⏰ **重要**: 由于API限制，批量研究需要较长时间")
                st.info("💡 每个样本将同时进行ABC和DSM-5评估")
                
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
                _run_batch_research(experiments)
        
        else:
            st.error("请先选择严重程度和评估情境")


def _run_batch_research(experiments):
    """执行批量研究"""
    st.success("🔬 双重评估研究进行中...")
    
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_container = st.empty()
    
    def update_progress(current, total):
        progress = current / total
        progress_bar.progress(progress)
        remaining_time = (total - current) * 25 / 60
        status_text.text(f"研究进度: {current}/{total} ({progress:.1%}) - 预计还需 {remaining_time:.1f} 分钟")
    
    try:
        results = run_batch_processing(
            experiments, 
            run_single_experiment, 
            update_progress,
            "双重评估"
        )
        
        successful_results = [r for r in results if 'error' not in r]
        failed_results = [r for r in results if 'error' in r]
        
        st.session_state.experiment_records.extend(successful_results)
        st.session_state.current_batch_results = successful_results
        
        with result_container:
            st.success(f"✅ 双重评估研究完成！")
            st.write(f"**成功评估**: {len(successful_results)} 个样本")
            st.write(f"**评估结果**: {len(successful_results)*2} 个（ABC+DSM-5）")
            
            if failed_results:
                st.error(f"**失败评估**: {len(failed_results)} 个")
            
            if successful_results:
                st.subheader("📈 双重评估结果概览")
                
                # 分析评估一致性
                consistency_analysis = analyze_batch_consistency(successful_results)
                
                col_cons1, col_cons2, col_cons3 = st.columns(3)
                with col_cons1:
                    st.metric("样本总数", len(successful_results))
                with col_cons2:
                    st.metric("一致率", f"{consistency_analysis['consistency_rate']:.1f}%")
                with col_cons3:
                    st.metric("相关系数", f"{consistency_analysis['correlation']:.3f}")
                
                # 显示严重程度对比
                comparison_df = create_severity_comparison_df(successful_results)
                st.dataframe(comparison_df, use_container_width=True)
                
                # 可视化对比
                fig = create_assessment_comparison_plot(successful_results)
                st.plotly_chart(fig, use_container_width=True)
        
        st.session_state.batch_running = False
        
        if st.button("🔄 进行新研究", use_container_width=True):
            st.session_state.batch_ready = False
            st.session_state.batch_running = False
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ 研究出错: {str(e)}")
        st.session_state.batch_running = False
        if st.button("🔄 重新尝试", use_container_width=True):
            st.rerun()