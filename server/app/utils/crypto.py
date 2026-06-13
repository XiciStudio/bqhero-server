"""ECB DES encryption matching the game client's decryption.

Game client (StyleClass.as) decrypts with:
    key = "ESTAAPI_"
    cipher = new ECBMode(new DESKey(key))
    result = cipher.decrypt(base64_decode(data))

Format for money values: "timestamp####amount"
"""

import base64
import hashlib
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import config


def _des_encrypt(plaintext: str) -> bytes:
    """Encrypt string with ECB DES using the game key."""
    key = config.DES_KEY.encode("utf-8")[:8]  # DES uses 8-byte key
    cipher = DES.new(key, DES.MODE_ECB)
    padded = pad(plaintext.encode("utf-8"), DES.block_size)
    return cipher.encrypt(padded)


def _des_decrypt(ciphertext: bytes) -> str:
    """Decrypt bytes with ECB DES using the game key."""
    key = config.DES_KEY.encode("utf-8")[:8]
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted = cipher.decrypt(ciphertext)
    unpadded = unpad(decrypted, DES.block_size)
    return unpadded.decode("utf-8")


def encrypt_money(money: int, timestamp: str) -> str:
    """Encrypt money value for GetMoney/GetTotalRecharge response.

    Format: base64(DES_ECB("timestamp####money"))
    """
    plaintext = f"{timestamp}####{money}"
    encrypted = _des_encrypt(plaintext)
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_money(encrypted_str: str) -> tuple:
    """Decrypt money response. Returns (timestamp, money)."""
    data = base64.b64decode(encrypted_str)
    plaintext = _des_decrypt(data)
    timestamp, money_str = plaintext.split("####", 1)
    return timestamp, int(money_str)


def encrypt_userkey(data: str) -> str:
    """Encrypt data with 'userkey' key (for registration response).

    The original uses a custom encrypt/decrypt module. We use the same
    DES scheme with a different key.
    """
    cipher = DES.new(config.USER_KEY.encode("utf-8")[:8].ljust(8, b"\x00"), DES.MODE_ECB)
    padded = pad(data.encode("utf-8"), DES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode("ascii")


def encrypt_exchange_code(data: str) -> str:
    """Encrypt exchange code data."""
    cipher = DES.new(config.EXCHANGE_CODE_KEY.encode("utf-8")[:8].ljust(8, b"\x00"), DES.MODE_ECB)
    padded = pad(data.encode("utf-8"), DES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_exchange_code(code: str) -> str:
    """Decrypt exchange code. Returns 'id&num&type&used'."""
    raw = base64.b64decode(code)
    cipher = DES.new(config.EXCHANGE_CODE_KEY.encode("utf-8")[:8].ljust(8, b"\x00"), DES.MODE_ECB)
    decrypted = cipher.decrypt(raw)
    unpadded = unpad(decrypted, DES.block_size)
    return unpadded.decode("utf-8")


def md5_hash(data: str) -> str:
    """MD5 hash, matching the game client's com.adobe.crypto.MD5."""
    return hashlib.md5(data.encode("utf-8")).hexdigest()


def get_verify(uid: str, money: str, gameid: str, token: str) -> str:
    """Generate verify signature matching MainProxy.as getVerify().

    verify = MD5(MD5(MD5("SDALPlsldlnSLWPElsdslSB" + uid + money + gameid + token + "PKsls0")))
    """
    inner = "SDALPlsldlnSLWPElsdslSB" + uid + money + gameid + token + "PKsls0"
    h1 = md5_hash(inner)
    h2 = md5_hash(h1)
    return md5_hash(h2)


def get_sign(param1: str, gameid: str, param2: str) -> str:
    """Generate sign matching MainProxy.as getSign()."""
    return md5_hash(param1 + gameid + param2 + "123456abcdefghijklmnopqrstuvwxyz")
