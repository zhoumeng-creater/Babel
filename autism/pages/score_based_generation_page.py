"""基于分数生成对话页面

根据目标评估分数生成相应的孤独症儿童行为对话
"""
import streamlit as st
import pandas as pd
import datetime
import json
import plotly.graph_objects as go
from typing import Dict, Any, List

from autism.configs import CLINICAL_SCENE_CONFIG
from autism.generation.score_to_profile_mapper import ScoreToProfileMapper
from autism.generation.score_based_dialogue_generator import ScoreBasedDialogueGenerator


def page_score_based_generation():
    """分数生成页面主函数"""
    st.header("🎯 基于评估分数生成对话")
    st.markdown("根据目标评估分数反向生成符合该分数特征的孤独症儿童行为对话")
    
    # 创建选项卡
    tabs = st.tabs([
        "📝 单次生成",
        "📊 批量生成",
        "📥 分数导入",
        "🔍 验证工具"
    ])
    
    with tabs[0]:
        single_score_generation()
    
    with tabs[1]:
        batch_score_generation()
    
    with tabs[2]:
        score_import_generation()
    
    with tabs[3]:
        score_validation_tool()


def single_score_generation():
    """单次分数生成"""
    st.subheader("📝 根据单个分数集生成对话")
    
    # 初始化生成器
    if 'score_generator' not in st.session_state:
        st.session_state.score_generator = ScoreBasedDialogueGenerator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 1️⃣ 设置目标分数")
        
        # 选择要设置的量表
        use_abc = st.checkbox("ABC量表", value=True)
        use_dsm5 = st.checkbox("DSM-5标准", value=True)
        use_cars = st.checkbox("CARS量表", value=False)
        use_assq = st.checkbox("ASSQ筛查", value=False)
        
        target_scores = {}
        
        if use_abc:
            abc_score = st.slider(
                "ABC总分 (0-158)",
                min_value=0,
                max_value=158,
                value=75,
                help="≥67分为孤独症，53-66分为轻度，<53分为非孤独症"
            )
            target_scores['abc_total'] = abc_score
            
            # 显示对应的严重程度
            if abc_score >= 101:
                st.info("对应：重度孤独症")
            elif abc_score >= 67:
                st.info("对应：中度孤独症")
            elif abc_score >= 53:
                st.info("对应：轻度孤独症")
            else:
                st.info("对应：边缘或正常")
        
        if use_dsm5:
            dsm5_score = st.slider(
                "DSM-5核心症状 (1.0-5.0)",
                min_value=1.0,
                max_value=5.0,
                value=3.5,
                step=0.1,
                help="分数越高，症状越严重"
            )
            target_scores['dsm5_core'] = dsm5_score
            
            if dsm5_score >= 4.0:
                st.info("对应：需要非常大量支持")
            elif dsm5_score >= 3.0:
                st.info("对应：需要大量支持")
            elif dsm5_score >= 2.0:
                st.info("对应：需要支持")
            else:
                st.info("对应：需要较少支持")
        
        if use_cars:
            cars_score = st.slider(
                "CARS总分 (15-60)",
                min_value=15,
                max_value=60,
                value=35,
                help="≥37为重度，30-36为中度，<30为轻度或正常"
            )
            target_scores['cars_total'] = cars_score
            
            if cars_score >= 37:
                st.info("对应：重度孤独症")
            elif cars_score >= 30:
                st.info("对应：中度孤独症")
            else:
                st.info("对应：轻度或正常")
        
        if use_assq:
            assq_score = st.slider(
                "ASSQ筛查分 (0-54)",
                min_value=0,
                max_value=54,
                value=20,
                help="≥22为高风险，15-21为中风险，<15为低风险"
            )
            target_scores['assq_total'] = assq_score
            
            if assq_score >= 22:
                st.info("对应：高风险")
            elif assq_score >= 15:
                st.info("对应：中风险")
            else:
                st.info("对应：低风险")
    
    with col2:
        st.write("### 2️⃣ 场景设置")
        
        # 选择评估场景
        selected_scene = st.selectbox(
            "选择评估场景",
            list(CLINICAL_SCENE_CONFIG.keys()),
            help="选择生成对话的场景背景"
        )
        
        scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
        
        selected_activity = st.selectbox(
            "选择活动",
            scene_data['activities']
        )
        
        selected_trigger = st.selectbox(
            "选择触发因素",
            scene_data['triggers']
        )
        
        # 生成参数
        st.write("### 生成参数")
        
        max_attempts = st.number_input(
            "最大尝试次数",
            min_value=1,
            max_value=5,
            value=3,
            help="生成对话的最大尝试次数，以获得最接近目标分数的结果"
        )
        
        # 显示容差设置
        with st.expander("容差设置"):
            st.write("各量表的容差范围：")
            st.write("- ABC总分: ±10分")
            st.write("- DSM-5核心: ±0.5")
            st.write("- CARS总分: ±5分")
            st.write("- ASSQ筛查: ±5分")
    
    # 生成按钮
    st.divider()
    
    if st.button("🚀 生成对话", type="primary", use_container_width=True):
        if not target_scores:
            st.error("请至少选择一个量表并设置目标分数")
        else:
            with st.spinner("正在生成符合目标分数的对话..."):
                # 准备场景配置
                scene_config = {
                    'scene': selected_scene,
                    'activity': selected_activity,
                    'trigger': selected_trigger
                }
                
                # 确定要验证的量表
                scales_to_validate = []
                if 'abc_total' in target_scores:
                    scales_to_validate.append('ABC')
                if 'dsm5_core' in target_scores:
                    scales_to_validate.append('DSM5')
                if 'cars_total' in target_scores:
                    scales_to_validate.append('CARS')
                if 'assq_total' in target_scores:
                    scales_to_validate.append('ASSQ')
                
                # 修改生成器的最大尝试次数
                st.session_state.score_generator.max_generation_attempts = max_attempts
                
                # 生成对话
                result = st.session_state.score_generator.generate_from_scores(
                    target_scores,
                    scene_config,
                    scales_to_validate,
                    verbose=True
                )
                
                # 保存结果
                st.session_state.score_generation_result = result
                
                if result['success']:
                    st.success("✅ 成功生成符合目标分数的对话！")
                else:
                    st.warning("⚠️ 生成的对话接近但未完全匹配目标分数")
    
    # 显示结果
    if 'score_generation_result' in st.session_state:
        display_score_generation_results(st.session_state.score_generation_result)


def display_score_generation_results(result: Dict[str, Any]):
    """显示分数生成结果"""
    st.divider()
    st.subheader("📊 生成结果")
    
    # 创建选项卡
    tabs = st.tabs(["分数对比", "生成的对话", "特征配置", "生成历史"])
    
    with tabs[0]:
        st.write("### 目标分数 vs 实际分数")
        
        # 显示分数对比
        comparison_data = []
        for scale in result['target_scores']:
            target = result['target_scores'][scale]
            actual = result['actual_scores'].get(scale, 0)
            deviation = result['score_deviations'].get(scale, 0)
            
            scale_name = {
                'abc_total': 'ABC总分',
                'dsm5_core': 'DSM-5核心',
                'cars_total': 'CARS总分',
                'assq_total': 'ASSQ筛查'
            }.get(scale, scale)
            
            comparison_data.append({
                '量表': scale_name,
                '目标分数': target,
                '实际分数': actual,
                '偏差': f"{deviation:+.1f}",
                '状态': '✅' if abs(deviation) <= st.session_state.score_generator.score_tolerance.get(scale, 5) else '⚠️'
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # 可视化对比
        create_score_comparison_chart(result['target_scores'], result['actual_scores'])
        
        # 显示评估结果
        if 'evaluation_result' in result:
            st.write("### 详细评估结果")
            
            eval_result = result['evaluation_result']
            
            if 'abc_evaluation' in eval_result:
                with st.expander("ABC量表评估详情"):
                    abc_eval = eval_result['abc_evaluation']
                    st.write(f"**总分**: {abc_eval['total_score']}")
                    st.write(f"**严重程度**: {abc_eval['severity']}")
                    st.write("**领域得分**:")
                    for domain, score in abc_eval['domain_scores'].items():
                        st.write(f"  - {domain}: {score}")
            
            if 'dsm5_evaluation' in eval_result:
                with st.expander("DSM-5评估详情"):
                    dsm5_eval = eval_result['dsm5_evaluation']
                    st.write(f"**核心症状平均分**: {dsm5_eval['core_symptom_average']:.2f}")
                    st.write("**各维度得分**:")
                    for dim, score in dsm5_eval['scores'].items():
                        st.write(f"  - {dim}: {score}")
    
    with tabs[1]:
        st.write("### 生成的对话内容")
        st.text_area(
            "对话",
            result['dialogue'],
            height=400,
            disabled=True
        )
        
        # 下载按钮
        st.download_button(
            label="📥 下载对话",
            data=result['dialogue'],
            file_name=f"score_generated_dialogue_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with tabs[2]:
        st.write("### 生成的孤独症特征配置")
        
        profile = result['autism_profile']
        
        st.write(f"**严重程度**: {profile.get('severity_level', '未知')}")
        st.write(f"**社交特征**: {profile.get('social_characteristics', '')}")
        st.write(f"**沟通特征**: {profile.get('communication_characteristics', '')}")
        st.write(f"**行为特征**: {profile.get('behavioral_characteristics', '')}")
        st.write(f"**认知特征**: {profile.get('cognitive_characteristics', '')}")
        st.write(f"**情绪特征**: {profile.get('emotional_characteristics', '')}")
        st.write(f"**日常生活**: {profile.get('daily_living', '')}")
        
        if 'behavioral_examples' in profile:
            st.write("**行为示例**:")
            for i, example in enumerate(profile['behavioral_examples'], 1):
                st.write(f"{i}. {example}")
    
    with tabs[3]:
        st.write("### 生成尝试历史")
        
        if 'generation_history' in result:
            history = result['generation_history']
            st.write(f"共尝试 {len(history)} 次")
            
            # 显示每次尝试的结果
            for attempt in history:
                with st.expander(f"第 {attempt['attempt']} 次尝试"):
                    st.write(f"**距离分数**: {attempt['distance']:.3f}")
                    st.write("**实际分数**:")
                    for scale, score in attempt['actual_scores'].items():
                        st.write(f"  - {scale}: {score}")


def create_score_comparison_chart(target_scores: Dict[str, float], actual_scores: Dict[str, float]):
    """创建分数对比图表"""
    scales = []
    targets = []
    actuals = []
    
    scale_names = {
        'abc_total': 'ABC',
        'dsm5_core': 'DSM-5',
        'cars_total': 'CARS',
        'assq_total': 'ASSQ'
    }
    
    for scale in target_scores:
        if scale in actual_scores:
            scales.append(scale_names.get(scale, scale))
            
            # 归一化到0-100范围
            if scale == 'abc_total':
                targets.append(target_scores[scale] / 158 * 100)
                actuals.append(actual_scores[scale] / 158 * 100)
            elif scale == 'dsm5_core':
                targets.append(target_scores[scale] / 5 * 100)
                actuals.append(actual_scores[scale] / 5 * 100)
            elif scale == 'cars_total':
                targets.append(target_scores[scale] / 60 * 100)
                actuals.append(actual_scores[scale] / 60 * 100)
            elif scale == 'assq_total':
                targets.append(target_scores[scale] / 54 * 100)
                actuals.append(actual_scores[scale] / 54 * 100)
    
    # 创建雷达图
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=targets,
        theta=scales,
        fill='toself',
        name='目标分数',
        line_color='blue'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=actuals,
        theta=scales,
        fill='toself',
        name='实际分数',
        line_color='green'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="分数匹配度雷达图（归一化）"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def batch_score_generation():
    """批量分数生成"""
    st.subheader("📊 批量生成对话")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 批量分数设置")
        
        # 预设分数组合
        preset = st.selectbox(
            "选择预设组合",
            ["自定义", "轻中重三组", "ABC量表全范围", "DSM-5全范围"]
        )
        
        if preset == "轻中重三组":
            score_sets = [
                {"abc_total": 45, "dsm5_core": 2.0},  # 轻度
                {"abc_total": 75, "dsm5_core": 3.0},  # 中度
                {"abc_total": 105, "dsm5_core": 4.0}  # 重度
            ]
            st.json(score_sets)
        
        elif preset == "ABC量表全范围":
            score_sets = [
                {"abc_total": 30},
                {"abc_total": 60},
                {"abc_total": 90},
                {"abc_total": 120},
                {"abc_total": 150}
            ]
            st.json(score_sets)
        
        elif preset == "DSM-5全范围":
            score_sets = [
                {"dsm5_core": 1.5},
                {"dsm5_core": 2.5},
                {"dsm5_core": 3.5},
                {"dsm5_core": 4.5}
            ]
            st.json(score_sets)
        
        else:  # 自定义
            st.write("请输入JSON格式的分数集合")
            score_json = st.text_area(
                "分数集合 (JSON格式)",
                value='[{"abc_total": 75, "dsm5_core": 3.5}]',
                height=150
            )
            
            try:
                score_sets = json.loads(score_json)
                st.success(f"已解析 {len(score_sets)} 组分数")
            except json.JSONDecodeError:
                st.error("JSON格式错误")
                score_sets = []
    
    with col2:
        st.write("### 批量生成参数")
        
        use_same_scene = st.checkbox("使用相同场景", value=True)
        
        if use_same_scene:
            selected_scene = st.selectbox(
                "选择场景",
                list(CLINICAL_SCENE_CONFIG.keys())
            )
            scene_data = CLINICAL_SCENE_CONFIG[selected_scene]
            selected_activity = st.selectbox("活动", scene_data['activities'])
            selected_trigger = st.selectbox("触发", scene_data['triggers'])
        
        # 执行批量生成
        if st.button("🚀 开始批量生成", type="primary"):
            if not score_sets:
                st.error("请设置有效的分数集合")
            else:
                # 初始化生成器
                if 'score_generator' not in st.session_state:
                    st.session_state.score_generator = ScoreBasedDialogueGenerator()
                
                # 准备场景配置
                if use_same_scene:
                    scene_configs = [{
                        'scene': selected_scene,
                        'activity': selected_activity,
                        'trigger': selected_trigger
                    }] * len(score_sets)
                else:
                    scene_configs = None
                
                # 批量生成
                with st.spinner(f"正在批量生成 {len(score_sets)} 个对话..."):
                    results = st.session_state.score_generator.generate_batch_from_scores(
                        score_sets,
                        scene_configs
                    )
                    
                    st.session_state.batch_generation_results = results
                    st.success(f"✅ 成功生成 {len(results)} 个对话")
    
    # 显示批量结果
    if 'batch_generation_results' in st.session_state:
        display_batch_generation_results(st.session_state.batch_generation_results)


def display_batch_generation_results(results: List[Dict[str, Any]]):
    """显示批量生成结果"""
    st.divider()
    st.subheader("批量生成结果")
    
    # 汇总统计
    success_count = sum(1 for r in results if r['success'])
    st.metric("成功率", f"{success_count}/{len(results)}")
    
    # 结果表格
    result_data = []
    for r in results:
        row = {
            '序号': r['batch_index'],
            '状态': '✅' if r['success'] else '⚠️'
        }
        
        # 添加目标分数
        for scale in r['target_scores']:
            scale_name = {
                'abc_total': 'ABC目标',
                'dsm5_core': 'DSM5目标',
                'cars_total': 'CARS目标',
                'assq_total': 'ASSQ目标'
            }.get(scale, scale)
            row[scale_name] = r['target_scores'][scale]
        
        # 添加实际分数
        for scale in r['actual_scores']:
            scale_name = {
                'abc_total': 'ABC实际',
                'dsm5_core': 'DSM5实际',
                'cars_total': 'CARS实际',
                'assq_total': 'ASSQ实际'
            }.get(scale, scale)
            row[scale_name] = r['actual_scores'][scale]
        
        result_data.append(row)
    
    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df, use_container_width=True)
    
    # 导出功能
    if st.button("📥 导出所有结果"):
        # 准备导出数据
        export_data = []
        for r in results:
            export_data.append({
                'experiment_id': r['experiment_id'],
                'success': r['success'],
                'target_scores': r['target_scores'],
                'actual_scores': r['actual_scores'],
                'dialogue': r['dialogue'][:500] + '...'  # 截断对话
            })
        
        # 转换为JSON
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="下载JSON",
            data=export_json,
            file_name=f"batch_score_generation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def score_import_generation():
    """分数导入生成"""
    st.subheader("📥 从文件导入分数生成对话")
    
    uploaded_file = st.file_uploader(
        "上传分数文件",
        type=['csv', 'json', 'xlsx'],
        help="支持CSV、JSON、Excel格式"
    )
    
    if uploaded_file:
        # 解析文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.write("### 导入的数据预览")
            st.dataframe(df.head())
            
            # 映射列名
            st.write("### 列名映射")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                abc_col = st.selectbox(
                    "ABC总分列",
                    ['无'] + list(df.columns),
                    index=0
                )
            
            with col2:
                dsm5_col = st.selectbox(
                    "DSM5核心症状列",
                    ['无'] + list(df.columns),
                    index=0
                )
            
            with col3:
                cars_col = st.selectbox(
                    "CARS总分列",
                    ['无'] + list(df.columns),
                    index=0
                )
            
            with col4:
                assq_col = st.selectbox(
                    "ASSQ筛查分列",
                    ['无'] + list(df.columns),
                    index=0
                )
            
            # 转换为分数集合
            if st.button("转换并生成"):
                score_sets = []
                
                for _, row in df.iterrows():
                    scores = {}
                    if abc_col != '无':
                        scores['abc_total'] = float(row[abc_col])
                    if dsm5_col != '无':
                        scores['dsm5_core'] = float(row[dsm5_col])
                    if cars_col != '无':
                        scores['cars_total'] = float(row[cars_col])
                    if assq_col != '无':
                        scores['assq_total'] = float(row[assq_col])
                    
                    if scores:
                        score_sets.append(scores)
                
                if score_sets:
                    st.success(f"已转换 {len(score_sets)} 组分数")
                    st.session_state.imported_score_sets = score_sets
                    
                    # TODO: 调用批量生成
                    st.info("请使用批量生成功能处理导入的分数")
                else:
                    st.error("未能提取有效的分数数据")
        
        elif uploaded_file.name.endswith('.json'):
            try:
                data = json.load(uploaded_file)
                st.json(data)
                # TODO: 处理JSON数据
            except Exception as e:
                st.error(f"JSON解析错误: {e}")
        
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            st.dataframe(df.head())
            # TODO: 处理Excel数据


def score_validation_tool():
    """分数验证工具"""
    st.subheader("🔍 对话分数验证工具")
    st.markdown("验证已有对话是否符合目标分数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 输入对话")
        dialogue = st.text_area(
            "对话内容",
            height=300,
            placeholder="粘贴要验证的对话内容..."
        )
        
        st.write("### 目标分数")
        target_scores = {}
        
        use_abc = st.checkbox("验证ABC分数", value=True)
        if use_abc:
            target_scores['abc_total'] = st.number_input(
                "ABC目标分数",
                min_value=0,
                max_value=158,
                value=75
            )
        
        use_dsm5 = st.checkbox("验证DSM-5分数", value=True)
        if use_dsm5:
            target_scores['dsm5_core'] = st.number_input(
                "DSM-5目标分数",
                min_value=1.0,
                max_value=5.0,
                value=3.5,
                step=0.1
            )
    
    with col2:
        st.write("### 验证设置")
        
        # 选择场景（用于评估）
        selected_scene = st.selectbox(
            "评估场景",
            list(CLINICAL_SCENE_CONFIG.keys())
        )
        
        # 选择严重程度模板（用于评估）
        from autism.configs import UNIFIED_AUTISM_PROFILES
        selected_template = st.selectbox(
            "参考模板",
            list(UNIFIED_AUTISM_PROFILES.keys())
        )
        
        if st.button("🔍 验证对话", type="primary"):
            if not dialogue or not target_scores:
                st.error("请输入对话和目标分数")
            else:
                # 初始化生成器
                if 'score_generator' not in st.session_state:
                    st.session_state.score_generator = ScoreBasedDialogueGenerator()
                
                # 验证对话
                with st.spinner("正在验证对话..."):
                    validation_result = st.session_state.score_generator.validate_dialogue_against_scores(
                        dialogue,
                        target_scores,
                        UNIFIED_AUTISM_PROFILES[selected_template],
                        {'scene': selected_scene, 'activity': '', 'trigger': ''}
                    )
                    
                    st.session_state.validation_result = validation_result
    
    # 显示验证结果
    if 'validation_result' in st.session_state:
        display_validation_results(st.session_state.validation_result)


def display_validation_results(validation: Dict[str, Any]):
    """显示验证结果"""
    st.divider()
    st.subheader("验证结果")
    
    if validation['passed']:
        st.success("✅ 对话符合目标分数要求！")
    else:
        st.warning("⚠️ 对话与目标分数存在偏差")
    
    # 显示偏差详情
    st.write("### 分数偏差分析")
    
    deviation_data = []
    for scale, dev_info in validation['deviations'].items():
        scale_name = {
            'abc_total': 'ABC总分',
            'dsm5_core': 'DSM-5核心',
            'cars_total': 'CARS总分',
            'assq_total': 'ASSQ筛查'
        }.get(scale, scale)
        
        deviation_data.append({
            '量表': scale_name,
            '目标': validation['target_scores'][scale],
            '实际': validation['actual_scores'][scale],
            '偏差': f"{dev_info['absolute']:+.1f}",
            '偏差率': f"{dev_info['percentage']:+.1f}%",
            '容差内': '✅' if dev_info['within_tolerance'] else '❌'
        })
    
    deviation_df = pd.DataFrame(deviation_data)
    st.dataframe(deviation_df, use_container_width=True, hide_index=True)