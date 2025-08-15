"""快速评估页面 - 使用增强版功能"""
import streamlit as st
import datetime
import pandas as pd

from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation import (
    run_enhanced_experiment,  # 使用增强版
    AVAILABLE_SCALES,
    DEFAULT_SCALES
)
from autism.ui_components.result_display import display_dual_assessment_results


def page_quick_assessment():
    """快速评估页面 - 增强版（支持多量表但默认使用双量表）"""
    st.header("🩺 快速临床评估")
    st.markdown("生成孤独症儿童行为表现，支持多种量表评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 选择评估对象")
        
        # 严重程度选择
        selected_severity = st.selectbox("选择严重程度", list(UNIFIED_AUTISM_PROFILES.keys()))
        profile = UNIFIED_AUTISM_PROFILES[selected_severity]
        
        # 显示特征
        with st.expander("查看孤独症特征配置", expanded=True):
            st.write(f"**类型**: {profile['name']}")
            st.write(f"**社交特征**: {profile['social_characteristics']}")
            st.write(f"**沟通特征**: {profile['communication_characteristics']}")
            st.write(f"**行为特征**: {profile['behavioral_characteristics']}")
            st.write(f"**认知特征**: {profile['cognitive_characteristics']}")
            st.write(f"**情绪特征**: {profile['emotional_characteristics']}")
            st.write(f"**日常生活**: {profile['daily_living']}")
            
            st.write("**典型行为示例**:")
            for i, example in enumerate(profile['behavioral_examples'][:3], 1):
                st.write(f"{i}. {example}")
        
        # 场景选择
        selected_scene = st.selectbox("选择评估情境", list(CLINICAL_SCENE_CONFIG.keys()))
        scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
        
        with st.expander("评估情境详情"):
            st.write(f"**目标**: {scene_data['target']}")
            st.write(f"**观察要点**: {', '.join(scene_data['observation_points'])}")
        
        selected_activity = st.selectbox("选择观察活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择触发因素", scene_data['triggers'])
    
    with col2:
        st.subheader("🔍 执行评估")
        
        # 量表选择（默认隐藏在高级选项中）
        with st.expander("⚙️ 高级选项 - 量表选择", expanded=False):
            st.write("选择要使用的评估量表：")
            
            # 快速选择
            quick_select = st.radio(
                "快速选择",
                ["标准双量表（ABC+DSM-5）", "全面四量表", "自定义"],
                horizontal=True
            )
            
            if quick_select == "标准双量表（ABC+DSM-5）":
                selected_scales = ['ABC', 'DSM5']
                st.info("✅ 使用ABC和DSM-5标准评估")
            elif quick_select == "全面四量表":
                selected_scales = ['ABC', 'DSM5', 'CARS', 'ASSQ']
                st.info("✅ 使用全部四个量表")
            else:
                # 自定义选择
                selected_scales = []
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.checkbox("ABC量表", value=True):
                        selected_scales.append('ABC')
                    if st.checkbox("CARS量表", value=False):
                        selected_scales.append('CARS')
                with col_b:
                    if st.checkbox("DSM-5标准", value=True):
                        selected_scales.append('DSM5')
                    if st.checkbox("ASSQ筛查", value=False):
                        selected_scales.append('ASSQ')
                    else:
                        # 默认使用双量表
                        selected_scales = DEFAULT_SCALES
        
        # 显示将使用的量表
        st.write("**评估量表**:")
        scale_names = [AVAILABLE_SCALES[s]['name'] for s in selected_scales]
        st.info(f"将使用: {', '.join(scale_names)}")
        
        if st.button("🚀 开始评估", type="primary", use_container_width=True):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            
            experiment_config = {
                'template': selected_severity,
                'scene': selected_scene,
                'activity': selected_activity,
                'trigger': selected_trigger,
                'autism_profile': profile.copy(),
                'experiment_id': f"QUICK_{selected_severity[:4]}_{timestamp}",
                'selected_scales': selected_scales  # 传递选择的量表
            }
            
            with st.spinner(f"🤖 正在生成行为对话并进行{len(selected_scales)}个量表评估..."):
                # 使用增强版评估函数
                result = run_enhanced_experiment(experiment_config)
            
            if 'error' not in result:
                st.session_state.experiment_records.append(result)
                st.success(f"✅ 评估完成！ID: {result['experiment_id']}")
                
                # 显示结果摘要
                display_assessment_summary(result)
                
                # 详细结果（根据使用的量表显示）
                with st.expander("📊 查看详细评估结果", expanded=True):
                    tabs = []
                    if 'abc_evaluation' in result:
                        tabs.append("ABC量表")
                    if 'dsm5_evaluation' in result:
                        tabs.append("DSM-5标准")
                    if 'cars_evaluation' in result:
                        tabs.append("CARS量表")
                    if 'assq_evaluation' in result:
                        tabs.append("ASSQ筛查")
                    
                    if len(tabs) > 1:
                        tab_objects = st.tabs(tabs)
                        tab_index = 0
                        
                        if 'abc_evaluation' in result:
                            with tab_objects[tab_index]:
                                display_abc_results(result['abc_evaluation'])
                            tab_index += 1
                        
                        if 'dsm5_evaluation' in result:
                            with tab_objects[tab_index]:
                                display_dsm5_results(result['dsm5_evaluation'])
                            tab_index += 1
                        
                        if 'cars_evaluation' in result:
                            with tab_objects[tab_index]:
                                display_cars_results(result['cars_evaluation'])
                            tab_index += 1
                        
                        if 'assq_evaluation' in result:
                            with tab_objects[tab_index]:
                                display_assq_results(result['assq_evaluation'])
                    else:
                        # 只有一个量表时直接显示
                        if 'abc_evaluation' in result:
                            display_abc_results(result['abc_evaluation'])
                        elif 'dsm5_evaluation' in result:
                            display_dsm5_results(result['dsm5_evaluation'])
                        elif 'cars_evaluation' in result:
                            display_cars_results(result['cars_evaluation'])
                        elif 'assq_evaluation' in result:
                            display_assq_results(result['assq_evaluation'])
                
                # 对话预览
                with st.expander("💬 查看行为观察对话", expanded=False):
                    dialogue_lines = result['dialogue'].split('\n')[:20]
                    for line in dialogue_lines:
                        if ':' in line and line.strip():
                            if '孤独症儿童' in line:
                                st.markdown(f"🧒 {line}")
                            else:
                                st.markdown(f"👤 {line}")
                    
                    if len(result['dialogue'].split('\n')) > 20:
                        st.markdown("*...完整对话已保存，可在'评估记录管理'中查看*")
            else:
                st.error(f"❌ 评估失败: {result['error']}")


def display_assessment_summary(result):
    """显示评估结果摘要"""
    st.write("### 📊 评估结果摘要")
    
    cols = st.columns(len(result.get('selected_scales', [])))
    
    for idx, scale in enumerate(result.get('selected_scales', [])):
        with cols[idx]:
            if scale == 'ABC' and 'abc_evaluation' in result:
                abc = result['abc_evaluation']
                st.metric(
                    "ABC总分",
                    abc['total_score'],
                    abc['severity']
                )
            elif scale == 'DSM5' and 'dsm5_evaluation' in result:
                dsm5 = result['dsm5_evaluation']
                st.metric(
                    "DSM-5核心症状",
                    f"{dsm5['core_symptom_average']:.2f}",
                    dsm5['severity_level']
                )
            elif scale == 'CARS' and 'cars_evaluation' in result:
                cars = result['cars_evaluation']
                st.metric(
                    "CARS总分",
                    f"{cars['total_score']:.1f}",
                    cars['severity']
                )
            elif scale == 'ASSQ' and 'assq_evaluation' in result:
                assq = result['assq_evaluation']
                st.metric(
                    "ASSQ筛查",
                    assq['total_score'],
                    assq['screening_result']['screening_result']
                )


def display_abc_results(abc_eval):
    """显示ABC量表结果"""
    st.write("#### ABC量表评估结果")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总分", abc_eval['total_score'])
        st.metric("严重程度", abc_eval['severity'])
    
    with col2:
        st.metric("临床意义", "阳性" if abc_eval.get('clinical_range', False) else "阴性")
        if 'interpretation' in abc_eval:
            st.info(abc_eval['interpretation']['recommendation'])
    
    # 领域得分
    st.write("**各领域得分：**")
    domain_df = pd.DataFrame.from_dict(
        abc_eval['domain_scores'], 
        orient='index', 
        columns=['得分']
    )
    st.dataframe(domain_df, use_container_width=True)


def display_dsm5_results(dsm5_eval):
    """显示DSM-5评估结果"""
    st.write("#### DSM-5标准评估结果")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("核心症状均值", f"{dsm5_eval['core_symptom_average']:.2f}")
        st.metric("严重程度", dsm5_eval['severity_level'])
    
    with col2:
        meets = dsm5_eval['meets_criteria']['overall']
        st.metric("符合诊断标准", "是" if meets else "否")
    
    # 各维度得分
    st.write("**症状维度评分：**")
    scores_df = pd.DataFrame.from_dict(
        dsm5_eval['scores'], 
        orient='index', 
        columns=['评分']
    )
    st.dataframe(scores_df, use_container_width=True)


def display_cars_results(cars_eval):
    """显示CARS量表结果"""
    st.write("#### CARS量表评估结果")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总分", f"{cars_eval['total_score']:.1f}")
        st.metric("严重程度", cars_eval['severity'])
    
    with col2:
        st.metric("临床截断", "阳性" if cars_eval['clinical_cutoff'] else "阴性")
        st.info(cars_eval.get('severity_category', ''))
    
    # 项目得分（显示前10项）
    st.write("**主要项目得分：**")
    items = list(cars_eval['item_scores'].items())[:10]
    items_df = pd.DataFrame(items, columns=['项目', '得分'])
    st.dataframe(items_df, use_container_width=True)


def display_assq_results(assq_eval):
    """显示ASSQ筛查结果"""
    st.write("#### ASSQ筛查评估结果")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总分", assq_eval['total_score'])
        st.metric("筛查结果", assq_eval['screening_result']['screening_result'])
    
    with col2:
        st.metric("风险等级", assq_eval['risk_level'])
        st.metric("阳性筛查", "是" if assq_eval['positive_screen'] else "否")
    
    # 类别得分
    if 'category_scores' in assq_eval:
        st.write("**类别得分：**")
        cat_df = pd.DataFrame.from_dict(
            assq_eval['category_scores'], 
            orient='index', 
            columns=['得分']
        )
        st.dataframe(cat_df, use_container_width=True)