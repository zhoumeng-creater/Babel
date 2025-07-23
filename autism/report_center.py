"""孤独症平台报告中心页面 - 基于ABC量表"""
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
    """ABC报告中心页面"""
    st.header("📊 ABC评估报告中心")
    st.markdown("基于ABC孤独症行为量表生成专业评估报告和研究数据")
    
    records = st.session_state.experiment_records
    
    if not records:
        st.warning("📊 暂无评估数据，请先进行ABC评估")
        st.stop()
    
    st.success(f"📊 当前共有 {len(records)} 条ABC评估记录可生成报告")
    
    # 报告类型选择
    st.subheader("📋 选择报告类型")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📄 标准ABC报告")
        
        # 基础CSV报告
        if st.button("📊 下载ABC评估数据 (CSV)", use_container_width=True):
            export_data = prepare_clinical_export_data(records)
            csv_content = export_to_csv(export_data)
            
            st.download_button(
                label="⬇️ 下载ABC评估数据",
                data=csv_content,
                file_name=f"abc_assessment_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
        
        # 行为记录下载
        if st.button("💬 下载行为观察记录 (TXT)", use_container_width=True):
            observation_content = create_observation_text(records)
            
            st.download_button(
                label="⬇️ 下载行为观察记录",
                data=export_to_text(observation_content),
                file_name=f"abc_behavior_observations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime='text/plain'
            )
        
        # JSON完整数据
        if st.button("🔧 下载完整ABC数据 (JSON)", use_container_width=True):
            json_data = create_complete_json_data(records)
            json_str = export_to_json(json_data)
            
            st.download_button(
                label="⬇️ 下载完整ABC数据",
                data=json_str.encode('utf-8'),
                file_name=f"abc_complete_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime='application/json'
            )
    
    with col2:
        st.write("### 📈 专业分析报告")
        
        # 生成ABC分析报告
        if st.button("📊 生成ABC统计分析", use_container_width=True):
            with st.spinner("正在生成ABC分析报告..."):
                analysis = generate_clinical_analysis(records)
            
            st.success("✅ ABC分析报告生成完成！")
            
            # 显示分析预览
            with st.expander("📋 ABC分析报告预览", expanded=True):
                if analysis.get('评估概况'):
                    st.write("**评估概况:**")
                    for key, value in analysis['评估概况'].items():
                        st.write(f"- {key}: {value}")
                
                if analysis.get('ABC总分统计'):
                    st.write("**ABC总分统计:**")
                    for key, value in analysis['ABC总分统计'].items():
                        st.write(f"- {key}: {value}")
                
                if analysis.get('严重程度分布'):
                    st.write("**严重程度分布:**")
                    for key, value in analysis['严重程度分布'].items():
                        st.write(f"- {key}: {value}")
                
                if analysis.get('临床发现与建议'):
                    st.write("**临床发现与建议:**")
                    for finding in analysis['临床发现与建议']:
                        st.write(f"- {finding}")
            
            # 提供分析报告下载
            analysis_json = export_to_json(analysis)
            st.download_button(
                label="⬇️ 下载ABC分析报告 (JSON)",
                data=analysis_json.encode('utf-8'),
                file_name=f"abc_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime='application/json'
            )
        
        # Excel专业报告
        if EXCEL_AVAILABLE:
            if st.button("📋 生成专业Excel报告", use_container_width=True):
                with st.spinner("正在生成专业Excel报告..."):
                    analysis = generate_clinical_analysis(records)
                    excel_data = create_abc_excel_report(records, analysis)
                
                if excel_data:
                    st.success("✅ 专业Excel报告生成完成！")
                    
                    st.download_button(
                        label="⬇️ 下载专业Excel报告",
                        data=excel_data,
                        file_name=f"abc_professional_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
                    analysis = generate_clinical_analysis(records)
                
                # 创建详细文本报告
                detailed_report = create_detailed_text_report(records, analysis)
                
                st.success("✅ 详细文本报告生成完成！")
                
                st.download_button(
                    label="⬇️ 下载详细文本报告",
                    data=export_to_text(detailed_report),
                    file_name=f"abc_detailed_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime='text/plain'
                )
        
        # 研究数据包
        if st.button("📦 生成完整研究数据包", use_container_width=True, type="primary"):
            with st.spinner("正在生成完整研究数据包..."):
                zip_data = create_research_package(records)
            
            st.success("✅ 完整研究数据包生成完成！")
            
            st.download_button(
                label="⬇️ 下载完整研究数据包 (ZIP)",
                data=zip_data,
                file_name=f"abc_research_package_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime='application/zip'
            )
    
    # 数据统计概览
    display_data_overview(records)
    
    # 数据预览
    display_data_preview(records)


def create_observation_text(records):
    """创建ABC行为观察记录文本"""
    observation_content = []
    observation_content.append("=" * 70)
    observation_content.append("孤独症儿童ABC行为观察记录")
    observation_content.append("基于ABC孤独症行为量表")
    observation_content.append("=" * 70)
    observation_content.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    observation_content.append(f"评估记录总数: {len(records)}")
    observation_content.append("=" * 70)
    observation_content.append("")
    
    for i, record in enumerate(records, 1):
        observation_content.append(f"\n【ABC评估 {i}】")
        observation_content.append(f"评估ID: {record['experiment_id']}")
        observation_content.append(f"评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        observation_content.append(f"配置类型: {record.get('template', '自定义')}")
        observation_content.append(f"评估情境: {record['scene']}")
        observation_content.append(f"观察活动: {record.get('activity', '未指定')}")
        observation_content.append(f"触发因素: {record.get('trigger', '未指定')}")
        observation_content.append(f"ABC总分: {record['abc_total_score']}")
        observation_content.append(f"严重程度: {record['abc_severity']}")
        observation_content.append("-" * 50)
        
        observation_content.append("各领域得分:")
        for metric, score in record['evaluation_scores'].items():
            observation_content.append(f"  • {metric}: {score}")
        
        if 'identified_behaviors' in record and record['identified_behaviors']:
            observation_content.append("识别到的行为:")
            for domain, behaviors in record['identified_behaviors'].items():
                if behaviors:
                    observation_content.append(f"  {domain}:")
                    for behavior in behaviors:
                        observation_content.append(f"    - {behavior}")
        
        observation_content.append("行为观察对话:")
        observation_content.append(record['dialogue'])
        observation_content.append("-" * 50)
        observation_content.append("")
    
    return observation_content


def create_complete_json_data(records):
    """创建完整的ABC JSON数据"""
    analysis = generate_clinical_analysis(records)
    
    json_data = {
        'abc_assessment_report': {
            'report_metadata': {
                'generation_time': datetime.datetime.now().isoformat(),
                'assessment_tool': 'ABC孤独症行为量表',
                'total_assessments': len(records),
                'platform_version': 'ABC量表版 v1.0'
            },
            'assessment_summary': analysis,
            'detailed_assessments': []
        }
    }
    
    for record in records:
        assessment_record = record.copy()
        assessment_record['timestamp'] = record['timestamp'].isoformat()
        
        json_data['abc_assessment_report']['detailed_assessments'].append(assessment_record)
    
    return json_data


def create_abc_excel_report(records, analysis):
    """创建ABC专业Excel报告"""
    if not EXCEL_AVAILABLE:
        return None
    
    workbook = create_excel_workbook()
    
    # 1. ABC评估概览
    overview_sheet = workbook.create_sheet("ABC评估概览")
    overview_sheet.append(["孤独症儿童ABC行为评估报告"])
    overview_sheet.append([])
    overview_sheet.append(["报告生成时间", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    overview_sheet.append(["评估工具", "ABC孤独症行为量表（57项）"])
    overview_sheet.append([])
    
    overview_sheet.append(["评估概况"])
    for key, value in analysis.get('评估概况', {}).items():
        overview_sheet.append([key, value])
    
    overview_sheet.append([])
    overview_sheet.append(["ABC总分统计"])
    for key, value in analysis.get('ABC总分统计', {}).items():
        overview_sheet.append([key, value])
    
    overview_sheet.append([])
    overview_sheet.append(["严重程度分布"])
    for key, value in analysis.get('严重程度分布', {}).items():
        overview_sheet.append([key, value])
    
    overview_sheet.append([])
    overview_sheet.append(["临床发现与建议"])
    for finding in analysis.get('临床发现与建议', []):
        overview_sheet.append([finding])
    
    # 2. 详细评估数据
    data_sheet = workbook.create_sheet("详细评估数据")
    headers = ["评估ID", "时间", "配置类型", "ABC严重程度", "评估情境", "观察活动", 
              "触发因素", "ABC总分", "感觉领域", "交往领域", "躯体运动", 
              "语言领域", "社交自理", "主要行为表现", "备注"]
    data_sheet.append(headers)
    
    for record in records:
        scores = record['evaluation_scores']
        
        # 提取主要行为
        main_behaviors = []
        if 'identified_behaviors' in record:
            for behaviors in record['identified_behaviors'].values():
                main_behaviors.extend(behaviors[:2])  # 每个领域取前2个
        main_behaviors_str = '; '.join(main_behaviors[:5])  # 最多显示5个
        
        row = [
            record['experiment_id'],
            record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            record.get('template', '自定义'),
            record['abc_severity'],
            record['scene'],
            record.get('activity', ''),
            record.get('trigger', ''),
            record['abc_total_score'],
            scores['感觉领域得分'],
            scores['交往领域得分'],
            scores['躯体运动领域得分'],
            scores['语言领域得分'],
            scores['社交与自理领域得分'],
            main_behaviors_str,
            record.get('notes', '')
        ]
        data_sheet.append(row)
    
    # 3. 各领域得分分析
    domain_sheet = workbook.create_sheet("各领域得分分析")
    if analysis.get('各领域得分分析'):
        domain_headers = ["领域", "平均分", "最高分", "最低分", "占满分比例"]
        domain_sheet.append(domain_headers)
        
        for domain, stats in analysis['各领域得分分析'].items():
            row = [
                domain.replace("得分", ""),
                stats['平均分'],
                stats['最高分'],
                stats['最低分'],
                stats['占满分比例']
            ]
            domain_sheet.append(row)
    
    # 4. 高频行为分析
    if analysis.get('高频行为表现'):
        behavior_sheet = workbook.create_sheet("高频行为分析")
        behavior_sheet.append(["行为表现", "出现次数和比例"])
        
        for behavior, frequency in list(analysis['高频行为表现'].items())[:20]:
            behavior_sheet.append([behavior, frequency])
    
    # 5. 行为清单
    behavior_list_sheet = workbook.create_sheet("ABC行为清单")
    behavior_list_sheet.append(["评估ID", "识别到的所有行为"])
    
    for record in records:
        if 'identified_behaviors' in record:
            all_behaviors = []
            for domain, behaviors in record['identified_behaviors'].items():
                for behavior in behaviors:
                    all_behaviors.append(f"[{domain}] {behavior}")
            
            behavior_list_sheet.append([
                record['experiment_id'],
                '; '.join(all_behaviors)
            ])
    
    # 6. 对话记录
    dialogue_sheet = workbook.create_sheet("对话记录")
    dialogue_sheet.append(["评估ID", "严重程度", "评估情境", "对话内容"])
    
    for record in records:
        dialogue_sheet.append([
            record['experiment_id'],
            record['abc_severity'],
            record['scene'],
            record['dialogue']
        ])
    
    # 应用专业样式
    apply_excel_styles(workbook, header_color="4472C4", header_font_color="FFFFFF")
    
    # 特殊样式处理
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and any(keyword in str(cell.value) for keyword in ['重度', '中度', '孤独症']):
                    from openpyxl.styles import PatternFill
                    cell.fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
    
    return export_to_excel(workbook)


def create_detailed_text_report(records, analysis):
    """创建ABC详细文本报告"""
    detailed_report = []
    detailed_report.append("孤独症儿童ABC评估详细报告")
    detailed_report.append("=" * 50)
    detailed_report.append(f"报告生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    detailed_report.append(f"评估工具: ABC孤独症行为量表")
    detailed_report.append(f"评估标准: 总分≥67分为孤独症")
    detailed_report.append("")
    
    # 添加评估概况
    detailed_report.append("一、评估概况")
    detailed_report.append("-" * 30)
    for key, value in analysis.get('评估概况', {}).items():
        detailed_report.append(f"{key}: {value}")
    detailed_report.append("")
    
    # 添加ABC总分统计
    detailed_report.append("二、ABC总分统计")
    detailed_report.append("-" * 30)
    for key, value in analysis.get('ABC总分统计', {}).items():
        detailed_report.append(f"{key}: {value}")
    detailed_report.append("")
    
    # 添加严重程度分布
    detailed_report.append("三、严重程度分布")
    detailed_report.append("-" * 30)
    for key, value in analysis.get('严重程度分布', {}).items():
        detailed_report.append(f"{key}: {value}")
    detailed_report.append("")
    
    # 添加各领域分析
    if analysis.get('各领域得分分析'):
        detailed_report.append("四、各领域得分分析")
        detailed_report.append("-" * 30)
        for domain, stats in analysis['各领域得分分析'].items():
            detailed_report.append(f"\n{domain}:")
            for key, value in stats.items():
                detailed_report.append(f"  - {key}: {value}")
        detailed_report.append("")
    
    # 添加高频行为
    if analysis.get('高频行为表现'):
        detailed_report.append("五、高频行为表现（前10项）")
        detailed_report.append("-" * 30)
        for i, (behavior, frequency) in enumerate(list(analysis['高频行为表现'].items())[:10], 1):
            detailed_report.append(f"{i}. {behavior}: {frequency}")
        detailed_report.append("")
    
    # 添加临床发现
    detailed_report.append("六、临床发现与建议")
    detailed_report.append("-" * 30)
    for i, finding in enumerate(analysis.get('临床发现与建议', []), 1):
        detailed_report.append(f"{i}. {finding}")
    detailed_report.append("")
    
    # 添加个案明细
    detailed_report.append("七、个案评估明细")
    detailed_report.append("-" * 30)
    for i, record in enumerate(records, 1):
        detailed_report.append(f"\n个案 {i}: {record['experiment_id']}")
        detailed_report.append(f"  评估时间: {record['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        detailed_report.append(f"  ABC总分: {record['abc_total_score']}")
        detailed_report.append(f"  严重程度: {record['abc_severity']}")
        detailed_report.append(f"  评估情境: {record['scene']}")
    
    return detailed_report


def create_research_package(records):
    """创建研究数据包"""
    # 生成分析
    analysis = generate_clinical_analysis(records)
    
    # 准备各种格式的数据
    files_dict = {}
    
    # 1. 基础ABC数据CSV
    export_data = prepare_clinical_export_data(records)
    files_dict["01_ABC评估数据.csv"] = export_to_csv(export_data)
    
    # 2. 专业分析报告
    if EXCEL_AVAILABLE:
        excel_data = create_abc_excel_report(records, analysis)
        if excel_data:
            files_dict["02_专业分析报告.xlsx"] = excel_data
    
    if "02_专业分析报告.xlsx" not in files_dict:
        # Excel不可用时的文本报告
        detailed_report = create_detailed_text_report(records, analysis)
        files_dict["02_专业分析报告.txt"] = '\n'.join(detailed_report)
    
    # 3. 完整研究数据JSON
    complete_data = create_complete_json_data(records)
    files_dict["03_完整研究数据.json"] = export_to_json(complete_data)
    
    # 4. 行为观察记录
    observation_content = create_observation_text(records)
    files_dict["04_行为观察记录.txt"] = '\n'.join(observation_content)
    
    # 5. README文件
    readme_content = create_readme_content(records, EXCEL_AVAILABLE)
    files_dict["README.txt"] = readme_content
    
    return create_zip_package(files_dict)


def create_readme_content(records, excel_available):
    """创建README内容"""
    readme_content = f"""
孤独症儿童AI模拟实验平台 - ABC量表版
研究数据包说明文档
======================================

生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
评估记录数: {len(records)}
评估工具: ABC孤独症行为量表（Autism Behavior Checklist）

文件说明:
--------
1. 01_ABC评估数据.csv
   - 包含所有评估的核心数据
   - 适用于统计分析和数据可视化
   - 包含ABC总分和各领域得分

"""
    if excel_available:
        readme_content += """2. 02_专业分析报告.xlsx
   - 多工作表Excel专业报告
   - 包含统计分析、行为清单和详细记录
   - 适用于临床报告和学术研究
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
   - 适用于程序处理和深度分析
   - 包含完整的行为识别记录

4. 04_行为观察记录.txt
   - 所有评估的对话记录
   - 用于质性分析和行为模式研究
   - 包含识别到的具体行为

5. README.txt
   - 本说明文档

ABC量表说明:
-----------
ABC量表包含57个行为项目，分为5个领域：
- 感觉领域（9项）：感觉异常相关行为
- 交往领域（12项）：社交互动障碍
- 躯体运动领域（12项）：刻板重复动作
- 语言领域（13项）：语言沟通缺陷
- 社交与自理领域（11项）：生活自理和适应

评分标准：
- 总分≥67分：孤独症
- 总分53-66分：轻度孤独症
- 总分40-52分：边缘状态/可疑
- 总分<40分：非孤独症

使用建议:
--------
1. 临床应用:
   - 使用ABC总分进行初步筛查
   - 分析各领域得分确定干预重点
   - 关注高频行为制定个体化方案

2. 研究应用:
   - 使用完整数据进行统计分析
   - 行为模式分析和分类研究
   - 干预效果评估

3. 教学应用:
   - ABC量表使用培训
   - 行为识别技能训练
   - 案例教学和讨论

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
  Journal of Child Psychology and Psychiatry, 21(3), 221-229.

- 中文版ABC量表的信效度研究

质量保证:
--------
本平台严格遵循ABC量表的原始设计，
确保行为识别和评分的准确性，
所有评估结果均可追溯到具体行为表现。

版权声明:
--------
本数据包仅供学术研究和临床实践使用，
请遵循相关伦理规范和数据保护法规。
"""
    return readme_content


def display_data_overview(records):
    """显示数据统计概览"""
    st.subheader("📈 数据统计概览")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("ABC评估总数", len(records))
    
    with col_stat2:
        avg_total = np.mean([r['abc_total_score'] for r in records])
        st.metric("平均ABC总分", f"{avg_total:.1f}")
    
    with col_stat3:
        severities = [r['abc_severity'] for r in records]
        autism_count = len([s for s in severities if '孤独症' in s and '非' not in s])
        st.metric("孤独症阳性数", f"{autism_count} ({autism_count/len(records)*100:.1f}%)")
    
    with col_stat4:
        if records:
            time_span = (max(r['timestamp'] for r in records) - min(r['timestamp'] for r in records)).days
            st.metric("评估时间跨度(天)", time_span)


def display_data_preview(records):
    """显示数据预览"""
    st.subheader("📊 ABC数据预览")
    
    preview_data = []
    for record in records[:10]:
        preview_data.append({
            '评估ID': record['experiment_id'][:20] + '...' if len(record['experiment_id']) > 20 else record['experiment_id'],
            '时间': record['timestamp'].strftime('%m-%d %H:%M'),
            'ABC总分': record['abc_total_score'],
            '严重程度': record['abc_severity'],
            '评估情境': record['scene'].replace('结构化', '结构'),
            '行为数': sum(len(behaviors) for behaviors in record.get('identified_behaviors', {}).values())
        })
    
    df_preview = pd.DataFrame(preview_data)
    st.dataframe(df_preview, use_container_width=True)
    
    if len(records) > 10:
        st.info(f"显示前10条记录，共{len(records)}条。完整数据请通过上方下载功能获取。")