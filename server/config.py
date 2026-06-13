"""Application configuration."""

import os

# Database (SQLite)
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bqtjsf.db"))

# Server
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8080))
SERVER_NAME = os.environ.get("SERVER_NAME", "sunblog.fun")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")

# Game files directory (for static SWF serving)
GAME_FILES_DIR = os.environ.get("GAME_FILES_DIR", r"E:\爆枪私服\game_files")

# Admin
ADMIN_KEY = os.environ.get("ADMIN_KEY", "sXk7m9TabUGvkaU77Ao9rNSLdOO1GOpt")

# Encryption (must match game client)
DES_KEY = "ESTAAPI_"
EXCHANGE_CODE_KEY = "exchange_code"
USER_KEY = "userkey"

# CDN fallback for missing game files
CDN_BASE_URL = os.environ.get("CDN_BASE_URL", "https://sbai.4399.com/4399swf/upload_swf/ftp15/linxy/20150324/gun/")

# Token constants (hardcoded per original)
TOKEN_VALUE = "114514"
SESSION_VALUE = "114514"
SAVE_TOKEN_VALUE = "I_love_you"
