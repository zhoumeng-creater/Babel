"""数据分析页面 - 修复版本"""
import streamlit as st
import numpy as np

from autism.analysis import generate_clinical_analysis, get_behavior_summary_stats
from autism.ui_components.visualization import (
    create_correlation_scatter,
    display_abc_analysis,
    display_dsm5_analysis,
    display_comprehensive_comparison,
    display_statistical_analysis
)


def page_data_analysis():
    """数据分析页面 - 支持双重评估数据分析"""
    st.header("📈 临床数据分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行临床评估")
        st.stop()
    
    # 添加数据格式检查和迁移功能
    if st.sidebar.button("🔧 修复数据格式"):
        with st.spinner("正在标准化数据格式..."):
            migrated_count = _migrate_data_format()
            if migrated_count > 0:
                st.success(f"✅ 成功标准化 {migrated_count} 条记录")
                st.rerun()
            else:
                st.info("📊 所有数据已经是标准格式")
    
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
        # 计算平均ABC总分 - 添加格式兼容性检查
        abc_scores = []
        for r in records:
            if 'abc_evaluation' in r:
                # 新格式
                abc_scores.append(r['abc_evaluation']['total_score'])
            elif 'abc_total_score' in r:
                # 旧格式
                abc_scores.append(r['abc_total_score'])
            elif 'evaluation_scores' in r and r.get('assessment_standard') == 'ABC':
                # 计算旧格式的总分
                total = sum(r['evaluation_scores'].values())
                abc_scores.append(total)
        
        if abc_scores:
            avg_abc = np.mean(abc_scores)
            st.metric("平均ABC总分", f"{avg_abc:.1f}")
        else:
            st.metric("平均ABC总分", "N/A")
            
    with col4:
        # 计算平均DSM-5核心症状 - 添加格式兼容性检查
        dsm5_scores = []
        for r in records:
            if 'dsm5_evaluation' in r:
                # 新格式
                dsm5_scores.append(r['dsm5_evaluation']['core_symptom_average'])
            elif 'dsm5_core_symptom_average' in r:
                # 旧格式
                dsm5_scores.append(r['dsm5_core_symptom_average'])
            elif 'evaluation_scores' in r and r.get('assessment_standard') == 'DSM5':
                # 计算旧格式的核心症状均分
                scores = r['evaluation_scores']
                core_metrics = ['社交情感互惠缺陷', '非言语交流缺陷', 
                              '发展维持关系缺陷', '刻板重复动作']
                core_scores = [scores.get(m, 0) for m in core_metrics if m in scores]
                if core_scores:
                    dsm5_scores.append(np.mean(core_scores))
        
        if dsm5_scores:
            avg_dsm5 = np.mean(dsm5_scores)
            st.metric("平均DSM-5核心", f"{avg_dsm5:.2f}")
        else:
            st.metric("平均DSM-5核心", "N/A")
    
    # 评估一致性分析 - 只分析包含两种评估的记录
    unified_records = [r for r in records if 
                      ('abc_evaluation' in r and 'dsm5_evaluation' in r) or
                      ('abc_total_score' in r and 'dsm5_core_symptom_average' in r)]
    
    if unified_records:
        st.subheader("🔄 ABC与DSM-5评估一致性分析")
        
        consistency_results = _analyze_consistency(unified_records)
        
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
        fig_scatter = create_correlation_scatter(unified_records)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("📊 没有包含双重评估的记录，无法进行一致性分析")
    
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


def _analyze_consistency(records):
    """分析ABC和DSM-5评估的一致性 - 支持新旧格式"""
    from scipy import stats
    
    abc_scores = []
    dsm5_scores = []
    agreements = 0
    
    for record in records:
        # 获取ABC总分 - 支持新旧格式
        if 'abc_evaluation' in record:
            abc_total = record['abc_evaluation']['total_score']
        elif 'abc_total_score' in record:
            abc_total = record['abc_total_score']
        else:
            # 从evaluation_scores计算
            abc_total = sum(record.get('evaluation_scores', {}).values())
        
        # 获取DSM5核心症状均分 - 支持新旧格式
        if 'dsm5_evaluation' in record:
            dsm5_core = record['dsm5_evaluation']['core_symptom_average']
        elif 'dsm5_core_symptom_average' in record:
            dsm5_core = record['dsm5_core_symptom_average']
        else:
            # 从evaluation_scores计算
            scores = record.get('evaluation_scores', {})
            core_metrics = ['社交情感互惠缺陷', '非言语交流缺陷', 
                          '发展维持关系缺陷', '刻板重复动作']
            core_scores = [scores.get(m, 0) for m in core_metrics if m in scores]
            dsm5_core = np.mean(core_scores) if core_scores else 0
        
        # 标准化分数
        abc_normalized = abc_total / 158
        dsm5_normalized = dsm5_core / 5
        
        abc_scores.append(abc_normalized)
        dsm5_scores.append(dsm5_normalized)
        
        # 判断一致性
        abc_severe = abc_total >= 67
        dsm5_severe = dsm5_core >= 3.5
        if abc_severe == dsm5_severe:
            agreements += 1
    
    # 计算相关性和p值
    if len(records) > 1:
        correlation, p_value = stats.pearsonr(abc_scores, dsm5_scores)
    else:
        correlation, p_value = 0, 1
    
    return {
        'correlation': correlation,
        'p_value': p_value,
        'agreement_rate': (agreements / len(records)) * 100 if records else 0,
        'mean_difference': np.mean([abs(a - d) for a, d in zip(abc_scores, dsm5_scores)])
    }


def _migrate_data_format():
    """迁移所有记录到标准格式"""
    records = st.session_state.experiment_records
    migrated_count = 0
    
    # 领域名称映射
    domain_mapping = {
        '感觉': '感觉领域得分',
        '交往': '交往领域得分',
        '躯体运动': '躯体运动领域得分',
        '运动': '躯体运动领域得分',
        '语言': '语言领域得分',
        '社交与自理': '社交与自理领域得分',
        '自理': '社交与自理领域得分'
    }
    
    for record in records:
        needs_migration = False
        
        # 检查并迁移ABC评估数据
        if 'abc_evaluation' in record and 'domain_scores' in record['abc_evaluation']:
            domain_scores = record['abc_evaluation']['domain_scores']
            new_domain_scores = {}
            
            for domain, score in domain_scores.items():
                # 标准化领域名称
                if domain in domain_mapping:
                    normalized_domain = domain_mapping[domain]
                    needs_migration = True
                elif not domain.endswith('领域得分'):
                    normalized_domain = f"{domain}领域得分"
                    needs_migration = True
                else:
                    normalized_domain = domain
                
                new_domain_scores[normalized_domain] = score
            
            if needs_migration:
                record['abc_evaluation']['domain_scores'] = new_domain_scores
                migrated_count += 1
        
        # 处理旧格式数据
        elif 'evaluation_scores' in record and record.get('assessment_standard') == 'ABC':
            # 转换为新格式
            scores = record['evaluation_scores']
            total_score = sum(scores.values())
            
            # 计算领域分数
            domain_scores = {}
            
            # 尝试从evaluation_scores中提取
            for key, value in scores.items():
                if key in domain_mapping:
                    normalized_key = domain_mapping[key]
                    domain_scores[normalized_key] = value
            
            # 如果没有找到，使用默认计算
            if not domain_scores:
                domain_scores = {
                    '感觉领域得分': sum(scores.get(item, 0) for item in ['感觉', '感觉异常'] if item in scores),
                    '交往领域得分': sum(scores.get(item, 0) for item in ['交往', '人际交往困难'] if item in scores),
                    '躯体运动领域得分': scores.get('躯体运动', 0),
                    '语言领域得分': sum(scores.get(item, 0) for item in ['语言', '重复性语言'] if item in scores),
                    '社交与自理领域得分': scores.get('生活自理', 0)
                }
            
            # 计算严重程度
            if total_score <= 30:
                severity = '无明显症状'
            elif total_score <= 67:
                severity = '轻度'
            elif total_score <= 100:
                severity = '中度'
            else:
                severity = '重度'
            
            # 创建新格式的评估数据
            record['abc_evaluation'] = {
                'total_score': total_score,
                'severity': severity,
                'domain_scores': domain_scores,
                'identified_behaviors': {}
            }
            
            # 如果没有DSM5评估，添加空的
            if 'dsm5_evaluation' not in record:
                record['dsm5_evaluation'] = {
                    'core_symptom_average': 0,
                    'scores': {},
                    'note': '此记录仅包含ABC评估'
                }
            
            migrated_count += 1
    
    return migrated_count