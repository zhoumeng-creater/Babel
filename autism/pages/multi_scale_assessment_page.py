"""
多量表评估页面 - 支持自定义量表选择
"""
import streamlit as st
import datetime
import pandas as pd

from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation.enhanced_unified_evaluator import (
    run_enhanced_experiment,
    AVAILABLE_SCALES,
    DEFAULT_SCALES,
    COMPREHENSIVE_SCALES,
    get_scale_selection_recommendations
)


def page_multi_scale_assessment():
    """多量表评估页面 - 支持量表选择"""
    st.header("🔬 多量表综合评估")
    st.markdown("选择适合的评估量表组合，进行个性化的孤独症评估")
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.subheader("📋 量表选择")
        
        # 快速选择预设
        preset_option = st.radio(
            "选择评估方案",
            ["自定义选择", "标准评估", "全面评估", "快速筛查"],
            help="选择预设方案或自定义量表组合"
        )
        
        # 根据预设确定量表
        if preset_option == "标准评估":
            selected_scales = DEFAULT_SCALES
            st.info("✅ 使用ABC量表和DSM-5标准")
        elif preset_option == "全面评估":
            selected_scales = COMPREHENSIVE_SCALES
            st.info("✅ 使用所有4个量表")
        elif preset_option == "快速筛查":
            selected_scales = ['ASSQ', 'ABC']
            st.info("✅ 使用ASSQ和ABC快速筛查")
        else:
            # 自定义选择
            st.write("**选择要使用的量表：**")
            
            scale_selections = {}
            for scale_key, scale_info in AVAILABLE_SCALES.items():
                col_check, col_info = st.columns([1, 3])
                with col_check:
                    # 默认选中ABC和DSM5
                    default_checked = scale_key in DEFAULT_SCALES
                    scale_selections[scale_key] = st.checkbox(
                        scale_info['name'],
                        value=default_checked,
                        key=f"scale_{scale_key}"
                    )
                with col_info:
                    if st.button("ℹ️", key=f"info_{scale_key}"):
                        st.info(f"""
                        **{scale_info['full_name']}**
                        - 类型: {scale_info['type']}
                        - 年龄: {scale_info['age_range']}
                        - 项目: {scale_info['items']}
                        - 时长: {scale_info['time']}
                        """)
            
            selected_scales = [k for k, v in scale_selections.items() if v]
            
            if not selected_scales:
                st.warning("⚠️ 请至少选择一个评估量表")
            else:
                st.success(f"✅ 已选择 {len(selected_scales)} 个量表")
        
        # 显示预计时间
        if selected_scales:
            total_time = estimate_assessment_time(selected_scales)
            st.metric("预计评估时间", f"{total_time} 分钟")
        
        # 年龄和目的输入（用于推荐）
        with st.expander("获取量表推荐"):
            child_age = st.number_input("儿童年龄（月）", min_value=18, max_value=216, value=48)
            assessment_purpose = st.selectbox(
                "评估目的",
                ["diagnostic", "screening", "comprehensive"],
                format_func=lambda x: {
                    "diagnostic": "诊断评估",
                    "screening": "筛查",
                    "comprehensive": "全面评估"
                }[x]
            )
            
            if st.button("获取推荐"):
                recommendations = get_scale_selection_recommendations(
                    age=child_age,
                    purpose=assessment_purpose
                )
                st.info(f"""
                **推荐方案：**
                - 量表: {', '.join([AVAILABLE_SCALES[s]['name'] for s in recommendations['recommended_scales']])}
                - 原因: {recommendations['reason']}
                - 预计时间: {recommendations['estimated_time']}分钟
                """)
    
    with col2:
        st.subheader("🎯 评估配置")
        
        # 选择严重程度模板
        selected_severity = st.selectbox(
            "选择严重程度模板",
            list(UNIFIED_AUTISM_PROFILES.keys()),
            help="选择孤独症严重程度配置"
        )
        
        profile = UNIFIED_AUTISM_PROFILES[selected_severity]
        
        # 显示配置特征
        with st.expander("查看配置特征", expanded=False):
            st.write(f"**配置名称**: {profile['name']}")
            st.write(f"**社交特征**: {profile['social_characteristics']}")
            st.write(f"**沟通特征**: {profile['communication_characteristics']}")
            st.write(f"**行为特征**: {profile['behavioral_characteristics']}")
        
        # 选择评估情境
        selected_scene = st.selectbox("选择评估情境", list(CLINICAL_SCENE_CONFIG.keys()))
        scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
        
        # 显示场景信息
        with st.expander("评估情境详情"):
            st.write(f"**目标**: {scene_data['target']}")
            st.write(f"**观察要点**: {', '.join(scene_data['observation_points'])}")
        
        selected_activity = st.selectbox("选择观察活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择触发因素", scene_data['triggers'])
        
        # 量表对比选项
        st.write("**评估选项**")
        compare_scales = st.checkbox("生成量表对比分析", value=True)
        save_individual = st.checkbox("保存各量表详细结果", value=True)
    
    with col3:
        st.subheader("🚀 执行评估")
        
        if not selected_scales:
            st.error("请选择至少一个评估量表")
        else:
            # 显示将要使用的量表
            st.write("**将使用以下量表：**")
            for scale in selected_scales:
                st.write(f"• {AVAILABLE_SCALES[scale]['name']}")
            
            if st.button("🩺 开始多量表评估", type="primary", use_container_width=True):
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                
                experiment_config = {
                    'template': selected_severity,
                    'scene': selected_scene,
                    'activity': selected_activity,
                    'trigger': selected_trigger,
                    'autism_profile': profile.copy(),
                    'experiment_id': f"MULTI_{selected_severity[:4]}_{timestamp}",
                    'selected_scales': selected_scales  # 传递选择的量表
                }
                
                with st.spinner(f"🤖 正在进行{len(selected_scales)}个量表评估..."):
                    result = run_enhanced_experiment(experiment_config)
                
                if 'error' not in result:
                    st.session_state.experiment_records.append(result)
                    st.success(f"✅ 多量表评估完成！ID: {result['experiment_id']}")
                    
                    # 显示评估结果
                    display_multi_scale_results(result, compare_scales)
                    
                    # 对话预览
                    with st.expander("查看行为观察对话", expanded=False):
                        dialogue_lines = result['dialogue'].split('\n')[:15]
                        for line in dialogue_lines:
                            if ':' in line and line.strip():
                                if '孤独症儿童' in line:
                                    st.markdown(f"🧒 {line}")
                                else:
                                    st.markdown(f"👤 {line}")
                        
                        if len(result['dialogue'].split('\n')) > 15:
                            st.markdown("*...查看完整记录请前往'评估记录管理'*")
                else:
                    st.error(f"❌ 评估失败: {result['error']}")


def estimate_assessment_time(selected_scales: list) -> int:
    """估算评估时间"""
    time_mapping = {
        'ABC': 15,
        'DSM5': 25,
        'CARS': 25,
        'ASSQ': 10
    }
    
    total_time = sum(time_mapping.get(scale, 15) for scale in selected_scales)
    # 如果多个量表，减少一些时间（因为共享对话生成）
    if len(selected_scales) > 1:
        total_time = int(total_time * 0.8)
    
    return total_time


def display_multi_scale_results(result: dict, show_comparison: bool = True):
    """显示多量表评估结果"""
    st.subheader("📊 评估结果")
    
    # 创建标签页显示各量表结果
    scale_tabs = []
    if 'abc_evaluation' in result:
        scale_tabs.append("ABC量表")
    if 'dsm5_evaluation' in result:
        scale_tabs.append("DSM-5标准")
    if 'cars_evaluation' in result:
        scale_tabs.append("CARS量表")
    if 'assq_evaluation' in result:
        scale_tabs.append("ASSQ筛查")
    
    if show_comparison and 'scale_comparison' in result:
        scale_tabs.append("量表对比")
    
    tabs = st.tabs(scale_tabs)
    tab_index = 0
    
    # ABC量表结果
    if 'abc_evaluation' in result:
        with tabs[tab_index]:
            abc = result['abc_evaluation']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总分", abc['total_score'])
            with col2:
                st.metric("严重程度", abc['severity'])
            with col3:
                st.metric("临床意义", "阳性" if abc['clinical_range'] else "阴性")
            
            # 领域得分
            st.write("**领域得分：**")
            domain_df = pd.DataFrame.from_dict(abc['domain_scores'], orient='index', columns=['得分'])
            st.dataframe(domain_df, use_container_width=True)
            
            # 识别的行为
            if abc['identified_behaviors']:
                st.write("**识别的主要行为：**")
                for domain, behaviors in abc['identified_behaviors'].items():
                    if behaviors:
                        st.write(f"• {domain}: {', '.join(behaviors[:3])}")
        tab_index += 1
    
    # DSM-5标准结果
    if 'dsm5_evaluation' in result:
        with tabs[tab_index]:
            dsm5 = result['dsm5_evaluation']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("核心症状", f"{dsm5['core_symptom_average']:.2f}")
            with col2:
                st.metric("严重程度", dsm5['severity_level'])
            with col3:
                criteria_met = dsm5['meets_criteria']['overall']
                st.metric("符合标准", "是" if criteria_met else "否")
            
            # 各维度得分
            st.write("**症状维度评分：**")
            scores_df = pd.DataFrame.from_dict(dsm5['scores'], orient='index', columns=['评分'])
            st.dataframe(scores_df, use_container_width=True)
            
            # 临床观察
            if dsm5['clinical_observations']:
                st.write("**临床观察要点：**")
                for category, observations in dsm5['clinical_observations'].items():
                    if observations:
                        st.write(f"• {category}: {', '.join(observations[:3])}")
        tab_index += 1
    
    # CARS量表结果
    if 'cars_evaluation' in result:
        with tabs[tab_index]:
            cars = result['cars_evaluation']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总分", f"{cars['total_score']:.1f}")
            with col2:
                st.metric("严重程度", cars['severity'])
            with col3:
                st.metric("临床意义", "阳性" if cars['clinical_cutoff'] else "阴性")
            
            # 项目得分热力图
            st.write("**CARS各项目评分：**")
            items_df = pd.DataFrame.from_dict(cars['item_scores'], orient='index', columns=['评分'])
            items_df = items_df.sort_values('评分', ascending=False)
            st.dataframe(
                items_df.style.background_gradient(cmap='RdYlGn_r', vmin=1, vmax=4),
                use_container_width=True
            )
            
            # 解释和建议
            if 'interpretation' in cars:
                interp = cars['interpretation']
                st.info(f"**临床意义**: {interp['clinical_significance']}")
                if interp['recommendations']:
                    st.write("**建议：**")
                    for rec in interp['recommendations']:
                        st.write(f"• {rec}")
        tab_index += 1
    
    # ASSQ筛查结果
    if 'assq_evaluation' in result:
        with tabs[tab_index]:
            assq = result['assq_evaluation']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总分", assq['total_score'])
            with col2:
                st.metric("筛查结果", assq['screening_result']['screening_result'])
            with col3:
                st.metric("风险等级", assq['risk_level'])
            
            # 类别得分
            st.write("**各类别得分：**")
            category_df = pd.DataFrame.from_dict(assq['category_scores'], orient='index', columns=['得分'])
            st.dataframe(category_df, use_container_width=True)
            
            # 类别解释
            if 'category_interpretation' in assq:
                st.write("**类别评估：**")
                for category, interpretation in assq['category_interpretation'].items():
                    st.write(f"• {category}: {interpretation}")
            
            # 筛查建议
            screening = assq['screening_result']
            if screening['recommendations']:
                st.write("**筛查建议：**")
                for rec in screening['recommendations']:
                    st.write(f"• {rec}")
        tab_index += 1
    
    # 量表对比
    if show_comparison and 'scale_comparison' in result:
        with tabs[tab_index]:
            comparison = result['scale_comparison']
            
            # 一致性分析
            if 'consistency' in comparison and comparison['consistency']:
                st.write("**量表一致性：**")
                st.info(f"整体一致性: {comparison['consistency'].get('overall', '未评估')}")
            
            # 严重程度对比
            if 'severity_agreement' in comparison and comparison['severity_agreement']:
                st.write("**各量表严重程度判断：**")
                severity_df = pd.DataFrame.from_dict(
                    comparison['severity_agreement'], 
                    orient='index', 
                    columns=['严重程度']
                )
                st.dataframe(severity_df, use_container_width=True)
            
            # 关键发现
            if 'key_findings' in comparison and comparison['key_findings']:
                st.write("**综合发现：**")
                for finding in comparison['key_findings']:
                    st.write(f"• {finding}")
            
            # 评估摘要
            if 'evaluation_summary' in result:
                summary = result['evaluation_summary']
                st.write("**评估摘要：**")
                if summary['severity_consensus']:
                    st.info(f"**共识结果**: {summary['severity_consensus']}")
                if summary['recommendations']:
                    st.write("**综合建议：**")
                    for rec in summary['recommendations']:
                        st.write(f"• {rec}")