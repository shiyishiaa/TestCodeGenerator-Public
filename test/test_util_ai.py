import unittest
from pathlib import Path

from loguru import logger

from util import chat


class TestCase(unittest.TestCase):
    __system = "You are a helpful assistant."

    def setUp(self):
        self.image_folder = Path(__file__).parent / "image"
        self.text = "What's your name?"
        self.texts = [
            self.text,
            self.text,
        ]
        self.image_url = str((self.image_folder / "img_1.png").resolve())
        self.image_urls = [
            str((self.image_folder / "img_1.png").resolve()),
            str((self.image_folder / "img_2.png").resolve()),
        ]

    def test_no_text_and_image_url(self):
        self.assertRaises(ValueError, chat, system=None, text=None, image_url=None)
        logger.info("No text and image url")

    def test_single_text(self):
        reply = chat(system=self.__system, text=self.text)
        logger.info(reply)
        self.assertIsNotNone(reply)

    def test_multiple_texts(self):
        reply = chat(system=self.__system, text=self.texts)
        logger.info(reply)
        self.assertIsNotNone(reply)

    def test_single_image_url(self):
        reply = chat(system=self.__system, image_url=self.image_url)
        logger.info(reply)
        self.assertIsNotNone(reply)

    def test_multiple_image_urls(self):
        reply = chat(system=self.__system, image_url=self.image_urls)
        logger.info(reply)
        self.assertIsNotNone(reply)


if __name__ == '__main__':
    unittest.main()
