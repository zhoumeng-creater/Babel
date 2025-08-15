"""基于分数的对话生成器

根据目标评估分数生成相应的孤独症儿童行为对话
"""
import datetime
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import streamlit as st

from common.api_client import call_kimi_api
from autism.configs import CLINICAL_SCENE_CONFIG
from autism.evaluation.enhanced_unified_evaluator import (
    run_enhanced_experiment,
    evaluate_dialogue_with_scales
)

from .score_to_profile_mapper import ScoreToProfileMapper


class ScoreBasedDialogueGenerator:
    """基于评估分数生成对话的生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.mapper = ScoreToProfileMapper()
        self.max_generation_attempts = 3
        self.score_tolerance = {
            'abc_total': 10,  # ABC总分容差±10分
            'dsm5_core': 0.5,  # DSM5核心症状容差±0.5
            'cars_total': 5,   # CARS总分容差±5分
            'assq_total': 5    # ASSQ筛查分容差±5分
        }
    
    def generate_from_scores(
        self,
        target_scores: Dict[str, float],
        scene_config: Optional[Dict[str, Any]] = None,
        scales_to_validate: Optional[List[str]] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        根据目标评估分数生成对话
        
        Args:
            target_scores: 目标分数 {'abc_total': 75, 'dsm5_core': 3.5, ...}
            scene_config: 场景配置 {'scene': '...', 'activity': '...', 'trigger': '...'}
            scales_to_validate: 用于验证的量表列表
            verbose: 是否显示详细信息
        
        Returns:
            包含生成对话和验证结果的字典
        """
        if verbose and st:
            st.info("🎯 开始根据目标分数生成对话...")
        
        # 1. 将分数映射为autism_profile
        initial_profile = self.mapper.map_scores_to_profile(target_scores)
        
        if verbose and st:
            st.write(f"✓ 已生成初始特征配置，严重程度：{initial_profile['severity_level']}")
        
        # 2. 优化profile以更好匹配目标分数
        optimized_profile = self.mapper.optimize_profile_for_scores(
            initial_profile,
            target_scores,
            max_iterations=5
        )
        
        # 3. 设置默认场景配置
        if not scene_config:
            scene_config = self._get_default_scene_config()
        
        # 4. 确定要验证的量表
        if not scales_to_validate:
            scales_to_validate = self._determine_scales_from_scores(target_scores)
        
        # 5. 生成对话并验证
        best_result = None
        best_distance = float('inf')
        generation_history = []
        
        for attempt in range(self.max_generation_attempts):
            if verbose and st:
                st.write(f"🔄 生成尝试 {attempt + 1}/{self.max_generation_attempts}")
            
            # 生成对话
            dialogue = self._generate_dialogue_with_scores(
                optimized_profile,
                target_scores,
                scene_config,
                attempt
            )
            
            # 评估生成的对话
            scene_data = CLINICAL_SCENE_CONFIG[scene_config['scene']]
            evaluation_result = evaluate_dialogue_with_scales(
                dialogue,
                optimized_profile,
                scene_data,
                scales_to_validate
            )
            
            # 计算实际分数
            actual_scores = self._extract_actual_scores(evaluation_result, scales_to_validate)
            
            # 计算与目标的距离
            distance = self._calculate_score_distance(actual_scores, target_scores)
            
            # 记录生成历史
            generation_history.append({
                'attempt': attempt + 1,
                'dialogue': dialogue,
                'actual_scores': actual_scores,
                'distance': distance,
                'evaluation': evaluation_result
            })
            
            if verbose and st:
                self._display_score_comparison(target_scores, actual_scores)
            
            # 检查是否满足容差要求
            if self._check_tolerance(actual_scores, target_scores):
                if verbose and st:
                    st.success(f"✅ 成功！生成的对话符合目标分数要求")
                
                return self._prepare_final_result(
                    dialogue,
                    optimized_profile,
                    scene_config,
                    target_scores,
                    actual_scores,
                    evaluation_result,
                    generation_history,
                    success=True
                )
            
            # 保存最佳结果
            if distance < best_distance:
                best_distance = distance
                best_result = {
                    'dialogue': dialogue,
                    'actual_scores': actual_scores,
                    'evaluation': evaluation_result
                }
            
            # 如果差距较大，调整profile
            if distance > 0.3:
                optimized_profile = self._adjust_profile_based_on_gap(
                    optimized_profile,
                    actual_scores,
                    target_scores
                )
        
        # 返回最佳结果
        if verbose and st:
            st.warning(f"⚠️ 未能完全匹配目标分数，返回最接近的结果")
        
        return self._prepare_final_result(
            best_result['dialogue'],
            optimized_profile,
            scene_config,
            target_scores,
            best_result['actual_scores'],
            best_result['evaluation'],
            generation_history,
            success=False
        )
    
    def generate_batch_from_scores(
        self,
        score_sets: List[Dict[str, float]],
        scene_configs: Optional[List[Dict[str, Any]]] = None,
        scales_to_validate: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量生成基于分数的对话
        
        Args:
            score_sets: 目标分数集合列表
            scene_configs: 场景配置列表
            scales_to_validate: 验证量表列表
        
        Returns:
            生成结果列表
        """
        results = []
        
        # 如果没有提供场景配置，使用默认配置
        if not scene_configs:
            scene_configs = [self._get_default_scene_config() for _ in score_sets]
        
        # 确保场景配置数量匹配
        if len(scene_configs) < len(score_sets):
            scene_configs.extend([self._get_default_scene_config()] * (len(score_sets) - len(scene_configs)))
        
        for i, (scores, scene) in enumerate(zip(score_sets, scene_configs)):
            if st:
                st.write(f"📝 处理第 {i+1}/{len(score_sets)} 个评估...")
            
            result = self.generate_from_scores(
                scores,
                scene,
                scales_to_validate,
                verbose=False
            )
            
            result['batch_index'] = i + 1
            results.append(result)
        
        return results
    
    def validate_dialogue_against_scores(
        self,
        dialogue: str,
        target_scores: Dict[str, float],
        autism_profile: Dict[str, Any],
        scene_config: Dict[str, Any],
        scales: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        验证对话是否符合目标分数
        
        Returns:
            验证结果，包含实际分数、偏差和是否通过
        """
        if not scales:
            scales = self._determine_scales_from_scores(target_scores)
        
        # 评估对话
        scene_data = CLINICAL_SCENE_CONFIG[scene_config['scene']]
        evaluation_result = evaluate_dialogue_with_scales(
            dialogue,
            autism_profile,
            scene_data,
            scales
        )
        
        # 提取实际分数
        actual_scores = self._extract_actual_scores(evaluation_result, scales)
        
        # 计算偏差
        deviations = {}
        for scale in target_scores:
            if scale in actual_scores:
                deviation = actual_scores[scale] - target_scores[scale]
                deviation_percent = (deviation / target_scores[scale] * 100) if target_scores[scale] != 0 else 0
                deviations[scale] = {
                    'absolute': deviation,
                    'percentage': deviation_percent,
                    'within_tolerance': abs(deviation) <= self.score_tolerance.get(scale, 5)
                }
        
        # 判断是否通过验证
        all_within_tolerance = all(d['within_tolerance'] for d in deviations.values())
        
        return {
            'target_scores': target_scores,
            'actual_scores': actual_scores,
            'deviations': deviations,
            'passed': all_within_tolerance,
            'evaluation_details': evaluation_result
        }
    
    # ========== 私有辅助方法 ==========
    
    def _get_default_scene_config(self) -> Dict[str, Any]:
        """获取默认场景配置"""
        scene_name = list(CLINICAL_SCENE_CONFIG.keys())[0]
        scene_data = CLINICAL_SCENE_CONFIG[scene_name]
        
        return {
            'scene': scene_name,
            'activity': scene_data['activities'][0],
            'trigger': scene_data['triggers'][0]
        }
    
    def _determine_scales_from_scores(self, target_scores: Dict[str, float]) -> List[str]:
        """根据目标分数确定要使用的量表"""
        scales = []
        
        if 'abc_total' in target_scores:
            scales.append('ABC')
        if 'dsm5_core' in target_scores:
            scales.append('DSM5')
        if 'cars_total' in target_scores:
            scales.append('CARS')
        if 'assq_total' in target_scores:
            scales.append('ASSQ')
        
        # 如果没有指定，默认使用ABC和DSM5
        if not scales:
            scales = ['ABC', 'DSM5']
        
        return scales
    
    def _generate_dialogue_with_scores(
        self,
        autism_profile: Dict[str, Any],
        target_scores: Dict[str, float],
        scene_config: Dict[str, Any],
        attempt: int
    ) -> str:
        """生成符合目标分数的对话"""
        # 构建强调目标分数的system prompt
        system_prompt = self._build_score_targeted_prompt(autism_profile, target_scores, attempt)
        
        # 构建场景prompt
        scene_data = CLINICAL_SCENE_CONFIG[scene_config['scene']]
        dialogue_prompt = (
            f"临床观察情境：{scene_config['scene']} - {scene_config['activity']}\n"
            f"观察要点：{', '.join(scene_data['observation_points'][:3])}\n"
            f"触发因素：{scene_config['trigger']}\n"
            f"参与角色：孤独症儿童、{scene_data['roles'][1]}、{scene_data['roles'][2]}\n"
            f"\n【重要】：请生成行为表现，使得：\n"
        )
        
        # 添加具体的分数要求
        if 'abc_total' in target_scores:
            dialogue_prompt += f"- ABC量表评分约为{target_scores['abc_total']}分\n"
        if 'dsm5_core' in target_scores:
            dialogue_prompt += f"- DSM-5核心症状严重度约为{target_scores['dsm5_core']}/5\n"
        if 'cars_total' in target_scores:
            dialogue_prompt += f"- CARS总分约为{target_scores['cars_total']}分\n"
        if 'assq_total' in target_scores:
            dialogue_prompt += f"- ASSQ筛查分约为{target_scores['assq_total']}分\n"
        
        dialogue_prompt += (
            f"\n要求：15-20轮对话，准确体现上述评分水平的行为特征。\n"
            f"格式：'角色名:内容'，每句换行。"
        )
        
        # 调整温度参数（后续尝试降低温度以获得更稳定的结果）
        temperature = 0.7 - (attempt * 0.1)
        
        return call_kimi_api(dialogue_prompt, system_prompt, temperature=temperature)
    
    def _build_score_targeted_prompt(
        self,
        autism_profile: Dict[str, Any],
        target_scores: Dict[str, float],
        attempt: int
    ) -> str:
        """构建针对目标分数的system prompt"""
        # 基础描述
        prompt = (
            "你是一个专业的临床行为观察专家。你需要生成符合特定评估分数的孤独症儿童行为表现。\n\n"
            f"目标评估分数：\n"
        )
        
        # 添加分数要求和对应的行为指导
        severity_guidance = []
        
        if 'abc_total' in target_scores:
            abc_score = target_scores['abc_total']
            prompt += f"- ABC量表总分：{abc_score}分（满分158分）\n"
            
            if abc_score >= 100:
                severity_guidance.append("展现严重的孤独症行为，包括明显的社交障碍、语言缺陷、刻板行为")
            elif abc_score >= 67:
                severity_guidance.append("展现中度孤独症行为，社交和沟通困难明显，有重复行为")
            elif abc_score >= 53:
                severity_guidance.append("展现轻到中度的孤独症特征，部分社交困难，轻度刻板行为")
            else:
                severity_guidance.append("展现轻微的孤独症倾向，主要是社交不适和轻微的行为特点")
        
        if 'dsm5_core' in target_scores:
            dsm5_score = target_scores['dsm5_core']
            prompt += f"- DSM-5核心症状：{dsm5_score}/5.0\n"
            
            if dsm5_score >= 4.0:
                severity_guidance.append("需要非常大量的支持，功能严重受损")
            elif dsm5_score >= 3.0:
                severity_guidance.append("需要大量支持，日常功能明显受限")
            elif dsm5_score >= 2.0:
                severity_guidance.append("需要支持，在无支持情况下有明显困难")
            else:
                severity_guidance.append("需要一些支持，主要在社交场合")
        
        if 'cars_total' in target_scores:
            cars_score = target_scores['cars_total']
            prompt += f"- CARS总分：{cars_score}分（15-60分）\n"
            
            if cars_score >= 37:
                severity_guidance.append("重度孤独症表现，多个领域严重异常")
            elif cars_score >= 30:
                severity_guidance.append("中度孤独症，明显但非严重的异常")
            else:
                severity_guidance.append("轻度或无孤独症，轻微异常")
        
        if 'assq_total' in target_scores:
            assq_score = target_scores['assq_total']
            prompt += f"- ASSQ筛查分：{assq_score}分（0-54分）\n"
            
            if assq_score >= 22:
                severity_guidance.append("高风险，明显的孤独症特征")
            elif assq_score >= 15:
                severity_guidance.append("中等风险，需要进一步评估")
            else:
                severity_guidance.append("低风险，轻微特征")
        
        # 添加行为指导
        prompt += f"\n行为表现指导：\n"
        for guidance in severity_guidance:
            prompt += f"- {guidance}\n"
        
        # 添加具体的特征配置
        prompt += f"\n孤独症儿童特征配置：\n"
        prompt += f"【社交特征】：{autism_profile['social_characteristics']}\n"
        prompt += f"【沟通特征】：{autism_profile['communication_characteristics']}\n"
        prompt += f"【行为特征】：{autism_profile['behavioral_characteristics']}\n"
        prompt += f"【认知特征】：{autism_profile['cognitive_characteristics']}\n"
        prompt += f"【情绪特征】：{autism_profile['emotional_characteristics']}\n"
        prompt += f"【日常生活】：{autism_profile['daily_living']}\n"
        
        # 添加行为示例
        if 'behavioral_examples' in autism_profile:
            prompt += f"\n典型行为示例：\n"
            for i, example in enumerate(autism_profile['behavioral_examples'][:5], 1):
                prompt += f"{i}. {example}\n"
        
        # 根据尝试次数调整指导
        if attempt > 0:
            prompt += (
                f"\n【第{attempt + 1}次生成】请更精确地匹配目标分数，"
                f"确保行为表现的严重程度与分数完全一致。"
            )
        
        prompt += (
            "\n\n生成要求：\n"
            "1. 行为表现必须与目标分数高度一致\n"
            "2. 包含足够的具体行为细节供评估\n"
            "3. 避免过度夸张或过度轻描淡写\n"
            "4. 确保行为的频率和强度符合分数要求\n"
        )
        
        return prompt
    
    def _extract_actual_scores(
        self,
        evaluation_result: Dict[str, Any],
        scales: List[str]
    ) -> Dict[str, float]:
        """从评估结果中提取实际分数"""
        actual_scores = {}
        
        if 'ABC' in scales and 'abc_evaluation' in evaluation_result:
            actual_scores['abc_total'] = evaluation_result['abc_evaluation']['total_score']
        
        if 'DSM5' in scales and 'dsm5_evaluation' in evaluation_result:
            actual_scores['dsm5_core'] = evaluation_result['dsm5_evaluation']['core_symptom_average']
        
        if 'CARS' in scales and 'cars_evaluation' in evaluation_result:
            actual_scores['cars_total'] = evaluation_result['cars_evaluation']['total_score']
        
        if 'ASSQ' in scales and 'assq_evaluation' in evaluation_result:
            actual_scores['assq_total'] = evaluation_result['assq_evaluation']['total_score']
        
        return actual_scores
    
    def _calculate_score_distance(
        self,
        actual_scores: Dict[str, float],
        target_scores: Dict[str, float]
    ) -> float:
        """计算实际分数与目标分数的距离"""
        distance = 0.0
        count = 0
        
        for scale in target_scores:
            if scale in actual_scores:
                # 归一化差异
                if scale == 'abc_total':
                    diff = abs(actual_scores[scale] - target_scores[scale]) / 158
                elif scale == 'dsm5_core':
                    diff = abs(actual_scores[scale] - target_scores[scale]) / 5
                elif scale == 'cars_total':
                    diff = abs(actual_scores[scale] - target_scores[scale]) / 60
                elif scale == 'assq_total':
                    diff = abs(actual_scores[scale] - target_scores[scale]) / 54
                else:
                    diff = abs(actual_scores[scale] - target_scores[scale])
                
                distance += diff
                count += 1
        
        return distance / count if count > 0 else 1.0
    
    def _check_tolerance(
        self,
        actual_scores: Dict[str, float],
        target_scores: Dict[str, float]
    ) -> bool:
        """检查实际分数是否在容差范围内"""
        for scale in target_scores:
            if scale in actual_scores:
                diff = abs(actual_scores[scale] - target_scores[scale])
                tolerance = self.score_tolerance.get(scale, 5)
                
                if diff > tolerance:
                    return False
        
        return True
    
    def _display_score_comparison(
        self,
        target_scores: Dict[str, float],
        actual_scores: Dict[str, float]
    ):
        """显示分数对比"""
        if st:
            cols = st.columns(len(target_scores))
            
            for i, scale in enumerate(target_scores):
                with cols[i]:
                    target = target_scores[scale]
                    actual = actual_scores.get(scale, 0)
                    diff = actual - target
                    
                    # 显示量表名称
                    scale_name = {
                        'abc_total': 'ABC总分',
                        'dsm5_core': 'DSM5核心',
                        'cars_total': 'CARS总分',
                        'assq_total': 'ASSQ筛查'
                    }.get(scale, scale)
                    
                    st.metric(
                        scale_name,
                        f"{actual:.1f}",
                        f"{diff:+.1f}",
                        delta_color="inverse" if scale in ['abc_total', 'cars_total', 'assq_total'] else "normal"
                    )
                    st.caption(f"目标: {target:.1f}")
    
    def _adjust_profile_based_on_gap(
        self,
        profile: Dict[str, Any],
        actual_scores: Dict[str, float],
        target_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """根据分数差距调整profile"""
        adjusted = profile.copy()
        
        # 计算需要的调整
        adjustments = {}
        for scale in target_scores:
            if scale in actual_scores:
                adjustments[scale] = target_scores[scale] - actual_scores[scale]
        
        # 应用调整
        if 'abc_total' in adjustments:
            gap = adjustments['abc_total']
            
            if gap > 20:  # 实际分数太低，需要加重症状
                adjusted['behavioral_characteristics'] = (
                    adjusted['behavioral_characteristics']
                    .replace("偶尔", "频繁")
                    .replace("轻度", "重度")
                )
                adjusted['social_characteristics'] = (
                    adjusted['social_characteristics']
                    .replace("有时", "经常")
                    .replace("能够", "困难")
                )
            elif gap < -20:  # 实际分数太高，需要减轻症状
                adjusted['behavioral_characteristics'] = (
                    adjusted['behavioral_characteristics']
                    .replace("频繁", "偶尔")
                    .replace("重度", "轻度")
                )
                adjusted['social_characteristics'] = (
                    adjusted['social_characteristics']
                    .replace("经常", "有时")
                    .replace("困难", "能够")
                )
        
        return adjusted
    
    def _prepare_final_result(
        self,
        dialogue: str,
        profile: Dict[str, Any],
        scene_config: Dict[str, Any],
        target_scores: Dict[str, float],
        actual_scores: Dict[str, float],
        evaluation_result: Dict[str, Any],
        generation_history: List[Dict[str, Any]],
        success: bool
    ) -> Dict[str, Any]:
        """准备最终返回结果"""
        # 生成唯一ID
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        experiment_id = f"SCORE_GEN_{timestamp}"
        
        return {
            'experiment_id': experiment_id,
            'timestamp': datetime.datetime.now(),
            'generation_method': 'score_based',
            'success': success,
            'dialogue': dialogue,
            'autism_profile': profile,
            'scene_config': scene_config,
            'target_scores': target_scores,
            'actual_scores': actual_scores,
            'score_deviations': {
                scale: actual_scores.get(scale, 0) - target_scores[scale]
                for scale in target_scores
            },
            'evaluation_result': evaluation_result,
            'generation_history': generation_history,
            'notes': (
                f"基于目标分数生成的对话 - "
                f"{'成功匹配' if success else '最佳近似'}"
            )
        }