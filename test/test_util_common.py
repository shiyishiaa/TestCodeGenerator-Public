import sys
import unittest

from loguru import logger

from util import encrypt, decrypt
from util.util_common import load_key, generate_and_store_key


class TestUtilCommon(unittest.TestCase):
    generate_key = '--generate-key' in sys.argv

    @unittest.skipIf(not generate_key, "skip generate_and_store_key")
    def test_a_generate_and_store_key(self):
        key = generate_and_store_key()
        logger.info(f"generate_and_store_key: {key}")
        self.assertIsNotNone(key, "generate_and_store_key should not be None")

    def test_b_load_key(self):
        key = load_key()
        logger.info(f"load_key: {key}")
        self.assertIsNotNone(key, "load_key should not be None")

    def test_c_encrypt(self):
        e = encrypt("test")
        logger.info(f"encrypt: {e}")
        self.assertIsNotNone(e, "encrypt should not be None")

    def test_d_decrypt(self):
        d = decrypt(encrypt("test"))
        logger.info(f"decrypt: {d}")
        self.assertEqual(d, "test")


if __name__ == "__main__":
    unittest.main()
