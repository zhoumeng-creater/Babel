"""快速评估页面"""
import streamlit as st
import datetime

from autism.config import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluator import run_single_experiment


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
                from autism.ui_components.result_display import display_dual_assessment_results
                display_dual_assessment_results(result)
                
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