"""个性化评估设计页面 - 增强版（支持多量表）"""
import streamlit as st
import datetime
import pandas as pd

from autism.configs import UNIFIED_AUTISM_PROFILES, CLINICAL_SCENE_CONFIG
# 修改导入：使用增强版函数
from autism.evaluation import (
    run_enhanced_experiment,  # 使用增强版
    AVAILABLE_SCALES,
    DEFAULT_SCALES
)
from autism.ui_components.result_display import (
    display_abc_detailed_results,
    display_dsm5_detailed_results,
    display_assessment_comparison
)


def page_custom_assessment():
    """个性化评估设计页面 - 支持多量表评估"""
    st.header("⚙️ 个性化评估设计")
    st.markdown("自定义孤独症特征，生成行为表现并进行多量表评估")
    
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
        
        # ✨ 新增：量表选择
        st.write("### 📋 评估量表选择")
        
        use_default_scales = st.checkbox("使用标准双量表（ABC+DSM-5）", value=True)
        
        if use_default_scales:
            selected_scales = DEFAULT_SCALES
            st.info("✅ 将使用ABC和DSM-5进行评估")
        else:
            st.write("**自定义量表组合：**")
            selected_scales = []
            
            col_scale1, col_scale2 = st.columns(2)
            with col_scale1:
                if st.checkbox("ABC量表", value=True, key="custom_abc"):
                    selected_scales.append('ABC')
                if st.checkbox("CARS量表", value=False, key="custom_cars"):
                    selected_scales.append('CARS')
            with col_scale2:
                if st.checkbox("DSM-5标准", value=True, key="custom_dsm5"):
                    selected_scales.append('DSM5')
                if st.checkbox("ASSQ筛查", value=False, key="custom_assq"):
                    selected_scales.append('ASSQ')
            
            if selected_scales:
                scale_names = [AVAILABLE_SCALES[s]['name'] for s in selected_scales]
                st.info(f"将使用: {', '.join(scale_names)}")
            else:
                st.warning("请至少选择一个评估量表")
    
    with col2:
        st.subheader("👤 特征配置")
        
        template_base = st.selectbox("基于模板", ["自定义"] + list(UNIFIED_AUTISM_PROFILES.keys()))
        
        if template_base != "自定义":
            base_profile = UNIFIED_AUTISM_PROFILES[template_base].copy()
            st.info(f"基于: {base_profile['name']}")
        else:
            base_profile = _get_default_custom_profile()
        
        st.write("**自定义特征描述**")
        
        # 特征编辑区域
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
    st.subheader("🔬 执行个性化评估")
    
    if st.button("🩺 开始个性化评估", type="primary", use_container_width=True):
        if not selected_scales:
            st.error("请选择至少一个评估量表")
            return
            
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        
        experiment_config = {
            'template': template_base if template_base != "自定义" else "个性化配置",
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'autism_profile': custom_profile,
            'experiment_id': f"CUSTOM_{timestamp}",
            'selected_scales': selected_scales  # ✨ 添加量表选择
        }
        
        with st.spinner(f"🤖 正在生成个性化评估（{len(selected_scales)}个量表）..."):
            # 使用增强版评估函数
            result = run_enhanced_experiment(experiment_config)
        
        if 'error' not in result:
            st.session_state.experiment_records.append(result)
            
            st.success(f"✅ 个性化评估完成！ID: {result['experiment_id']}")
            
            # 显示详细评估结果
            st.subheader("📊 个性化评估详细结果")
            
            # 根据使用的量表创建标签页
            tabs = []
            if 'abc_evaluation' in result:
                tabs.append("ABC量表评估")
            if 'dsm5_evaluation' in result:
                tabs.append("DSM-5标准评估")
            if 'cars_evaluation' in result:
                tabs.append("CARS量表评估")
            if 'assq_evaluation' in result:
                tabs.append("ASSQ筛查结果")
            if len(selected_scales) > 1 and 'scale_comparison' in result:
                tabs.append("量表对比分析")
            
            if tabs:
                tab_objects = st.tabs(tabs)
                tab_idx = 0
                
                # ABC评估结果
                if 'abc_evaluation' in result:
                    with tab_objects[tab_idx]:
                        display_abc_detailed_results(result['abc_evaluation'])
                    tab_idx += 1
                
                # DSM-5评估结果
                if 'dsm5_evaluation' in result:
                    with tab_objects[tab_idx]:
                        display_dsm5_detailed_results(result['dsm5_evaluation'])
                    tab_idx += 1
                
                # CARS评估结果
                if 'cars_evaluation' in result:
                    with tab_objects[tab_idx]:
                        display_cars_detailed_results(result['cars_evaluation'])
                    tab_idx += 1
                
                # ASSQ评估结果
                if 'assq_evaluation' in result:
                    with tab_objects[tab_idx]:
                        display_assq_detailed_results(result['assq_evaluation'])
                    tab_idx += 1
                
                # 量表对比
                if len(selected_scales) > 1 and 'scale_comparison' in result:
                    with tab_objects[tab_idx]:
                        display_scale_comparison(result)
            
            # 对话预览
            with st.expander("💬 查看生成的行为对话", expanded=False):
                dialogue_lines = result['dialogue'].split('\n')[:20]
                for line in dialogue_lines:
                    if ':' in line and line.strip():
                        if '孤独症儿童' in line:
                            st.markdown(f"🧒 {line}")
                        else:
                            st.markdown(f"👤 {line}")
                
                if len(result['dialogue'].split('\n')) > 20:
                    st.markdown("*...完整对话已保存*")
                
        else:
            st.error(f"❌ 评估失败: {result['error']}")
    
    # 保存配置
    if st.button("💾 保存评估配置", use_container_width=True):
        st.session_state.custom_autism_profile = custom_profile
        st.session_state.custom_scene_config = {
            'scene': selected_scene,
            'activity': selected_activity,
            'trigger': selected_trigger,
            'scales': selected_scales  # 保存量表选择
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


def display_cars_detailed_results(cars_eval):
    """显示CARS量表详细结果"""
    st.write("#### CARS量表评估结果")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总分", f"{cars_eval['total_score']:.1f}")
    with col2:
        st.metric("严重程度", cars_eval['severity'])
    with col3:
        st.metric("临床截断", "阳性" if cars_eval['clinical_cutoff'] else "阴性")
    
    # 显示各项目得分
    st.write("**CARS各项目评分：**")
    items_df = pd.DataFrame.from_dict(
        cars_eval['item_scores'], 
        orient='index', 
        columns=['评分']
    )
    items_df = items_df.sort_values('评分', ascending=False)
    
    # 使用颜色标记高分项目
    st.dataframe(
        items_df.style.background_gradient(cmap='RdYlGn_r', vmin=1, vmax=4),
        use_container_width=True
    )
    
    # 解释和建议
    if 'interpretation' in cars_eval:
        st.info(f"**临床解释**: {cars_eval['interpretation']['clinical_significance']}")
        if cars_eval['interpretation']['recommendations']:
            st.write("**干预建议**:")
            for rec in cars_eval['interpretation']['recommendations']:
                st.write(f"• {rec}")


def display_assq_detailed_results(assq_eval):
    """显示ASSQ筛查详细结果"""
    st.write("#### ASSQ筛查评估结果")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总分", assq_eval['total_score'])
    with col2:
        st.metric("筛查结果", assq_eval['screening_result']['screening_result'])
    with col3:
        st.metric("风险等级", assq_eval['risk_level'])
    
    # 类别得分
    if 'category_scores' in assq_eval:
        st.write("**各类别得分：**")
        cat_df = pd.DataFrame.from_dict(
            assq_eval['category_scores'], 
            orient='index', 
            columns=['得分']
        )
        st.bar_chart(cat_df)
    
    # 筛查建议
    if 'screening_result' in assq_eval:
        result = assq_eval['screening_result']
        if result['recommendations']:
            st.write("**筛查建议：**")
            for rec in result['recommendations']:
                st.write(f"• {rec}")


def display_scale_comparison(result):
    """显示量表对比分析"""
    st.write("#### 量表对比分析")
    
    if 'scale_comparison' in result:
        comparison = result['scale_comparison']
        
        # 一致性评估
        if 'consistency' in comparison and comparison['consistency']:
            consistency = comparison['consistency'].get('overall', '未评估')
            if consistency == '一致':
                st.success(f"✅ 量表评估结果一致")
            elif consistency == '部分一致':
                st.warning(f"⚠️ 量表评估结果部分一致")
            else:
                st.error(f"❌ 量表评估结果不一致")
        
        # 严重程度对比
        if 'severity_agreement' in comparison:
            st.write("**各量表严重程度判断：**")
            severity_df = pd.DataFrame.from_dict(
                comparison['severity_agreement'], 
                orient='index', 
                columns=['严重程度']
            )
            st.table(severity_df)
        
        # 关键发现
        if 'key_findings' in comparison and comparison['key_findings']:
            st.write("**关键发现：**")
            for finding in comparison['key_findings']:
                st.info(finding)