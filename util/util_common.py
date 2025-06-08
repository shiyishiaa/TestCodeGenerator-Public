import base64
from threading import Lock

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from loguru import logger

_key_lock = Lock()


def generate_and_store_key() -> bytes:
    """Generates a new AES key and stores it securely."""
    key = get_random_bytes(32)
    logger.info("Generated new AES-256 key")
    from .util_qt import write_settings
    write_settings("encryption", "key", key)
    return key


def load_key() -> bytes:
    """Loads the AES key from disk."""
    with _key_lock:
        from .util_qt import read_settings
        if key := read_settings("encryption", "key", type_=bytes):
            if len(key) not in (16, 24, 32):
                raise ValueError("Invalid AES key length (must be 16, 24, or 32 bytes)")
            return key
        else:
            return generate_and_store_key()


def encrypt(plaintext: str) -> str:
    """Encrypts text using AES-GCM."""
    plaintext_bytes = plaintext.encode('utf-8')
    nonce = get_random_bytes(12)
    cipher = AES.new(load_key(), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext_bytes)
    encrypted_data = nonce + ciphertext + tag
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt(encrypted_data_b64: str) -> str:
    """Decrypts text using AES-GCM."""
    try:
        encrypted_data = base64.b64decode(encrypted_data_b64)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:-16]
        tag = encrypted_data[-16:]
        cipher = AES.new(load_key(), AES.MODE_GCM, nonce=nonce)
        plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext_bytes.decode('utf-8')
    except Exception as e:
        logger.error("Decryption failed!")
        raise ValueError("Decryption failed: Invalid or tampered data") from e
