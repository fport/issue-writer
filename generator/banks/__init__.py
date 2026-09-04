"""Icerik havuzlari.

Domain modulleri import edildiklerinde kendilerini DOMAINS'e kaydeder; bu yuzden
import'lar "kullanilmiyor" gorunur ama yan etkileri icin gereklidir.
"""
# ruff: noqa: F401
from . import (
    core,
    d1_fin_ecom_saas,
    d2_ecom_saas,
    d3_health_log_edu,
    d4_devops_game_media,
    d5_betting,
)
from .core import DOMAINS

__all__ = ["DOMAINS", "core"]
