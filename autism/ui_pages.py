"""孤独症平台UI页面组件 - 支持DSM-5和ABC双标准"""
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
    ABC_SEVERITY_PROFILES, CLINICAL_SCENE_CONFIG, ABC_EVALUATION_METRICS, ABC_BEHAVIOR_ITEMS,
    DSM5_SEVERITY_PROFILES, DSM5_EVALUATION_METRICS
)
from .evaluator import run_single_experiment, generate_experiment_batch
from .analyzer import (
    generate_clinical_analysis, 
    extract_behavior_specific_samples,
    calculate_sample_similarity,
    find_similar_samples,
    analyze_behavior_associations,
    get_behavior_summary_stats
)

def page_quick_assessment():
    """快速评估页面 - 支持DSM-5和ABC双标准"""
    st.header("🩺 快速临床评估")
    st.markdown("使用DSM-5或ABC标准进行快速临床评估")
    
    # 评估标准选择
    assessment_standard = st.radio(
        "选择评估标准",
        ["ABC孤独症行为量表", "DSM-5诊断标准"],
        help="ABC量表包含57个行为项目，DSM-5标准基于核心症状评估"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 选择评估对象")
        
        if assessment_standard == "ABC孤独症行为量表":
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
        else:  # DSM-5标准
            selected_severity = st.selectbox("严重程度分级", list(DSM5_SEVERITY_PROFILES.keys()))
            profile = DSM5_SEVERITY_PROFILES[selected_severity]
            
            # 显示DSM-5特征
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
            standard_code = 'ABC' if assessment_standard == "ABC孤独症行为量表" else 'DSM5'
            
            experiment_config = {
                'template': selected_severity,
                'scene': selected_scene,
                'activity': selected_activity,
                'trigger': selected_trigger,
                'autism_profile': profile.copy(),
                'experiment_id': f"{standard_code}_{selected_severity[:4]}_{timestamp}",
                'assessment_standard': standard_code
            }
            
            with st.spinner("🤖 正在生成临床评估对话..."):
                result = run_single_experiment(experiment_config)
            
            if 'error' not in result:
                st.session_state.experiment_records.append(result)
                
                st.success(f"✅ 临床评估完成！ID: {result['experiment_id']}")
                
                # 显示评估结果
                st.subheader("📊 临床评估结果")
                
                if assessment_standard == "ABC孤独症行为量表":
                    # ABC评估结果显示
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
                    
                    # ABC临床建议
                    st.subheader("💡 临床建议")
                    if total_score >= 67:
                        st.error("🚨 建议：ABC评分显示明确孤独症表现，需要综合干预治疗")
                    elif total_score >= 53:
                        st.warning("⚠️ 建议：轻度孤独症表现，建议早期干预和行为训练")
                    elif total_score >= 40:
                        st.info("ℹ️ 建议：边缘状态，需要密切观察和定期评估")
                    else:
                        st.success("✅ 建议：未达孤独症标准，但仍需关注个别领域表现")
                
                else:  # DSM-5评估结果
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
                    
                    # DSM-5临床建议
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
                
                # 对话预览（两种标准共用）
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
                    
            else:
                st.error(f"❌ 评估失败: {result['error']}")


def page_batch_research():
    """批量研究页面 - 支持DSM-5和ABC双标准"""
    st.header("🔬 批量临床研究")
    st.markdown("使用DSM-5或ABC标准进行多组对照研究")
    
    # 评估标准选择
    assessment_standard = st.radio(
        "选择评估标准",
        ["ABC孤独症行为量表", "DSM-5诊断标准"],
        help="选择用于批量研究的评估标准"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        research_scale = st.radio(
            "选择研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究"],
            help="根据研究需要选择合适的样本规模"
        )
        
        # 根据评估标准选择不同的严重程度配置
        if assessment_standard == "ABC孤独症行为量表":
            severity_profiles = ABC_SEVERITY_PROFILES
        else:
            severity_profiles = DSM5_SEVERITY_PROFILES
        
        if research_scale == "试点研究（推荐）":
            default_severities = list(severity_profiles.keys())[:2]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            st.info("🚀 试点研究：验证评估效果，约需5-8分钟")
        elif research_scale == "标准研究":
            default_severities = list(severity_profiles.keys())[:3]
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            st.info("⏳ 标准研究：获得可靠统计数据，约需20-30分钟")
        else:
            default_severities = list(severity_profiles.keys())
            default_contexts = list(CLINICAL_SCENE_CONFIG.keys())
            default_repeats = 2
            st.warning("⏰ 大样本研究：完整研究数据，约需60-90分钟")
        
        selected_severities = st.multiselect(
            "选择严重程度组", 
            list(severity_profiles.keys()),
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
            severity_dict = {k: severity_profiles[k] for k in selected_severities}
            context_dict = {k: CLINICAL_SCENE_CONFIG[k] for k in selected_contexts}
            
            standard_code = 'ABC' if assessment_standard == "ABC孤独症行为量表" else 'DSM5'
            
            experiments = generate_experiment_batch(
                severity_dict, 
                context_dict, 
                repeats_per_combo,
                assessment_standard=standard_code
            )
            
            st.info(f"📊 将生成 {len(experiments)} 个{assessment_standard}评估")
            
            # 研究设计预览
            with st.expander("研究设计预览", expanded=False):
                preview_df = pd.DataFrame([
                    {
                        '评估标准': assessment_standard[:3],
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
        
        # 使用不同的session state键来区分标准
        batch_ready_key = f"{assessment_standard}_batch_ready"
        batch_running_key = f"{assessment_standard}_batch_running"
        
        if batch_ready_key not in st.session_state:
            st.session_state[batch_ready_key] = False
        if batch_running_key not in st.session_state:
            st.session_state[batch_running_key] = False
        
        if selected_severities and selected_contexts:
            estimated_minutes = len(experiments) * 25 / 60
            st.info(f"📊 评估数量: {len(experiments)}")
            st.info(f"⏰ 预计时间: {estimated_minutes:.1f} 分钟")
            
            if not st.session_state[batch_ready_key] and not st.session_state[batch_running_key]:
                if st.button("⚡ 准备开始研究", use_container_width=True):
                    st.session_state[batch_ready_key] = True
                    st.rerun()
            
            elif st.session_state[batch_ready_key] and not st.session_state[batch_running_key]:
                st.warning("⏰ **重要**: 由于API限制，批量研究需要较长时间")
                st.info("💡 确认后将立即开始，请保持网络稳定")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("❌ 取消", use_container_width=True):
                        st.session_state[batch_ready_key] = False
                        st.rerun()
                
                with col_btn2:
                    if st.button("✅ 开始研究", type="primary", use_container_width=True):
                        st.session_state[batch_running_key] = True
                        st.session_state[batch_ready_key] = False
                        st.rerun()
            
            elif st.session_state[batch_running_key]:
                st.success(f"🔬 {assessment_standard}研究进行中...")
                
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
                        f"{assessment_standard}实验"
                    )
                    
                    successful_results = [r for r in results if 'error' not in r]
                    failed_results = [r for r in results if 'error' in r]
                    
                    st.session_state.experiment_records.extend(successful_results)
                    st.session_state.current_batch_results = successful_results
                    
                    with result_container:
                        st.success(f"✅ {assessment_standard}研究完成！")
                        st.write(f"**成功评估**: {len(successful_results)} 个")
                        
                        if failed_results:
                            st.error(f"**失败评估**: {len(failed_results)} 个")
                        
                        if successful_results:
                            st.subheader("📈 研究结果概览")
                            
                            if assessment_standard == "ABC孤独症行为量表":
                                # ABC结果统计
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
                            else:
                                # DSM-5结果统计
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
                    
                    st.session_state[batch_running_key] = False
                    
                    if st.button("🔄 进行新研究", use_container_width=True):
                        st.session_state[batch_ready_key] = False
                        st.session_state[batch_running_key] = False
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ 研究出错: {str(e)}")
                    st.session_state[batch_running_key] = False
                    if st.button("🔄 重新尝试", use_container_width=True):
                        st.rerun()
        
        else:
            st.error("请先选择严重程度和评估情境")


def page_custom_assessment():
    """个性化评估设计页面 - 支持DSM-5和ABC双标准"""
    st.header("⚙️ 个性化评估设计")
    st.markdown("基于DSM-5或ABC标准自定义个体化评估参数")
    
    # 评估标准选择
    assessment_standard = st.radio(
        "选择评估标准",
        ["ABC孤独症行为量表", "DSM-5诊断标准"],
        help="选择个性化评估使用的标准"
    )
    
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
        
        if assessment_standard == "ABC孤独症行为量表":
            # ABC配置
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
            
        else:  # DSM-5配置
            template_base = st.selectbox("基于标准分级", ["自定义"] + list(DSM5_SEVERITY_PROFILES.keys()))
            
            if template_base != "自定义":
                base_profile = DSM5_SEVERITY_PROFILES[template_base]
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
        standard_code = 'ABC' if assessment_standard == "ABC孤独症行为量表" else 'DSM5'
        
        experiment_config = {
            'template': template_base if template_base != "自定义" else "个性化配置",
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'autism_profile': autism_profile,
            'experiment_id': f"CUSTOM_{standard_code}_{timestamp}",
            'assessment_standard': standard_code
        }
        
        with st.spinner("🤖 正在生成个性化评估..."):
            result = run_single_experiment(experiment_config)
        
        if 'error' not in result:
            st.session_state.experiment_records.append(result)
            
            st.success(f"✅ 个性化评估完成！ID: {result['experiment_id']}")
            
            # 显示详细评估结果
            st.subheader("📊 个性化评估结果")
            
            if assessment_standard == "ABC孤独症行为量表":
                # ABC个性化结果
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
                
                # ABC个性化建议
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
                    
            else:  # DSM-5个性化结果
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
                
                # DSM-5个性化建议
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
            'trigger': selected_trigger,
            'assessment_standard': assessment_standard
        }
        st.success("✅ 个性化配置已保存！")


def page_data_analysis():
    """数据分析页面 - 支持DSM-5和ABC双标准"""
    st.header("📈 临床数据分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行临床评估")
        st.stop()
    
    # 分析数据中的评估标准
    abc_records = [r for r in records if r.get('assessment_standard') == 'ABC']
    dsm5_records = [r for r in records if r.get('assessment_standard') == 'DSM5']
    
    # 显示数据概览
    st.subheader("🏥 评估数据概览")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("评估总数", len(records))
    with col2:
        st.metric("ABC评估", len(abc_records))
    with col3:
        st.metric("DSM-5评估", len(dsm5_records))
    with col4:
        contexts = [r['scene'] for r in records]
        unique_contexts = len(set(contexts))
        st.metric("评估情境数", unique_contexts)
    
    # 选择要分析的数据集
    analysis_option = st.radio(
        "选择分析数据集",
        ["全部数据", "仅ABC评估", "仅DSM-5评估"],
        help="选择要分析的评估数据"
    )
    
    if analysis_option == "仅ABC评估" and not abc_records:
        st.warning("暂无ABC评估数据")
        st.stop()
    elif analysis_option == "仅DSM-5评估" and not dsm5_records:
        st.warning("暂无DSM-5评估数据")
        st.stop()
    
    # 确定分析数据集
    if analysis_option == "仅ABC评估":
        analysis_records = abc_records
    elif analysis_option == "仅DSM-5评估":
        analysis_records = dsm5_records
    else:
        analysis_records = records
    
    # 生成分析
    analysis = generate_clinical_analysis(analysis_records)
    
    # ABC特定分析
    if analysis_option != "仅DSM-5评估" and abc_records:
        st.subheader("📊 ABC量表分析")
        
        # ABC总分分布图
        if abc_records:
            total_scores = [r['abc_total_score'] for r in abc_records]
            
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
            domain_percentages = {}
            for domain in ABC_EVALUATION_METRICS.keys():
                scores = [r['evaluation_scores'][domain] for r in abc_records]
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
    
    # DSM-5特定分析
    if analysis_option != "仅ABC评估" and dsm5_records:
        st.subheader("🧠 DSM-5核心症状分析")
        
        # 核心症状雷达图
        avg_scores = {}
        for metric in DSM5_EVALUATION_METRICS.keys():
            scores = [r['evaluation_scores'][metric] for r in dsm5_records]
            avg_scores[metric] = np.mean(scores)
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(avg_scores.values()),
            theta=list(avg_scores.keys()),
            fill='toself',
            name='平均缺陷程度',
            line_color='rgb(100, 100, 255)'
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
    
    # 严重程度分布饼图
    st.subheader("📊 严重程度分布")
    
    if analysis_option == "仅ABC评估" or (analysis_option == "全部数据" and abc_records):
        # ABC严重程度分布
        severity_counts = {}
        for record in abc_records:
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
    
    if analysis_option == "仅DSM-5评估" or (analysis_option == "全部数据" and dsm5_records):
        # DSM-5严重程度分布
        severity_counts = {}
        for record in dsm5_records:
            severity = record.get('template', '自定义')
            if severity not in severity_counts:
                severity_counts[severity] = 0
            severity_counts[severity] += 1
        
        fig_pie = px.pie(
            values=list(severity_counts.values()),
            names=list(severity_counts.keys()),
            title="DSM-5严重程度分布"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # 高频行为分析（仅ABC）
    if analysis_option != "仅DSM-5评估" and abc_records:
        st.subheader("🔍 高频行为表现")
        
        if '高频行为表现' in analysis:
            behavior_df = pd.DataFrame([
                {'行为': behavior, '出现情况': frequency}
                for behavior, frequency in list(analysis['高频行为表现'].items())[:10]
            ])
            st.dataframe(behavior_df, use_container_width=True)
        
        # 高级行为特征分析
        with st.expander("📋 行为特征筛选", expanded=False):
            # 获取所有出现过的行为
            all_behaviors_set = set()
            for record in abc_records:
                if 'identified_behaviors' in record:
                    for behaviors in record['identified_behaviors'].values():
                        all_behaviors_set.update(behaviors)
            
            all_behaviors_list = sorted(list(all_behaviors_set))
            
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
                        abc_records, selected_behaviors, logic
                    )
                    
                    st.success(f"找到 {len(matched_samples)} 个符合条件的样本")
                    
                    # 显示筛选结果
                    if matched_samples:
                        # 行为统计
                        st.write("**行为出现统计：**")
                        stats_df = pd.DataFrame([
                            {'行为': behavior, '出现次数': count, 
                             '出现率': f"{count/len(abc_records)*100:.1f}%"}
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
    
    # 情境效应分析
    st.subheader("🎭 评估情境效应分析")
    
    context_data = {}
    for record in analysis_records:
        context = record['scene']
        if context not in context_data:
            context_data[context] = []
        
        # 根据评估标准计算综合表现得分
        if record.get('assessment_standard') == 'ABC':
            # ABC使用总分（分数越高症状越严重）
            comprehensive_score = record['abc_total_score']
        else:
            # DSM-5使用核心症状平均分（分数越高症状越严重）
            comprehensive_score = (record['evaluation_scores']['社交互动质量'] + 
                                 record['evaluation_scores']['沟通交流能力'] + 
                                 record['evaluation_scores']['刻板重复行为']) / 3 * 20  # 转换到类似ABC的尺度
        
        context_data[context].append(comprehensive_score)
    
    if len(context_data) > 1:
        context_comparison = []
        for context, scores in context_data.items():
            avg_score = np.mean(scores)
            context_comparison.append({
                '评估情境': context,
                '样本数': len(scores),
                '平均表现': avg_score,
                '标准差': np.std(scores),
                '表现水平': '较好' if avg_score < 50 else '中等' if avg_score < 70 else '困难'
            })
        
        df_context = pd.DataFrame(context_comparison)
        
        fig_context = px.bar(
            df_context,
            x='评估情境',
            y='平均表现',
            color='表现水平',
            title="不同评估情境下的表现对比",
            labels={'平均表现': '症状严重程度'},
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
                if '严重' in finding or '明确' in finding:
                    st.error(f"{i}. {finding}")
                elif '轻度' in finding or '边缘' in finding:
                    st.warning(f"{i}. {finding}")
                else:
                    st.info(f"{i}. {finding}")
        
        with col_finding2:
            st.write("### 💡 循证干预建议")
            st.write("**基于评估结果的干预建议**:")
            
            if analysis_option != "仅DSM-5评估" and abc_records:
                # ABC干预建议
                avg_total = np.mean([r['abc_total_score'] for r in abc_records])
                
                if avg_total >= 67:
                    st.write("• 🎯 **综合干预方案**")
                    st.write("  - 应用行为分析(ABA)")
                    st.write("  - 结构化教学(TEACCH)")
                    st.write("  - 感觉统合训练")
                    st.write("  - 语言和沟通治疗")
                elif avg_total >= 53:
                    st.write("• 🗣️ **早期干预**")
                    st.write("  - 社交技能训练")
                    st.write("  - 图片交换沟通系统(PECS)")
                    st.write("  - 行为支持计划")
            
            if analysis_option != "仅ABC评估" and dsm5_records:
                # DSM-5干预建议
                social_avg = np.mean([r['evaluation_scores']['社交互动质量'] for r in dsm5_records])
                comm_avg = np.mean([r['evaluation_scores']['沟通交流能力'] for r in dsm5_records])
                repetitive_avg = np.mean([r['evaluation_scores']['刻板重复行为'] for r in dsm5_records])
                
                if social_avg >= 4.0:
                    st.write("• 🎯 **社交技能训练** (SST)")
                    st.write("  - 结构化社交技能教学")
                    st.write("  - 同伴中介干预")
                    st.write("  - 视频建模技术")
                
                if comm_avg >= 4.0:
                    st.write("• 🗣️ **沟通干预**")
                    st.write("  - 功能性沟通训练")
                    st.write("  - AAC辅助沟通")
                    st.write("  - 语言行为干预")
                
                if repetitive_avg >= 4.0:
                    st.write("• 🔄 **行为干预**")
                    st.write("  - 功能性行为评估")
                    st.write("  - 正向行为支持")
                    st.write("  - 环境结构化")
    
    # 统计显著性检验
    if len(analysis_records) > 10:
        st.subheader("📐 统计学分析")
        
        try:
            # 根据评估标准进行不同的统计分析
            if analysis_option == "仅ABC评估":
                # ABC评分的组间比较
                severity_groups = {}
                for record in abc_records:
                    severity = record['abc_severity']
                    if severity not in severity_groups:
                        severity_groups[severity] = []
                    severity_groups[severity].append(record['abc_total_score'])
                
                if len(severity_groups) >= 2:
                    group_values = list(severity_groups.values())
                    f_stat, p_value = stats.f_oneway(*group_values)
                    
                    st.write(f"**ABC总分的单因素方差分析**:")
                    st.write(f"- F统计量: {f_stat:.3f}")
                    st.write(f"- p值: {p_value:.3f}")
                    
                    if p_value < 0.05:
                        st.success("✅ 不同严重程度组间ABC总分差异具有统计学意义 (p < 0.05)")
                    else:
                        st.info("ℹ️ 不同严重程度组间ABC总分差异无统计学意义 (p ≥ 0.05)")
            
            elif analysis_option == "仅DSM-5评估":
                # DSM-5核心症状的组间比较
                severity_groups = {}
                for record in dsm5_records:
                    severity = record.get('template', '自定义')
                    if severity not in severity_groups:
                        severity_groups[severity] = []
                    
                    core_score = (record['evaluation_scores']['社交互动质量'] + 
                                 record['evaluation_scores']['沟通交流能力'] + 
                                 record['evaluation_scores']['刻板重复行为']) / 3
                    severity_groups[severity].append(core_score)
                
                if len(severity_groups) >= 2:
                    group_values = list(severity_groups.values())
                    f_stat, p_value = stats.f_oneway(*group_values)
                    
                    st.write(f"**DSM-5核心症状的单因素方差分析**:")
                    st.write(f"- F统计量: {f_stat:.3f}")
                    st.write(f"- p值: {p_value:.3f}")
                    
                    if p_value < 0.05:
                        st.success("✅ 不同严重程度组间核心症状差异具有统计学意义 (p < 0.05)")
                    else:
                        st.info("ℹ️ 不同严重程度组间核心症状差异无统计学意义 (p ≥ 0.05)")
                        
        except ImportError:
            st.info("💡 安装scipy模块可启用统计学分析功能")


def page_records_management():
    """评估记录管理页面 - 支持DSM-5和ABC双标准"""
    st.header("📚 评估记录管理")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.info("📝 暂无评估记录")
        st.stop()
    
    # 统计各标准的记录数
    abc_count = len([r for r in records if r.get('assessment_standard') == 'ABC'])
    dsm5_count = len([r for r in records if r.get('assessment_standard') == 'DSM5'])
    
    st.subheader(f"📊 共有 {len(records)} 条临床评估记录")
    st.write(f"ABC评估: {abc_count} 条 | DSM-5评估: {dsm5_count} 条")
    
    # 高级筛选选项
    col_filter1, col_filter2, col_filter3, col_filter4, col_filter5 = st.columns(5)
    
    with col_filter1:
        standard_filter = st.selectbox(
            "按评估标准筛选",
            ["全部", "ABC量表", "DSM-5标准"]
        )
    
    with col_filter2:
        severity_options = ["全部"]
        if standard_filter == "ABC量表":
            severity_options.extend(["重度孤独症", "中度孤独症", "轻度孤独症", "边缘状态", "非孤独症"])
        elif standard_filter == "DSM-5标准":
            severity_options.extend(list(DSM5_SEVERITY_PROFILES.keys()))
        else:
            severity_options.extend(list(set([r.get('abc_severity', r.get('template', '自定义')) for r in records])))
        
        severity_filter = st.selectbox("按严重程度筛选", severity_options)
    
    with col_filter3:
        context_filter = st.selectbox(
            "按评估情境筛选",
            ["全部"] + list(set([r['scene'] for r in records]))
        )
    
    with col_filter4:
        score_filter = st.selectbox(
            "按评分筛选",
            ["全部", "高分", "中分", "低分"]
        )
    
    with col_filter5:
        sort_by = st.selectbox(
            "排序方式", 
            ["时间倒序", "时间正序", "严重程度", "评估标准"]
        )
    
    # 应用筛选
    filtered_records = records
    
    if standard_filter == "ABC量表":
        filtered_records = [r for r in filtered_records if r.get('assessment_standard') == 'ABC']
    elif standard_filter == "DSM-5标准":
        filtered_records = [r for r in filtered_records if r.get('assessment_standard') == 'DSM5']
    
    if severity_filter != "全部":
        if standard_filter == "ABC量表":
            filtered_records = [r for r in filtered_records if r.get('abc_severity') == severity_filter]
        else:
            filtered_records = [r for r in filtered_records if r.get('template', '自定义') == severity_filter]
    
    if context_filter != "全部":
        filtered_records = [r for r in filtered_records if r['scene'] == context_filter]
    
    if score_filter != "全部":
        if score_filter == "高分":
            if standard_filter == "ABC量表":
                filtered_records = [r for r in filtered_records if r.get('abc_total_score', 0) >= 67]
            else:
                filtered_records = [r for r in filtered_records if 
                                  (r['evaluation_scores']['社交互动质量'] + 
                                   r['evaluation_scores']['沟通交流能力'] + 
                                   r['evaluation_scores']['刻板重复行为']) / 3 >= 4.0]
        elif score_filter == "中分":
            if standard_filter == "ABC量表":
                filtered_records = [r for r in filtered_records if 40 <= r.get('abc_total_score', 0) < 67]
            else:
                filtered_records = [r for r in filtered_records if 
                                  2.5 <= (r['evaluation_scores']['社交互动质量'] + 
                                          r['evaluation_scores']['沟通交流能力'] + 
                                          r['evaluation_scores']['刻板重复行为']) / 3 < 4.0]
        else:  # 低分
            if standard_filter == "ABC量表":
                filtered_records = [r for r in filtered_records if r.get('abc_total_score', 0) < 40]
            else:
                filtered_records = [r for r in filtered_records if 
                                  (r['evaluation_scores']['社交互动质量'] + 
                                   r['evaluation_scores']['沟通交流能力'] + 
                                   r['evaluation_scores']['刻板重复行为']) / 3 < 2.5]
    
    # 应用排序
    if sort_by == "时间正序":
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'])
    elif sort_by == "严重程度":
        def get_severity_score(record):
            if record.get('assessment_standard') == 'ABC':
                return record.get('abc_total_score', 0)
            else:
                return (record['evaluation_scores']['社交互动质量'] + 
                       record['evaluation_scores']['沟通交流能力'] + 
                       record['evaluation_scores']['刻板重复行为']) / 3
        filtered_records = sorted(filtered_records, key=get_severity_score, reverse=True)
    elif sort_by == "评估标准":
        filtered_records = sorted(filtered_records, key=lambda x: x.get('assessment_standard', 'ABC'))
    else:  # 时间倒序
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
    
    st.write(f"筛选后记录数: {len(filtered_records)}")
    
    # 记录列表显示
    for i, record in enumerate(filtered_records):
        
        # 获取评估标准
        assessment_standard = record.get('assessment_standard', 'ABC')
        standard_label = "ABC" if assessment_standard == 'ABC' else "DSM-5"
        
        # 获取严重程度标签
        if assessment_standard == 'ABC':
            severity = record.get('abc_severity', '未知')
            total_score = record.get('abc_total_score', 0)
            
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
            
            display_info = f"[{standard_label}] ABC:{total_score} - {severity_label}"
        else:
            # DSM-5评估
            core_severity = (record['evaluation_scores']['社交互动质量'] + 
                            record['evaluation_scores']['沟通交流能力'] + 
                            record['evaluation_scores']['刻板重复行为']) / 3
            
            if core_severity >= 4.0:
                severity_label = "🔴 极重度"
            elif core_severity >= 3.0:
                severity_label = "🟠 重度"
            elif core_severity >= 2.0:
                severity_label = "🟡 中度"
            else:
                severity_label = "🟢 轻度"
            
            display_info = f"[{standard_label}] 核心:{core_severity:.2f} - {severity_label}"
        
        template_info = f" - {record.get('template', '自定义')}" if record.get('template') else ""
        
        with st.expander(f"🩺 {record['experiment_id']}{template_info} - {display_info} ({record['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📋 评估基本信息:**")
                st.write(f"• 评估标准: {standard_label}")
                st.write(f"• 配置类型: {record.get('template', '自定义')}")
                st.write(f"• 评估情境: {record['scene']}")
                st.write(f"• 观察活动: {record.get('activity', '未指定')}")
                st.write(f"• 触发因素: {record.get('trigger', '未指定')}")
                st.write(f"• 评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if assessment_standard == 'ABC':
                    st.write("**🎯 ABC评估结果:**")
                    st.write(f"• ABC总分: {record.get('abc_total_score', 'N/A')}")
                    st.write(f"• 严重程度: {record.get('abc_severity', 'N/A')}")
                else:
                    if record.get('autism_profile'):
                        st.write("**👤 DSM-5特征配置:**")
                        profile = record['autism_profile']
                        st.write(f"• DSM-5严重程度: {profile.get('dsm5_severity', 'N/A')}")
                        st.write(f"• 社交沟通缺陷: {profile.get('social_communication', 'N/A')}/5")
                        st.write(f"• 刻板重复行为: {profile.get('restricted_repetitive', 'N/A')}/5")
            
            with col2:
                st.write("**📊 评估得分:**")
                
                scores = record['evaluation_scores']
                
                if assessment_standard == 'ABC':
                    # ABC各领域得分
                    for domain, score in scores.items():
                        max_score = ABC_EVALUATION_METRICS[domain]['max_score']
                        percentage = score / max_score * 100
                        
                        if percentage >= 60:
                            st.error(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
                        elif percentage >= 40:
                            st.warning(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
                        else:
                            st.success(f"• {domain}: {score}/{max_score} ({percentage:.0f}%)")
                else:
                    # DSM-5评分
                    st.write("*DSM-5核心症状:*")
                    for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']:
                        score = scores[metric]
                        if score >= 4.0:
                            st.error(f"• {metric}: {score}/5 (严重)")
                        elif score >= 3.0:
                            st.warning(f"• {metric}: {score}/5 (中度)")
                        else:
                            st.success(f"• {metric}: {score}/5 (轻度)")
                    
                    st.write("*相关功能:*")
                    for metric in ['感官处理能力', '情绪行为调节', '认知适应功能']:
                        st.write(f"• {metric}: {scores[metric]}/5")
            
            with col3:
                st.write("**🔍 临床观察:**")
                
                if assessment_standard == 'ABC' and 'identified_behaviors' in record:
                    all_behaviors = []
                    for domain, behaviors in record['identified_behaviors'].items():
                        if behaviors:
                            st.write(f"*{domain}:*")
                            for behavior in behaviors[:3]:  # 每个领域显示前3个
                                st.write(f"• {behavior}")
                            if len(behaviors) > 3:
                                st.write(f"  ...还有{len(behaviors)-3}个")
                elif 'clinical_observations' in record and record['clinical_observations']:
                    for category, observations in record['clinical_observations'].items():
                        if observations:
                            st.write(f"*{category}:*")
                            for obs in observations:
                                st.write(f"• {obs}")
                else:
                    st.write("暂无特殊观察记录")
                
                if record.get('notes'):
                    st.write(f"**📝 备注:** {record['notes']}")
            
            # 对话记录
            st.write("**💬 行为观察对话记录:**")
            dialogue_lines = record['dialogue'].split('\n')
            dialogue_text = '\n'.join([line for line in dialogue_lines if line.strip() and ':' in line])
            
            unique_key = f"{assessment_standard}_dialogue_{i}_{record['experiment_id']}_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}"
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

            with col_btn4:
                if st.button(f"🔍 查找相似", key=f"similar_{record['experiment_id']}"):
                    if assessment_standard == 'ABC':
                        with st.spinner("正在查找相似样本..."):
                            similar_samples = find_similar_samples(
                                record, 
                                [r for r in st.session_state.experiment_records if r.get('assessment_standard') == 'ABC'],
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
                    else:
                        st.info("相似度分析功能目前仅支持ABC评估")