# -*- coding: utf-8 -*-
"""
Curriculum Package
Exports CURRICULUM_MODULES combining all 7 authoritative engineering modules.
"""

from app.curriculum.module1_fundamentals import MODULE_1
from app.curriculum.module2_control_flow import MODULE_2
from app.curriculum.module3_data_structures import MODULE_3
from app.curriculum.module4_functions import MODULE_4
from app.curriculum.module5_oop import MODULE_5
from app.curriculum.module6_advanced import MODULE_6
from app.curriculum.module7_practical import MODULE_7

CURRICULUM_MODULES = [
    MODULE_1,
    MODULE_2,
    MODULE_3,
    MODULE_4,
    MODULE_5,
    MODULE_6,
    MODULE_7,
]

