"""
量表数据迁移和兼容性处理模块
确保新增的CARS和ASSQ量表与现有系统兼容
"""
import datetime
from typing import Dict, List, Any, Optional


def migrate_evaluation_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    迁移评估记录以支持新的量表结构
    
    Args:
        record: 原始评估记录
    
    Returns:
        迁移后的记录
    """
    migrated = record.copy()
    
    # 检查并设置评估标准字段
    if 'assessment_standard' not in migrated:
        # 根据现有字段推断评估标准
        if 'abc_evaluation' in migrated and 'dsm5_evaluation' in migrated:
            migrated['assessment_standard'] = 'UNIFIED'
        elif 'abc_evaluation' in migrated or 'abc_total_score' in migrated:
            migrated['assessment_standard'] = 'ABC'
        elif 'dsm5_evaluation' in migrated or 'dsm5_core_symptom_average' in migrated:
            migrated['assessment_standard'] = 'DSM5'
        else:
            migrated['assessment_standard'] = 'UNKNOWN'
    
    # 添加量表选择字段（如果不存在）
    if 'selected_scales' not in migrated:
        scales = []
        if 'abc_evaluation' in migrated or 'abc_total_score' in migrated:
            scales.append('ABC')
        if 'dsm5_evaluation' in migrated or 'dsm5_core_symptom_average' in migrated:
            scales.append('DSM5')
        if 'cars_evaluation' in migrated:
            scales.append('CARS')
        if 'assq_evaluation' in migrated:
            scales.append('ASSQ')
        
        migrated['selected_scales'] = scales if scales else ['ABC', 'DSM5']
    
    # 迁移旧格式的ABC评估
    if 'abc_total_score' in migrated and 'abc_evaluation' not in migrated:
        migrated['abc_evaluation'] = {
            'total_score': migrated.get('abc_total_score', 0),
            'severity': migrated.get('abc_severity', '未知'),
            'domain_scores': migrated.get('abc_domain_scores', {}),
            'identified_behaviors': migrated.get('abc_behaviors', {}),
            'interpretation': {
                'clinical_range': migrated.get('abc_total_score', 0) >= 67,
                'severity_level': migrated.get('abc_severity', '未知')
            }
        }
    
    # 迁移旧格式的DSM5评估
    if 'dsm5_core_symptom_average' in migrated and 'dsm5_evaluation' not in migrated:
        migrated['dsm5_evaluation'] = {
            'core_symptom_average': migrated.get('dsm5_core_symptom_average', 0),
            'scores': migrated.get('evaluation_scores', {}),
            'clinical_observations': migrated.get('clinical_observations', {}),
            'severity_level': determine_dsm5_severity(migrated.get('dsm5_core_symptom_average', 0))
        }
    
    return migrated


def determine_dsm5_severity(core_average: float) -> str:
    """根据DSM-5核心症状均分确定严重程度"""
    if core_average < 2:
        return '亚临床'
    elif core_average < 3:
        return '需要支持'
    elif core_average < 4:
        return '需要大量支持'
    else:
        return '需要非常大量支持'


def batch_migrate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批量迁移评估记录
    
    Args:
        records: 原始记录列表
    
    Returns:
        迁移后的记录列表
    """
    migrated_records = []
    migration_stats = {
        'total': len(records),
        'migrated': 0,
        'already_current': 0,
        'errors': 0
    }
    
    for record in records:
        try:
            # 检查是否需要迁移
            if needs_migration(record):
                migrated = migrate_evaluation_record(record)
                migrated_records.append(migrated)
                migration_stats['migrated'] += 1
            else:
                migrated_records.append(record)
                migration_stats['already_current'] += 1
        except Exception as e:
            print(f"迁移记录时出错: {e}")
            migrated_records.append(record)  # 保留原始记录
            migration_stats['errors'] += 1
    
    # 打印迁移统计
    print(f"数据迁移完成:")
    print(f"- 总记录数: {migration_stats['total']}")
    print(f"- 已迁移: {migration_stats['migrated']}")
    print(f"- 已是最新: {migration_stats['already_current']}")
    print(f"- 错误: {migration_stats['errors']}")
    
    return migrated_records


def needs_migration(record: Dict[str, Any]) -> bool:
    """
    检查记录是否需要迁移
    
    Args:
        record: 评估记录
    
    Returns:
        是否需要迁移
    """
    # 检查是否有旧格式字段
    old_fields = [
        'abc_total_score',
        'abc_severity', 
        'dsm5_core_symptom_average',
        'evaluation_scores'
    ]
    
    # 检查是否缺少新格式字段
    new_fields = [
        'selected_scales',
        'assessment_standard'
    ]
    
    has_old_fields = any(field in record for field in old_fields)
    missing_new_fields = any(field not in record for field in new_fields)
    
    # 检查是否有新格式的评估结构
    has_old_structure = (
        ('abc_total_score' in record and 'abc_evaluation' not in record) or
        ('dsm5_core_symptom_average' in record and 'dsm5_evaluation' not in record)
    )
    
    return has_old_fields or missing_new_fields or has_old_structure


def validate_scale_data(evaluation_data: Dict[str, Any], scale: str) -> Dict[str, Any]:
    """
    验证和修复量表数据的完整性
    
    Args:
        evaluation_data: 量表评估数据
        scale: 量表类型 ('ABC', 'DSM5', 'CARS', 'ASSQ')
    
    Returns:
        验证结果
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'fixed_fields': []
    }
    
    if scale == 'ABC':
        # 验证ABC数据
        required_fields = ['total_score', 'severity', 'domain_scores']
        for field in required_fields:
            if field not in evaluation_data:
                validation_result['errors'].append(f"缺少必需字段: {field}")
                validation_result['valid'] = False
        
        # 验证总分范围
        if 'total_score' in evaluation_data:
            score = evaluation_data['total_score']
            if not 0 <= score <= 158:
                validation_result['warnings'].append(f"ABC总分超出正常范围: {score}")
    
    elif scale == 'DSM5':
        # 验证DSM-5数据
        required_fields = ['scores', 'core_symptom_average']
        for field in required_fields:
            if field not in evaluation_data:
                validation_result['errors'].append(f"缺少必需字段: {field}")
                validation_result['valid'] = False
        
        # 验证核心症状均分
        if 'core_symptom_average' in evaluation_data:
            avg = evaluation_data['core_symptom_average']
            if not 0 <= avg <= 5:
                validation_result['warnings'].append(f"DSM-5核心症状均分超出范围: {avg}")
    
    elif scale == 'CARS':
        # 验证CARS数据
        required_fields = ['total_score', 'severity', 'item_scores']
        for field in required_fields:
            if field not in evaluation_data:
                validation_result['errors'].append(f"缺少必需字段: {field}")
                validation_result['valid'] = False
        
        # 验证总分范围
        if 'total_score' in evaluation_data:
            score = evaluation_data['total_score']
            if not 15 <= score <= 60:
                validation_result['warnings'].append(f"CARS总分超出正常范围: {score}")
        
        # 验证项目数
        if 'item_scores' in evaluation_data:
            if len(evaluation_data['item_scores']) != 15:
                validation_result['warnings'].append(
                    f"CARS项目数不正确: {len(evaluation_data['item_scores'])}/15"
                )
    
    elif scale == 'ASSQ':
        # 验证ASSQ数据
        required_fields = ['total_score', 'screening_result']
        for field in required_fields:
            if field not in evaluation_data:
                validation_result['errors'].append(f"缺少必需字段: {field}")
                validation_result['valid'] = False
        
        # 验证总分范围
        if 'total_score' in evaluation_data:
            score = evaluation_data['total_score']
            if not 0 <= score <= 54:
                validation_result['warnings'].append(f"ASSQ总分超出正常范围: {score}")
    
    return validation_result


def export_scale_comparison(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    导出量表比较数据
    
    Args:
        records: 评估记录列表
    
    Returns:
        量表比较统计
    """
    comparison_data = {
        'total_records': len(records),
        'scale_usage': {
            'ABC': 0,
            'DSM5': 0,
            'CARS': 0,
            'ASSQ': 0
        },
        'multi_scale_records': 0,
        'consistency_analysis': [],
        'severity_distribution': {}
    }
    
    for record in records:
        # 统计量表使用情况
        scales_used = record.get('selected_scales', [])
        for scale in scales_used:
            if scale in comparison_data['scale_usage']:
                comparison_data['scale_usage'][scale] += 1
        
        # 统计多量表记录
        if len(scales_used) > 1:
            comparison_data['multi_scale_records'] += 1
            
            # 分析一致性（如果有多个量表）
            if 'scale_comparison' in record:
                comparison = record['scale_comparison']
                if 'consistency' in comparison:
                    comparison_data['consistency_analysis'].append({
                        'record_id': record.get('experiment_id', 'unknown'),
                        'scales': scales_used,
                        'consistency': comparison['consistency'].get('overall', 'unknown')
                    })
    
    # 计算百分比
    if comparison_data['total_records'] > 0:
        comparison_data['scale_usage_percentage'] = {
            scale: (count / comparison_data['total_records']) * 100
            for scale, count in comparison_data['scale_usage'].items()
        }
        
        comparison_data['multi_scale_percentage'] = (
            comparison_data['multi_scale_records'] / comparison_data['total_records']
        ) * 100
    
    return comparison_data


def create_migration_report(original_records: List[Dict], migrated_records: List[Dict]) -> str:
    """
    创建迁移报告
    
    Args:
        original_records: 原始记录
        migrated_records: 迁移后记录
    
    Returns:
        迁移报告文本
    """
    report = []
    report.append("=" * 50)
    report.append("量表数据迁移报告")
    report.append("=" * 50)
    report.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 基本统计
    report.append("## 基本统计")
    report.append(f"- 原始记录数: {len(original_records)}")
    report.append(f"- 迁移后记录数: {len(migrated_records)}")
    report.append("")
    
    # 量表覆盖统计
    report.append("## 量表覆盖情况")
    
    # 统计迁移前的量表使用
    before_stats = {'ABC': 0, 'DSM5': 0, 'CARS': 0, 'ASSQ': 0}
    for record in original_records:
        if 'abc_evaluation' in record or 'abc_total_score' in record:
            before_stats['ABC'] += 1
        if 'dsm5_evaluation' in record or 'dsm5_core_symptom_average' in record:
            before_stats['DSM5'] += 1
        if 'cars_evaluation' in record:
            before_stats['CARS'] += 1
        if 'assq_evaluation' in record:
            before_stats['ASSQ'] += 1
    
    # 统计迁移后的量表使用
    after_stats = {'ABC': 0, 'DSM5': 0, 'CARS': 0, 'ASSQ': 0}
    for record in migrated_records:
        for scale in record.get('selected_scales', []):
            if scale in after_stats:
                after_stats[scale] += 1
    
    report.append("迁移前:")
    for scale, count in before_stats.items():
        report.append(f"  - {scale}: {count} 条记录")
    
    report.append("")
    report.append("迁移后:")
    for scale, count in after_stats.items():
        report.append(f"  - {scale}: {count} 条记录")
    
    # 数据完整性检查
    report.append("")
    report.append("## 数据完整性")
    
    missing_data = 0
    for record in migrated_records:
        if 'selected_scales' not in record or not record['selected_scales']:
            missing_data += 1
    
    report.append(f"- 包含量表信息的记录: {len(migrated_records) - missing_data}")
    report.append(f"- 缺少量表信息的记录: {missing_data}")
    
    # 建议
    report.append("")
    report.append("## 建议")
    if missing_data > 0:
        report.append("- 部分记录缺少量表信息，建议手动检查")
    if before_stats['CARS'] == 0 and before_stats['ASSQ'] == 0:
        report.append("- 历史数据中没有CARS和ASSQ评估，新功能可以正常使用")
    report.append("- 建议备份原始数据后再进行迁移")
    
    report.append("")
    report.append("=" * 50)
    
    return "\n".join(report)