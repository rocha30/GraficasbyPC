"""
Mathematical utilities for 3D graphics
"""
from .MathLib import *

__all__ = [
    'TranslationMatrix', 'RotationMatrix', 'ScaleMatrix',
    'normalize', 'dot_product', 'cross_product', 'magnitude',
    'calculate_normal', 'lerp', 'clamp'
]