"""正常儿童平台UI页面组件"""
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

from common.batch_processor import run_batch_processing
from common.ui_components import display_metric_with_color
from .config import CHILDREN_DEVELOPMENT_PROFILES, DEVELOPMENT_SCENE_CONFIG, DEVELOPMENT_EVALUATION_METRICS
from .evaluator import run_single_observation, generate_observation_batch
from .analyzer import generate_development_analysis


def page_quick_observation():
    """快速发育观察页面"""
    st.header("👶 快速发育观察")
    st.markdown("使用标准化年龄段分级进行快速儿童发展观察")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👦 选择观察对象")
        selected_age_group = st.selectbox("年龄发展阶段", list(CHILDREN_DEVELOPMENT_PROFILES.keys()))
        
        profile = CHILDREN_DEVELOPMENT_PROFILES[selected_age_group]
        
        # 显示发展特征
        with st.expander("查看发展特征配置", expanded=True):
            st.write(f"**发展阶段特征**: {profile['stage_characteristics']}")
            st.write(f"**语言发展水平**: {profile['language_development']}/5")
            st.write(f"**社交技能水平**: {profile['social_skills']}/5")
            st.write(f"**认知能力水平**: {profile['cognitive_ability']}/5")
            st.write(f"**情绪调节能力**: {profile['emotional_regulation']}/5")
            st.write(f"**运动技能发展**: {profile['motor_skills']}/5")
            st.write(f"**独立性水平**: {profile['independence_level']}/5")
            st.write(f"**典型兴趣**: {profile['typical_interests']}")
            st.write(f"**发展重点**: {profile['development_focus']}")
        
        selected_scene = st.selectbox("选择观察情境", list(DEVELOPMENT_SCENE_CONFIG.keys()))
        
        scene_data = DEVELOPMENT_SCENE_CONFIG[selected_scene]
        
        # 显示场景信息
        with st.expander("观察情境详情"):
            st.write(f"**目标**: {scene_data['target']}")
            st.write(f"**观察要点**: {', '.join(scene_data['observation_points'])}")
        
        selected_activity = st.selectbox("选择观察活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择情境触发", scene_data['triggers'])
    
    with col2:
        st.subheader("🔍 执行观察")
        
        if st.button("🌟 开始发育观察", type="primary", use_container_width=True):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            observation_config = {
                'template': selected_age_group,
                'scene': selected_scene,
                'activity': selected_activity,
                'trigger': selected_trigger,
                'child_profile': profile.copy(),
                'observation_id': f"DEV_{selected_age_group[:4]}_{timestamp}"
            }
            
            with st.spinner("🤖 正在生成发育观察对话..."):
                result = run_single_observation(observation_config)
            
            if 'error' not in result:
                st.session_state.observation_records.append(result)
                
                st.success(f"✅ 发育观察完成！ID: {result['observation_id']}")
                
                # 显示观察结果
                st.subheader("📊 发育观察结果")
                
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    st.write("**发展能力评估得分** (5分为最高水平):")
                    for metric, score in result['evaluation_scores'].items():
                        # 根据得分显示不同颜色
                        if score >= 4.5:
                            st.success(f"{metric}: {score}/5.0 (优秀)")
                        elif score >= 4.0:
                            st.info(f"{metric}: {score}/5.0 (良好)")
                        elif score >= 3.0:
                            st.warning(f"{metric}: {score}/5.0 (一般)")
                        else:
                            st.error(f"{metric}: {score}/5.0 (需关注)")
                
                with col_result2:
                    st.write("**发展观察要点**:")
                    if 'developmental_observations' in result:
                        for category, observations in result['developmental_observations'].items():
                            if observations:
                                st.write(f"**{category}**: {', '.join(observations)}")
                    
                    st.write("**对话预览**:")
                    dialogue_lines = result['dialogue'].split('\n')[:8]
                    for line in dialogue_lines:
                        if ':' in line and line.strip():
                            if '儿童' in line:
                                st.markdown(f"👶 {line}")
                            else:
                                st.markdown(f"👤 {line}")
                    
                    if len(result['dialogue'].split('\n')) > 8:
                        st.markdown("*...查看完整记录请前往'观察记录管理'*")
                
                # 显示发展建议
                st.subheader("💡 发展建议")
                development_avg = sum(result['evaluation_scores'].values()) / len(result['evaluation_scores'])
                
                if development_avg >= 4.5:
                    st.success("🌟 发展表现优秀！建议继续保持多样化的成长环境")
                elif development_avg >= 4.0:
                    st.info("👍 发展表现良好！可适当增加挑战性活动")
                elif development_avg >= 3.0:
                    st.warning("📈 发展基本正常，建议增加针对性的成长活动")
                else:
                    st.error("🔍 某些方面需要重点关注，建议咨询专业儿童发展指导")
                    
            else:
                st.error(f"❌ 观察失败: {result['error']}")


def page_batch_research():
    """批量发展研究页面"""
    st.header("📊 批量发展研究")
    st.markdown("进行多组发展对照研究，获取统计学有效的发展数据")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 研究设计")
        
        research_scale = st.radio(
            "选择研究规模",
            ["试点研究（推荐）", "标准研究", "大样本研究"],
            help="根据研究需要选择合适的样本规模"
        )
        
        if research_scale == "试点研究（推荐）":
            default_ages = list(CHILDREN_DEVELOPMENT_PROFILES.keys())[:2]
            default_contexts = list(DEVELOPMENT_SCENE_CONFIG.keys())[:2]
            default_repeats = 1
            st.info("🚀 试点研究：验证观察工具效果，约需5-8分钟")
        elif research_scale == "标准研究":
            default_ages = list(CHILDREN_DEVELOPMENT_PROFILES.keys())[:3]
            default_contexts = list(DEVELOPMENT_SCENE_CONFIG.keys())[:3]
            default_repeats = 2
            st.info("⏳ 标准研究：获得可靠发展数据，约需20-30分钟")
        else:
            default_ages = list(CHILDREN_DEVELOPMENT_PROFILES.keys())
            default_contexts = list(DEVELOPMENT_SCENE_CONFIG.keys())
            default_repeats = 2
            st.warning("⏰ 大样本研究：完整发展研究数据，约需60-90分钟")
        
        selected_ages = st.multiselect(
            "选择年龄段组", 
            list(CHILDREN_DEVELOPMENT_PROFILES.keys()),
            default=default_ages
        )
        
        selected_contexts = st.multiselect(
            "选择观察情境",
            list(DEVELOPMENT_SCENE_CONFIG.keys()),
            default=default_contexts
        )
        
        repeats_per_combo = st.slider(
            "每组合重复次数", 
            1, 3, 
            default_repeats,
            help="增加重复次数提高统计可靠性"
        )
        
        if selected_ages and selected_contexts:
            age_dict = {k: CHILDREN_DEVELOPMENT_PROFILES[k] for k in selected_ages}
            context_dict = {k: DEVELOPMENT_SCENE_CONFIG[k] for k in selected_contexts}
            
            observations = generate_observation_batch(
                age_dict, 
                context_dict, 
                repeats_per_combo
            )
            
            st.info(f"📊 将生成 {len(observations)} 个发展观察")
            
            # 研究设计预览
            with st.expander("研究设计预览", expanded=False):
                preview_df = pd.DataFrame([
                    {
                        '年龄段': obs['template'],
                        '观察情境': obs['scene'],
                        '观察活动': obs['activity'],
                        '情境触发': obs['trigger']
                    } for obs in observations[:10]
                ])
                st.dataframe(preview_df)
                if len(observations) > 10:
                    st.write(f"*...还有 {len(observations) - 10} 个观察*")
    
    with col2:
        st.subheader("🚀 执行研究")
        
        if 'development_batch_ready' not in st.session_state:
            st.session_state.development_batch_ready = False
        if 'development_batch_running' not in st.session_state:
            st.session_state.development_batch_running = False
        
        if selected_ages and selected_contexts:
            estimated_minutes = len(observations) * 25 / 60
            st.info(f"📊 观察数量: {len(observations)}")
            st.info(f"⏰ 预计时间: {estimated_minutes:.1f} 分钟")
            
            if not st.session_state.development_batch_ready and not st.session_state.development_batch_running:
                if st.button("⚡ 准备开始研究", use_container_width=True):
                    st.session_state.development_batch_ready = True
                    st.rerun()
            
            elif st.session_state.development_batch_ready and not st.session_state.development_batch_running:
                st.warning("⏰ **重要**: 由于API限制，批量研究需要较长时间")
                st.info("💡 确认后将立即开始，请保持网络稳定")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("❌ 取消", use_container_width=True):
                        st.session_state.development_batch_ready = False
                        st.rerun()
                
                with col_btn2:
                    if st.button("✅ 开始研究", type="primary", use_container_width=True):
                        st.session_state.development_batch_running = True
                        st.session_state.development_batch_ready = False
                        st.rerun()
            
            elif st.session_state.development_batch_running:
                st.success("🔬 发展研究进行中...")
                
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
                        observations, 
                        run_single_observation, 
                        update_progress,
                        "发展观察"
                    )
                    
                    successful_results = [r for r in results if 'error' not in r]
                    failed_results = [r for r in results if 'error' in r]
                    
                    st.session_state.observation_records.extend(successful_results)
                    st.session_state.current_batch_results = successful_results
                    
                    with result_container:
                        st.success(f"✅ 发展研究完成！")
                        st.write(f"**成功观察**: {len(successful_results)} 个")
                        
                        if failed_results:
                            st.error(f"**失败观察**: {len(failed_results)} 个")
                        
                        if successful_results:
                            st.subheader("📈 研究结果概览")
                            
                            # 按年龄段统计
                            age_stats = {}
                            for result in successful_results:
                                age_group = result['template']
                                if age_group not in age_stats:
                                    age_stats[age_group] = []
                                
                                # 计算综合发展得分
                                development_score = sum(result['evaluation_scores'].values()) / len(result['evaluation_scores'])
                                age_stats[age_group].append(development_score)
                            
                            stats_df = pd.DataFrame([
                                {
                                    '年龄段': age_group,
                                    '样本数': len(scores),
                                    '发展指数均值': f"{np.mean(scores):.2f}",
                                    '标准差': f"{np.std(scores):.2f}",
                                    '95%置信区间': f"{np.mean(scores) - 1.96*np.std(scores)/np.sqrt(len(scores)):.2f}-{np.mean(scores) + 1.96*np.std(scores)/np.sqrt(len(scores)):.2f}"
                                } for age_group, scores in age_stats.items()
                            ])
                            
                            st.dataframe(stats_df, use_container_width=True)
                    
                    st.session_state.development_batch_running = False
                    
                    if st.button("🔄 进行新研究", use_container_width=True):
                        st.session_state.development_batch_ready = False
                        st.session_state.development_batch_running = False
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ 研究出错: {str(e)}")
                    st.session_state.development_batch_running = False
                    if st.button("🔄 重新尝试", use_container_width=True):
                        st.rerun()
        
        else:
            st.error("请先选择年龄段和观察情境")


def page_custom_observation():
    """个性化观察设计页面"""
    st.header("⚙️ 个性化观察设计")
    st.markdown("基于儿童发展理论自定义个体化观察参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎭 观察情境设置")
        selected_scene = st.selectbox("选择观察情境", list(DEVELOPMENT_SCENE_CONFIG.keys()))
        scene_data = DEVELOPMENT_SCENE_CONFIG[selected_scene]
        
        st.info(f"**观察目标**: {scene_data['target']}")
        
        # 显示观察要点
        with st.expander("发展观察要点"):
            for point in scene_data['observation_points']:
                st.write(f"• {point}")
        
        selected_activity = st.selectbox("选择观察活动", scene_data['activities'])
        selected_trigger = st.selectbox("选择情境触发", scene_data['triggers'])
    
    with col2:
        st.subheader("👶 儿童发展配置")
        
        template_base = st.selectbox("基于年龄段模板", ["自定义"] + list(CHILDREN_DEVELOPMENT_PROFILES.keys()))
        
        if template_base != "自定义":
            base_profile = CHILDREN_DEVELOPMENT_PROFILES[template_base]
            st.info(f"基于: {base_profile['stage_characteristics']}")
        else:
            base_profile = {
                'language_development': 3,
                'social_skills': 3,
                'cognitive_ability': 3,
                'emotional_regulation': 3,
                'motor_skills': 3,
                'independence_level': 3,
                'typical_interests': "各种游戏、探索活动",
                'development_focus': "全面发展",
                'stage_characteristics': "自定义配置"
            }
        
        st.write("**发展能力配置** (基于儿童发展心理学)")
        
        language_dev = st.slider(
            "语言发展水平", 1, 5, base_profile['language_development'],
            help="1=语言发展滞后，5=语言发展超前"
        )
        
        social_skills = st.slider(
            "社交技能水平", 1, 5, base_profile['social_skills'],
            help="1=社交技能需支持，5=社交技能优秀"
        )
        
        st.write("**其他发展配置**")
        
        cognitive_ability = st.slider(
            "认知能力水平", 1, 5, base_profile['cognitive_ability'],
            help="1=认知发展滞后，5=认知发展超前"
        )
        
        emotional_regulation = st.slider(
            "情绪调节能力", 1, 5, base_profile['emotional_regulation'],
            help="1=情绪调节困难，5=情绪调节成熟"
        )
        
        motor_skills = st.slider(
            "运动技能发展", 1, 5, base_profile['motor_skills'],
            help="1=运动发展滞后，5=运动技能优秀"
        )
        
        independence_level = st.slider(
            "独立性水平", 1, 5, base_profile['independence_level'],
            help="1=依赖性强，5=独立性强"
        )
        
        typical_interests = st.text_input(
            "典型兴趣爱好", 
            base_profile['typical_interests'],
            help="描述该儿童的主要兴趣和爱好"
        )
        
        development_focus = st.text_input(
            "发展重点",
            base_profile['development_focus'],
            help="当前阶段的主要发展任务"
        )
        
        # 根据配置自动推断发展特征
        total_development = language_dev + social_skills + cognitive_ability + emotional_regulation + motor_skills + independence_level
        avg_development = total_development / 6
        
        if avg_development >= 4.5:
            stage_desc = "发展优秀，各项能力超前"
        elif avg_development >= 4.0:
            stage_desc = "发展良好，能力均衡"
        elif avg_development >= 3.0:
            stage_desc = "发展正常，稳步成长"
        else:
            stage_desc = "发展需关注，需要更多支持"
        
        st.info(f"**推断的发展特征**: {stage_desc}")
        
        child_profile = {
            'language_development': language_dev,
            'social_skills': social_skills,
            'cognitive_ability': cognitive_ability,
            'emotional_regulation': emotional_regulation,
            'motor_skills': motor_skills,
            'independence_level': independence_level,
            'typical_interests': typical_interests,
            'development_focus': development_focus,
            'stage_characteristics': stage_desc
        }
    
    # 执行个性化观察
    st.subheader("🔍 执行个性化观察")
    
    if st.button("🌟 开始个性化观察", type="primary", use_container_width=True):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        observation_config = {
            'template': template_base if template_base != "自定义" else "个性化配置",
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'child_profile': child_profile,
            'observation_id': f"CUSTOM_{timestamp}"
        }
        
        with st.spinner("🤖 正在生成个性化观察..."):
            result = run_single_observation(observation_config)
        
        if 'error' not in result:
            st.session_state.observation_records.append(result)
            
            st.success(f"✅ 个性化观察完成！ID: {result['observation_id']}")
            
            # 显示详细观察结果
            st.subheader("📊 个性化观察结果")
            
            col_res1, col_res2, col_res3 = st.columns(3)
            
            with col_res1:
                st.write("**核心发展评估**:")
                st.metric("语言沟通发展", f"{result['evaluation_scores']['语言沟通发展']:.2f}/5")
                st.metric("社交互动能力", f"{result['evaluation_scores']['社交互动能力']:.2f}/5")
                st.metric("认知学习能力", f"{result['evaluation_scores']['认知学习能力']:.2f}/5")
                
                core_avg = (result['evaluation_scores']['语言沟通发展'] + 
                           result['evaluation_scores']['社交互动能力'] + 
                           result['evaluation_scores']['认知学习能力']) / 3
                st.metric("核心发展指数", f"{core_avg:.2f}/5")
            
            with col_res2:
                st.write("**其他发展评估**:")
                st.metric("情绪调节发展", f"{result['evaluation_scores']['情绪调节发展']:.2f}/5")
                st.metric("运动技能发展", f"{result['evaluation_scores']['运动技能发展']:.2f}/5")
                st.metric("独立自理能力", f"{result['evaluation_scores']['独立自理能力']:.2f}/5")
                
                all_avg = sum(result['evaluation_scores'].values()) / len(result['evaluation_scores'])
                st.metric("综合发展指数", f"{all_avg:.2f}/5")
            
            with col_res3:
                st.write("**发展观察**:")
                if 'developmental_observations' in result:
                    for category, observations in result['developmental_observations'].items():
                        if observations:
                            st.write(f"**{category}**:")
                            for obs in observations:
                                st.write(f"• {obs}")
                
            # 个性化建议
            st.subheader("💡 个性化发展建议")
            
            suggestions = []
            
            if result['evaluation_scores']['语言沟通发展'] >= 4.5:
                suggestions.append("🗣️ 语言发展优秀：可以尝试更复杂的表达活动和双语学习")
            elif result['evaluation_scores']['语言沟通发展'] < 3.0:
                suggestions.append("📚 语言发展需关注：建议增加阅读、故事分享和对话练习")
            
            if result['evaluation_scores']['社交互动能力'] >= 4.5:
                suggestions.append("👥 社交能力突出：可以承担小组领导角色，帮助其他孩子")
            elif result['evaluation_scores']['社交互动能力'] < 3.0:
                suggestions.append("🤝 社交能力需提升：建议多参与团体活动和角色扮演游戏")
            
            if result['evaluation_scores']['认知学习能力'] >= 4.5:
                suggestions.append("🧠 认知能力优秀：可以提供更有挑战性的学习任务")
            elif result['evaluation_scores']['认知学习能力'] < 3.0:
                suggestions.append("📖 认知发展需支持：建议通过游戏化学习增强学习兴趣")
            
            if result['evaluation_scores']['情绪调节发展'] < 3.0:
                suggestions.append("😌 情绪调节需指导：建议情绪识别训练和放松技巧练习")
            
            if result['evaluation_scores']['运动技能发展'] >= 4.5:
                suggestions.append("🏃 运动技能优秀：可以尝试更复杂的体育活动和精细动作训练")
            elif result['evaluation_scores']['运动技能发展'] < 3.0:
                suggestions.append("🤸 运动发展需加强：建议增加户外活动和手工制作")
            
            if not suggestions:
                suggestions.append("✅ 整体发展均衡良好，建议继续多样化的成长体验")
            
            for suggestion in suggestions:
                st.success(suggestion)
                
        else:
            st.error(f"❌ 观察失败: {result['error']}")
    
    # 保存配置
    if st.button("💾 保存观察配置", use_container_width=True):
        st.session_state.custom_child_profile = child_profile
        st.session_state.custom_scene_config = {
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger
        }
        st.success("✅ 个性化配置已保存！")


def page_data_analysis():
    """发展数据分析页面"""
    st.header("📈 发展数据分析")
    
    records = st.session_state.observation_records
    
    if not records:
        st.warning("📊 暂无观察数据，请先进行发展观察")
        st.stop()
    
    # 生成发展分析
    analysis = generate_development_analysis(records)
    
    # 发展概况
    st.subheader("🌟 发展观察概况")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("观察总数", len(records))
    with col2:
        age_groups = [r.get('template', '自定义') for r in records]
        most_common = max(set(age_groups), key=age_groups.count) if age_groups else "无"
        st.metric("主要年龄段", most_common.split('期')[0])
    with col3:
        contexts = [r['scene'] for r in records]
        most_used_context = max(set(contexts), key=contexts.count)
        st.metric("主要观察情境", most_used_context.replace('日常', ''))
    with col4:
        all_development_scores = []
        for r in records:
            development_score = sum(r['evaluation_scores'].values()) / len(r['evaluation_scores'])
            all_development_scores.append(development_score)
        avg_development = np.mean(all_development_scores)
        st.metric("平均发展指数", f"{avg_development:.2f}/5")
    
    # 发展能力雷达图
    st.subheader("🎯 发展能力分析")
    
    # 发展能力雷达图
    avg_scores = {}
    for metric in DEVELOPMENT_EVALUATION_METRICS.keys():
        scores = [r['evaluation_scores'][metric] for r in records]
        avg_scores[metric] = np.mean(scores)
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=list(avg_scores.values()),
        theta=list(avg_scores.keys()),
        fill='toself',
        name='平均发展水平',
        line_color='rgb(100, 200, 100)'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['需支持', '需关注', '一般', '良好', '优秀']
            )),
        showlegend=True,
        title="儿童发展能力雷达图",
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # 年龄段对比分析
    st.subheader("📊 年龄段发展对比")
    
    if len(set([r.get('template', '自定义') for r in records])) > 1:
        age_data = {}
        for record in records:
            age_group = record.get('template', '自定义')
            if age_group not in age_data:
                age_data[age_group] = {
                    '语言沟通': [],
                    '社交互动': [],
                    '认知学习': [],
                    '情绪调节': [],
                    '运动技能': [],
                    '独立能力': []
                }
            
            age_data[age_group]['语言沟通'].append(record['evaluation_scores']['语言沟通发展'])
            age_data[age_group]['社交互动'].append(record['evaluation_scores']['社交互动能力'])
            age_data[age_group]['认知学习'].append(record['evaluation_scores']['认知学习能力'])
            age_data[age_group]['情绪调节'].append(record['evaluation_scores']['情绪调节发展'])
            age_data[age_group]['运动技能'].append(record['evaluation_scores']['运动技能发展'])
            age_data[age_group]['独立能力'].append(record['evaluation_scores']['独立自理能力'])
        
        # 创建对比图表
        comparison_data = []
        for age_group, abilities in age_data.items():
            for ability, scores in abilities.items():
                comparison_data.append({
                    '年龄段': age_group,
                    '发展领域': ability,
                    '平均得分': np.mean(scores),
                    '标准差': np.std(scores)
                })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        fig_comparison = px.bar(
            df_comparison, 
            x='年龄段', 
            y='平均得分', 
            color='发展领域',
            title="不同年龄段的发展领域对比",
            labels={'平均得分': '发展水平 (1-5分)'},
            height=400
        )
        fig_comparison.update_layout(yaxis_range=[1, 5])
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # 观察情境效应分析
    st.subheader("🎭 观察情境效应分析")
    
    context_data = {}
    for record in records:
        context = record['scene']
        if context not in context_data:
            context_data[context] = []
        
        # 计算综合表现得分
        comprehensive_score = sum(record['evaluation_scores'].values()) / len(record['evaluation_scores'])
        context_data[context].append(comprehensive_score)
    
    if len(context_data) > 1:
        context_comparison = []
        for context, scores in context_data.items():
            context_comparison.append({
                '观察情境': context,
                '样本数': len(scores),
                '平均表现': np.mean(scores),
                '标准差': np.std(scores),
                '表现水平': '优秀' if np.mean(scores) >= 4.5 else '良好' if np.mean(scores) >= 4.0 else '一般'
            })
        
        df_context = pd.DataFrame(context_comparison)
        
        fig_context = px.bar(
            df_context,
            x='观察情境',
            y='平均表现',
            color='表现水平',
            title="不同观察情境下的表现对比",
            labels={'平均表现': '平均发展水平 (1-5分)'},
            height=400
        )
        st.plotly_chart(fig_context, use_container_width=True)
        
        # 显示情境分析表格
        st.dataframe(df_context.drop('表现水平', axis=1), use_container_width=True)
    
    # 发展建议和指导
    st.subheader("🔍 发展发现与成长指导")
    
    if analysis.get('发展建议与指导'):
        col_finding1, col_finding2 = st.columns(2)
        
        with col_finding1:
            st.write("### 📋 主要发展发现")
            for i, finding in enumerate(analysis['发展建议与指导'], 1):
                if '优秀' in finding or '良好' in finding:
                    st.success(f"{i}. {finding}")
                elif '需要' in finding or '关注' in finding:
                    st.warning(f"{i}. {finding}")
                else:
                    st.info(f"{i}. {finding}")
        
        with col_finding2:
            st.write("### 💡 成长支持建议")
            
            # 基于观察结果提供具体建议
            language_avg = np.mean([r['evaluation_scores']['语言沟通发展'] for r in records])
            social_avg = np.mean([r['evaluation_scores']['社交互动能力'] for r in records])
            cognitive_avg = np.mean([r['evaluation_scores']['认知学习能力'] for r in records])
            
            st.write("**基于发展心理学的成长建议**:")
            
            if language_avg >= 4.5:
                st.write("• 🗣️ **语言发展超前**")
                st.write("  - 可以尝试第二语言学习")
                st.write("  - 增加复杂表达和创作活动")
                st.write("  - 参与讲故事和演讲活动")
            elif language_avg < 3.0:
                st.write("• 📚 **语言发展需支持**")
                st.write("  - 增加亲子阅读时间")
                st.write("  - 多进行对话练习")
                st.write("  - 使用游戏化语言学习")
            
            if social_avg >= 4.5:
                st.write("• 👥 **社交能力突出**")
                st.write("  - 可以承担小组长角色")
                st.write("  - 参与更多团队合作项目")
                st.write("  - 培养领导力和同理心")
            elif social_avg < 3.0:
                st.write("• 🤝 **社交技能需培养**")
                st.write("  - 多参与集体活动")
                st.write("  - 练习分享和合作")
                st.write("  - 学习社交礼仪和情感表达")
            
            if cognitive_avg >= 4.5:
                st.write("• 🧠 **认知能力优秀**")
                st.write("  - 提供更有挑战性的任务")
                st.write("  - 培养创造性思维")
                st.write("  - 探索STEM和艺术活动")
            elif cognitive_avg < 3.0:
                st.write("• 📖 **认知发展需引导**")
                st.write("  - 通过游戏化学习")
                st.write("  - 培养观察和思考习惯")
                st.write("  - 循序渐进建立学习兴趣")
    
    # 统计显著性检验（如果有多组数据）
    age_groups = [r.get('template', '自定义') for r in records]
    if len(set(age_groups)) > 1:
        st.subheader("📐 统计学分析")
        
        try:
            # 进行方差分析
            groups = {}
            for record in records:
                age_group = record.get('template', '自定义')
                if age_group not in groups:
                    groups[age_group] = []
                
                development_score = sum(record['evaluation_scores'].values()) / len(record['evaluation_scores'])
                groups[age_group].append(development_score)
            
            if len(groups) >= 2:
                group_values = list(groups.values())
                f_stat, p_value = stats.f_oneway(*group_values)
                
                st.write(f"**单因素方差分析结果**:")
                st.write(f"- F统计量: {f_stat:.3f}")
                st.write(f"- p值: {p_value:.3f}")
                
                if p_value < 0.05:
                    st.success("✅ 不同年龄段间发展差异具有统计学意义 (p < 0.05)")
                else:
                    st.info("ℹ️ 不同年龄段间发展差异无统计学意义 (p ≥ 0.05)")
        
        except ImportError:
            st.info("💡 安装scipy模块可启用统计学分析功能")


def page_records_management():
    """观察记录管理页面"""
    st.header("📚 观察记录管理")
    
    records = st.session_state.observation_records
    
    if not records:
        st.info("📝 暂无观察记录")
        st.stop()
    
    st.subheader(f"📊 共有 {len(records)} 条发展观察记录")
    
    # 高级筛选选项
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        age_filter = st.selectbox(
            "按年龄段筛选", 
            ["全部"] + list(set([r.get('template', '自定义') for r in records]))
        )
    
    with col_filter2:
        context_filter = st.selectbox(
            "按观察情境筛选",
            ["全部"] + list(set([r['scene'] for r in records]))
        )
    
    with col_filter3:
        development_filter = st.selectbox(
            "按发展水平筛选",
            ["全部", "优秀 (4.5-5分)", "良好 (4-4.5分)", "一般 (3-4分)", "需关注 (1-3分)"]
        )
    
    with col_filter4:
        sort_by = st.selectbox(
            "排序方式", 
            ["时间倒序", "时间正序", "综合发展指数", "语言发展水平", "社交能力水平"]
        )
    
    # 应用筛选
    filtered_records = records
    
    if age_filter != "全部":
        filtered_records = [r for r in filtered_records if r.get('template', '自定义') == age_filter]
    
    if context_filter != "全部":
        filtered_records = [r for r in filtered_records if r['scene'] == context_filter]
    
    if development_filter != "全部":
        def get_development_score(record):
            return sum(record['evaluation_scores'].values()) / len(record['evaluation_scores'])
        
        if development_filter == "优秀 (4.5-5分)":
            filtered_records = [r for r in filtered_records if get_development_score(r) >= 4.5]
        elif development_filter == "良好 (4-4.5分)":
            filtered_records = [r for r in filtered_records if 4.0 <= get_development_score(r) < 4.5]
        elif development_filter == "一般 (3-4分)":
            filtered_records = [r for r in filtered_records if 3.0 <= get_development_score(r) < 4.0]
        elif development_filter == "需关注 (1-3分)":
            filtered_records = [r for r in filtered_records if get_development_score(r) < 3.0]
    
    # 应用排序
    if sort_by == "时间正序":
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'])
    elif sort_by == "综合发展指数":
        filtered_records = sorted(filtered_records, 
            key=lambda x: sum(x['evaluation_scores'].values()) / len(x['evaluation_scores']), 
            reverse=True)
    elif sort_by == "语言发展水平":
        filtered_records = sorted(filtered_records, 
            key=lambda x: x['evaluation_scores']['语言沟通发展'], reverse=True)
    elif sort_by == "社交能力水平":
        filtered_records = sorted(filtered_records, 
            key=lambda x: x['evaluation_scores']['社交互动能力'], reverse=True)
    else:  # 时间倒序
        filtered_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
    
    st.write(f"筛选后记录数: {len(filtered_records)}")
    
    # 记录列表显示
    for i, record in enumerate(filtered_records):
        
        # 计算综合发展指数
        development_index = sum(record['evaluation_scores'].values()) / len(record['evaluation_scores'])
        
        development_label = ""
        if development_index >= 4.5:
            development_label = "🌟 优秀"
        elif development_index >= 4.0:
            development_label = "👍 良好"
        elif development_index >= 3.0:
            development_label = "📈 一般"
        else:
            development_label = "🔍 需关注"
        
        template_info = f" - {record.get('template', '自定义')}" if record.get('template') else ""
        
        with st.expander(f"🌟 {record['observation_id']}{template_info} - {record['scene']} - {development_label} ({record['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📋 观察基本信息:**")
                if record.get('template'):
                    st.write(f"• 年龄发展阶段: {record['template']}")
                st.write(f"• 观察情境: {record['scene']}")
                st.write(f"• 观察活动: {record.get('activity', '未指定')}")
                st.write(f"• 情境触发: {record.get('trigger', '未指定')}")
                st.write(f"• 观察时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if record.get('child_profile'):
                    st.write("**👶 儿童发展配置:**")
                    profile = record['child_profile']
                    st.write(f"• 发展阶段: {profile.get('stage_characteristics', 'N/A')}")
                    st.write(f"• 语言发展: {profile.get('language_development', 'N/A')}/5")
                    st.write(f"• 社交技能: {profile.get('social_skills', 'N/A')}/5")
                    st.write(f"• 认知能力: {profile.get('cognitive_ability', 'N/A')}/5")
                    st.write(f"• 典型兴趣: {profile.get('typical_interests', 'N/A')}")
            
            with col2:
                st.write("**📊 发展评估得分:**")
                
                scores = record['evaluation_scores']
                
                # 核心发展能力
                st.write("*核心发展能力:*")
                language_score = scores['语言沟通发展']
                social_score = scores['社交互动能力']
                cognitive_score = scores['认知学习能力']
                
                if language_score >= 4.5:
                    st.success(f"• 语言沟通发展: {language_score}/5 (优秀)")
                elif language_score >= 4.0:
                    st.info(f"• 语言沟通发展: {language_score}/5 (良好)")
                elif language_score >= 3.0:
                    st.warning(f"• 语言沟通发展: {language_score}/5 (一般)")
                else:
                    st.error(f"• 语言沟通发展: {language_score}/5 (需关注)")
                
                if social_score >= 4.5:
                    st.success(f"• 社交互动能力: {social_score}/5 (优秀)")
                elif social_score >= 4.0:
                    st.info(f"• 社交互动能力: {social_score}/5 (良好)")
                elif social_score >= 3.0:
                    st.warning(f"• 社交互动能力: {social_score}/5 (一般)")
                else:
                    st.error(f"• 社交互动能力: {social_score}/5 (需关注)")
                
                if cognitive_score >= 4.5:
                    st.success(f"• 认知学习能力: {cognitive_score}/5 (优秀)")
                elif cognitive_score >= 4.0:
                    st.info(f"• 认知学习能力: {cognitive_score}/5 (良好)")
                elif cognitive_score >= 3.0:
                    st.warning(f"• 认知学习能力: {cognitive_score}/5 (一般)")
                else:
                    st.error(f"• 认知学习能力: {cognitive_score}/5 (需关注)")
                
                # 其他发展能力
                st.write("*其他发展能力:*")
                st.write(f"• 情绪调节发展: {scores['情绪调节发展']}/5")
                st.write(f"• 运动技能发展: {scores['运动技能发展']}/5")
                st.write(f"• 独立自理能力: {scores['独立自理能力']}/5")
                
                st.write(f"**综合发展指数: {development_index:.2f}/5**")
            
            with col3:
                st.write("**🔍 发展观察记录:**")
                if 'developmental_observations' in record and record['developmental_observations']:
                    for category, observations in record['developmental_observations'].items():
                        if observations:
                            st.write(f"*{category}:*")
                            for obs in observations:
                                st.write(f"• {obs}")
                else:
                    st.write("暂无特殊发展观察记录")
                
                if record.get('notes'):
                    st.write(f"**📝 备注:** {record['notes']}")
            
            # 对话记录
            st.write("**💬 行为观察对话记录:**")
            dialogue_lines = record['dialogue'].split('\n')
            dialogue_text = '\n'.join([line for line in dialogue_lines if line.strip() and ':' in line])
            
            unique_key = f"development_dialogue_{i}_{record['observation_id']}_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}"
            st.text_area("", dialogue_text, height=200, key=unique_key)
            
            # 快速操作按钮
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button(f"📋 生成发展报告", key=f"report_{record['observation_id']}"):
                    st.info("发展报告生成功能开发中...")
            
            with col_btn2:
                if st.button(f"📈 发展趋势", key=f"trend_{record['observation_id']}"):
                    st.info("发展趋势分析功能开发中...")
            
            with col_btn3:
                if st.button(f"🔄 重复观察", key=f"repeat_{record['observation_id']}"):
                    st.info("重复观察功能开发中...")