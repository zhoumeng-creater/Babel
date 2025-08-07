"""数据存储管理器 - 处理导入数据与现有数据的集成"""
import streamlit as st
import datetime
import uuid
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class DataStorageManager:
    """数据存储管理器"""
    
    def __init__(self, assessment_type: str = 'autism'):
        self.assessment_type = assessment_type
        self.key_prefix = 'experiment' if assessment_type == 'autism' else 'observation'
        
    def merge_imported_data(self, imported_records: List[Dict[str, Any]], 
                          merge_strategy: str = 'append') -> Tuple[int, List[str]]:
        """
        合并导入的数据到session state
        
        Args:
            imported_records: 导入的记录列表
            merge_strategy: 合并策略 ('append', 'replace', 'skip_duplicates')
            
        Returns:
            (成功合并数, 冲突信息列表)
        """
        # 确保session state中有记录列表
        if 'experiment_records' not in st.session_state:
            st.session_state.experiment_records = []
        
        existing_records = st.session_state.experiment_records
        conflicts = []
        merged_count = 0
        
        if merge_strategy == 'replace':
            # 替换策略：清空现有数据
            st.session_state.experiment_records = []
            existing_records = []
        
        # 创建现有记录的索引
        existing_index = self._create_record_index(existing_records)
        
        for record in imported_records:
            # 处理记录ID
            record_id = self._process_record_id(record)
            
            # 检查重复
            if merge_strategy == 'skip_duplicates':
                duplicate_info = self._check_duplicate(record, existing_index)
                if duplicate_info:
                    conflicts.append(duplicate_info)
                    continue
            
            # 标准化记录
            standardized_record = self._standardize_record(record)
            
            # 添加导入元数据
            standardized_record['import_metadata'] = {
                'imported_at': datetime.datetime.now(),
                'original_id': record.get(f'{self.key_prefix}_id', None),
                'source': 'imported'
            }
            
            # 添加到记录列表
            st.session_state.experiment_records.append(standardized_record)
            merged_count += 1
        
        # 更新统计信息
        self._update_statistics()
        
        return merged_count, conflicts
    
    def _create_record_index(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        """创建记录索引用于快速查找"""
        index = defaultdict(list)
        
        for record in records:
            # 基于时间戳和场景创建索引
            timestamp = record.get('timestamp')
            scene = record.get('scene', '')
            
            if timestamp:
                # 创建时间+场景的键
                time_key = f"{timestamp.strftime('%Y-%m-%d %H:%M')}_{scene}"
                index[time_key].append(record)
            
            # 基于ID创建索引
            record_id = record.get(f'{self.key_prefix}_id')
            if record_id:
                index[f"id_{record_id}"].append(record)
        
        return index
    
    def _check_duplicate(self, record: Dict, existing_index: Dict) -> str:
        """检查是否为重复记录"""
        # 检查ID重复
        record_id = record.get(f'{self.key_prefix}_id')
        if record_id and f"id_{record_id}" in existing_index:
            return f"ID重复: {record_id}"
        
        # 检查时间+场景重复
        timestamp = record.get('timestamp')
        scene = record.get('scene', '')
        
        if timestamp and isinstance(timestamp, datetime.datetime):
            time_key = f"{timestamp.strftime('%Y-%m-%d %H:%M')}_{scene}"
            if time_key in existing_index:
                # 进一步检查内容相似度
                existing = existing_index[time_key][0]
                if self._is_similar_record(record, existing):
                    return f"相似记录: {timestamp.strftime('%Y-%m-%d %H:%M')} - {scene}"
        
        return None
    
    def _is_similar_record(self, record1: Dict, record2: Dict) -> bool:
        """判断两条记录是否相似"""
        # 比较关键字段
        key_fields = ['scene', 'activity', 'template']
        
        for field in key_fields:
            if record1.get(field) != record2.get(field):
                return False
        
        # 比较评分（如果存在）
        if self.assessment_type == 'autism':
            # 比较ABC或DSM5评分
            if 'abc_evaluation' in record1 and 'abc_evaluation' in record2:
                score1 = record1['abc_evaluation'].get('total_score', 0)
                score2 = record2['abc_evaluation'].get('total_score', 0)
                if abs(score1 - score2) > 5:  # 允许小的差异
                    return False
        else:
            # 比较儿童发展评分
            if 'evaluation_scores' in record1 and 'evaluation_scores' in record2:
                scores1 = record1['evaluation_scores']
                scores2 = record2['evaluation_scores']
                # 简单比较是否相同
                if scores1 != scores2:
                    return False
        
        return True
    
    def _process_record_id(self, record: Dict) -> str:
        """处理记录ID，确保唯一性"""
        id_field = f'{self.key_prefix}_id'
        
        if id_field not in record:
            # 生成新ID
            record[id_field] = f"{self.key_prefix.upper()}_{datetime.datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        else:
            # 检查ID格式，必要时添加前缀
            original_id = record[id_field]
            if not original_id.startswith(self.key_prefix.upper()):
                record[id_field] = f"{self.key_prefix.upper()}_IMP_{original_id}"
        
        return record[id_field]
    
    def _standardize_record(self, record: Dict) -> Dict:
        """标准化记录格式"""
        # 确保必需字段存在
        standardized = record.copy()
        
        # 确保有时间戳
        if 'timestamp' not in standardized or not standardized['timestamp']:
            standardized['timestamp'] = datetime.datetime.now()
        elif isinstance(standardized['timestamp'], str):
            # 尝试解析字符串时间戳
            try:
                from common.importer.base_importer import BaseImporter
                importer = BaseImporter(self.assessment_type)
                standardized['timestamp'] = importer._parse_timestamp(standardized['timestamp'])
            except:
                standardized['timestamp'] = datetime.datetime.now()
        
        # 确保有场景
        if 'scene' not in standardized:
            standardized['scene'] = '未知场景'
        
        # 确保有评估类型
        if 'assessment_type' not in standardized:
            standardized['assessment_type'] = self.assessment_type
        
        return standardized
    
    def _update_statistics(self):
        """更新统计信息"""
        if 'experiment_records' in st.session_state:
            records = st.session_state.experiment_records
            
            # 更新统计
            st.session_state['total_records'] = len(records)
            
            # 按来源统计
            imported_count = sum(1 for r in records 
                               if r.get('import_metadata', {}).get('source') == 'imported')
            st.session_state['imported_records'] = imported_count
            st.session_state['native_records'] = len(records) - imported_count
    
    def get_import_summary(self) -> Dict[str, Any]:
        """获取导入数据摘要"""
        if 'experiment_records' not in st.session_state:
            return {
                'total_records': 0,
                'imported_records': 0,
                'native_records': 0,
                'last_import': None
            }
        
        records = st.session_state.experiment_records
        imported_records = [r for r in records 
                          if r.get('import_metadata', {}).get('source') == 'imported']
        
        last_import = None
        if imported_records:
            import_times = [r['import_metadata']['imported_at'] 
                          for r in imported_records 
                          if 'imported_at' in r.get('import_metadata', {})]
            if import_times:
                last_import = max(import_times)
        
        return {
            'total_records': len(records),
            'imported_records': len(imported_records),
            'native_records': len(records) - len(imported_records),
            'last_import': last_import
        }
    
    def cleanup_import_metadata(self):
        """清理导入元数据（可选）"""
        if 'experiment_records' in st.session_state:
            for record in st.session_state.experiment_records:
                if 'import_metadata' in record:
                    del record['import_metadata']