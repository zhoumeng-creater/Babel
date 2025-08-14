"""
增强版快速评估页面 - 支持量表选择功能
"""
import streamlit as st
import datetime
import pandas as pd

from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation.enhanced_unified_evaluator import (
    run_enhanced_experiment,
    AVAILABLE_SCALES,
    DEFAULT_SCALES,
    get_scale_selection_recommendations
)
from autism.ui_components.result_display import display_dual_assessment_results


def page_quick_assessment_enhanced():
    """增强版快速评估页面 - 支持量表选择"""
    st.header("⚡ 快速临床评估")
    st.markdown("快速生成行为观察并进行多量表评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 评估设置")
        
        # 快速量表选择
        assessment_mode = st.selectbox(
            "评估模式",
            ["标准双量表", "全面四量表", "快速筛查", "自定义选择"],
            help="选择评估模式决定使用哪些量表"
        )
        
        # 根据模式确定量表
        if assessment_mode == "标准双量表":
            selected_scales = ['ABC', 'DSM5']
            st.info("✅ 使用ABC + DSM-5（推荐）")
        elif assessment_mode == "全面四量表":
            selected_scales = ['ABC', 'DSM5', 'CARS', 'ASSQ']
            st.warning("⏱️ 全面评估需要更多时间")
        elif assessment_mode == "快速筛查":
            selected_scales = ['ASSQ']
            st.info("⚡ 仅使用ASSQ快速筛查")
        else:
            # 自定义选择
            st.write("选择量表：")
            col_abc, col_dsm5 = st.columns(2)
            col_cars, col_assq = st.columns(2)
            
            selected_scales = []
            with col_abc:
                if st.checkbox("ABC量表", value=True):
                    selected_scales.append('ABC')
            with col_dsm5:
                if st.checkbox("DSM-5标准", value=True):
                    selected_scales.append('DSM5')
            with col_cars:
                if st.checkbox("CARS量表", value=False):
                    selected_scales.append('CARS')
            with col_assq:
                if st.checkbox("ASSQ筛查", value=False):
                    selected_scales.append('ASSQ')
        
        # 显示选中的量表信息
        if selected_scales:
            total_items = sum(
                AVAILABLE_SCALES[s].get('items', 10) if isinstance(AVAILABLE_SCALES[s].get('items'), int) else 10
                for s in selected_scales
            )
            st.metric("评估项目总数", total_items)
        
        # 严重程度选择
        selected_severity = st.selectbox("选择严重程度", list(UNIFIED_AUTISM_PROFILES.keys()))
        profile = UNIFIED_AUTISM_PROFILES[selected_severity]
        
        # 简要显示特征
        with st.expander("查看特征概要"):
            st.write(f"**{profile['name']}**")
            st.write(f"社交: {profile['social_characteristics'][:50]}...")
            st.write(f"沟通: {profile['communication_characteristics'][:50]}...")
            st.write(f"行为: {profile['behavioral_characteristics'][:50]}...")
        
        # 场景选择
        selected_scene = st.selectbox("选择评估情境", list(CLINICAL_SCENE_CONFIG.keys()))
        scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
        
        # 显示场景信息
        with st.expander("评估情境详情"):
            st.write(f"**目标**: {scene_data['target']}")
            st.write(f"**观察要点**: {', '.join(scene_data['observation_points'])}")
        
        selected_activity = st.selectbox("选择观察活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择触发因素", scene_data['triggers'])
    
    with col2:
        st.subheader("🔬 执行评估")
        
        # 显示将使用的量表
        if selected_scales:
            st.write("**将进行以下评估：**")
            for scale in selected_scales:
                scale_info = AVAILABLE_SCALES[scale]
                st.write(f"• **{scale_info['name']}** - {scale_info['type']}")
        else:
            st.error("请至少选择一个评估量表")
        
        # 年龄输入（用于验证量表适用性）
        child_age = st.number_input(
            "儿童年龄（月）",
            min_value=18,
            max_value=216,
            value=60,
            help="部分量表有年龄要求"
        )
        
        # 检查量表年龄适用性
        age_warnings = check_scale_age_compatibility(selected_scales, child_age)
        if age_warnings:
            for warning in age_warnings:
                st.warning(warning)
        
        if st.button("🩺 开始快速评估", type="primary", use_container_width=True):
            if not selected_scales:
                st.error("请选择至少一个评估量表")
            else:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                
                experiment_config = {
                    'template': selected_severity,
                    'scene': selected_scene,
                    'activity': selected_activity,
                    'trigger': selected_trigger,
                    'autism_profile': profile.copy(),
                    'experiment_id': f"QUICK_{selected_severity[:4]}_{timestamp}",
                    'selected_scales': selected_scales,
                    'child_age': child_age
                }
                
                with st.spinner(f"🤖 正在生成行为观察并进行{len(selected_scales)}项评估..."):
                    result = run_enhanced_experiment(experiment_config)
                
                if 'error' not in result:
                    st.session_state.experiment_records.append(result)
                    
                    st.success(f"✅ 评估完成！ID: {result['experiment_id']}")
                    
                    # 显示评估结果摘要
                    display_assessment_summary(result)
                    
                    # 详细结果
                    with st.expander("查看详细评估结果", expanded=True):
                        display_detailed_results(result)
                    
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
                            st.markdown("*...完整对话已保存*")
                    
                    # 下载选项
                    if st.button("💾 保存评估报告"):
                        save_assessment_report(result)
                        st.success("报告已保存")
                        
                else:
                    st.error(f"❌ 评估失败: {result['error']}")


def check_scale_age_compatibility(selected_scales: list, age_months: int) -> list:
    """检查量表年龄适用性"""
    warnings = []
    age_years = age_months / 12
    
    if 'CARS' in selected_scales and age_years < 2:
        warnings.append("⚠️ CARS量表建议用于2岁以上儿童")
    
    if 'ASSQ' in selected_scales:
        if age_years < 6:
            warnings.append("⚠️ ASSQ筛查主要用于6-17岁儿童，结果可能不够准确")
        elif age_years > 17:
            warnings.append("⚠️ ASSQ筛查主要用于6-17岁儿童")
    
    if 'ABC' in selected_scales and age_months < 18:
        warnings.append("⚠️ ABC量表建议用于18个月以上儿童")
    
    return warnings


def display_assessment_summary(result: dict):
    """显示评估结果摘要"""
    st.subheader("📊 评估结果摘要")
    
    # 创建列显示各量表核心结果
    cols = st.columns(len(result.get('selected_scales', [])))
    
    for idx, scale in enumerate(result.get('selected_scales', [])):
        with cols[idx]:
            if scale == 'ABC' and 'abc_evaluation' in result:
                abc = result['abc_evaluation']
                st.metric(
                    "ABC量表",
                    f"{abc['total_score']}分",
                    abc['severity'],
                    delta_color="inverse" if abc['total_score'] >= 67 else "normal"
                )
            
            elif scale == 'DSM5' and 'dsm5_evaluation' in result:
                dsm5 = result['dsm5_evaluation']
                st.metric(
                    "DSM-5标准",
                    f"{dsm5['core_symptom_average']:.1f}",
                    dsm5['severity_level'],
                    delta_color="inverse" if dsm5['core_symptom_average'] >= 3 else "normal"
                )
            
            elif scale == 'CARS' and 'cars_evaluation' in result:
                cars = result['cars_evaluation']
                st.metric(
                    "CARS量表",
                    f"{cars['total_score']:.1f}分",
                    cars['severity'],
                    delta_color="inverse" if cars['total_score'] >= 30 else "normal"
                )
            
            elif scale == 'ASSQ' and 'assq_evaluation' in result:
                assq = result['assq_evaluation']
                st.metric(
                    "ASSQ筛查",
                    f"{assq['total_score']}分",
                    assq['risk_level'],
                    delta_color="inverse" if assq['total_score'] >= 13 else "normal"
                )
    
    # 显示一致性分析（如果有多个量表）
    if 'scale_comparison' in result and len(result['selected_scales']) > 1:
        st.write("**量表一致性：**")
        comparison = result['scale_comparison']
        if 'consistency' in comparison:
            consistency = comparison['consistency'].get('overall', '未评估')
            if consistency == '完全一致':
                st.success(f"✅ {consistency}")
            elif consistency == '部分一致':
                st.info(f"⚠️ {consistency}")
            else:
                st.warning(f"⚠️ {consistency}")
    
    # 显示综合建议
    if 'evaluation_summary' in result:
        summary = result['evaluation_summary']
        if summary.get('severity_consensus'):
            st.info(f"**综合评估**: {summary['severity_consensus']}")
        
        if summary.get('recommendations'):
            st.write("**建议：**")
            for rec in summary['recommendations'][:3]:  # 只显示前3条建议
                st.write(f"• {rec}")


def display_detailed_results(result: dict):
    """显示详细评估结果"""
    # 使用标签页组织不同量表的结果
    tabs = []
    
    if 'abc_evaluation' in result:
        tabs.append("ABC详情")
    if 'dsm5_evaluation' in result:
        tabs.append("DSM-5详情")
    if 'cars_evaluation' in result:
        tabs.append("CARS详情")
    if 'assq_evaluation' in result:
        tabs.append("ASSQ详情")
    
    if tabs:
        tab_objects = st.tabs(tabs)
        tab_index = 0
        
        # ABC量表详情
        if 'abc_evaluation' in result:
            with tab_objects[tab_index]:
                abc = result['abc_evaluation']
                
                # 领域得分表
                st.write("**领域得分分布：**")
                domain_df = pd.DataFrame.from_dict(
                    abc['domain_scores'], 
                    orient='index', 
                    columns=['得分']
                )
                st.dataframe(
                    domain_df.style.background_gradient(cmap='RdYlGn_r'),
                    use_container_width=True
                )
                
                # 主要行为
                if abc['identified_behaviors']:
                    st.write("**识别的主要行为：**")
                    for domain, behaviors in list(abc['identified_behaviors'].items())[:3]:
                        if behaviors:
                            st.write(f"• {domain}: {', '.join(behaviors[:2])}")
            tab_index += 1
        
        # DSM-5详情
        if 'dsm5_evaluation' in result:
            with tab_objects[tab_index]:
                dsm5 = result['dsm5_evaluation']
                
                # 核心症状
                st.write("**核心症状评分：**")
                core_scores = {
                    '社交互动': dsm5['scores'].get('社交互动质量', 0),
                    '沟通交流': dsm5['scores'].get('沟通交流能力', 0),
                    '刻板行为': dsm5['scores'].get('刻板重复行为', 0)
                }
                core_df = pd.DataFrame.from_dict(
                    core_scores,
                    orient='index',
                    columns=['评分']
                )
                st.dataframe(
                    core_df.style.background_gradient(cmap='RdYlGn_r', vmin=1, vmax=5),
                    use_container_width=True
                )
                
                # 诊断标准
                st.write("**DSM-5诊断标准：**")
                criteria = dsm5['meets_criteria']
                for criterion, met in criteria.items():
                    if met:
                        st.write(f"✅ {criterion}")
                    else:
                        st.write(f"❌ {criterion}")
            tab_index += 1
        
        # CARS详情
        if 'cars_evaluation' in result:
            with tab_objects[tab_index]:
                cars = result['cars_evaluation']
                
                # 显示前5个最高分项目
                st.write("**最需关注的领域（得分最高）：**")
                top_items = sorted(
                    cars['item_scores'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                for item, score in top_items:
                    severity = "轻度" if score < 2 else "中度" if score < 3 else "重度"
                    st.write(f"• {item}: {score:.1f} ({severity})")
                
                # 临床解释
                if 'interpretation' in cars:
                    st.info(cars['interpretation']['clinical_significance'])
            tab_index += 1
        
        # ASSQ详情
        if 'assq_evaluation' in result:
            with tab_objects[tab_index]:
                assq = result['assq_evaluation']
                
                # 类别得分
                st.write("**各领域筛查得分：**")
                category_df = pd.DataFrame.from_dict(
                    assq['category_scores'],
                    orient='index',
                    columns=['得分']
                )
                st.dataframe(
                    category_df.style.background_gradient(cmap='RdYlGn_r'),
                    use_container_width=True
                )
                
                # 筛查结果
                screening = assq['screening_result']
                if screening['screening_result'] == '阳性':
                    st.error(f"筛查结果: {screening['screening_result']}")
                elif screening['screening_result'] == '边缘':
                    st.warning(f"筛查结果: {screening['screening_result']}")
                else:
                    st.success(f"筛查结果: {screening['screening_result']}")
                
                st.write(f"临床意义: {screening['clinical_significance']}")


def save_assessment_report(result: dict):
    """保存评估报告到session_state"""
    # 这里可以扩展为实际的文件保存功能
    if 'saved_reports' not in st.session_state:
        st.session_state.saved_reports = []
    
    report = {
        'id': result['experiment_id'],
        'timestamp': result['timestamp'],
        'scales': result['selected_scales'],
        'summary': result.get('evaluation_summary', {}),
        'data': result
    }
    
    st.session_state.saved_reports.append(report)