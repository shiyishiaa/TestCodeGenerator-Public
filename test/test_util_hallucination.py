from pathlib import Path
from unittest import TestCase

from loguru import logger

from util import hallucination


class TestHallucination(TestCase):
    def test_hallucination(self):
        image_path = Path("../_screenshots/vue-element-admin/charts_2024_05_16_22_30_42.png")
        result = hallucination(image_path)
        logger.info(result)
        assert result
