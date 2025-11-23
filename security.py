import os
from cryptography.fernet import Fernet
import bcrypt
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

    def _load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
            return key

    def encrypt_file(self, file_path):
        """Encrypts a file in place."""
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = self.cipher_suite.encrypt(data)
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        return True

    def decrypt_file(self, file_path):
        """Returns decrypted content of a file."""
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        return self.cipher_suite.decrypt(encrypted_data)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, stored_hash, password):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

    def get_file_hash(self, file_path):
        """Generate SHA-256 hash of a file for integrity checking."""
        sha256_hash = hashes.Hash(hashes.SHA256())
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.finalize().hex()
