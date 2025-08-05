"""个性化评估设计页面"""
import streamlit as st
import datetime

from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
from autism.evaluation import run_single_experiment
from autism.ui_components.result_display import (
    display_abc_detailed_results,
    display_dsm5_detailed_results,
    display_assessment_comparison
)


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
            base_profile = _get_default_custom_profile()
        
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


def _get_default_custom_profile():
    """获取默认的自定义配置"""
    return {
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