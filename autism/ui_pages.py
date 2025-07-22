"""孤独症平台UI页面组件"""
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

from common.batch_processor import run_batch_processing
from common.ui_components import display_metric_with_color
from .config import CLINICAL_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG, CLINICAL_EVALUATION_METRICS
from .evaluator import run_single_experiment, generate_experiment_batch
from .analyzer import generate_clinical_analysis


def page_quick_assessment():
    """临床快速评估页面"""
    st.header("🩺 临床快速评估")
    st.markdown("使用标准化严重程度分级进行快速临床行为评估")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 选择评估对象")
        selected_severity = st.selectbox("严重程度分级", list(CLINICAL_AUTISM_PROFILES.keys()))
        
        profile = CLINICAL_AUTISM_PROFILES[selected_severity]
        
        # 显示临床特征
        with st.expander("查看DSM-5特征配置", expanded=True):
            st.write(f"**DSM-5严重程度**: {profile['dsm5_severity']}")
            st.write(f"**社交沟通缺陷**: {profile['social_communication']}/5")
            st.write(f"**刻板重复行为**: {profile['restricted_repetitive']}/5")
            st.write(f"**感官处理异常**: {profile['sensory_processing']}/5")
            st.write(f"**认知功能水平**: {profile['cognitive_function']}/5")
            st.write(f"**适应行为能力**: {profile['adaptive_behavior']}/5")
            st.write(f"**语言发展水平**: {profile['language_level']}/5")
            st.write(f"**特殊兴趣**: {profile['special_interests']}")
            st.write(f"**所需支持**: {profile['support_needs']}")
        
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
        
        if st.button("🩺 开始临床评估", type="primary", use_container_width=True):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            experiment_config = {
                'template': selected_severity,
                'scene': selected_scene,
                'activity': selected_activity,
                'trigger': selected_trigger,
                'autism_profile': profile.copy(),
                'experiment_id': f"CLIN_{selected_severity[:4]}_{timestamp}"
            }
            
            with st.spinner("🤖 正在生成临床评估对话..."):
                result = run_single_experiment(experiment_config)
            
            if 'error' not in result:
                st.session_state.experiment_records.append(result)
                
                st.success(f"✅ 临床评估完成！ID: {result['experiment_id']}")
                
                # 显示评估结果
                st.subheader("📊 临床评估结果")
                
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    st.write("**核心症状评估得分** (5分为最严重):")
                    for metric, score in result['evaluation_scores'].items():
                        # 根据得分显示不同颜色
                        if score >= 4.0:
                            st.error(f"{metric}: {score}/5.0 (严重)")
                        elif score >= 3.0:
                            st.warning(f"{metric}: {score}/5.0 (中度)")
                        else:
                            st.success(f"{metric}: {score}/5.0 (轻度)")
                
                with col_result2:
                    st.write("**临床观察要点**:")
                    if 'clinical_observations' in result:
                        for category, observations in result['clinical_observations'].items():
                            if observations:
                                st.write(f"**{category}**: {', '.join(observations)}")
                    
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
                core_avg = (result['evaluation_scores']['社交互动质量'] + 
                           result['evaluation_scores']['沟通交流能力'] + 
                           result['evaluation_scores']['刻板重复行为']) / 3
                
                if core_avg >= 4.0:
                    st.error("🚨 建议：核心症状严重，需要密集型干预和专业支持")
                elif core_avg >= 3.0:
                    st.warning("⚠️ 建议：核心症状中等，建议结构化教学和行为干预")
                else:
                    st.success("✅ 建议：症状相对较轻，可重点进行社交技能训练")
                    
            else:
                st.error(f"❌ 评估失败: {result['error']}")


def page_batch_research():
    """批量临床研究页面"""
    st.header("🔬 批量临床研究")
    st.markdown("进行多组临床对照研究，获取统计学有效的评估数据")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        research_scale = st.radio(
            "选择研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究"],
            help="根据研究需要选择合适的样本规模"
        )
        
        if research_scale == "试点研究（推荐）":
            default_severities = list(CLINICAL_AUTISM_PROFILES.keys())[:2]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            st.info("🚀 试点研究：验证评估工具效果，约需5-8分钟")
        elif research_scale == "标准研究":
            default_severities = list(CLINICAL_AUTISM_PROFILES.keys())[:3]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            st.info("⏳ 标准研究：获得可靠统计数据，约需20-30分钟")
        else:
            default_severities = list(CLINICAL_AUTISM_PROFILES.keys())
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())
            default_repeats = 2
            st.warning("⏰ 大样本研究：完整临床研究数据，约需60-90分钟")
        
        selected_severities = st.multiselect(
            "选择严重程度组", 
            list(CLINICAL_AUTISM_PROFILES.keys()),
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
            severity_dict = {k: CLINICAL_AUTISM_PROFILES[k] for k in selected_severities}
            context_dict = {k: CLINICAL_SCENE_CONFIG[k] for k in selected_contexts}
            
            experiments = generate_experiment_batch(
                severity_dict, 
                context_dict, 
                repeats_per_combo
            )
            
            st.info(f"📊 将生成 {len(experiments)} 个临床评估")
            
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
        
        if 'clinical_batch_ready' not in st.session_state:
            st.session_state.clinical_batch_ready = False
        if 'clinical_batch_running' not in st.session_state:
            st.session_state.clinical_batch_running = False
        
        if selected_severities and selected_contexts:
            estimated_minutes = len(experiments) * 25 / 60
            st.info(f"📊 评估数量: {len(experiments)}")
            st.info(f"⏰ 预计时间: {estimated_minutes:.1f} 分钟")
            
            if not st.session_state.clinical_batch_ready and not st.session_state.clinical_batch_running:
                if st.button("⚡ 准备开始研究", use_container_width=True):
                    st.session_state.clinical_batch_ready = True
                    st.rerun()
            
            elif st.session_state.clinical_batch_ready and not st.session_state.clinical_batch_running:
                st.warning("⏰ **重要**: 由于API限制，批量研究需要较长时间")
                st.info("💡 确认后将立即开始，请保持网络稳定")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("❌ 取消", use_container_width=True):
                        st.session_state.clinical_batch_ready = False
                        st.rerun()
                
                with col_btn2:
                    if st.button("✅ 开始研究", type="primary", use_container_width=True):
                        st.session_state.clinical_batch_running = True
                        st.session_state.clinical_batch_ready = False
                        st.rerun()
            
            elif st.session_state.clinical_batch_running:
                st.success("🔬 临床研究进行中...")
                
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
                        "临床实验"
                    )
                    
                    successful_results = [r for r in results if 'error' not in r]
                    failed_results = [r for r in results if 'error' in r]
                    
                    st.session_state.experiment_records.extend(successful_results)
                    st.session_state.current_batch_results = successful_results
                    
                    with result_container:
                        st.success(f"✅ 临床研究完成！")
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
                                
                                # 计算核心症状综合得分
                                core_score = (result['evaluation_scores']['社交互动质量'] + 
                                            result['evaluation_scores']['沟通交流能力'] + 
                                            result['evaluation_scores']['刻板重复行为']) / 3
                                severity_stats[severity].append(core_score)
                            
                            stats_df = pd.DataFrame([
                                {
                                    '严重程度': severity,
                                    '样本数': len(scores),
                                    '核心症状均值': f"{np.mean(scores):.2f}",
                                    '标准差': f"{np.std(scores):.2f}",
                                    '95%置信区间': f"{np.mean(scores) - 1.96*np.std(scores)/np.sqrt(len(scores)):.2f}-{np.mean(scores) + 1.96*np.std(scores)/np.sqrt(len(scores)):.2f}"
                                } for severity, scores in severity_stats.items()
                            ])
                            
                            st.dataframe(stats_df, use_container_width=True)
                    
                    st.session_state.clinical_batch_running = False
                    
                    if st.button("🔄 进行新研究", use_container_width=True):
                        st.session_state.clinical_batch_ready = False
                        st.session_state.clinical_batch_running = False
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ 研究出错: {str(e)}")
                    st.session_state.clinical_batch_running = False
                    if st.button("🔄 重新尝试", use_container_width=True):
                        st.rerun()
        
        else:
            st.error("请先选择严重程度和评估情境")


def page_custom_assessment():
    """个性化评估设计页面"""
    st.header("⚙️ 个性化评估设计")
    st.markdown("基于DSM-5标准自定义个体化临床评估参数")
    
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
        st.subheader("👤 DSM-5特征配置")
        
        template_base = st.selectbox("基于标准分级", ["自定义"] + list(CLINICAL_AUTISM_PROFILES.keys()))
        
        if template_base != "自定义":
            base_profile = CLINICAL_AUTISM_PROFILES[template_base]
            st.info(f"基于: {base_profile['dsm5_severity']}")
        else:
            base_profile = {
                'social_communication': 3,
                'restricted_repetitive': 3,
                'sensory_processing': 3,
                'cognitive_function': 3,
                'adaptive_behavior': 3,
                'language_level': 3,
                'special_interests': "特定物体、活动或主题",
                'support_needs': "中等支持",
                'dsm5_severity': "自定义配置"
            }
        
        st.write("**核心症状配置** (基于DSM-5诊断标准A、B条目)")
        
        social_comm = st.slider(
            "A. 社交沟通缺陷程度", 1, 5, base_profile['social_communication'],
            help="1=无明显缺陷，5=严重缺陷（社会情感互惠性、非语言沟通、关系发展困难）"
        )
        
        repetitive_behavior = st.slider(
            "B. 刻板重复行为程度", 1, 5, base_profile['restricted_repetitive'],
            help="1=很少重复行为，5=严重重复行为（刻板动作、仪式、狭隘兴趣、感官异常）"
        )
        
        st.write("**相关功能配置**")
        
        sensory_processing = st.slider(
            "感官处理异常程度", 1, 5, base_profile['sensory_processing'],
            help="1=正常处理，5=严重异常（过敏、寻求、逃避）"
        )
        
        cognitive_function = st.slider(
            "认知功能水平", 1, 5, base_profile['cognitive_function'],
            help="1=重度障碍，5=正常范围"
        )
        
        adaptive_behavior = st.slider(
            "适应行为能力", 1, 5, base_profile['adaptive_behavior'],
            help="1=严重困难，5=年龄适宜"
        )
        
        language_level = st.slider(
            "语言发展水平", 1, 5, base_profile['language_level'],
            help="1=无功能性语言，5=年龄适宜"
        )
        
        special_interests = st.text_input(
            "特殊兴趣/限制性兴趣", 
            base_profile['special_interests'],
            help="描述具体的特殊兴趣或重复行为"
        )
        
        # 根据配置自动推断支持需求
        total_severity = social_comm + repetitive_behavior
        if total_severity >= 8:
            support_level = "需要非常大量支持"
            dsm5_level = "需要非常大量支持"
        elif total_severity >= 6:
            support_level = "需要大量支持"
            dsm5_level = "需要大量支持"
        else:
            support_level = "需要支持"
            dsm5_level = "需要支持"
        
        st.info(f"**推断的DSM-5严重程度**: {dsm5_level}")
        st.info(f"**推断的支持需求**: {support_level}")
        
        autism_profile = {
            'social_communication': social_comm,
            'restricted_repetitive': repetitive_behavior,
            'sensory_processing': sensory_processing,
            'cognitive_function': cognitive_function,
            'adaptive_behavior': adaptive_behavior,
            'language_level': language_level,
            'special_interests': special_interests,
            'support_needs': support_level,
            'dsm5_severity': dsm5_level
        }
    
    # 执行个性化评估
    st.subheader("🔬 执行个性化评估")
    
    if st.button("🩺 开始个性化评估", type="primary", use_container_width=True):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        experiment_config = {
            'template': template_base if template_base != "自定义" else "个性化配置",
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'autism_profile': autism_profile,
            'experiment_id': f"CUSTOM_{timestamp}"
        }
        
        with st.spinner("🤖 正在生成个性化评估..."):
            result = run_single_experiment(experiment_config)
        
        if 'error' not in result:
            st.session_state.experiment_records.append(result)
            
            st.success(f"✅ 个性化评估完成！ID: {result['experiment_id']}")
            
            # 显示详细评估结果
            st.subheader("📊 个性化评估结果")
            
            col_res1, col_res2, col_res3 = st.columns(3)
            
            with col_res1:
                st.write("**核心症状评估**:")
                st.metric("社交沟通缺陷", f"{result['evaluation_scores']['社交互动质量']:.2f}/5")
                st.metric("刻板重复行为", f"{result['evaluation_scores']['刻板重复行为']:.2f}/5")
                
                core_avg = (result['evaluation_scores']['社交互动质量'] + 
                           result['evaluation_scores']['刻板重复行为']) / 2
                st.metric("核心症状综合", f"{core_avg:.2f}/5")
            
            with col_res2:
                st.write("**相关功能评估**:")
                st.metric("沟通交流能力", f"{result['evaluation_scores']['沟通交流能力']:.2f}/5")
                st.metric("感官处理能力", f"{result['evaluation_scores']['感官处理能力']:.2f}/5")
                st.metric("情绪行为调节", f"{result['evaluation_scores']['情绪行为调节']:.2f}/5")
                st.metric("认知适应功能", f"{result['evaluation_scores']['认知适应功能']:.2f}/5")
            
            with col_res3:
                st.write("**临床观察**:")
                if 'clinical_observations' in result:
                    for category, observations in result['clinical_observations'].items():
                        if observations:
                            st.write(f"**{category}**:")
                            for obs in observations:
                                st.write(f"• {obs}")
                
            # 个性化建议
            st.subheader("💡 个性化干预建议")
            
            suggestions = []
            
            if result['evaluation_scores']['社交互动质量'] >= 4:
                suggestions.append("🎯 优先目标：社交技能训练（眼神接触、轮流交替、情感分享）")
            
            if result['evaluation_scores']['沟通交流能力'] >= 4:
                suggestions.append("🗣️ 沟通干预：语言治疗、AAC辅助沟通、社交语用训练")
            
            if result['evaluation_scores']['刻板重复行为'] >= 4:
                suggestions.append("🔄 行为管理：功能性行为分析、替代行为训练、环境结构化")
            
            if result['evaluation_scores']['感官处理能力'] >= 4:
                suggestions.append("🌈 感官支持：感觉统合治疗、环境调适、自我调节策略")
            
            if result['evaluation_scores']['情绪行为调节'] >= 4:
                suggestions.append("😌 情绪支持：情绪识别训练、应对策略教学、行为干预")
            
            if not suggestions:
                suggestions.append("✅ 整体表现良好，建议维持现有支持并监测发展")
            
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
    """临床数据分析页面"""
    st.header("📈 临床数据分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行临床评估")
        st.stop()
    
    # 生成临床分析
    analysis = generate_clinical_analysis(records)
    
    # 临床概况
    st.subheader("🏥 临床评估概况")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("评估总数", len(records))
    with col2:
        severities = [r.get('template', '自定义') for r in records]
        most_common = max(set(severities), key=severities.count) if severities else "无"
        st.metric("主要严重程度", most_common.split('（')[0])
    with col3:
        contexts = [r['scene'] for r in records]
        most_used_context = max(set(contexts), key=contexts.count)
        st.metric("主要评估情境", most_used_context.replace('结构化', '结构'))
    with col4:
        all_core_scores = []
        for r in records:
            core_score = (r['evaluation_scores']['社交互动质量'] + 
                         r['evaluation_scores']['沟通交流能力'] + 
                         r['evaluation_scores']['刻板重复行为']) / 3
            all_core_scores.append(core_score)
        avg_core = np.mean(all_core_scores)
        st.metric("平均核心症状", f"{avg_core:.2f}/5")
    
    # DSM-5核心症状分析
    st.subheader("🧠 DSM-5核心症状分析")
    
    # 核心症状雷达图
    avg_scores = {}
    for metric in CLINICAL_EVALUATION_METRICS.keys():
        scores = [r['evaluation_scores'][metric] for r in records]
        avg_scores[metric] = np.mean(scores)
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=list(avg_scores.values()),
        theta=list(avg_scores.keys()),
        fill='toself',
        name='平均缺陷程度',
        line_color='rgb(255, 100, 100)'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['正常', '轻度', '中度', '明显', '严重']
            )),
        showlegend=True,
        title="DSM-5核心症状及相关功能评估雷达图",
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # 严重程度对比分析
    st.subheader("📊 严重程度组间对比")
    
    if len(set([r.get('template', '自定义') for r in records])) > 1:
        severity_data = {}
        for record in records:
            severity = record.get('template', '自定义')
            if severity not in severity_data:
                severity_data[severity] = {
                    '社交沟通缺陷': [],
                    '刻板重复行为': [],
                    '感官处理异常': [],
                    '认知适应缺陷': []
                }
            
            severity_data[severity]['社交沟通缺陷'].append(
                (record['evaluation_scores']['社交互动质量'] + 
                 record['evaluation_scores']['沟通交流能力']) / 2
            )
            severity_data[severity]['刻板重复行为'].append(
                record['evaluation_scores']['刻板重复行为']
            )
            severity_data[severity]['感官处理异常'].append(
                record['evaluation_scores']['感官处理能力']
            )
            severity_data[severity]['认知适应缺陷'].append(
                record['evaluation_scores']['认知适应功能']
            )
        
        # 创建对比图表
        comparison_data = []
        for severity, metrics in severity_data.items():
            for metric, scores in metrics.items():
                comparison_data.append({
                    '严重程度': severity,
                    '症状域': metric,
                    '平均得分': np.mean(scores),
                    '标准差': np.std(scores)
                })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        fig_comparison = px.bar(
            df_comparison, 
            x='严重程度', 
            y='平均得分', 
            color='症状域',
            title="不同严重程度组的症状域对比",
            labels={'平均得分': '缺陷程度 (1-5分)'},
            height=400
        )
        fig_comparison.update_layout(yaxis_range=[1, 5])
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # 评估情境效应分析
    st.subheader("🎭 评估情境效应分析")
    
    context_data = {}
    for record in records:
        context = record['scene']
        if context not in context_data:
            context_data[context] = []
        
        # 计算综合表现得分（得分越低表现越好）
        comprehensive_score = np.mean(list(record['evaluation_scores'].values()))
        context_data[context].append(comprehensive_score)
    
    if len(context_data) > 1:
        context_comparison = []
        for context, scores in context_data.items():
            context_comparison.append({
                '评估情境': context,
                '样本数': len(scores),
                '平均表现': np.mean(scores),
                '标准差': np.std(scores),
                '表现水平': '较好' if np.mean(scores) < 3.0 else '中等' if np.mean(scores) < 4.0 else '困难'
            })
        
        df_context = pd.DataFrame(context_comparison)
        
        fig_context = px.bar(
            df_context,
            x='评估情境',
            y='平均表现',
            color='表现水平',
            title="不同评估情境下的表现对比",
            labels={'平均表现': '平均困难程度 (1-5分)'},
            height=400
        )
        st.plotly_chart(fig_context, use_container_width=True)
        
        # 显示情境分析表格
        st.dataframe(df_context.drop('表现水平', axis=1), use_container_width=True)
    
    # 临床发现和建议
    st.subheader("🔍 临床发现与干预建议")
    
    if analysis.get('临床发现与建议'):
        col_finding1, col_finding2 = st.columns(2)
        
        with col_finding1:
            st.write("### 📋 主要临床发现")
            for i, finding in enumerate(analysis['临床发现与建议'], 1):
                if '建议' in finding:
                    st.success(f"{i}. {finding}")
                elif '严重' in finding:
                    st.error(f"{i}. {finding}")
                else:
                    st.info(f"{i}. {finding}")
        
        with col_finding2:
            st.write("### 💡 循证干预建议")
            
            # 基于评估结果提供具体建议
            social_avg = np.mean([r['evaluation_scores']['社交互动质量'] for r in records])
            comm_avg = np.mean([r['evaluation_scores']['沟通交流能力'] for r in records])
            repetitive_avg = np.mean([r['evaluation_scores']['刻板重复行为'] for r in records])
            
            st.write("**基于循证实践的干预建议**:")
            
            if social_avg >= 4.0:
                st.write("• 🎯 **社交技能训练** (SST)")
                st.write("  - 结构化社交技能教学")
                st.write("  - 同伴中介干预")
                st.write("  - 视频建模技术")
            
            if comm_avg >= 4.0:
                st.write("• 🗣️ **沟通干预**")
                st.write("  - 功能性沟通训练")
                st.write("  - 图片交换沟通系统(PECS)")
                st.write("  - 语言行为干预")
            
            if repetitive_avg >= 4.0:
                st.write("• 🔄 **行为干预**")
                st.write("  - 应用行为分析(ABA)")
                st.write("  - 功能性行为评估")
                st.write("  - 正向行为支持")
    
    # 统计显著性检验（如果有多组数据）
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
                
                core_score = (record['evaluation_scores']['社交互动质量'] + 
                             record['evaluation_scores']['沟通交流能力'] + 
                             record['evaluation_scores']['刻板重复行为']) / 3
                groups[severity].append(core_score)
            
            if len(groups) >= 2:
                group_values = list(groups.values())
                f_stat, p_value = stats.f_oneway(*group_values)
                
                st.write(f"**单因素方差分析结果**:")
                st.write(f"- F统计量: {f_stat:.3f}")
                st.write(f"- p值: {p_value:.3f}")
                
                if p_value < 0.05:
                    st.success("✅ 不同严重程度组间差异具有统计学意义 (p < 0.05)")
                else:
                    st.info("ℹ️ 不同严重程度组间差异无统计学意义 (p ≥ 0.05)")
        
        except ImportError:
            st.info("💡 安装scipy模块可启用统计学分析功能")


def page_records_management():
    """评估记录管理页面"""
    st.header("📚 评估记录管理")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.info("📝 暂无评估记录")
        st.stop()
    
    st.subheader(f"📊 共有 {len(records)} 条临床评估记录")
    
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
        score_filter = st.selectbox(
            "按严重程度筛选",
            ["全部", "轻度 (1-2分)", "中度 (2-3分)", "重度 (3-4分)", "极重度 (4-5分)"]
        )
    
    with col_filter4:
        sort_by = st.selectbox(
            "排序方式", 
            ["时间倒序", "时间正序", "核心症状严重度", "社交缺陷程度", "沟通缺陷程度"]
        )
    
    # 应用筛选
    filtered_records = records
    
    if severity_filter != "全部":
        filtered_records = [r for r in filtered_records if r.get('template', '自定义') == severity_filter]
    
    if context_filter != "全部":
        filtered_records = [r for r in filtered_records if r['scene'] == context_filter]
    
    if score_filter != "全部":
        def get_core_score(record):
            return (record['evaluation_scores']['社交互动质量'] + 
                   record['evaluation_scores']['沟通交流能力'] + 
                   record['evaluation_scores']['刻板重复行为']) / 3
        
        if score_filter == "轻度 (1-2分)":
            filtered_records = [r for r in filtered_records if get_core_score(r) <= 2.0]
        elif score_filter == "中度 (2-3分)":
            filtered_records = [r for r in filtered_records if 2.0 < get_core_score(r) <= 3.0]
        elif score_filter == "重度 (3-4分)":
            filtered_records = [r for r in filtered_records if 3.0 < get_core_score(r) <= 4.0]
        elif score_filter == "极重度 (4-5分)":
            filtered_records = [r for r in filtered_records if get_core_score(r) > 4.0]
    
    # 应用排序
    if sort_by == "时间正序":
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'])
    elif sort_by == "核心症状严重度":
        filtered_records = sorted(filtered_records, 
            key=lambda x: (x['evaluation_scores']['社交互动质量'] + 
                          x['evaluation_scores']['沟通交流能力'] + 
                          x['evaluation_scores']['刻板重复行为']) / 3, 
            reverse=True)
    elif sort_by == "社交缺陷程度":
        filtered_records = sorted(filtered_records, 
            key=lambda x: x['evaluation_scores']['社交互动质量'], reverse=True)
    elif sort_by == "沟通缺陷程度":
        filtered_records = sorted(filtered_records, 
            key=lambda x: x['evaluation_scores']['沟通交流能力'], reverse=True)
    else:  # 时间倒序
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
    
    st.write(f"筛选后记录数: {len(filtered_records)}")
    
    # 记录列表显示
    for i, record in enumerate(filtered_records):
        
        # 计算核心症状严重度
        core_severity = (record['evaluation_scores']['社交互动质量'] + 
                        record['evaluation_scores']['沟通交流能力'] + 
                        record['evaluation_scores']['刻板重复行为']) / 3
        
        severity_label = ""
        if core_severity >= 4.0:
            severity_label = "🔴 极重度"
        elif core_severity >= 3.0:
            severity_label = "🟠 重度"
        elif core_severity >= 2.0:
            severity_label = "🟡 中度"
        else:
            severity_label = "🟢 轻度"
        
        template_info = f" - {record.get('template', '自定义')}" if record.get('template') else ""
        
        with st.expander(f"🩺 {record['experiment_id']}{template_info} - {record['scene']} - {severity_label} ({record['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📋 评估基本信息:**")
                if record.get('template'):
                    st.write(f"• 严重程度分级: {record['template']}")
                st.write(f"• 评估情境: {record['scene']}")
                st.write(f"• 观察活动: {record.get('activity', '未指定')}")
                st.write(f"• 触发因素: {record.get('trigger', '未指定')}")
                st.write(f"• 评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if record.get('autism_profile'):
                    st.write("**👤 DSM-5特征配置:**")
                    profile = record['autism_profile']
                    st.write(f"• DSM-5严重程度: {profile.get('dsm5_severity', 'N/A')}")
                    st.write(f"• 社交沟通缺陷: {profile.get('social_communication', 'N/A')}/5")
                    st.write(f"• 刻板重复行为: {profile.get('restricted_repetitive', 'N/A')}/5")
                    st.write(f"• 认知功能水平: {profile.get('cognitive_function', 'N/A')}/5")
                    st.write(f"• 特殊兴趣: {profile.get('special_interests', 'N/A')}")
            
            with col2:
                st.write("**📊 临床评估得分:**")
                
                scores = record['evaluation_scores']
                
                # 核心症状
                st.write("*DSM-5核心症状:*")
                social_score = scores['社交互动质量']
                comm_score = scores['沟通交流能力']
                repetitive_score = scores['刻板重复行为']
                
                if social_score >= 4.0:
                    st.error(f"• 社交互动质量: {social_score}/5 (严重缺陷)")
                elif social_score >= 3.0:
                    st.warning(f"• 社交互动质量: {social_score}/5 (明显缺陷)")
                else:
                    st.success(f"• 社交互动质量: {social_score}/5 (轻度缺陷)")
                
                if comm_score >= 4.0:
                    st.error(f"• 沟通交流能力: {comm_score}/5 (严重缺陷)")
                elif comm_score >= 3.0:
                    st.warning(f"• 沟通交流能力: {comm_score}/5 (明显缺陷)")
                else:
                    st.success(f"• 沟通交流能力: {comm_score}/5 (轻度缺陷)")
                
                if repetitive_score >= 4.0:
                    st.error(f"• 刻板重复行为: {repetitive_score}/5 (严重程度)")
                elif repetitive_score >= 3.0:
                    st.warning(f"• 刻板重复行为: {repetitive_score}/5 (明显程度)")
                else:
                    st.success(f"• 刻板重复行为: {repetitive_score}/5 (轻度程度)")
                
                # 相关功能
                st.write("*相关功能:*")
                st.write(f"• 感官处理能力: {scores['感官处理能力']}/5")
                st.write(f"• 情绪行为调节: {scores['情绪行为调节']}/5")
                st.write(f"• 认知适应功能: {scores['认知适应功能']}/5")
                
                st.write(f"**核心症状综合严重度: {core_severity:.2f}/5**")
            
            with col3:
                st.write("**🔍 临床观察记录:**")
                if 'clinical_observations' in record and record['clinical_observations']:
                    for category, observations in record['clinical_observations'].items():
                        if observations:
                            st.write(f"*{category}:*")
                            for obs in observations:
                                st.write(f"• {obs}")
                else:
                    st.write("暂无特殊临床观察记录")
                
                if record.get('notes'):
                    st.write(f"**📝 备注:** {record['notes']}")
            
            # 对话记录
            st.write("**💬 行为观察对话记录:**")
            dialogue_lines = record['dialogue'].split('\n')
            dialogue_text = '\n'.join([line for line in dialogue_lines if line.strip() and ':' in line])
            
            unique_key = f"clinical_dialogue_{i}_{record['experiment_id']}_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}"
            st.text_area("", dialogue_text, height=200, key=unique_key)
            
            # 快速操作按钮
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button(f"📋 生成个案报告", key=f"report_{record['experiment_id']}"):
                    st.info("个案报告生成功能开发中...")
            
            with col_btn2:
                if st.button(f"📈 趋势分析", key=f"trend_{record['experiment_id']}"):
                    st.info("个体趋势分析功能开发中...")
            
            with col_btn3:
                if st.button(f"🔄 重复评估", key=f"repeat_{record['experiment_id']}"):
                    st.info("重复评估功能开发中...")