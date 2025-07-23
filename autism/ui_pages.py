"""孤独症平台UI页面组件 - 基于ABC量表"""
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

from common.batch_processor import run_batch_processing
from common.ui_components import display_metric_with_color
from .config import ABC_SEVERITY_PROFILES, CLINICAL_SCENE_CONFIG, ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS
from .evaluator import run_single_experiment, generate_experiment_batch
from .analyzer import (
    generate_clinical_analysis, 
    # 新增导入
    extract_behavior_specific_samples,
    calculate_sample_similarity,
    find_similar_samples,
    analyze_behavior_associations,
    get_behavior_summary_stats
)

def page_quick_assessment():
    """快速ABC评估页面"""
    st.header("🩺 快速ABC评估")
    st.markdown("使用ABC孤独症行为量表进行快速临床评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 选择评估对象")
        selected_severity = st.selectbox("严重程度分级", list(ABC_SEVERITY_PROFILES.keys()))
        
        profile = ABC_SEVERITY_PROFILES[selected_severity]
        
        # 显示ABC特征
        with st.expander("查看ABC行为特征配置", expanded=True):
            st.write(f"**严重程度**: {profile['description']}")
            st.write(f"**ABC总分范围**: {profile['total_score_range'][0]}-{profile['total_score_range'][1]}")
            st.write(f"**感觉异常程度**: {profile['sensory_abnormal']*100:.0f}%")
            st.write(f"**交往障碍程度**: {profile['social_impairment']*100:.0f}%")
            st.write(f"**躯体运动刻板**: {profile['motor_stereotypy']*100:.0f}%")
            st.write(f"**语言缺陷程度**: {profile['language_deficit']*100:.0f}%")
            st.write(f"**自理缺陷程度**: {profile['self_care_deficit']*100:.0f}%")
            st.write(f"**异常行为频率**: {profile['behavior_frequency']*100:.0f}%")
        
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
        
        if st.button("🩺 开始ABC评估", type="primary", use_container_width=True):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            experiment_config = {
                'template': selected_severity,
                'scene': selected_scene,
                'activity': selected_activity,
                'trigger': selected_trigger,
                'autism_profile': profile.copy(),
                'experiment_id': f"ABC_{selected_severity[:4]}_{timestamp}"
            }
            
            with st.spinner("🤖 正在生成ABC评估对话..."):
                result = run_single_experiment(experiment_config)
            
            if 'error' not in result:
                st.session_state.experiment_records.append(result)
                
                st.success(f"✅ ABC评估完成！ID: {result['experiment_id']}")
                
                # 显示评估结果
                st.subheader("📊 ABC评估结果")
                
                # 显示ABC总分
                total_score = result['abc_total_score']
                severity = result['abc_severity']
                
                if total_score >= 67:
                    st.error(f"**ABC总分: {total_score}** - {severity}")
                elif total_score >= 53:
                    st.warning(f"**ABC总分: {total_score}** - {severity}")
                elif total_score >= 40:
                    st.info(f"**ABC总分: {total_score}** - {severity}")
                else:
                    st.success(f"**ABC总分: {total_score}** - {severity}")
                
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    st.write("**各领域得分**:")
                    for metric, score in result['evaluation_scores'].items():
                        max_score = ABC_EVALUATION_METRICS[metric]['max_score']
                        percentage = score / max_score * 100
                        
                        if percentage >= 60:
                            st.error(f"{metric}: {score}/{max_score} ({percentage:.0f}%)")
                        elif percentage >= 40:
                            st.warning(f"{metric}: {score}/{max_score} ({percentage:.0f}%)")
                        else:
                            st.success(f"{metric}: {score}/{max_score} ({percentage:.0f}%)")
                
                with col_result2:
                    st.write("**识别到的行为**:")
                    if 'identified_behaviors' in result:
                        for domain, behaviors in result['identified_behaviors'].items():
                            if behaviors:
                                st.write(f"**{domain}**:")
                                for behavior in behaviors[:3]:  # 最多显示3个
                                    st.write(f"• {behavior}")
                    
                    st.write("**对话预览**:")
                    dialogue_lines = result['dialogue'].split('\n')[:8]
                    for line in dialogue_lines:
                        if ':' in line and line.strip():
                            if '孤独症儿童' in line:
                                st.markdown(f"🧒 {line}")
                            else:
                                st.markdown(f"👤 {line}")
                    
                    if len(result['dialogue'].split('\n')) > 8:
                        st.markdown("*...查看完整记录请前往'评估记录管理'*")
                
                # 显示临床建议
                st.subheader("💡 临床建议")
                
                if total_score >= 67:
                    st.error("🚨 建议：ABC评分显示明确孤独症表现，需要综合干预治疗")
                elif total_score >= 53:
                    st.warning("⚠️ 建议：轻度孤独症表现，建议早期干预和行为训练")
                elif total_score >= 40:
                    st.info("ℹ️ 建议：边缘状态，需要密切观察和定期评估")
                else:
                    st.success("✅ 建议：未达孤独症标准，但仍需关注个别领域表现")
                    
            else:
                st.error(f"❌ 评估失败: {result['error']}")


def page_batch_research():
    """批量ABC研究页面"""
    st.header("🔬 批量ABC研究")
    st.markdown("使用ABC量表进行多组对照研究")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        research_scale = st.radio(
            "选择研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究"],
            help="根据研究需要选择合适的样本规模"
        )
        
        if research_scale == "试点研究（推荐）":
            default_severities = list(ABC_SEVERITY_PROFILES.keys())[:2]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            st.info("🚀 试点研究：验证ABC评估效果，约需5-8分钟")
        elif research_scale == "标准研究":
            default_severities = list(ABC_SEVERITY_PROFILES.keys())[:3]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            st.info("⏳ 标准研究：获得可靠统计数据，约需20-30分钟")
        else:
            default_severities = list(ABC_SEVERITY_PROFILES.keys())
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())
            default_repeats = 2
            st.warning("⏰ 大样本研究：完整ABC研究数据，约需60-90分钟")
        
        selected_severities = st.multiselect(
            "选择严重程度组", 
            list(ABC_SEVERITY_PROFILES.keys()),
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
            severity_dict = {k: ABC_SEVERITY_PROFILES[k] for k in selected_severities}
            context_dict = {k: CLINICAL_SCENE_CONFIG[k] for k in selected_contexts}
            
            experiments = generate_experiment_batch(
                severity_dict, 
                context_dict, 
                repeats_per_combo
            )
            
            st.info(f"📊 将生成 {len(experiments)} 个ABC评估")
            
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
        
        if 'abc_batch_ready' not in st.session_state:
            st.session_state.abc_batch_ready = False
        if 'abc_batch_running' not in st.session_state:
            st.session_state.abc_batch_running = False
        
        if selected_severities and selected_contexts:
            estimated_minutes = len(experiments) * 25 / 60
            st.info(f"📊 评估数量: {len(experiments)}")
            st.info(f"⏰ 预计时间: {estimated_minutes:.1f} 分钟")
            
            if not st.session_state.abc_batch_ready and not st.session_state.abc_batch_running:
                if st.button("⚡ 准备开始研究", use_container_width=True):
                    st.session_state.abc_batch_ready = True
                    st.rerun()
            
            elif st.session_state.abc_batch_ready and not st.session_state.abc_batch_running:
                st.warning("⏰ **重要**: 由于API限制，批量研究需要较长时间")
                st.info("💡 确认后将立即开始，请保持网络稳定")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("❌ 取消", use_container_width=True):
                        st.session_state.abc_batch_ready = False
                        st.rerun()
                
                with col_btn2:
                    if st.button("✅ 开始研究", type="primary", use_container_width=True):
                        st.session_state.abc_batch_running = True
                        st.session_state.abc_batch_ready = False
                        st.rerun()
            
            elif st.session_state.abc_batch_running:
                st.success("🔬 ABC研究进行中...")
                
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
                        "ABC实验"
                    )
                    
                    successful_results = [r for r in results if 'error' not in r]
                    failed_results = [r for r in results if 'error' in r]
                    
                    st.session_state.experiment_records.extend(successful_results)
                    st.session_state.current_batch_results = successful_results
                    
                    with result_container:
                        st.success(f"✅ ABC研究完成！")
                        st.write(f"**成功评估**: {len(successful_results)} 个")
                        
                        if failed_results:
                            st.error(f"**失败评估**: {len(failed_results)} 个")
                        
                        if successful_results:
                            st.subheader("📈 研究结果概览")
                            
                            # 按严重程度统计
                            severity_stats = {}
                            for result in successful_results:
                                severity = result['template']
                                if severity not in severity_stats:
                                    severity_stats[severity] = []
                                
                                severity_stats[severity].append(result['abc_total_score'])
                            
                            stats_df = pd.DataFrame([
                                {
                                    '严重程度': severity,
                                    '样本数': len(scores),
                                    'ABC均分': f"{np.mean(scores):.1f}",
                                    '标准差': f"{np.std(scores):.1f}",
                                    '95%置信区间': f"{np.mean(scores) - 1.96*np.std(scores)/np.sqrt(len(scores)):.1f}-{np.mean(scores) + 1.96*np.std(scores)/np.sqrt(len(scores)):.1f}"
                                } for severity, scores in severity_stats.items()
                            ])
                            
                            st.dataframe(stats_df, use_container_width=True)
                    
                    st.session_state.abc_batch_running = False
                    
                    if st.button("🔄 进行新研究", use_container_width=True):
                        st.session_state.abc_batch_ready = False
                        st.session_state.abc_batch_running = False
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ 研究出错: {str(e)}")
                    st.session_state.abc_batch_running = False
                    if st.button("🔄 重新尝试", use_container_width=True):
                        st.rerun()
        
        else:
            st.error("请先选择严重程度和评估情境")


def page_custom_assessment():
    """个性化ABC评估设计页面"""
    st.header("⚙️ 个性化ABC评估设计")
    st.markdown("基于ABC量表自定义个体化评估参数")
    
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
        st.subheader("👤 ABC行为特征配置")
        
        template_base = st.selectbox("基于标准分级", ["自定义"] + list(ABC_SEVERITY_PROFILES.keys()))
        
        if template_base != "自定义":
            base_profile = ABC_SEVERITY_PROFILES[template_base].copy()
            st.info(f"基于: {base_profile['description']}")
        else:
            base_profile = {
                'sensory_abnormal': 0.5,
                'social_impairment': 0.5,
                'motor_stereotypy': 0.5,
                'language_deficit': 0.5,
                'self_care_deficit': 0.5,
                'behavior_frequency': 0.5,
                'total_score_range': [50, 70],
                'description': "自定义配置"
            }
        
        st.write("**各领域异常程度配置** (基于ABC量表)")
        
        sensory_level = st.slider(
            "感觉异常程度", 0.0, 1.0, base_profile['sensory_abnormal'],
            help="0=正常，1=严重异常"
        )
        
        social_level = st.slider(
            "交往障碍程度", 0.0, 1.0, base_profile['social_impairment'],
            help="0=正常交往，1=严重障碍"
        )
        
        motor_level = st.slider(
            "躯体运动刻板程度", 0.0, 1.0, base_profile['motor_stereotypy'],
            help="0=无刻板，1=严重刻板"
        )
        
        language_level = st.slider(
            "语言缺陷程度", 0.0, 1.0, base_profile['language_deficit'],
            help="0=语言正常，1=无语言"
        )
        
        selfcare_level = st.slider(
            "自理缺陷程度", 0.0, 1.0, base_profile['self_care_deficit'],
            help="0=完全自理，1=完全依赖"
        )
        
        behavior_freq = st.slider(
            "异常行为出现频率", 0.1, 1.0, base_profile['behavior_frequency'],
            help="行为出现的概率"
        )
        
        # 根据配置估算ABC总分范围
        estimated_min = int((sensory_level * 0.3 + social_level * 0.3 + 
                           motor_level * 0.2 + language_level * 0.3 + 
                           selfcare_level * 0.2) * 80)
        estimated_max = int((sensory_level * 0.5 + social_level * 0.5 + 
                           motor_level * 0.3 + language_level * 0.5 + 
                           selfcare_level * 0.3) * 120)
        
        # 判断严重程度
        if estimated_max >= 100:
            severity_desc = "重度孤独症配置"
        elif estimated_max >= 67:
            severity_desc = "中度孤独症配置"
        elif estimated_max >= 53:
            severity_desc = "轻度孤独症配置"
        elif estimated_max >= 40:
            severity_desc = "边缘状态配置"
        else:
            severity_desc = "非孤独症配置"
        
        st.info(f"**预估ABC总分范围**: {estimated_min}-{estimated_max}")
        st.info(f"**预估严重程度**: {severity_desc}")
        
        autism_profile = {
            'sensory_abnormal': sensory_level,
            'social_impairment': social_level,
            'motor_stereotypy': motor_level,
            'language_deficit': language_level,
            'self_care_deficit': selfcare_level,
            'behavior_frequency': behavior_freq,
            'total_score_range': [estimated_min, estimated_max],
            'description': severity_desc
        }
    
    # 执行个性化评估
    st.subheader("🔬 执行个性化评估")
    
    if st.button("🩺 开始个性化ABC评估", type="primary", use_container_width=True):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        experiment_config = {
            'template': template_base if template_base != "自定义" else "个性化配置",
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'autism_profile': autism_profile,
            'experiment_id': f"CUSTOM_ABC_{timestamp}"
        }
        
        with st.spinner("🤖 正在生成个性化ABC评估..."):
            result = run_single_experiment(experiment_config)
        
        if 'error' not in result:
            st.session_state.experiment_records.append(result)
            
            st.success(f"✅ 个性化评估完成！ID: {result['experiment_id']}")
            
            # 显示详细评估结果
            st.subheader("📊 个性化评估结果")
            
            # ABC总分
            total_score = result['abc_total_score']
            severity = result['abc_severity']
            
            col_total = st.columns(1)[0]
            with col_total:
                if total_score >= 67:
                    st.error(f"### ABC总分: {total_score} - {severity}")
                elif total_score >= 53:
                    st.warning(f"### ABC总分: {total_score} - {severity}")
                else:
                    st.info(f"### ABC总分: {total_score} - {severity}")
            
            col_res1, col_res2, col_res3 = st.columns(3)
            
            with col_res1:
                st.write("**各领域得分**:")
                for domain, score in result['evaluation_scores'].items():
                    max_score = ABC_EVALUATION_METRICS[domain]['max_score']
                    st.metric(domain.replace("得分", ""), 
                             f"{score}/{max_score}", 
                             f"{score/max_score*100:.0f}%")
            
            with col_res2:
                st.write("**主要行为表现**:")
                if 'identified_behaviors' in result:
                    all_behaviors = []
                    for behaviors in result['identified_behaviors'].values():
                        all_behaviors.extend(behaviors)
                    
                    for behavior in all_behaviors[:5]:  # 显示前5个
                        st.write(f"• {behavior}")
            
            with col_res3:
                st.write("**领域分析**:")
                scores = result['evaluation_scores']
                
                # 找出最严重的领域
                max_percentage = 0
                max_domain = ""
                for domain, score in scores.items():
                    max_score = ABC_EVALUATION_METRICS[domain]['max_score']
                    percentage = score / max_score * 100
                    if percentage > max_percentage:
                        max_percentage = percentage
                        max_domain = domain.replace("得分", "")
                
                st.write(f"**最严重领域**: {max_domain}")
                st.write(f"**严重程度**: {max_percentage:.0f}%")
                
            # 个性化建议
            st.subheader("💡 个性化干预建议")
            
            suggestions = []
            
            # 基于各领域得分提供建议
            for domain, score in result['evaluation_scores'].items():
                max_score = ABC_EVALUATION_METRICS[domain]['max_score']
                percentage = score / max_score * 100
                
                if percentage >= 60:
                    if "感觉" in domain:
                        suggestions.append("🌈 感觉统合训练：针对感觉过敏或迟钝进行专业干预")
                    elif "交往" in domain:
                        suggestions.append("👥 社交技能训练：结构化教学提升人际互动能力")
                    elif "躯体" in domain:
                        suggestions.append("🏃 行为干预：减少刻板动作，建立适应性行为")
                    elif "语言" in domain:
                        suggestions.append("🗣️ 语言治疗：提升沟通能力，必要时使用AAC")
                    elif "自理" in domain:
                        suggestions.append("🏠 生活技能训练：提高日常自理和独立能力")
            
            if total_score >= 67:
                suggestions.append("🏥 建议：进行全面的多学科评估和综合干预")
            
            if not suggestions:
                suggestions.append("✅ 各领域表现相对均衡，建议定期监测和预防性干预")
            
            for suggestion in suggestions:
                st.success(suggestion)
                
        else:
            st.error(f"❌ 评估失败: {result['error']}")
    
    # 保存配置
    if st.button("💾 保存评估配置", use_container_width=True):
        st.session_state.custom_autism_profile = autism_profile
        st.session_state.custom_scene_config = {
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger
        }
        st.success("✅ 个性化配置已保存！")


def page_data_analysis():
    """ABC数据分析页面"""
    st.header("📈 ABC数据分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行ABC评估")
        st.stop()
    
    # 生成分析
    analysis = generate_clinical_analysis(records)
    
    # 评估概况
    st.subheader("🏥 评估概况")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("评估总数", len(records))
    with col2:
        avg_total = np.mean([r['abc_total_score'] for r in records])
        st.metric("平均ABC总分", f"{avg_total:.1f}")
    with col3:
        severities = [r['abc_severity'] for r in records]
        most_common = max(set(severities), key=severities.count) if severities else "无"
        st.metric("主要严重程度", most_common)
    with col4:
        contexts = [r['scene'] for r in records]
        most_used_context = max(set(contexts), key=contexts.count)
        st.metric("主要评估情境", most_used_context.replace('结构化', '结构'))
    
    # ABC总分分布图
    st.subheader("📊 ABC总分分布")
    
    total_scores = [r['abc_total_score'] for r in records]
    
    fig_hist = px.histogram(
        x=total_scores,
        nbins=20,
        title="ABC总分分布直方图",
        labels={'x': 'ABC总分', 'y': '频次'}
    )
    
    # 添加诊断阈值线
    fig_hist.add_vline(x=67, line_dash="dash", line_color="red", 
                      annotation_text="孤独症阈值(67分)")
    fig_hist.add_vline(x=53, line_dash="dash", line_color="orange", 
                      annotation_text="轻度阈值(53分)")
    
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # 各领域得分雷达图
    st.subheader("🎯 各领域平均得分")
    
    # 计算各领域平均得分百分比
    domain_percentages = {}
    for domain in ABC_EVALUATION_METRICS.keys():
        scores = [r['evaluation_scores'][domain] for r in records]
        max_score = ABC_EVALUATION_METRICS[domain]['max_score']
        avg_percentage = np.mean(scores) / max_score * 100
        domain_percentages[domain.replace("得分", "")] = avg_percentage
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=list(domain_percentages.values()),
        theta=list(domain_percentages.keys()),
        fill='toself',
        name='平均得分百分比',
        line_color='rgb(255, 100, 100)'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%'
            )),
        showlegend=True,
        title="ABC各领域平均得分百分比",
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # 严重程度分布饼图
    st.subheader("📊 严重程度分布")
    
    severity_counts = {}
    for record in records:
        severity = record['abc_severity']
        if severity not in severity_counts:
            severity_counts[severity] = 0
        severity_counts[severity] += 1
    
    fig_pie = px.pie(
        values=list(severity_counts.values()),
        names=list(severity_counts.keys()),
        title="ABC严重程度分布"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # 高频行为分析
    st.subheader("🔍 高频行为表现")
    
    if '高频行为表现' in analysis:
        behavior_df = pd.DataFrame([
            {'行为': behavior, '出现情况': frequency}
            for behavior, frequency in list(analysis['高频行为表现'].items())[:10]
        ])
        st.dataframe(behavior_df, use_container_width=True)
    
    # 情境效应分析
    st.subheader("🎭 情境效应分析")
    
    if '情境效应分析' in analysis:
        context_data = []
        for context, data in analysis['情境效应分析'].items():
            context_data.append({
                '评估情境': context,
                '评估次数': data['评估次数'],
                'ABC平均总分': float(data['ABC平均总分']),
                '主要行为': ', '.join(data['主要表现'][:2])
            })
        
        df_context = pd.DataFrame(context_data)
        
        fig_context = px.bar(
            df_context,
            x='评估情境',
            y='ABC平均总分',
            title="不同情境下的ABC平均总分",
            labels={'ABC平均总分': 'ABC平均总分'},
            height=400
        )
        fig_context.add_hline(y=67, line_dash="dash", line_color="red", 
                            annotation_text="孤独症阈值")
        st.plotly_chart(fig_context, use_container_width=True)
    
    # 临床发现和建议
    st.subheader("🔍 临床发现与干预建议")
    
    if analysis.get('临床发现与建议'):
        col_finding1, col_finding2 = st.columns(2)
        
        with col_finding1:
            st.write("### 📋 主要临床发现")
            for i, finding in enumerate(analysis['临床发现与建议'], 1):
                if '建议' not in finding:
                    if '严重' in finding or '明确' in finding:
                        st.error(f"{i}. {finding}")
                    elif '轻度' in finding or '边缘' in finding:
                        st.warning(f"{i}. {finding}")
                    else:
                        st.info(f"{i}. {finding}")
        
        with col_finding2:
            st.write("### 💡 干预建议")
            for i, finding in enumerate(analysis['临床发现与建议'], 1):
                if '建议' in finding:
                    st.success(f"{i}. {finding}")

    # ========== 新增：高级行为特征分析 ==========
    st.subheader("🔍 高级行为特征分析")
    
    # 获取所有出现过的行为
    all_behaviors_set = set()
    for record in records:
        if 'identified_behaviors' in record:
            for behaviors in record['identified_behaviors'].values():
                all_behaviors_set.update(behaviors)
    
    all_behaviors_list = sorted(list(all_behaviors_set))
    
    # 行为特征筛选
    with st.expander("📋 行为特征筛选", expanded=False):
        col_filter1, col_filter2 = st.columns([3, 1])
        
        with col_filter1:
            selected_behaviors = st.multiselect(
                "选择目标行为（可多选）",
                all_behaviors_list,
                help="选择您想要筛选的特定行为"
            )
        
        with col_filter2:
            filter_logic = st.radio(
                "筛选逻辑",
                ["包含任一行为", "包含所有行为"],
                help="选择行为筛选的逻辑关系"
            )
        
        if st.button("🔍 筛选样本", use_container_width=True):
            if selected_behaviors:
                logic = 'OR' if filter_logic == "包含任一行为" else 'AND'
                matched_samples, behavior_stats = extract_behavior_specific_samples(
                    records, selected_behaviors, logic
                )
                
                st.success(f"找到 {len(matched_samples)} 个符合条件的样本")
                
                # 显示筛选结果
                if matched_samples:
                    # 行为统计
                    st.write("**行为出现统计：**")
                    stats_df = pd.DataFrame([
                        {'行为': behavior, '出现次数': count, 
                         '出现率': f"{count/len(records)*100:.1f}%"}
                        for behavior, count in behavior_stats.items()
                    ])
                    st.dataframe(stats_df, use_container_width=True)
                    
                    # 样本列表
                    st.write("**符合条件的样本：**")
                    sample_summary = []
                    for item in matched_samples[:20]:  # 最多显示20个
                        record = item['record']
                        sample_summary.append({
                            '评估ID': record['experiment_id'][:30] + '...' if len(record['experiment_id']) > 30 else record['experiment_id'],
                            '严重程度': record['abc_severity'],
                            'ABC总分': record['abc_total_score'],
                            '匹配行为数': item['match_count'],
                            '匹配的行为': ', '.join(item['matched_behaviors'][:3])
                        })
                    
                    st.dataframe(pd.DataFrame(sample_summary), use_container_width=True)
                    
                    if len(matched_samples) > 20:
                        st.info(f"显示前20个结果，共{len(matched_samples)}个")
            else:
                st.warning("请先选择要筛选的行为")
    
    # 行为关联分析
    with st.expander("🔗 行为关联分析", expanded=False):
        min_support = st.slider(
            "最小支持度（%）",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            help="行为共同出现的最低频率阈值"
        )
        
        if st.button("📊 分析行为关联", use_container_width=True):
            associations, co_matrix = analyze_behavior_associations(
                records, min_support=min_support/100
            )
            
            if associations:
                st.write(f"**发现 {len(associations)} 个行为关联规则：**")
                
                # 显示前10个最强关联
                assoc_df = pd.DataFrame(associations[:10])
                assoc_df['支持度'] = assoc_df['support'].apply(lambda x: f"{x*100:.1f}%")
                assoc_df['置信度'] = assoc_df['confidence'].apply(lambda x: f"{x*100:.1f}%")
                assoc_df['提升度'] = assoc_df['lift'].apply(lambda x: f"{x:.2f}")
                
                display_df = assoc_df[['behavior1', 'behavior2', '支持度', '置信度', '提升度', 'co_occurrences']]
                display_df.columns = ['行为1', '行为2', '支持度', '置信度', '提升度', '共现次数']
                
                st.dataframe(display_df, use_container_width=True)
                
                st.info("💡 置信度表示：出现行为1时，同时出现行为2的概率")
                st.info("💡 提升度>1表示：两个行为存在正相关关系")
            else:
                st.warning(f"在{min_support}%的支持度下未发现行为关联")
    
    # 统计显著性检验
    severities = [r.get('template', '自定义') for r in records]
    if len(set(severities)) > 1:
        st.subheader("📐 统计学分析")
        
        try:
            # 进行方差分析
            groups = {}
            for record in records:
                severity = record.get('template', '自定义')
                if severity not in groups:
                    groups[severity] = []
                groups[severity].append(record['abc_total_score'])
            
            if len(groups) >= 2:
                group_values = list(groups.values())
                f_stat, p_value = stats.f_oneway(*group_values)
                
                st.write(f"**单因素方差分析结果**:")
                st.write(f"- F统计量: {f_stat:.3f}")
                st.write(f"- p值: {p_value:.3f}")
                
                if p_value < 0.05:
                    st.success("✅ 不同严重程度组间ABC总分差异具有统计学意义 (p < 0.05)")
                else:
                    st.info("ℹ️ 不同严重程度组间ABC总分差异无统计学意义 (p ≥ 0.05)")
        
        except ImportError:
            st.info("💡 安装scipy模块可启用统计学分析功能")


def page_records_management():
    """评估记录管理页面"""
    st.header("📚 评估记录管理")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.info("📝 暂无评估记录")
        st.stop()
    
    st.subheader(f"📊 共有 {len(records)} 条ABC评估记录")
    
    # 高级筛选选项
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        severity_filter = st.selectbox(
            "按ABC严重程度筛选", 
            ["全部"] + list(set([r['abc_severity'] for r in records]))
        )
    
    with col_filter2:
        context_filter = st.selectbox(
            "按评估情境筛选",
            ["全部"] + list(set([r['scene'] for r in records]))
        )
    
    with col_filter3:
        score_filter = st.selectbox(
            "按ABC总分筛选",
            ["全部", "非孤独症 (<40分)", "边缘 (40-52分)", 
             "轻度 (53-66分)", "中度 (67-100分)", "重度 (>100分)"]
        )
    
    with col_filter4:
        sort_by = st.selectbox(
            "排序方式", 
            ["时间倒序", "时间正序", "ABC总分高到低", "ABC总分低到高"]
        )
    
    # 应用筛选
    filtered_records = records
    
    if severity_filter != "全部":
        filtered_records = [r for r in filtered_records if r['abc_severity'] == severity_filter]
    
    if context_filter != "全部":
        filtered_records = [r for r in filtered_records if r['scene'] == context_filter]
    
    if score_filter != "全部":
        if score_filter == "非孤独症 (<40分)":
            filtered_records = [r for r in filtered_records if r['abc_total_score'] < 40]
        elif score_filter == "边缘 (40-52分)":
            filtered_records = [r for r in filtered_records if 40 <= r['abc_total_score'] <= 52]
        elif score_filter == "轻度 (53-66分)":
            filtered_records = [r for r in filtered_records if 53 <= r['abc_total_score'] <= 66]
        elif score_filter == "中度 (67-100分)":
            filtered_records = [r for r in filtered_records if 67 <= r['abc_total_score'] <= 100]
        elif score_filter == "重度 (>100分)":
            filtered_records = [r for r in filtered_records if r['abc_total_score'] > 100]
    
    # 应用排序
    if sort_by == "时间正序":
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'])
    elif sort_by == "ABC总分高到低":
        filtered_records = sorted(filtered_records, key=lambda x: x['abc_total_score'], reverse=True)
    elif sort_by == "ABC总分低到高":
        filtered_records = sorted(filtered_records, key=lambda x: x['abc_total_score'])
    else:  # 时间倒序
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
    
    st.write(f"筛选后记录数: {len(filtered_records)}")
    
    # 记录列表显示
    for i, record in enumerate(filtered_records):
        
        # ABC总分和严重程度标签
        total_score = record['abc_total_score']
        severity = record['abc_severity']
        
        severity_label = ""
        if total_score >= 101:
            severity_label = "🔴 重度"
        elif total_score >= 67:
            severity_label = "🟠 中度"
        elif total_score >= 53:
            severity_label = "🟡 轻度"
        elif total_score >= 40:
            severity_label = "🔵 边缘"
        else:
            severity_label = "🟢 非孤独症"
        
        template_info = f" - {record.get('template', '自定义')}" if record.get('template') else ""
        
        with st.expander(f"🩺 {record['experiment_id']}{template_info} - ABC:{total_score} - {severity_label} ({record['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📋 评估基本信息:**")
                st.write(f"• 配置类型: {record.get('template', '自定义')}")
                st.write(f"• 评估情境: {record['scene']}")
                st.write(f"• 观察活动: {record.get('activity', '未指定')}")
                st.write(f"• 触发因素: {record.get('trigger', '未指定')}")
                st.write(f"• 评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                st.write("**🎯 ABC评估结果:**")
                st.write(f"• ABC总分: {total_score}")
                st.write(f"• 严重程度: {severity}")
            
            with col2:
                st.write("**📊 各领域得分:**")
                
                scores = record['evaluation_scores']
                
                for domain, score in scores.items():
                    max_score = ABC_EVALUATION_METRICS[domain]['max_score']
                    percentage = score / max_score * 100
                    
                    if percentage >= 60:
                        st.error(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
                    elif percentage >= 40:
                        st.warning(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
                    else:
                        st.success(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
            
            with col3:
                st.write("**🔍 识别到的行为:**")
                if 'identified_behaviors' in record:
                    all_behaviors = []
                    for domain, behaviors in record['identified_behaviors'].items():
                        if behaviors:
                            st.write(f"*{domain}:*")
                            for behavior in behaviors[:3]:  # 每个领域显示前3个
                                st.write(f"• {behavior}")
                            if len(behaviors) > 3:
                                st.write(f"  ...还有{len(behaviors)-3}个")
                else:
                    st.write("暂无行为记录")
                
                if record.get('notes'):
                    st.write(f"**📝 备注:** {record['notes']}")
            
            # 对话记录
            st.write("**💬 行为观察对话记录:**")
            dialogue_lines = record['dialogue'].split('\n')
            dialogue_text = '\n'.join([line for line in dialogue_lines if line.strip() and ':' in line])
            
            unique_key = f"abc_dialogue_{i}_{record['experiment_id']}_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}"
            st.text_area("", dialogue_text, height=200, key=unique_key)
            
            # 快速操作按钮
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)  
            
            with col_btn1:
                if st.button(f"📋 生成个案报告", key=f"report_{record['experiment_id']}"):
                    st.info("个案报告生成功能开发中...")
            
            with col_btn2:
                if st.button(f"📈 趋势分析", key=f"trend_{record['experiment_id']}"):
                    st.info("个体趋势分析功能开发中...")
            
            with col_btn3:
                if st.button(f"🔄 重复评估", key=f"repeat_{record['experiment_id']}"):
                    st.info("重复评估功能开发中...")

            with col_btn4:  # 新增按钮
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
                                   f"相似度: {item['similarity']:.2%} - "
                                   f"ABC总分: {similar_record['abc_total_score']}")
                    else:
                        st.info("未找到相似度超过70%的样本")