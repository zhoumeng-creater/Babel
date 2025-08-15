"""干预评估页面

实现干预策略的应用和效果对比
"""
import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from typing import Dict, Any, List

from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation.enhanced_unified_evaluator import run_enhanced_experiment
from autism.intervention.intervention_manager import InterventionManager
from autism.intervention.intervention_config import (
    BEHAVIORAL_INTERVENTIONS,
    SOCIAL_INTERVENTIONS,
    COMMUNICATION_INTERVENTIONS,
    SENSORY_INTERVENTIONS,
    COGNITIVE_INTERVENTIONS,
    COMPREHENSIVE_PACKAGES
)


def page_intervention_assessment():
    """干预评估页面"""
    st.header("🎯 干预效果评估")
    st.markdown("模拟干预策略的应用，评估和对比干预前后的行为变化")
    
    # 初始化干预管理器
    if 'intervention_manager' not in st.session_state:
        st.session_state.intervention_manager = InterventionManager()
    
    # 创建选项卡
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏥 单次干预评估",
        "📊 批量干预研究",
        "📈 干预历史分析",
        "📚 干预策略库"
    ])
    
    with tab1:
        single_intervention_assessment()
    
    with tab2:
        batch_intervention_study()
    
    with tab3:
        intervention_history_analysis()
    
    with tab4:
        intervention_strategy_library()


def single_intervention_assessment():
    """单次干预评估"""
    st.subheader("🏥 单次干预评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 1️⃣ 基线评估设置")
        
        # 选择严重程度
        selected_severity = st.selectbox(
            "选择基线严重程度",
            list(UNIFIED_AUTISM_PROFILES.keys()),
            help="选择儿童的初始孤独症严重程度"
        )
        
        # 选择评估场景
        selected_scene = st.selectbox(
            "选择评估场景",
            list(CLINICAL_SCENE_CONFIG.keys())
        )
        
        scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
        selected_activity = st.selectbox("选择活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择触发因素", scene_data['triggers'])
        
        # 选择评估量表
        selected_scales = st.multiselect(
            "选择评估量表",
            ['ABC', 'DSM5', 'CARS', 'ASSQ'],
            default=['ABC', 'DSM5'],
            help="选择用于评估的量表"
        )
    
    with col2:
        st.write("### 2️⃣ 干预策略选择")
        
        # 选择干预类别
        intervention_categories = {
            "行为干预": BEHAVIORAL_INTERVENTIONS,
            "社交干预": SOCIAL_INTERVENTIONS,
            "沟通干预": COMMUNICATION_INTERVENTIONS,
            "感觉干预": SENSORY_INTERVENTIONS,
            "认知干预": COGNITIVE_INTERVENTIONS,
            "综合干预": COMPREHENSIVE_PACKAGES
        }
        
        selected_category = st.selectbox(
            "选择干预类别",
            list(intervention_categories.keys()),
            help="选择干预策略的类别"
        )
        
        # 选择具体策略
        available_strategies = intervention_categories[selected_category]
        selected_strategy = st.selectbox(
            "选择具体策略",
            list(available_strategies.keys())
        )
        
        # 显示策略详情
        strategy_details = available_strategies[selected_strategy]
        with st.expander("策略详情", expanded=True):
            st.write(f"**名称**: {strategy_details['name']}")
            st.write(f"**描述**: {strategy_details['description']}")
            
            if 'target_behaviors' in strategy_details:
                st.write(f"**目标行为**: {', '.join(strategy_details['target_behaviors'])}")
            elif 'target_skills' in strategy_details:
                st.write(f"**目标技能**: {', '.join(strategy_details['target_skills'])}")
            
            if 'evidence_base' in strategy_details:
                st.write(f"**循证基础**: {strategy_details['evidence_base']}")
        
        # 干预参数设置
        st.write("### 干预参数")
        intervention_duration = st.select_slider(
            "干预时长",
            options=["1个月", "3个月", "6个月", "12个月"],
            value="3个月"
        )
        
        intervention_intensity = st.select_slider(
            "干预强度",
            options=["每周10小时", "每周15小时", "每周20小时", "每周25小时", "每周30小时", "每周40小时"],
            value="每周20小时"
        )
    
    # 执行评估
    st.divider()
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔍 生成基线评估", type="primary", use_container_width=True):
            with st.spinner("正在生成基线行为表现..."):
                # 准备基线配置
                baseline_config = {
                    'template': selected_severity,
                    'scene': selected_scene,
                    'activity': selected_activity,
                    'trigger': selected_trigger,
                    'autism_profile': UNIFIED_AUTISM_PROFILES[selected_severity],
                    'experiment_id': f"BASELINE_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'selected_scales': selected_scales
                }
                
                # 生成基线评估
                baseline_result = run_enhanced_experiment(baseline_config)
                
                # 保存到会话状态
                st.session_state.baseline_result = baseline_result
                st.session_state.baseline_config = baseline_config
                
                st.success("✅ 基线评估完成！")
    
    with col_action2:
        if st.button(
            "🎯 应用干预策略",
            type="secondary",
            use_container_width=True,
            disabled='baseline_result' not in st.session_state
        ):
            if 'baseline_result' in st.session_state:
                with st.spinner("正在模拟干预效果..."):
                    # 应用干预
                    intervention_result, intervention_config = st.session_state.intervention_manager.apply_intervention(
                        st.session_state.baseline_config,
                        selected_category,
                        selected_strategy,
                        intervention_duration,
                        intervention_intensity
                    )
                    
                    # 保存结果
                    st.session_state.intervention_result = intervention_result
                    st.session_state.intervention_config = intervention_config
                    
                    st.success("✅ 干预模拟完成！")
    
    with col_action3:
        if st.button(
            "📊 对比分析",
            type="secondary",
            use_container_width=True,
            disabled='intervention_result' not in st.session_state
        ):
            if 'baseline_result' in st.session_state and 'intervention_result' in st.session_state:
                # 生成对比分析
                comparison = st.session_state.intervention_manager.compare_intervention_effects(
                    st.session_state.baseline_result,
                    st.session_state.intervention_result
                )
                st.session_state.intervention_comparison = comparison
    
    # 显示结果
    if 'baseline_result' in st.session_state:
        st.divider()
        st.subheader("📊 评估结果")
        
        # 创建结果选项卡
        result_tabs = st.tabs(["基线评估", "干预后评估", "对比分析", "详细报告"])
        
        with result_tabs[0]:
            display_baseline_results(st.session_state.baseline_result)
        
        with result_tabs[1]:
            if 'intervention_result' in st.session_state:
                display_intervention_results(st.session_state.intervention_result)
            else:
                st.info("请先应用干预策略")
        
        with result_tabs[2]:
            if 'intervention_comparison' in st.session_state:
                display_comparison_results(st.session_state.intervention_comparison)
            else:
                st.info("请先进行对比分析")
        
        with result_tabs[3]:
            if 'intervention_comparison' in st.session_state:
                display_intervention_report()
            else:
                st.info("请完成干预评估流程")


def display_baseline_results(baseline_result: Dict[str, Any]):
    """显示基线评估结果"""
    st.write("### 基线行为表现")
    
    # 显示各量表得分
    metrics_cols = st.columns(4)
    
    if 'abc_evaluation' in baseline_result:
        with metrics_cols[0]:
            st.metric(
                "ABC总分",
                baseline_result['abc_evaluation']['total_score'],
                baseline_result['abc_evaluation']['severity']
            )
    
    if 'dsm5_evaluation' in baseline_result:
        with metrics_cols[1]:
            st.metric(
                "DSM-5核心症状",
                f"{baseline_result['dsm5_evaluation']['core_symptom_average']:.2f}",
                "需要支持" if baseline_result['dsm5_evaluation']['core_symptom_average'] >= 3 else "轻度"
            )
    
    if 'cars_evaluation' in baseline_result:
        with metrics_cols[2]:
            st.metric(
                "CARS总分",
                baseline_result['cars_evaluation']['total_score'],
                baseline_result['cars_evaluation']['clinical_range']
            )
    
    if 'assq_evaluation' in baseline_result:
        with metrics_cols[3]:
            st.metric(
                "ASSQ筛查分",
                baseline_result['assq_evaluation']['total_score'],
                baseline_result['assq_evaluation']['risk_level']
            )
    
    # 显示识别的行为
    if 'abc_evaluation' in baseline_result:
        st.write("#### 识别的主要行为")
        behaviors = baseline_result['abc_evaluation'].get('identified_behaviors', {})
        if behaviors:
            behavior_df = pd.DataFrame(
                [(k, v) for k, v in behaviors.items()],
                columns=['行为类型', '频率']
            )
            st.dataframe(behavior_df, use_container_width=True)
    
    # 显示对话片段
    with st.expander("查看行为对话"):
        st.text(baseline_result.get('dialogue', '无对话记录')[:500] + "...")


def display_intervention_results(intervention_result: Dict[str, Any]):
    """显示干预后的评估结果"""
    st.write("### 干预后行为表现")
    
    # 显示干预信息
    if 'intervention_applied' in intervention_result:
        intervention_info = intervention_result['intervention_applied']
        st.info(
            f"**已应用干预**: {intervention_info['name']} | "
            f"**时长**: {intervention_info['duration']} | "
            f"**强度**: {intervention_info['intensity']}"
        )
    
    # 显示各量表得分
    metrics_cols = st.columns(4)
    
    if 'abc_evaluation' in intervention_result:
        with metrics_cols[0]:
            baseline_score = st.session_state.baseline_result['abc_evaluation']['total_score']
            current_score = intervention_result['abc_evaluation']['total_score']
            change = current_score - baseline_score
            
            st.metric(
                "ABC总分",
                current_score,
                f"{change:+d}",
                delta_color="inverse"
            )
    
    if 'dsm5_evaluation' in intervention_result:
        with metrics_cols[1]:
            baseline_score = st.session_state.baseline_result['dsm5_evaluation']['core_symptom_average']
            current_score = intervention_result['dsm5_evaluation']['core_symptom_average']
            change = current_score - baseline_score
            
            st.metric(
                "DSM-5核心症状",
                f"{current_score:.2f}",
                f"{change:+.2f}",
                delta_color="inverse"
            )
    
    if 'cars_evaluation' in intervention_result:
        with metrics_cols[2]:
            baseline_score = st.session_state.baseline_result['cars_evaluation']['total_score']
            current_score = intervention_result['cars_evaluation']['total_score']
            change = current_score - baseline_score
            
            st.metric(
                "CARS总分",
                current_score,
                f"{change:+d}",
                delta_color="inverse"
            )
    
    if 'assq_evaluation' in intervention_result:
        with metrics_cols[3]:
            baseline_score = st.session_state.baseline_result['assq_evaluation']['total_score']
            current_score = intervention_result['assq_evaluation']['total_score']
            change = current_score - baseline_score
            
            st.metric(
                "ASSQ筛查分",
                current_score,
                f"{change:+d}",
                delta_color="inverse"
            )
    
    # 显示改善的行为
    st.write("#### 行为变化")
    if 'abc_evaluation' in intervention_result and 'abc_evaluation' in st.session_state.baseline_result:
        baseline_behaviors = set(st.session_state.baseline_result['abc_evaluation'].get('identified_behaviors', {}).keys())
        current_behaviors = set(intervention_result['abc_evaluation'].get('identified_behaviors', {}).keys())
        
        reduced_behaviors = baseline_behaviors - current_behaviors
        persisted_behaviors = baseline_behaviors & current_behaviors
        new_behaviors = current_behaviors - baseline_behaviors
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**减少的行为** ✅")
            for behavior in reduced_behaviors:
                st.write(f"- {behavior}")
        
        with col2:
            st.write("**持续的行为** ⚠️")
            for behavior in list(persisted_behaviors)[:5]:
                st.write(f"- {behavior}")
        
        with col3:
            st.write("**新出现的行为** ❓")
            for behavior in new_behaviors:
                st.write(f"- {behavior}")


def display_comparison_results(comparison: Dict[str, Any]):
    """显示对比分析结果"""
    st.write("### 干预效果对比分析")
    
    # 整体效果摘要
    st.write("#### 整体效果")
    summary_cols = st.columns(len(comparison.get('summary', {})))
    for i, (key, value) in enumerate(comparison.get('summary', {}).items()):
        with summary_cols[i]:
            st.metric(key, value)
    
    # 改善领域分析
    st.write("#### 改善分析")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**显著改善领域** 🎯")
        for area in comparison.get('improvement_areas', []):
            st.success(area)
    
    with col2:
        st.write("**无明显变化领域** ➡️")
        for area in comparison.get('no_change_areas', []):
            st.warning(area)
    
    with col3:
        st.write("**需要关注领域** ⚠️")
        for area in comparison.get('deterioration_areas', []):
            st.error(area)
    
    # 临床意义
    st.write("#### 临床意义评估")
    for scale, significance in comparison.get('clinical_significance', {}).items():
        st.info(f"**{scale}**: {significance}")
    
    # 可视化对比
    st.write("#### 量表得分对比图")
    create_intervention_comparison_chart(comparison)
    
    # 建议
    st.write("#### 后续建议")
    for rec in comparison.get('recommendations', []):
        st.write(f"• {rec}")


def create_intervention_comparison_chart(comparison: Dict[str, Any]):
    """创建干预前后对比图表"""
    if 'detailed_changes' not in comparison:
        st.warning("无详细对比数据")
        return
    
    # 准备数据
    scales = []
    baseline_scores = []
    intervention_scores = []
    
    if 'ABC' in comparison['detailed_changes']:
        baseline_result = st.session_state.baseline_result
        intervention_result = st.session_state.intervention_result
        
        if 'abc_evaluation' in baseline_result and 'abc_evaluation' in intervention_result:
            scales.append('ABC总分')
            baseline_scores.append(baseline_result['abc_evaluation']['total_score'])
            intervention_scores.append(intervention_result['abc_evaluation']['total_score'])
    
    if 'DSM5' in comparison['detailed_changes']:
        if 'dsm5_evaluation' in baseline_result and 'dsm5_evaluation' in intervention_result:
            scales.append('DSM-5核心')
            baseline_scores.append(baseline_result['dsm5_evaluation']['core_symptom_average'] * 20)  # 放大显示
            intervention_scores.append(intervention_result['dsm5_evaluation']['core_symptom_average'] * 20)
    
    if 'CARS' in comparison['detailed_changes']:
        if 'cars_evaluation' in baseline_result and 'cars_evaluation' in intervention_result:
            scales.append('CARS总分')
            baseline_scores.append(baseline_result['cars_evaluation']['total_score'])
            intervention_scores.append(intervention_result['cars_evaluation']['total_score'])
    
    if 'ASSQ' in comparison['detailed_changes']:
        if 'assq_evaluation' in baseline_result and 'assq_evaluation' in intervention_result:
            scales.append('ASSQ筛查')
            baseline_scores.append(baseline_result['assq_evaluation']['total_score'])
            intervention_scores.append(intervention_result['assq_evaluation']['total_score'])
    
    # 创建图表
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='基线评估',
        x=scales,
        y=baseline_scores,
        marker_color='lightcoral'
    ))
    
    fig.add_trace(go.Bar(
        name='干预后评估',
        x=scales,
        y=intervention_scores,
        marker_color='lightgreen'
    ))
    
    fig.update_layout(
        title='干预前后量表得分对比',
        xaxis_title='评估量表',
        yaxis_title='得分',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_intervention_report():
    """显示干预报告"""
    st.write("### 干预效果评估报告")
    
    if ('baseline_result' in st.session_state and 
        'intervention_result' in st.session_state and 
        'intervention_comparison' in st.session_state):
        
        # 生成报告
        report = st.session_state.intervention_manager.generate_intervention_report(
            st.session_state.baseline_result,
            st.session_state.intervention_result,
            st.session_state.intervention_comparison
        )
        
        # 显示报告
        st.text_area(
            "详细报告",
            report,
            height=600,
            disabled=True
        )
        
        # 下载按钮
        st.download_button(
            label="📥 下载报告",
            data=report,
            file_name=f"intervention_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


def batch_intervention_study():
    """批量干预研究"""
    st.subheader("📊 批量干预研究")
    st.info("该功能允许批量测试不同干预策略的效果")
    
    # 研究设计
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 研究设计")
        
        # 选择严重程度组
        selected_severities = st.multiselect(
            "选择严重程度组",
            list(UNIFIED_AUTISM_PROFILES.keys()),
            default=list(UNIFIED_AUTISM_PROFILES.keys())[:2]
        )
        
        # 选择干预策略
        all_interventions = []
        for category, strategies in [
            ("行为干预", BEHAVIORAL_INTERVENTIONS),
            ("社交干预", SOCIAL_INTERVENTIONS),
            ("沟通干预", COMMUNICATION_INTERVENTIONS)
        ]:
            for strategy_name in strategies:
                all_interventions.append(f"{category}-{strategy_name}")
        
        selected_interventions = st.multiselect(
            "选择干预策略",
            all_interventions,
            default=all_interventions[:3]
        )
    
    with col2:
        st.write("### 研究参数")
        
        num_subjects_per_group = st.number_input(
            "每组样本数",
            min_value=1,
            max_value=10,
            value=3
        )
        
        intervention_duration = st.select_slider(
            "统一干预时长",
            options=["1个月", "3个月", "6个月"],
            value="3个月"
        )
        
        intervention_intensity = st.select_slider(
            "统一干预强度",
            options=["每周15小时", "每周20小时", "每周25小时"],
            value="每周20小时"
        )
    
    if st.button("🚀 开始批量研究", type="primary"):
        st.warning("批量研究功能正在开发中...")
        # TODO: 实现批量研究逻辑


def intervention_history_analysis():
    """干预历史分析"""
    st.subheader("📈 干预历史分析")
    
    if hasattr(st.session_state.intervention_manager, 'intervention_history'):
        history = st.session_state.intervention_manager.intervention_history
        
        if history:
            st.write(f"共进行了 {len(history)} 次干预评估")
            
            # 显示历史记录
            history_df = pd.DataFrame(history)
            st.dataframe(history_df, use_container_width=True)
            
            # TODO: 添加历史数据分析和可视化
        else:
            st.info("暂无干预历史记录")
    else:
        st.info("暂无干预历史记录")


def intervention_strategy_library():
    """干预策略库"""
    st.subheader("📚 干预策略库")
    st.markdown("基于循证医学的干预策略参考")
    
    # 策略类别选择
    category = st.selectbox(
        "选择策略类别",
        ["行为干预", "社交干预", "沟通干预", "感觉干预", "认知干预", "综合干预包"]
    )
    
    # 获取对应的策略
    strategies = {
        "行为干预": BEHAVIORAL_INTERVENTIONS,
        "社交干预": SOCIAL_INTERVENTIONS,
        "沟通干预": COMMUNICATION_INTERVENTIONS,
        "感觉干预": SENSORY_INTERVENTIONS,
        "认知干预": COGNITIVE_INTERVENTIONS,
        "综合干预包": COMPREHENSIVE_PACKAGES
    }[category]
    
    # 显示策略详情
    for strategy_name, strategy_details in strategies.items():
        with st.expander(f"📖 {strategy_name}"):
            st.write(f"**英文名**: {strategy_details['name']}")
            st.write(f"**描述**: {strategy_details['description']}")
            
            if 'target_behaviors' in strategy_details:
                st.write(f"**目标行为**: {', '.join(strategy_details['target_behaviors'])}")
            elif 'target_skills' in strategy_details:
                st.write(f"**目标技能**: {', '.join(strategy_details['target_skills'])}")
            elif 'target_areas' in strategy_details:
                st.write(f"**目标领域**: {', '.join(strategy_details['target_areas'])}")
            
            if 'implementation' in strategy_details:
                st.write("**实施方法**:")
                for key, value in strategy_details['implementation'].items():
                    st.write(f"  - {key}: {value}")
            
            if 'expected_improvements' in strategy_details:
                st.write("**预期改善**:")
                for area, improvement in strategy_details['expected_improvements'].items():
                    if improvement > 0:
                        st.write(f"  - {area}: +{improvement*100:.0f}%")
                    else:
                        st.write(f"  - {area}: {improvement*100:.0f}%")
            
            if 'evidence_base' in strategy_details:
                st.write(f"**循证基础**: {strategy_details['evidence_base']}")