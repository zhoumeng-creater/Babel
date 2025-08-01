"""孤独症平台UI页面组件 - 支持统一生成、双标准评估"""
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

from common.batch_processor import run_batch_processing
from common.ui_components import display_metric_with_color
from .config import (
    UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG, 
    ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS,
    DSM5_EVALUATION_METRICS
)
from .evaluator import run_single_experiment, generate_experiment_batch
from .analyzer import (
    generate_clinical_analysis, 
    extract_behavior_specific_samples,
    calculate_sample_similarity,
    find_similar_samples,
    analyze_behavior_associations,
    get_behavior_summary_stats,
    get_behavior_summary_stats
)


def page_quick_assessment():
    """快速评估页面 - 统一生成，双标准评估"""
    st.header("🩺 快速临床评估")
    st.markdown("生成孤独症儿童行为表现，同时进行ABC和DSM-5双重评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 选择评估对象")
        
        # 使用统一的严重程度配置
        selected_severity = st.selectbox("选择严重程度", list(UNIFIED_AUTISM_PROFILES.keys()))
        profile = UNIFIED_AUTISM_PROFILES[selected_severity]
        
        # 显示统一特征
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
            
            if len(profile['behavioral_examples']) > 3:
                st.write(f"...还有{len(profile['behavioral_examples'])-3}个行为示例")
        
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
        
        st.info("💡 将生成一次行为观察，同时使用ABC量表和DSM-5标准进行评估")
        
        if st.button("🩺 开始双重评估", type="primary", use_container_width=True):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            
            experiment_config = {
                'template': selected_severity,
                'scene': selected_scene,
                'activity': selected_activity,
                'trigger': selected_trigger,
                'autism_profile': profile.copy(),
                'experiment_id': f"UNI_{selected_severity[:4]}_{timestamp}"
            }
            
            with st.spinner("🤖 正在生成临床评估对话..."):
                result = run_single_experiment(experiment_config)
            
            if 'error' not in result:
                st.session_state.experiment_records.append(result)
                
                st.success(f"✅ 双重评估完成！ID: {result['experiment_id']}")
                
                # 显示评估结果
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
        
        else:
            st.error("请先选择严重程度和评估情境")


def page_custom_assessment():
    """个性化评估设计页面 - 统一生成，双标准评估"""
    st.header("⚙️ 个性化评估设计")
    st.markdown("自定义孤独症特征，生成行为表现并进行双重评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎭 评估情境设置")
        selected_scene = st.selectbox("选择评估情境", list(CLINICAL_SCENE_CONFIG.keys()))
        scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
        
        st.info(f"**评估目标**: {scene_data['target']}")
        
        # 显示观察要点
        with st.expander("临床观察要点"):
            for point in scene_data['observation_points']:
                st.write(f"• {point}")
        
        selected_activity = st.selectbox("选择观察活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择触发因素", scene_data['triggers'])
    
    with col2:
        st.subheader("👤 特征配置")
        
        template_base = st.selectbox("基于模板", ["自定义"] + list(UNIFIED_AUTISM_PROFILES.keys()))
        
        if template_base != "自定义":
            base_profile = UNIFIED_AUTISM_PROFILES[template_base].copy()
            st.info(f"基于: {base_profile['name']}")
        else:
            base_profile = {
                'name': "自定义配置",
                'social_characteristics': "社交能力受限，倾向独处",
                'communication_characteristics': "语言发展迟缓，理解困难",
                'behavioral_characteristics': "有重复刻板行为，兴趣狭窄",
                'cognitive_characteristics': "认知发展不均衡",
                'emotional_characteristics': "情绪调节困难",
                'daily_living': "需要支持和引导",
                'overall_functioning': "need_support",
                'behavioral_examples': ["重复某些动作", "对变化敏感", "语言使用特殊"]
            }
        
        st.write("**自定义特征描述**")
        
        social_char = st.text_area(
            "社交特征", 
            base_profile['social_characteristics'],
            height=60,
            help="描述社交互动的特点"
        )
        
        comm_char = st.text_area(
            "沟通特征", 
            base_profile['communication_characteristics'],
            height=60,
            help="描述语言和沟通能力"
        )
        
        behavior_char = st.text_area(
            "行为特征", 
            base_profile['behavioral_characteristics'],
            height=60,
            help="描述重复刻板行为和兴趣"
        )
        
        cognitive_char = st.text_area(
            "认知特征", 
            base_profile['cognitive_characteristics'],
            height=60,
            help="描述认知和学习能力"
        )
        
        emotional_char = st.text_area(
            "情绪特征", 
            base_profile['emotional_characteristics'],
            height=60,
            help="描述情绪表达和调节"
        )
        
        daily_living = st.text_area(
            "日常生活", 
            base_profile['daily_living'],
            height=60,
            help="描述自理和适应能力"
        )
        
        # 功能水平选择
        functioning_level = st.select_slider(
            "整体功能水平",
            options=['mainstream_with_support', 'need_support', 'need_substantial_support', 'need_very_substantial_support'],
            value=base_profile.get('overall_functioning', 'need_support'),
            format_func=lambda x: {
                'mainstream_with_support': '主流+支持',
                'need_support': '需要支持', 
                'need_substantial_support': '需要大量支持',
                'need_very_substantial_support': '需要非常大量支持'
            }[x]
        )
        
        # 行为示例
        st.write("**典型行为示例** (每行一个)")
        behavior_examples_text = st.text_area(
            "行为示例",
            '\n'.join(base_profile.get('behavioral_examples', [])),
            height=100,
            help="输入具体的行为表现示例"
        )
        
        behavior_examples = [ex.strip() for ex in behavior_examples_text.split('\n') if ex.strip()]
        
        # 构建自定义配置
        custom_profile = {
            'name': f"自定义 - {template_base}" if template_base != "自定义" else "完全自定义",
            'social_characteristics': social_char,
            'communication_characteristics': comm_char,
            'behavioral_characteristics': behavior_char,
            'cognitive_characteristics': cognitive_char,
            'emotional_characteristics': emotional_char,
            'daily_living': daily_living,
            'overall_functioning': functioning_level,
            'behavioral_examples': behavior_examples
        }
    
    # 执行个性化评估
    st.subheader("🔬 执行个性化双重评估")
    
    if st.button("🩺 开始个性化评估", type="primary", use_container_width=True):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        
        experiment_config = {
            'template': template_base if template_base != "自定义" else "个性化配置",
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'autism_profile': custom_profile,
            'experiment_id': f"CUSTOM_{timestamp}"
        }
        
        with st.spinner("🤖 正在生成个性化评估..."):
            result = run_single_experiment(experiment_config)
        
        if 'error' not in result:
            st.session_state.experiment_records.append(result)
            
            st.success(f"✅ 个性化双重评估完成！ID: {result['experiment_id']}")
            
            # 显示详细评估结果
            st.subheader("📊 个性化评估详细结果")
            
            # 创建标签页显示两种评估
            tab_abc, tab_dsm5, tab_compare = st.tabs(["ABC量表评估", "DSM-5标准评估", "对比分析"])
            
            with tab_abc:
                display_abc_detailed_results(result['abc_evaluation'])
            
            with tab_dsm5:
                display_dsm5_detailed_results(result['dsm5_evaluation'])
            
            with tab_compare:
                display_assessment_comparison(result)
                
        else:
            st.error(f"❌ 评估失败: {result['error']}")
    
    # 保存配置
    if st.button("💾 保存评估配置", use_container_width=True):
        st.session_state.custom_autism_profile = custom_profile
        st.session_state.custom_scene_config = {
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger
        }
        st.success("✅ 个性化配置已保存！")


def page_data_analysis():
    """数据分析页面 - 支持双重评估数据分析"""
    st.header("📈 临床数据分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行临床评估")
        st.stop()
    
    # 生成分析
    analysis = generate_clinical_analysis(records)
    
    # 数据概览
    st.subheader("🏥 评估数据概览")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("评估总数", len(records))
    with col2:
        st.metric("评估情境数", len(set(r['scene'] for r in records)))
    with col3:
        # 计算平均ABC总分
        avg_abc = np.mean([r['abc_evaluation']['total_score'] for r in records])
        st.metric("平均ABC总分", f"{avg_abc:.1f}")
    with col4:
        # 计算平均DSM-5核心症状
        avg_dsm5 = np.mean([r['dsm5_evaluation']['core_symptom_average'] for r in records])
        st.metric("平均DSM-5核心", f"{avg_dsm5:.2f}")
    
    # 评估一致性分析
    st.subheader("🔄 ABC与DSM-5评估一致性分析")
    
    consistency_results = get_behavior_summary_stats(records)
    
    col_cons1, col_cons2, col_cons3 = st.columns(3)
    with col_cons1:
        st.metric("Pearson相关系数", f"{consistency_results['correlation']:.3f}")
        st.write(f"p值: {consistency_results['p_value']:.4f}")
    with col_cons2:
        st.metric("一致性比例", f"{consistency_results['agreement_rate']:.1f}%")
        st.write("(严重程度判断一致)")
    with col_cons3:
        st.metric("评分差异", f"{consistency_results['mean_difference']:.2f}")
        st.write("(标准化后)")
    
    # 散点图显示相关性
    fig_scatter = create_correlation_scatter(records)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 分别显示两种评估的结果
    tab1, tab2, tab3 = st.tabs(["ABC量表分析", "DSM-5标准分析", "综合对比"])
    
    with tab1:
        display_abc_analysis(records, analysis)
    
    with tab2:
        display_dsm5_analysis(records, analysis)
    
    with tab3:
        display_comprehensive_comparison(records, analysis)
    
    # 统计显著性检验
    if len(records) > 10:
        st.subheader("📐 统计学分析")
        display_statistical_analysis(records)


def page_records_management():
    """评估记录管理页面 - 支持双重评估数据"""
    st.header("📚 评估记录管理")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.info("📝 暂无评估记录")
        st.stop()
    
    st.subheader(f"📊 共有 {len(records)} 条评估记录")
    
    # 高级筛选选项
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        severity_filter = st.selectbox(
            "按严重程度筛选",
            ["全部"] + list(set([r.get('template', '自定义') for r in records]))
        )
    
    with col_filter2:
        context_filter = st.selectbox(
            "按评估情境筛选",
            ["全部"] + list(set([r['scene'] for r in records]))
        )
    
    with col_filter3:
        # 基于ABC或DSM-5的筛选
        score_filter = st.selectbox(
            "按评分筛选",
            ["全部", "ABC高分(≥67)", "ABC低分(<53)", "DSM5重度(≥3.5)", "DSM5轻度(<2.5)"]
        )
    
    with col_filter4:
        sort_by = st.selectbox(
            "排序方式", 
            ["时间倒序", "时间正序", "ABC总分", "DSM-5核心症状", "一致性"]
        )
    
    # 应用筛选
    filtered_records = records.copy()
    
    if severity_filter != "全部":
        filtered_records = [r for r in filtered_records if r.get('template', '自定义') == severity_filter]
    
    if context_filter != "全部":
        filtered_records = [r for r in filtered_records if r['scene'] == context_filter]
    
    if score_filter != "全部":
        if score_filter == "ABC高分(≥67)":
            filtered_records = [r for r in filtered_records if r['abc_evaluation']['total_score'] >= 67]
        elif score_filter == "ABC低分(<53)":
            filtered_records = [r for r in filtered_records if r['abc_evaluation']['total_score'] < 53]
        elif score_filter == "DSM5重度(≥3.5)":
            filtered_records = [r for r in filtered_records if r['dsm5_evaluation']['core_symptom_average'] >= 3.5]
        elif score_filter == "DSM5轻度(<2.5)":
            filtered_records = [r for r in filtered_records if r['dsm5_evaluation']['core_symptom_average'] < 2.5]
    
    # 应用排序
    if sort_by == "时间正序":
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'])
    elif sort_by == "ABC总分":
        filtered_records = sorted(filtered_records, key=lambda x: x['abc_evaluation']['total_score'], reverse=True)
    elif sort_by == "DSM-5核心症状":
        filtered_records = sorted(filtered_records, key=lambda x: x['dsm5_evaluation']['core_symptom_average'], reverse=True)
    elif sort_by == "一致性":
        # 按ABC和DSM-5评估的一致性排序
        def get_consistency(record):
            abc_severe = record['abc_evaluation']['total_score'] >= 67
            dsm5_severe = record['dsm5_evaluation']['core_symptom_average'] >= 3.5
            return 1 if abc_severe == dsm5_severe else 0
        filtered_records = sorted(filtered_records, key=get_consistency, reverse=True)
    else:  # 时间倒序
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
    
    st.write(f"筛选后记录数: {len(filtered_records)}")
    
    # 记录列表显示
    for i, record in enumerate(filtered_records):
        
        # 获取双重评估结果
        abc_total = record['abc_evaluation']['total_score']
        abc_severity = record['abc_evaluation']['severity']
        dsm5_core = record['dsm5_evaluation']['core_symptom_average']
        
        # 判断一致性
        abc_severe = abc_total >= 67
        dsm5_severe = dsm5_core >= 3.5
        consistency = "✅" if abc_severe == dsm5_severe else "⚠️"
        
        # 显示标题
        display_title = (f"{consistency} {record['experiment_id']} - "
                        f"ABC:{abc_total} | DSM5:{dsm5_core:.2f} - "
                        f"{record['timestamp'].strftime('%m-%d %H:%M')}")
        
        with st.expander(display_title):
            
            # 基本信息
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📋 评估基本信息:**")
                st.write(f"• 配置类型: {record.get('template', '自定义')}")
                st.write(f"• 评估情境: {record['scene']}")
                st.write(f"• 观察活动: {record.get('activity', '未指定')}")
                st.write(f"• 触发因素: {record.get('trigger', '未指定')}")
                st.write(f"• 评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.write("**📊 ABC量表评估:**")
                st.write(f"• 总分: {abc_total}")
                st.write(f"• 严重程度: {abc_severity}")
                st.write("• 各领域得分:")
                for domain, score in record['abc_evaluation']['domain_scores'].items():
                    st.write(f"  - {domain}: {score}")
            
            with col3:
                st.write("**🧠 DSM-5标准评估:**")
                st.write(f"• 核心症状均值: {dsm5_core:.2f}")
                st.write("• 各维度评分:")
                for metric, score in record['dsm5_evaluation']['scores'].items():
                    if metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']:
                        st.write(f"  - {metric}: {score:.2f} ⭐")
                    else:
                        st.write(f"  - {metric}: {score:.2f}")
            
            # 对话记录
            st.write("**💬 行为观察对话记录:**")
            dialogue_text = record['dialogue']
            
            unique_key = f"dialogue_{i}_{record['experiment_id']}_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}"
            st.text_area("", dialogue_text, height=200, key=unique_key)
            
            # 快速操作按钮
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)  
            
            with col_btn1:
                if st.button(f"📋 生成报告", key=f"report_{record['experiment_id']}"):
                    st.info("双重评估报告生成功能开发中...")
            
            with col_btn2:
                if st.button(f"📈 详细分析", key=f"analysis_{record['experiment_id']}"):
                    display_single_record_analysis(record)
            
            with col_btn3:
                if st.button(f"🔄 重复评估", key=f"repeat_{record['experiment_id']}"):
                    st.info("重复评估功能开发中...")
            
            with col_btn4:
                if st.button(f"🔍 查找相似", key=f"similar_{record['experiment_id']}"):
                    with st.spinner("正在查找相似样本..."):
                        similar_samples = find_similar_samples(
                            record, 
                            st.session_state.experiment_records,
                            threshold=0.7,
                            max_results=5
                        )
                    
                    if similar_samples:
                        st.write("**相似样本：**")
                        for idx, item in enumerate(similar_samples, 1):
                            similar_record = item['record']
                            st.write(f"{idx}. {similar_record['experiment_id']} - "
                                   f"相似度: {item['similarity']:.2%}")
                    else:
                        st.info("未找到相似度超过70%的样本")


# ==================== 辅助函数 ====================

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
                for behavior, stats in behavior_stats['most_common'][:10]:
                    st.write(f"• {behavior}: {stats['count']}次 ({stats['percentage']:.1f}%)")


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