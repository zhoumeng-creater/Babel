"""CSV导入器实现"""
import pandas as pd
import io
from typing import List, Dict, Any, Tuple, Union
from .base_importer import BaseImporter, ImportError


class CSVImporter(BaseImporter):
    """CSV文件导入器"""
    
    def __init__(self, assessment_type: str = 'autism'):
        super().__init__(assessment_type)
        self.encoding_list = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'gb18030']
        
    def parse_file(self, file_content: Union[bytes, str, io.IOBase], **kwargs) -> List[Dict[str, Any]]:
        """
        解析CSV文件内容
        
        Args:
            file_content: 文件内容（字节、字符串或文件对象）
            **kwargs: 额外参数
                - encoding: 指定编码
                - delimiter: 分隔符
                
        Returns:
            解析后的记录列表
        """
        encoding = kwargs.get('encoding', None)
        delimiter = kwargs.get('delimiter', ',')
        
        # 尝试不同的编码
        if encoding:
            encodings_to_try = [encoding]
        else:
            encodings_to_try = self.encoding_list
        
        df = None
        successful_encoding = None
        
        for enc in encodings_to_try:
            try:
                if isinstance(file_content, bytes):
                    content = io.StringIO(file_content.decode(enc))
                elif isinstance(file_content, str):
                    content = io.StringIO(file_content)
                else:
                    content = file_content
                
                df = pd.read_csv(
                    content,
                    encoding=enc if not isinstance(file_content, (str, io.IOBase)) else None,
                    delimiter=delimiter,
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None']
                )
                successful_encoding = enc
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        
        if df is None:
            raise ImportError("无法解析CSV文件，请检查文件编码和格式")
        
        # 清理列名（去除空格和特殊字符）
        df.columns = df.columns.str.strip()
        
        # 转换为字典列表
        records = df.to_dict('records')
        
        # 处理空值
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, (int, float)) and pd.isna(value):
                    record[key] = None
        
        return records
    
    def validate_structure(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证CSV数据结构
        
        Args:
            data: 数据列表
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        if not data:
            errors.append("CSV文件为空")
            return False, errors
        
        # 获取第一行的列名作为参考
        first_row = data[0]
        columns = set(first_row.keys())
        
        # 检查必需字段
        if self.assessment_type == 'autism':
            required_columns = self._get_autism_required_columns()
        else:
            required_columns = self._get_children_required_columns()
        
        missing_columns = []
        for col in required_columns:
            if not any(col in c or c in col for c in columns):
                missing_columns.append(col)
        
        if missing_columns:
            errors.append(f"缺少必需列: {', '.join(missing_columns)}")
        
        # 检查所有行的列一致性
        for idx, row in enumerate(data[1:], start=2):
            row_columns = set(row.keys())
            if row_columns != columns:
                diff = columns.symmetric_difference(row_columns)
                errors.append(f"第{idx}行列不一致: {diff}")
                if len(errors) > 10:  # 限制错误数量
                    errors.append("...")
                    break
        
        return len(errors) == 0, errors
    
    def _get_autism_required_columns(self) -> List[str]:
        """获取孤独症评估必需列"""
        return ['评估时间', '评估情境']
    
    def _get_children_required_columns(self) -> List[str]:
        """获取儿童发展评估必需列"""
        return ['观察时间', '观察情境']
    
    def _convert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换CSV记录为标准格式
        
        Args:
            record: CSV记录
            
        Returns:
            转换后的记录
        """
        converted = {}
        
        # 处理时间字段
        time_fields = ['评估时间', '观察时间', 'timestamp']
        for field in time_fields:
            if field in record and record[field]:
                timestamp = self._parse_timestamp(str(record[field]))
                if timestamp:
                    converted['timestamp'] = timestamp
                    break
        
        if 'timestamp' not in converted:
            converted['timestamp'] = self._parse_timestamp('')
        
        # 根据评估类型处理不同字段
        if self.assessment_type == 'autism':
            converted.update(self._convert_autism_record(record))
        else:
            converted.update(self._convert_children_record(record))
        
        return converted
    
    def _convert_autism_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """转换孤独症评估记录"""
        converted = {
            'assessment_type': 'autism',
            'scene': record.get('评估情境', ''),
            'activity': record.get('观察活动', ''),
            'trigger': record.get('触发因素', ''),
            'notes': record.get('备注', ''),
            'template': record.get('配置类型', '自定义')
        }
        
        # 处理评估ID
        if '评估ID' in record:
            converted['experiment_id'] = record['评估ID']
        
        # 检测数据格式并转换评估数据
        if 'ABC总分' in record and 'DSM5核心症状均分' in record:
            # 统一评估格式
            converted['assessment_standard'] = 'UNIFIED'
            converted.update(self._extract_unified_scores(record))
        elif 'ABC总分' in record:
            # 旧版ABC格式
            converted['assessment_standard'] = 'ABC'
            converted.update(self._extract_abc_scores(record))
        elif 'DSM5_' in str(record.keys()):
            # 旧版DSM5格式
            converted['assessment_standard'] = 'DSM5'
            converted.update(self._extract_dsm5_scores(record))
        
        return converted
    
    def _convert_children_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """转换儿童发展评估记录"""
        converted = {
            'assessment_type': 'children',
            'scene': record.get('观察情境', ''),
            'activity': record.get('观察活动', ''),
            'trigger': record.get('情境触发', ''),
            'notes': record.get('备注', ''),
            'template': record.get('年龄发展阶段', '自定义')
        }
        
        # 处理观察ID
        if '观察ID' in record:
            converted['observation_id'] = record['观察ID']
        
        # 提取发展评分
        evaluation_scores = {}
        score_fields = [
            '语言沟通发展', '社交互动能力', '认知学习能力',
            '情绪调节发展', '运动技能发展', '独立自理能力'
        ]
        
        for field in score_fields:
            if field in record:
                try:
                    score = float(record[field])
                    evaluation_scores[field] = score
                except (ValueError, TypeError):
                    pass
        
        if evaluation_scores:
            converted['evaluation_scores'] = evaluation_scores
        
        # 提取儿童发展特征
        profile = {}
        profile_fields = {
            '发展阶段特征': 'stage_characteristics',
            '发展重点': 'development_focus',
            '语言发展配置': 'language_development',
            '社交技能配置': 'social_skills',
            '认知能力配置': 'cognitive_ability',
            '情绪调节配置': 'emotional_regulation',
            '运动技能配置': 'motor_skills',
            '独立性配置': 'independence_level',
            '典型兴趣描述': 'typical_interests'
        }
        
        for cn_field, en_field in profile_fields.items():
            if cn_field in record and record[cn_field]:
                profile[en_field] = record[cn_field]
        
        if profile:
            converted['child_profile'] = profile
        
        return converted
    
    def _extract_unified_scores(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """提取统一评估格式的分数 - 修复版"""
        result = {}
        
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
        
        # ABC评估数据
        abc_evaluation = {
            'total_score': self._safe_float(record.get('ABC总分', 0)),
            'severity': record.get('ABC严重程度', ''),
            'domain_scores': {}
        }
        
        # 提取ABC各领域分数
        for key, value in record.items():
            if key.startswith('ABC_') and key != 'ABC总分':
                # 去除 ABC_ 前缀
                domain = key.replace('ABC_', '')
                
                # 标准化领域名称
                if domain in domain_mapping:
                    normalized_domain = domain_mapping[domain]
                elif not domain.endswith('领域得分'):
                    # 如果不在映射表中且不以"领域得分"结尾，添加后缀
                    normalized_domain = f"{domain}领域得分"
                else:
                    # 已经是标准格式
                    normalized_domain = domain
                
                abc_evaluation['domain_scores'][normalized_domain] = self._safe_float(value)
        
        # 如果没有通过ABC_前缀找到领域分数，尝试其他可能的格式
        if not abc_evaluation['domain_scores']:
            # 尝试直接查找领域名称
            possible_domains = [
                '感觉', '交往', '躯体运动', '运动', '语言', '社交与自理', '自理',
                '感觉领域得分', '交往领域得分', '躯体运动领域得分', '语言领域得分', '社交与自理领域得分'
            ]
            
            for domain in possible_domains:
                if domain in record:
                    # 标准化领域名称
                    normalized_domain = domain_mapping.get(domain, domain)
                    if not normalized_domain.endswith('领域得分'):
                        normalized_domain = f"{normalized_domain}领域得分"
                    
                    abc_evaluation['domain_scores'][normalized_domain] = self._safe_float(record[domain])
        
        result['abc_evaluation'] = abc_evaluation
        
        # DSM-5评估数据
        dsm5_evaluation = {
            'core_symptom_average': self._safe_float(record.get('DSM5核心症状均分', 0)),
            'scores': {}
        }
        
        # 提取DSM-5各项分数
        for key, value in record.items():
            if key.startswith('DSM5_'):
                metric = key.replace('DSM5_', '')
                dsm5_evaluation['scores'][metric] = self._safe_float(value)
        
        result['dsm5_evaluation'] = dsm5_evaluation
        
        return result
    
    def _extract_abc_scores(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """提取ABC评分数据"""
        scores = {}
        
        # 固定的ABC评分项
        abc_items = [
            '感觉', '交往', '躯体运动', '语言', '生活自理',
            '视而不见听而不闻', '人际交往困难', '刻板活动',
            '对环境变化适应困难', '感觉异常', '重复性语言',
            '情感反应异常', '固定兴趣', '多动', '注意力不集中'
        ]
        
        for item in abc_items:
            if item in record:
                scores[item] = self._safe_int(record[item])
        
        return {'evaluation_scores': scores}
    
    def _extract_dsm5_scores(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """提取DSM-5评分数据"""
        scores = {}
        
        for key, value in record.items():
            if 'DSM5_' in key or '社交' in key or '刻板' in key:
                scores[key] = self._safe_float(value)
        
        return {'evaluation_scores': scores}
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        try:
            if pd.isna(value) or value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """安全转换为整数"""
        try:
            if pd.isna(value) or value is None:
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default