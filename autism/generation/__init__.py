"""基于分数的对话生成模块"""

from .score_to_profile_mapper import ScoreToProfileMapper
from .score_based_dialogue_generator import ScoreBasedDialogueGenerator

__all__ = [
    'ScoreToProfileMapper',
    'ScoreBasedDialogueGenerator'
]