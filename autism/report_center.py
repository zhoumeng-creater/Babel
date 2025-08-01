"""孤独症平台报告中心页面 - 支持统一评估和对比分析"""
import streamlit as st
import pandas as pd
import datetime
import json
import numpy as np

from common.config import EXCEL_AVAILABLE
from common.exporters import (
    export_to_csv, export_to_json, export_to_excel, 
    create_excel_workbook, apply_excel_styles, create_zip_package
)
from common.exporters.text_exporter import export_to_text
from .analyzer import generate_clinical_analysis, prepare_clinical_export_data


def page_report_center():
    """报告中心页面 - 支持统一评估报告和对比分析"""
    st.header("📊 临床评估报告中心")
    st.markdown("生成统一评估报告，包含ABC量表和DSM-5标准的综合分析")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行临床评估")
        st.stop()
    
    # 分析记录类型
    unified_records = [r for r in records if r.get('assessment_standard') == 'UNIFIED']
    legacy_abc_records = [r for r in records if r.get('assessment_standard') == 'ABC']
    legacy_dsm5_records = [r for r in records if r.get('assessment_standard') == 'DSM5']
    
    st.success(f"📊 当前共有 {len(records)} 条评估记录可生成报告")
    
    col_std1, col_std2, col_std3 = st.columns(3)
    with col_std1:
        st.info(f"📋 统一评估: {len(unified_records)} 条")
    with col_std2:
        st.info(f"📋 旧版ABC评估: {len(legacy_abc_records)} 条")
    with col_std3:
        st.info(f"📋 旧版DSM-5评估: {len(legacy_dsm5_records)} 条")
    
    # 报告类型选择
    st.subheader("📋 选择报告类型")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📄 标准报告")
        
        # 基础CSV报告
        if st.button("📊 下载评估数据 (CSV)", use_container_width=True):
            export_data = prepare_unified_export_data(records)
            csv_content = export_to_csv(export_data)
            
            st.download_button(
                label="⬇️ 下载评估数据",
                data=csv_content,
                file_name=f"autism_unified_assessment_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
        
        # 行为记录下载
        if st.button("💬 下载行为观察记录 (TXT)", use_container_width=True):
            observation_content = create_unified_observation_text(records)
            
            st.download_button(
                label="⬇️ 下载行为观察记录",
                data=export_to_text(observation_content),
                file_name=f"autism_behavior_observations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime='text/plain'
            )
        
        # JSON完整数据
        if st.button("🔧 下载完整数据 (JSON)", use_container_width=True):
            json_data = create_unified_json_data(records)
            json_str = export_to_json(json_data)
            
            st.download_button(
                label="⬇️ 下载完整数据",
                data=json_str.encode('utf-8'),
                file_name=f"autism_complete_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime='application/json'
            )
    
    with col2:
        st.write("### 📈 专业分析报告")
        
        # 生成分析报告
        if st.button("📊 生成统计分析", use_container_width=True):
            with st.spinner("正在生成分析报告..."):
                analysis = generate_unified_clinical_analysis(records)
            
            st.success("✅ 分析报告生成完成！")
            
            # 显示分析预览
            with st.expander("📋 分析报告预览", expanded=True):
                display_unified_analysis_preview(analysis, records)
            
            # 提供分析报告下载
            analysis_json = export_to_json(analysis)
            st.download_button(
                label="⬇️ 下载分析报告 (JSON)",
                data=analysis_json.encode('utf-8'),
                file_name=f"autism_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime='application/json'
            )
        
        # Excel专业报告
        if EXCEL_AVAILABLE:
            if st.button("📋 生成专业Excel报告", use_container_width=True):
                with st.spinner("正在生成专业Excel报告..."):
                    analysis = generate_unified_clinical_analysis(records)
                    excel_data = create_unified_excel_report(records, analysis)
                
                if excel_data:
                    st.success("✅ 专业Excel报告生成完成！")
                    
                    st.download_button(
                        label="⬇️ 下载专业Excel报告",
                        data=excel_data,
                        file_name=f"autism_professional_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                else:
                    st.error("❌ Excel报告生成失败，请尝试其他格式")
        else:
            st.info("💡 Excel报告功能需要安装openpyxl模块")
            st.code("pip install openpyxl")
            
            # 替代详细报告
            if st.button("📊 生成详细文本报告", use_container_width=True):
                with st.spinner("正在生成详细报告..."):
                    analysis = generate_unified_clinical_analysis(records)
                
                # 创建详细文本报告
                detailed_report = create_unified_detailed_text_report(records, analysis)
                
                st.success("✅ 详细文本报告生成完成！")
                
                st.download_button(
                    label="⬇️ 下载详细文本报告",
                    data=export_to_text(detailed_report),
                    file_name=f"autism_detailed_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime='text/plain'
                )
        
        # 对比分析报告（仅统一评估可用）
        if unified_records:
            if st.button("🔍 生成ABC-DSM5对比分析", use_container_width=True, type="secondary"):
                with st.spinner("正在生成对比分析..."):
                    comparison_report = generate_comparison_report(unified_records)
                
                st.success("✅ 对比分析报告生成完成！")
                
                # 显示对比分析预览
                with st.expander("📊 对比分析预览", expanded=True):
                    display_comparison_preview(comparison_report)
                
                # 下载对比报告
                comparison_json = export_to_json(comparison_report)
                st.download_button(
                    label="⬇️ 下载对比分析报告",
                    data=comparison_json.encode('utf-8'),
                    file_name=f"autism_comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime='application/json'
                )
        
        # 研究数据包
        if st.button("📦 生成完整研究数据包", use_container_width=True, type="primary"):
            with st.spinner("正在生成完整研究数据包..."):
                zip_data = create_unified_research_package(records)
            
            st.success("✅ 完整研究数据包生成完成！")
            
            st.download_button(
                label="⬇️ 下载完整研究数据包 (ZIP)",
                data=zip_data,
                file_name=f"autism_research_package_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime='application/zip'
            )
    
    # 数据统计概览
    display_unified_data_overview(records)
    
    # 数据预览
    display_unified_data_preview(records)


def prepare_unified_export_data(records):
    """准备导出数据 - 支持统一评估格式"""
    export_data = []
    
    for record in records:
        # 基础信息
        export_row = {
            '评估ID': record['experiment_id'],
            '评估时间': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            '评估类型': '统一评估' if record.get('assessment_standard') == 'UNIFIED' else record.get('assessment_standard', 'ABC'),
            '配置类型': record.get('template', '自定义'),
            '评估情境': record['scene'],
            '观察活动': record.get('activity', ''),
            '触发因素': record.get('trigger', ''),
            '备注': record.get('notes', '')
        }
        
        # 处理统一评估数据
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            # ABC评估结果
            abc_eval = record['abc_evaluation']
            export_row.update({
                'ABC总分': abc_eval['total_score'],
                'ABC严重程度': abc_eval['severity'],
                '感觉领域得分': abc_eval['domain_scores'].get('感觉领域得分', ''),
                '交往领域得分': abc_eval['domain_scores'].get('交往领域得分', ''),
                '躯体运动领域得分': abc_eval['domain_scores'].get('躯体运动领域得分', ''),
                '语言领域得分': abc_eval['domain_scores'].get('语言领域得分', ''),
                '社交与自理领域得分': abc_eval['domain_scores'].get('社交与自理领域得分', '')
            })
            
            # DSM-5评估结果
            dsm5_eval = record['dsm5_evaluation']
            export_row.update({
                '社交互动质量': dsm5_eval['scores'].get('社交互动质量', ''),
                '沟通交流能力': dsm5_eval['scores'].get('沟通交流能力', ''),
                '刻板重复行为': dsm5_eval['scores'].get('刻板重复行为', ''),
                '感官处理能力': dsm5_eval['scores'].get('感官处理能力', ''),
                '情绪行为调节': dsm5_eval['scores'].get('情绪行为调节', ''),
                '认知适应功能': dsm5_eval['scores'].get('认知适应功能', ''),
                'DSM5核心症状均值': round(dsm5_eval.get('core_symptom_average', 0), 2)
            })
            
            # 识别到的行为（前10个）
            if 'identified_behaviors' in abc_eval:
                all_behaviors = []
                for behaviors in abc_eval['identified_behaviors'].values():
                    all_behaviors.extend(behaviors)
                export_row['ABC识别行为'] = '; '.join(all_behaviors[:10])
            
            # 临床观察
            if 'clinical_observations' in dsm5_eval:
                observations = []
                for category, obs_list in dsm5_eval['clinical_observations'].items():
                    observations.extend([f"[{category}] {obs}" for obs in obs_list])
                export_row['DSM5临床观察'] = '; '.join(observations[:10])
                
        else:
            # 处理旧格式数据（向后兼容）
            if record.get('assessment_standard') == 'ABC':
                export_row.update({
                    'ABC总分': record.get('abc_total_score', ''),
                    'ABC严重程度': record.get('abc_severity', ''),
                })
                scores = record.get('evaluation_scores', {})
                for domain in ['感觉领域得分', '交往领域得分', '躯体运动领域得分', '语言领域得分', '社交与自理领域得分']:
                    export_row[domain] = scores.get(domain, '')
                    
            elif record.get('assessment_standard') == 'DSM5':
                scores = record.get('evaluation_scores', {})
                for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为', '感官处理能力', '情绪行为调节', '认知适应功能']:
                    export_row[metric] = scores.get(metric, '')
                
                if all(metric in scores for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                    core_avg = (scores['社交互动质量'] + scores['沟通交流能力'] + scores['刻板重复行为']) / 3
                    export_row['DSM5核心症状均值'] = round(core_avg, 2)
        
        export_data.append(export_row)
    
    return export_data


def create_unified_observation_text(records):
    """创建统一的行为观察记录文本"""
    observation_content = []
    observation_content.append("=" * 70)
    observation_content.append("孤独症儿童行为观察记录 - 统一评估报告")
    observation_content.append("基于ABC量表和DSM-5诊断标准的综合评估")
    observation_content.append("=" * 70)
    observation_content.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    observation_content.append(f"评估记录总数: {len(records)}")
    
    # 统计不同类型的记录
    unified_count = len([r for r in records if r.get('assessment_standard') == 'UNIFIED'])
    legacy_abc_count = len([r for r in records if r.get('assessment_standard') == 'ABC'])
    legacy_dsm5_count = len([r for r in records if r.get('assessment_standard') == 'DSM5'])
    
    observation_content.append(f"统一评估: {unified_count} 条 | 旧版ABC: {legacy_abc_count} 条 | 旧版DSM5: {legacy_dsm5_count} 条")
    observation_content.append("=" * 70)
    observation_content.append("")
    
    for i, record in enumerate(records, 1):
        observation_content.append(f"\n【评估记录 {i}】")
        observation_content.append(f"评估ID: {record['experiment_id']}")
        observation_content.append(f"评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        observation_content.append(f"配置类型: {record.get('template', '自定义')}")
        observation_content.append(f"评估情境: {record['scene']}")
        observation_content.append(f"观察活动: {record.get('activity', '未指定')}")
        observation_content.append(f"触发因素: {record.get('trigger', '未指定')}")
        
        # 统一评估格式
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            observation_content.append(f"评估类型: 统一评估（双标准）")
            observation_content.append("-" * 50)
            
            # ABC评估结果
            observation_content.append("【ABC量表评估】")
            abc_eval = record['abc_evaluation']
            observation_content.append(f"ABC总分: {abc_eval['total_score']}")
            observation_content.append(f"严重程度: {abc_eval['severity']}")
            observation_content.append("各领域得分:")
            for domain, score in abc_eval['domain_scores'].items():
                observation_content.append(f"  • {domain}: {score}")
            
            if abc_eval.get('identified_behaviors'):
                observation_content.append("识别到的主要行为:")
                for domain, behaviors in abc_eval['identified_behaviors'].items():
                    if behaviors:
                        observation_content.append(f"  {domain}: {', '.join(behaviors[:3])}")
            
            observation_content.append("")
            
            # DSM-5评估结果
            observation_content.append("【DSM-5标准评估】")
            dsm5_eval = record['dsm5_evaluation']
            observation_content.append(f"核心症状综合: {dsm5_eval.get('core_symptom_average', 0):.2f}/5.0")
            observation_content.append("各维度得分:")
            for metric, score in dsm5_eval['scores'].items():
                observation_content.append(f"  • {metric}: {score}/5.0")
            
            if dsm5_eval.get('clinical_observations'):
                observation_content.append("临床观察要点:")
                for category, observations in dsm5_eval['clinical_observations'].items():
                    if observations:
                        observation_content.append(f"  {category}: {', '.join(observations)}")
                        
        else:
            # 旧格式（向后兼容）
            if record.get('assessment_standard') == 'ABC':
                observation_content.append(f"评估类型: ABC量表")
                observation_content.append(f"ABC总分: {record.get('abc_total_score', 'N/A')}")
                observation_content.append(f"ABC严重程度: {record.get('abc_severity', 'N/A')}")
            elif record.get('assessment_standard') == 'DSM5':
                observation_content.append(f"评估类型: DSM-5标准")
                if 'evaluation_scores' in record:
                    scores = record['evaluation_scores']
                    if all(m in scores for m in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                        core_avg = (scores['社交互动质量'] + scores['沟通交流能力'] + scores['刻板重复行为']) / 3
                        observation_content.append(f"核心症状综合: {core_avg:.2f}/5.0")
            
            observation_content.append("-" * 50)
            if 'evaluation_scores' in record:
                observation_content.append("评估得分:")
                for metric, score in record['evaluation_scores'].items():
                    observation_content.append(f"  • {metric}: {score}")
        
        observation_content.append("\n行为观察对话:")
        observation_content.append(record['dialogue'])
        observation_content.append("-" * 50)
        observation_content.append("")
    
    return observation_content


def create_unified_json_data(records):
    """创建完整的JSON数据 - 支持统一评估格式"""
    # 生成分析
    analysis = generate_unified_clinical_analysis(records)
    
    json_data = {
        'assessment_report': {
            'report_metadata': {
                'generation_time': datetime.datetime.now().isoformat(),
                'assessment_tools': 'ABC量表 & DSM-5诊断标准（统一评估）',
                'total_assessments': len(records),
                'unified_assessments': len([r for r in records if r.get('assessment_standard') == 'UNIFIED']),
                'legacy_assessments': len([r for r in records if r.get('assessment_standard') != 'UNIFIED']),
                'platform_version': '统一评估版 v3.0'
            },
            'assessment_summary': analysis,
            'detailed_assessments': []
        }
    }
    
    for record in records:
        assessment_record = record.copy()
        assessment_record['timestamp'] = record['timestamp'].isoformat()
        json_data['assessment_report']['detailed_assessments'].append(assessment_record)
    
    return json_data


def create_unified_excel_report(records, analysis):
    """创建统一的Excel报告"""
    if not EXCEL_AVAILABLE:
        return None
    
    workbook = create_excel_workbook()
    
    # 1. 评估概览
    overview_sheet = workbook.create_sheet("评估概览")
    overview_sheet.append(["孤独症儿童行为评估报告 - 统一评估版"])
    overview_sheet.append(["基于ABC量表和DSM-5诊断标准的综合评估"])
    overview_sheet.append([])
    overview_sheet.append(["报告生成时间", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    
    # 统计不同类型的记录
    unified_records = [r for r in records if r.get('assessment_standard') == 'UNIFIED']
    legacy_records = [r for r in records if r.get('assessment_standard') != 'UNIFIED']
    
    overview_sheet.append(["统一评估数", len(unified_records)])
    overview_sheet.append(["旧版评估数", len(legacy_records)])
    overview_sheet.append([])
    
    # 显示分析结果
    if '评估概况' in analysis:
        overview_sheet.append(["评估概况"])
        for key, value in analysis['评估概况'].items():
            overview_sheet.append([key, value])
    
    # 2. 统一评估数据（如果有）
    if unified_records:
        unified_sheet = workbook.create_sheet("统一评估数据")
        unified_headers = [
            "评估ID", "时间", "配置类型", "评估情境",
            "ABC总分", "ABC严重程度", "感觉领域", "交往领域", "躯体运动", "语言领域", "社交自理",
            "社交互动", "沟通交流", "刻板行为", "感官处理", "情绪调节", "认知适应", "DSM5核心均值"
        ]
        unified_sheet.append(unified_headers)
        
        for record in unified_records:
            abc_eval = record.get('abc_evaluation', {})
            dsm5_eval = record.get('dsm5_evaluation', {})
            
            row = [
                record['experiment_id'],
                record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                record.get('template', '自定义'),
                record['scene'],
                abc_eval.get('total_score', ''),
                abc_eval.get('severity', ''),
                abc_eval.get('domain_scores', {}).get('感觉领域得分', ''),
                abc_eval.get('domain_scores', {}).get('交往领域得分', ''),
                abc_eval.get('domain_scores', {}).get('躯体运动领域得分', ''),
                abc_eval.get('domain_scores', {}).get('语言领域得分', ''),
                abc_eval.get('domain_scores', {}).get('社交与自理领域得分', ''),
                dsm5_eval.get('scores', {}).get('社交互动质量', ''),
                dsm5_eval.get('scores', {}).get('沟通交流能力', ''),
                dsm5_eval.get('scores', {}).get('刻板重复行为', ''),
                dsm5_eval.get('scores', {}).get('感官处理能力', ''),
                dsm5_eval.get('scores', {}).get('情绪行为调节', ''),
                dsm5_eval.get('scores', {}).get('认知适应功能', ''),
                f"{dsm5_eval.get('core_symptom_average', 0):.2f}"
            ]
            unified_sheet.append(row)
    
    # 3. 对比分析（仅统一评估）
    if unified_records:
        comparison_sheet = workbook.create_sheet("ABC-DSM5对比分析")
        comparison_sheet.append(["ABC与DSM-5评估结果对比分析"])
        comparison_sheet.append([])
        
        # 收集对比数据
        comparison_data = []
        for record in unified_records:
            if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
                abc_total = record['abc_evaluation']['total_score']
                abc_severity = record['abc_evaluation']['severity']
                dsm5_core = record['dsm5_evaluation']['core_symptom_average']
                
                # 判断DSM-5严重程度
                if dsm5_core >= 4.0:
                    dsm5_severity = "重度"
                elif dsm5_core >= 3.0:
                    dsm5_severity = "中度"
                else:
                    dsm5_severity = "轻度"
                
                comparison_data.append({
                    'ID': record['experiment_id'][:20] + '...',
                    'ABC总分': abc_total,
                    'ABC判定': abc_severity,
                    'DSM5核心': f"{dsm5_core:.2f}",
                    'DSM5判定': dsm5_severity,
                    '一致性': '一致' if (abc_severity == '重度孤独症' and dsm5_severity == '重度') or 
                              (abc_severity == '中度孤独症' and dsm5_severity == '中度') or
                              (abc_severity == '轻度孤独症' and dsm5_severity == '轻度') else '不一致'
                })
        
        # 写入对比数据
        if comparison_data:
            headers = ['评估ID', 'ABC总分', 'ABC判定', 'DSM5核心症状', 'DSM5判定', '判定一致性']
            comparison_sheet.append(headers)
            
            for data in comparison_data:
                comparison_sheet.append([
                    data['ID'],
                    data['ABC总分'],
                    data['ABC判定'],
                    data['DSM5核心'],
                    data['DSM5判定'],
                    data['一致性']
                ])
            
            # 统计一致性
            comparison_sheet.append([])
            consistent_count = len([d for d in comparison_data if d['一致性'] == '一致'])
            consistency_rate = consistent_count / len(comparison_data) * 100 if comparison_data else 0
            comparison_sheet.append(['判定一致率', f"{consistency_rate:.1f}%"])
    
    # 4. 旧版评估数据（如果有）
    if legacy_records:
        legacy_sheet = workbook.create_sheet("旧版评估数据")
        legacy_headers = ["评估ID", "时间", "评估标准", "配置类型", "评估情境", "主要得分"]
        legacy_sheet.append(legacy_headers)
        
        for record in legacy_records:
            if record.get('assessment_standard') == 'ABC':
                main_score = f"ABC总分: {record.get('abc_total_score', 'N/A')}"
            else:
                scores = record.get('evaluation_scores', {})
                if all(m in scores for m in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                    core_avg = (scores['社交互动质量'] + scores['沟通交流能力'] + scores['刻板重复行为']) / 3
                    main_score = f"DSM5核心: {core_avg:.2f}"
                else:
                    main_score = "N/A"
            
            row = [
                record['experiment_id'],
                record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                record.get('assessment_standard', 'ABC'),
                record.get('template', '自定义'),
                record['scene'],
                main_score
            ]
            legacy_sheet.append(row)
    
    # 5. 统计分析
    if any(key in analysis for key in ['ABC分析', 'DSM5分析', 'ABC-DSM5对比']):
        stats_sheet = workbook.create_sheet("统计分析")
        stats_sheet.append(["统计分析结果"])
        stats_sheet.append([])
        
        # 写入各种分析结果
        for section_name, section_data in analysis.items():
            if section_name in ['ABC分析', 'DSM5分析', 'ABC-DSM5对比']:
                stats_sheet.append([section_name])
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if isinstance(value, dict):
                            stats_sheet.append([key])
                            for k, v in value.items():
                                stats_sheet.append([f"  {k}", v])
                        else:
                            stats_sheet.append([key, value])
                else:
                    stats_sheet.append([str(section_data)])
                stats_sheet.append([])
    
    # 6. 对话记录
    dialogue_sheet = workbook.create_sheet("对话记录")
    dialogue_sheet.append(["评估ID", "评估类型", "配置类型", "评估情境", "对话内容"])
    
    for record in records[:50]:  # 限制数量避免文件过大
        assessment_type = "统一评估" if record.get('assessment_standard') == 'UNIFIED' else record.get('assessment_standard', 'ABC')
        dialogue_sheet.append([
            record['experiment_id'],
            assessment_type,
            record.get('template', '自定义'),
            record['scene'],
            record['dialogue'][:1000] + '...' if len(record['dialogue']) > 1000 else record['dialogue']
        ])
    
    # 应用样式
    apply_excel_styles(workbook, header_color="4472C4", header_font_color="FFFFFF")
    
    return export_to_excel(workbook)


def create_unified_detailed_text_report(records, analysis):
    """创建详细文本报告 - 支持统一评估"""
    detailed_report = []
    detailed_report.append("孤独症儿童评估详细报告 - 统一评估版")
    detailed_report.append("=" * 50)
    detailed_report.append(f"报告生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    detailed_report.append(f"评估标准: ABC量表 & DSM-5诊断标准（统一评估）")
    
    # 统计各类型记录
    unified_count = len([r for r in records if r.get('assessment_standard') == 'UNIFIED'])
    legacy_count = len([r for r in records if r.get('assessment_standard') != 'UNIFIED'])
    
    detailed_report.append(f"总评估数: {len(records)} (统一评估: {unified_count}, 旧版: {legacy_count})")
    detailed_report.append("")
    
    # 添加评估概况
    detailed_report.append("一、评估概况")
    detailed_report.append("-" * 30)
    for key, value in analysis.get('评估概况', {}).items():
        detailed_report.append(f"{key}: {value}")
    detailed_report.append("")
    
    # 添加统一评估的对比分析（如果有）
    if unified_count > 0 and 'ABC-DSM5对比' in analysis:
        detailed_report.append("二、ABC与DSM-5评估对比分析")
        detailed_report.append("-" * 30)
        
        comparison = analysis['ABC-DSM5对比']
        if '一致性分析' in comparison:
            for key, value in comparison['一致性分析'].items():
                detailed_report.append(f"{key}: {value}")
        
        if '相关性分析' in comparison:
            detailed_report.append("\n相关性分析:")
            for key, value in comparison['相关性分析'].items():
                detailed_report.append(f"  - {key}: {value}")
        detailed_report.append("")
    
    # 添加各标准的独立分析
    if 'ABC分析' in analysis:
        detailed_report.append("三、ABC量表分析")
        detailed_report.append("-" * 30)
        for key, value in analysis['ABC分析'].items():
            if isinstance(value, dict):
                detailed_report.append(f"\n{key}:")
                for k, v in value.items():
                    detailed_report.append(f"  - {k}: {v}")
            else:
                detailed_report.append(f"{key}: {value}")
        detailed_report.append("")
    
    if 'DSM5分析' in analysis:
        detailed_report.append("四、DSM-5标准分析")
        detailed_report.append("-" * 30)
        for key, value in analysis['DSM5分析'].items():
            if isinstance(value, dict):
                detailed_report.append(f"\n{key}:")
                for k, v in value.items():
                    detailed_report.append(f"  - {k}: {v}")
            else:
                detailed_report.append(f"{key}: {value}")
        detailed_report.append("")
    
    # 添加临床发现与建议
    if '临床发现与建议' in analysis:
        detailed_report.append("五、临床发现与建议")
        detailed_report.append("-" * 30)
        for i, finding in enumerate(analysis['临床发现与建议'], 1):
            detailed_report.append(f"{i}. {finding}")
        detailed_report.append("")
    
    # 添加个案明细（统一评估优先）
    detailed_report.append("六、个案评估明细")
    detailed_report.append("-" * 30)
    
    # 先显示统一评估
    unified_records = [r for r in records if r.get('assessment_standard') == 'UNIFIED']
    if unified_records:
        detailed_report.append("\n【统一评估个案】")
        for i, record in enumerate(unified_records[:10], 1):
            abc_eval = record.get('abc_evaluation', {})
            dsm5_eval = record.get('dsm5_evaluation', {})
            
            detailed_report.append(f"\n个案 {i}: {record['experiment_id']}")
            detailed_report.append(f"  评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            detailed_report.append(f"  配置类型: {record.get('template', '自定义')}")
            detailed_report.append(f"  评估情境: {record['scene']}")
            detailed_report.append(f"  ABC总分: {abc_eval.get('total_score', 'N/A')} ({abc_eval.get('severity', 'N/A')})")
            detailed_report.append(f"  DSM5核心症状: {dsm5_eval.get('core_symptom_average', 0):.2f}/5.0")
            
            # 判断一致性
            abc_severity = abc_eval.get('severity', '')
            dsm5_core = dsm5_eval.get('core_symptom_average', 0)
            
            if dsm5_core >= 4.0:
                dsm5_severity = "重度"
            elif dsm5_core >= 3.0:
                dsm5_severity = "中度"
            else:
                dsm5_severity = "轻度"
            
            consistency = "一致" if (
                (abc_severity == '重度孤独症' and dsm5_severity == '重度') or
                (abc_severity == '中度孤独症' and dsm5_severity == '中度') or
                (abc_severity == '轻度孤独症' and dsm5_severity == '轻度')
            ) else "不一致"
            
            detailed_report.append(f"  判定一致性: {consistency}")
    
    # 显示旧版评估（如果有）
    legacy_records = [r for r in records if r.get('assessment_standard') != 'UNIFIED']
    if legacy_records:
        detailed_report.append("\n【旧版评估个案】")
        for i, record in enumerate(legacy_records[:5], 1):
            detailed_report.append(f"\n个案 {i}: {record['experiment_id']}")
            detailed_report.append(f"  评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            detailed_report.append(f"  评估标准: {record.get('assessment_standard', 'ABC')}")
            detailed_report.append(f"  配置类型: {record.get('template', '自定义')}")
    
    return detailed_report


def create_unified_research_package(records):
    """创建研究数据包 - 支持统一评估"""
    # 生成分析
    analysis = generate_unified_clinical_analysis(records)
    
    # 准备各种格式的数据
    files_dict = {}
    
    # 1. 基础数据CSV
    export_data = prepare_unified_export_data(records)
    files_dict["01_评估数据.csv"] = export_to_csv(export_data)
    
    # 2. 专业分析报告
    if EXCEL_AVAILABLE:
        excel_data = create_unified_excel_report(records, analysis)
        if excel_data:
            files_dict["02_专业分析报告.xlsx"] = excel_data
    
    if "02_专业分析报告.xlsx" not in files_dict:
        # Excel不可用时的文本报告
        detailed_report = create_unified_detailed_text_report(records, analysis)
        files_dict["02_专业分析报告.txt"] = '\n'.join(detailed_report)
    
    # 3. 完整研究数据JSON
    complete_data = create_unified_json_data(records)
    files_dict["03_完整研究数据.json"] = export_to_json(complete_data)
    
    # 4. 行为观察记录
    observation_content = create_unified_observation_text(records)
    files_dict["04_行为观察记录.txt"] = '\n'.join(observation_content)
    
    # 5. 对比分析报告（如果有统一评估数据）
    unified_records = [r for r in records if r.get('assessment_standard') == 'UNIFIED']
    if unified_records:
        comparison_report = generate_comparison_report(unified_records)
        files_dict["05_ABC-DSM5对比分析.json"] = export_to_json(comparison_report)
    
    # 6. README文件
    readme_content = create_unified_readme_content(records, EXCEL_AVAILABLE)
    files_dict["README.txt"] = readme_content
    
    return create_zip_package(files_dict)


def create_unified_readme_content(records, excel_available):
    """创建README内容 - 统一评估版"""
    unified_count = len([r for r in records if r.get('assessment_standard') == 'UNIFIED'])
    legacy_abc_count = len([r for r in records if r.get('assessment_standard') == 'ABC'])
    legacy_dsm5_count = len([r for r in records if r.get('assessment_standard') == 'DSM5'])
    
    readme_content = f"""
孤独症儿童AI模拟实验平台 - 统一评估版
研究数据包说明文档
======================================

生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
评估记录数: {len(records)}
- 统一评估: {unified_count}条
- 旧版ABC评估: {legacy_abc_count}条
- 旧版DSM-5评估: {legacy_dsm5_count}条

评估模式说明:
------------
统一评估模式：
- 生成一次行为对话
- 同时进行ABC和DSM-5两种评估
- 实现真正的标准间对比研究

评估标准说明:
------------
1. ABC量表（孤独症行为量表）
   - 包含57个行为项目，分为5个领域
   - 总分≥67分为孤独症
   - 提供详细的行为识别和量化评分

2. DSM-5诊断标准
   - 基于美国精神疾病诊断与统计手册第五版
   - 评估核心症状：社交沟通缺陷和刻板重复行为
   - 提供功能缺陷程度评估（1-5分）

文件说明:
--------
1. 01_评估数据.csv
   - 包含所有评估的核心数据
   - 统一评估包含两种标准的结果
   - 适用于统计分析和数据可视化

"""
    if excel_available:
        readme_content += """2. 02_专业分析报告.xlsx
   - 多工作表Excel专业报告
   - 包含统一评估数据和对比分析
   - 展示ABC和DSM-5的评估结果对比
"""
    else:
        readme_content += """2. 02_专业分析报告.txt
   - 详细的文本格式专业报告
   - 包含统计分析和临床解释
   - 注意: Excel功能不可用，如需Excel格式请安装openpyxl
"""

    readme_content += """
3. 03_完整研究数据.json
   - 包含所有原始数据和元数据
   - 统一评估数据结构完整保留
   - 适用于程序处理和深度分析

4. 04_行为观察记录.txt
   - 所有评估的对话记录
   - 包含两种标准的评估结果
   - 用于质性分析和行为模式研究
"""

    if unified_count > 0:
        readme_content += """
5. 05_ABC-DSM5对比分析.json
   - 两种评估标准的对比分析
   - 包含一致性和相关性分析
   - 仅统一评估数据可用
"""

    readme_content += """
6. README.txt
   - 本说明文档

统一评估的优势:
-------------
1. 真实对比：同一行为样本，两种标准评估
2. 科学性高：避免了为特定标准"定制"行为
3. 临床价值：更接近真实的临床评估流程
4. 研究价值：可以研究两种标准的相关性和差异

数据结构说明:
-----------
统一评估记录包含：
- abc_evaluation: ABC量表评估结果
  - total_score: 总分
  - severity: 严重程度判定
  - domain_scores: 各领域得分
  - identified_behaviors: 识别到的行为
  
- dsm5_evaluation: DSM-5标准评估结果
  - scores: 各维度得分（1-5分）
  - clinical_observations: 临床观察
  - core_symptom_average: 核心症状均值

使用建议:
--------
1. 对比研究:
   - 分析ABC和DSM-5评估的一致性
   - 研究两种标准的相关性
   - 探索评估差异的原因

2. 临床应用:
   - 综合两种标准制定干预方案
   - 根据不同标准的特点选择评估工具
   - 提高诊断的准确性

3. 研究应用:
   - 使用统一评估数据进行标准间比较
   - 开发新的综合评估方法
   - 验证评估工具的信效度

技术支持:
--------
- 如需Excel功能，请安装: pip install openpyxl
- 数据分析建议使用: pandas, numpy, scipy
- 可视化建议使用: matplotlib, plotly

参考文献:
--------
- Krug, D. A., Arick, J., & Almond, P. (1980). 
  Behavior checklist for identifying severely handicapped 
  individuals with high levels of autistic behavior.
  
- American Psychiatric Association. (2013). 
  Diagnostic and statistical manual of mental disorders (5th ed.).

质量保证:
--------
本平台采用统一的行为生成机制，
确保评估的客观性和可比性。

版权声明:
--------
本数据包仅供学术研究和临床实践使用，
请遵循相关伦理规范和数据保护法规。
"""
    return readme_content


def display_unified_data_overview(records):
    """显示数据统计概览 - 支持统一评估"""
    st.subheader("📈 数据统计概览")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("评估总数", len(records))
    
    with col_stat2:
        # 统计评估类型
        unified_count = len([r for r in records if r.get('assessment_standard') == 'UNIFIED'])
        legacy_count = len([r for r in records if r.get('assessment_standard') != 'UNIFIED'])
        st.metric("统一/旧版", f"{unified_count}/{legacy_count}")
    
    with col_stat3:
        contexts = [r['scene'] for r in records]
        unique_contexts = len(set(contexts))
        st.metric("评估情境数", unique_contexts)
    
    with col_stat4:
        if records:
            time_span = (max(r['timestamp'] for r in records) - min(r['timestamp'] for r in records)).days
            st.metric("时间跨度(天)", time_span)


def display_unified_data_preview(records):
    """显示数据预览 - 支持统一评估"""
    st.subheader("📊 数据预览")
    
    preview_data = []
    for record in records[:10]:
        preview_row = {
            '评估ID': record['experiment_id'][:20] + '...' if len(record['experiment_id']) > 20 else record['experiment_id'],
            '时间': record['timestamp'].strftime('%m-%d %H:%M'),
            '类型': '统一' if record.get('assessment_standard') == 'UNIFIED' else record.get('assessment_standard', 'ABC')[:3],
            '配置': record.get('template', '自定义')[:8] + '...' if len(record.get('template', '自定义')) > 8 else record.get('template', '自定义'),
            '情境': record['scene'].replace('结构化', '结构')
        }
        
        # 根据评估类型显示不同的信息
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            # 统一评估
            abc_total = record['abc_evaluation']['total_score']
            dsm5_core = record['dsm5_evaluation']['core_symptom_average']
            preview_row['ABC总分'] = abc_total
            preview_row['DSM5核心'] = f"{dsm5_core:.2f}"
            
            # 判断一致性
            abc_severity = '重度' if abc_total >= 101 else '中度' if abc_total >= 67 else '轻度'
            dsm5_severity = '重度' if dsm5_core >= 4 else '中度' if dsm5_core >= 3 else '轻度'
            preview_row['一致性'] = '✓' if abc_severity == dsm5_severity else '✗'
        else:
            # 旧版评估
            if record.get('assessment_standard') == 'ABC':
                preview_row['主要指标'] = f"ABC:{record.get('abc_total_score', 'N/A')}"
            else:
                scores = record.get('evaluation_scores', {})
                if all(m in scores for m in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                    core_avg = (scores['社交互动质量'] + scores['沟通交流能力'] + scores['刻板重复行为']) / 3
                    preview_row['主要指标'] = f"DSM5:{core_avg:.2f}"
                else:
                    preview_row['主要指标'] = 'N/A'
        
        preview_data.append(preview_row)
    
    df_preview = pd.DataFrame(preview_data)
    st.dataframe(df_preview, use_container_width=True)
    
    if len(records) > 10:
        st.info(f"显示前10条记录，共{len(records)}条。完整数据请通过上方下载功能获取。")


def display_unified_analysis_preview(analysis, records):
    """显示分析预览 - 支持统一评估"""
    if analysis.get('评估概况'):
        st.write("**评估概况:**")
        for key, value in analysis['评估概况'].items():
            st.write(f"- {key}: {value}")
    
    # 显示统一评估的对比分析
    if 'ABC-DSM5对比' in analysis:
        st.write("\n**ABC与DSM-5对比分析:**")
        comparison = analysis['ABC-DSM5对比']
        
        if '一致性分析' in comparison:
            st.write("- 一致性分析:")
            for key, value in comparison['一致性分析'].items():
                st.write(f"  - {key}: {value}")
        
        if '相关性分析' in comparison:
            st.write("- 相关性分析:")
            for key, value in comparison['相关性分析'].items():
                st.write(f"  - {key}: {value}")
    
    # 分别显示ABC和DSM5的分析结果
    if 'ABC分析' in analysis:
        st.write("\n**ABC量表分析:**")
        if 'ABC总分统计' in analysis['ABC分析']:
            for key, value in analysis['ABC分析']['ABC总分统计'].items():
                st.write(f"- {key}: {value}")
    
    if 'DSM5分析' in analysis:
        st.write("\n**DSM-5标准分析:**")
        if '整体表现' in analysis['DSM5分析']:
            for key, value in analysis['DSM5分析']['整体表现'].items():
                st.write(f"- {key}: {value}")
    
    if analysis.get('临床发现与建议'):
        st.write("\n**临床发现与建议:**")
        for finding in analysis['临床发现与建议']:
            st.write(f"- {finding}")


def display_comparison_preview(comparison_report):
    """显示对比分析预览"""
    st.write("**评估标准对比分析**")
    
    if 'summary' in comparison_report:
        st.write("\n📊 对比概要:")
        for key, value in comparison_report['summary'].items():
            st.write(f"- {key}: {value}")
    
    if 'correlation_analysis' in comparison_report:
        st.write("\n📈 相关性分析:")
        corr = comparison_report['correlation_analysis']
        st.write(f"- ABC总分与DSM5核心症状相关系数: {corr.get('abc_dsm5_correlation', 'N/A')}")
        st.write(f"- 统计显著性: {corr.get('significance', 'N/A')}")
    
    if 'consistency_matrix' in comparison_report:
        st.write("\n🔍 一致性矩阵:")
        matrix = comparison_report['consistency_matrix']
        # 可以考虑用表格展示
        consistency_df = pd.DataFrame(matrix)
        st.dataframe(consistency_df)
    
    if 'recommendations' in comparison_report:
        st.write("\n💡 基于对比的建议:")
        for rec in comparison_report['recommendations']:
            st.write(f"- {rec}")


def generate_unified_clinical_analysis(records):
    """生成统一的临床分析 - 支持新旧数据格式"""
    if not records:
        return {}
    
    analysis = {}
    
    # 基础统计
    unified_count = len([r for r in records if r.get('assessment_standard') == 'UNIFIED'])
    legacy_count = len([r for r in records if r.get('assessment_standard') != 'UNIFIED'])
    
    analysis['评估概况'] = {
        '评估总数': len(records),
        '统一评估数': unified_count,
        '旧版评估数': legacy_count,
        '评估时间跨度': f"{min(r['timestamp'] for r in records).strftime('%Y-%m-%d')} 至 {max(r['timestamp'] for r in records).strftime('%Y-%m-%d')}",
        '涉及情境数': len(set(r['scene'] for r in records)),
        '涉及配置类型数': len(set(r.get('template', '自定义') for r in records))
    }
    
    # 收集ABC和DSM5数据（兼容新旧格式）
    abc_data = []
    dsm5_data = []
    
    for record in records:
        if 'abc_evaluation' in record:
            # 新格式
            abc_data.append({
                'total_score': record['abc_evaluation']['total_score'],
                'severity': record['abc_evaluation']['severity'],
                'domain_scores': record['abc_evaluation']['domain_scores'],
                'record': record
            })
        elif record.get('assessment_standard') == 'ABC':
            # 旧格式ABC
            abc_data.append({
                'total_score': record.get('abc_total_score', 0),
                'severity': record.get('abc_severity', '未知'),
                'domain_scores': {k: v for k, v in record.get('evaluation_scores', {}).items() 
                                if k in ['感觉领域得分', '交往领域得分', '躯体运动领域得分', '语言领域得分', '社交与自理领域得分']},
                'record': record
            })
        
        if 'dsm5_evaluation' in record:
            # 新格式
            dsm5_data.append({
                'scores': record['dsm5_evaluation']['scores'],
                'core_average': record['dsm5_evaluation']['core_symptom_average'],
                'record': record
            })
        elif record.get('assessment_standard') == 'DSM5':
            # 旧格式DSM5
            scores = record.get('evaluation_scores', {})
            core_avg = 0
            if all(m in scores for m in ['社交互动质量', '沟通交流能力', '刻板重复行为']):
                core_avg = (scores['社交互动质量'] + scores['沟通交流能力'] + scores['刻板重复行为']) / 3
            
            dsm5_data.append({
                'scores': scores,
                'core_average': core_avg,
                'record': record
            })
    
    # ABC分析
    if abc_data:
        analysis['ABC分析'] = analyze_abc_data(abc_data)
    
    # DSM5分析
    if dsm5_data:
        analysis['DSM5分析'] = analyze_dsm5_data(dsm5_data)
    
    # 如果有统一评估数据，进行对比分析
    if unified_count > 0:
        unified_records = [r for r in records if r.get('assessment_standard') == 'UNIFIED']
        analysis['ABC-DSM5对比'] = analyze_abc_dsm5_comparison(unified_records)
    
    # 生成临床发现和建议
    findings = []
    
    if 'ABC分析' in analysis and 'ABC总分统计' in analysis['ABC分析']:
        avg_abc = float(analysis['ABC分析']['ABC总分统计']['平均总分'])
        if avg_abc >= 67:
            findings.append(f"ABC评估显示明确的孤独症表现（平均总分: {avg_abc:.1f}）")
        elif avg_abc >= 53:
            findings.append(f"ABC评估显示轻度孤独症表现（平均总分: {avg_abc:.1f}）")
    
    if 'DSM5分析' in analysis and '整体表现' in analysis['DSM5分析']:
        core_avg_str = analysis['DSM5分析']['整体表现'].get('核心症状综合', '0')
        core_avg = float(core_avg_str.split('±')[0].strip())
        if core_avg >= 4.0:
            findings.append(f"DSM-5评估显示重度核心症状（平均: {core_avg:.2f}/5）")
        elif core_avg >= 3.0:
            findings.append(f"DSM-5评估显示中度核心症状（平均: {core_avg:.2f}/5）")
    
    if unified_count > 0 and 'ABC-DSM5对比' in analysis:
        consistency = analysis['ABC-DSM5对比'].get('一致性分析', {}).get('总体一致率', '0%')
        findings.append(f"ABC与DSM-5评估一致性: {consistency}")
        findings.append("建议综合两种评估结果制定个体化干预方案")
    
    analysis['临床发现与建议'] = findings
    
    return analysis


def analyze_abc_data(abc_data):
    """分析ABC数据"""
    abc_analysis = {}
    
    # ABC总分统计
    total_scores = [d['total_score'] for d in abc_data]
    if total_scores:
        abc_analysis['ABC总分统计'] = {
            '平均总分': f"{np.mean(total_scores):.1f}",
            '总分范围': f"{np.min(total_scores):.0f}-{np.max(total_scores):.0f}",
            '标准差': f"{np.std(total_scores):.1f}",
            '中位数': f"{np.median(total_scores):.0f}"
        }
    
    # 严重程度分布
    severity_counts = {}
    for data in abc_data:
        severity = data['severity']
        if severity not in severity_counts:
            severity_counts[severity] = 0
        severity_counts[severity] += 1
    
    if severity_counts:
        abc_analysis['严重程度分布'] = {
            k: f"{v} ({v/len(abc_data)*100:.1f}%)" 
            for k, v in severity_counts.items()
        }
    
    return abc_analysis


def analyze_dsm5_data(dsm5_data):
    """分析DSM5数据"""
    dsm5_analysis = {}
    
    # 收集各维度得分
    all_scores = {metric: [] for metric in ['社交互动质量', '沟通交流能力', '刻板重复行为', 
                                           '感官处理能力', '情绪行为调节', '认知适应功能']}
    
    for data in dsm5_data:
        for metric in all_scores:
            if metric in data['scores']:
                all_scores[metric].append(data['scores'][metric])
    
    # 整体表现统计
    overall = {}
    for metric, scores in all_scores.items():
        if scores:
            overall[f'{metric}'] = f"{np.mean(scores):.2f} ± {np.std(scores):.2f}"
    
    # 计算核心症状综合
    core_avgs = [d['core_average'] for d in dsm5_data if d['core_average'] > 0]
    if core_avgs:
        overall['核心症状综合'] = f"{np.mean(core_avgs):.2f} ± {np.std(core_avgs):.2f}"
    
    dsm5_analysis['整体表现'] = overall
    
    return dsm5_analysis


def analyze_abc_dsm5_comparison(unified_records):
    """分析ABC和DSM5评估的对比"""
    comparison = {}
    
    # 收集配对数据
    paired_data = []
    for record in unified_records:
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            abc_total = record['abc_evaluation']['total_score']
            dsm5_core = record['dsm5_evaluation']['core_symptom_average']
            
            # 判断严重程度
            if abc_total >= 101:
                abc_severity = '重度'
            elif abc_total >= 67:
                abc_severity = '中度'
            elif abc_total >= 53:
                abc_severity = '轻度'
            else:
                abc_severity = '非孤独症'
            
            if dsm5_core >= 4.0:
                dsm5_severity = '重度'
            elif dsm5_core >= 3.0:
                dsm5_severity = '中度'
            elif dsm5_core >= 2.0:
                dsm5_severity = '轻度'
            else:
                dsm5_severity = '轻度'
            
            paired_data.append({
                'abc_total': abc_total,
                'dsm5_core': dsm5_core,
                'abc_severity': abc_severity,
                'dsm5_severity': dsm5_severity,
                'consistent': abc_severity == dsm5_severity
            })
    
    if paired_data:
        # 一致性分析
        consistent_count = len([d for d in paired_data if d['consistent']])
        comparison['一致性分析'] = {
            '总体一致率': f"{consistent_count/len(paired_data)*100:.1f}%",
            '一致样本数': consistent_count,
            '不一致样本数': len(paired_data) - consistent_count
        }
        
        # 相关性分析
        if len(paired_data) > 2:
            abc_scores = [d['abc_total'] for d in paired_data]
            dsm5_scores = [d['dsm5_core'] for d in paired_data]
            
            # 计算相关系数
            correlation = np.corrcoef(abc_scores, dsm5_scores)[0, 1]
            comparison['相关性分析'] = {
                'ABC-DSM5相关系数': f"{correlation:.3f}",
                '相关性强度': '强' if abs(correlation) > 0.7 else '中等' if abs(correlation) > 0.4 else '弱'
            }
    
    return comparison


def generate_comparison_report(unified_records):
    """生成详细的对比分析报告"""
    report = {
        'summary': {},
        'correlation_analysis': {},
        'consistency_matrix': {},
        'case_analysis': [],
        'recommendations': []
    }
    
    # 收集数据
    paired_data = []
    for record in unified_records:
        if 'abc_evaluation' in record and 'dsm5_evaluation' in record:
            abc_eval = record['abc_evaluation']
            dsm5_eval = record['dsm5_evaluation']
            
            paired_data.append({
                'id': record['experiment_id'],
                'abc_total': abc_eval['total_score'],
                'abc_severity': abc_eval['severity'],
                'abc_domains': abc_eval['domain_scores'],
                'dsm5_scores': dsm5_eval['scores'],
                'dsm5_core': dsm5_eval['core_symptom_average']
            })
    
    if not paired_data:
        report['summary']['error'] = '无统一评估数据可供对比'
        return report
    
    # 概要统计
    report['summary'] = {
        '对比样本数': len(paired_data),
        'ABC总分范围': f"{min(d['abc_total'] for d in paired_data)}-{max(d['abc_total'] for d in paired_data)}",
        'DSM5核心症状范围': f"{min(d['dsm5_core'] for d in paired_data):.2f}-{max(d['dsm5_core'] for d in paired_data):.2f}"
    }
    
    # 相关性分析
    if len(paired_data) > 2:
        abc_totals = [d['abc_total'] for d in paired_data]
        dsm5_cores = [d['dsm5_core'] for d in paired_data]
        
        correlation = np.corrcoef(abc_totals, dsm5_cores)[0, 1]
        
        # 简单的显著性判断
        n = len(paired_data)
        t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
        # 自由度为n-2的t分布，双尾检验
        # 这里使用简化的判断
        significant = abs(t_stat) > 2.0  # 约等于p<0.05的临界值
        
        report['correlation_analysis'] = {
            'abc_dsm5_correlation': f"{correlation:.3f}",
            'significance': '显著' if significant else '不显著',
            'interpretation': f"ABC总分与DSM-5核心症状存在{'强' if abs(correlation) > 0.7 else '中等' if abs(correlation) > 0.4 else '弱'}相关"
        }
    
    # 一致性矩阵
    severity_mapping = {
        'abc': ['非孤独症', '轻度孤独症', '中度孤独症', '重度孤独症'],
        'dsm5': ['轻度', '中度', '重度']
    }
    
    # 创建一致性矩阵
    matrix = {}
    for abc_sev in severity_mapping['abc']:
        matrix[abc_sev] = {}
        for dsm5_sev in severity_mapping['dsm5']:
            matrix[abc_sev][dsm5_sev] = 0
    
    # 填充矩阵
    for data in paired_data:
        abc_sev = data['abc_severity']
        
        # 根据DSM5核心症状判断严重程度
        if data['dsm5_core'] >= 4.0:
            dsm5_sev = '重度'
        elif data['dsm5_core'] >= 3.0:
            dsm5_sev = '中度'
        else:
            dsm5_sev = '轻度'
        
        if abc_sev in matrix and dsm5_sev in matrix[abc_sev]:
            matrix[abc_sev][dsm5_sev] += 1
    
    report['consistency_matrix'] = matrix
    
    # 个案分析（找出差异最大的案例）
    for data in paired_data:
        # 标准化分数以便比较
        abc_normalized = data['abc_total'] / 158  # ABC最高分158
        dsm5_normalized = data['dsm5_core'] / 5  # DSM5最高5分
        
        discrepancy = abs(abc_normalized - dsm5_normalized)
        
        if discrepancy > 0.3:  # 差异超过30%
            report['case_analysis'].append({
                'id': data['id'][:20] + '...',
                'abc_total': data['abc_total'],
                'dsm5_core': f"{data['dsm5_core']:.2f}",
                'discrepancy': f"{discrepancy:.2%}",
                'note': 'ABC和DSM-5评估存在较大差异'
            })
    
    # 基于对比的建议
    report['recommendations'] = [
        "两种评估工具侧重点不同：ABC注重行为频率统计，DSM-5注重功能缺陷程度",
        "建议结合使用两种评估工具，全面了解个体表现",
        "当两种评估结果不一致时，需要进一步的临床观察和评估",
        "ABC量表适合行为筛查和监测，DSM-5标准适合诊断分类和支持需求评估"
    ]
    
    return report