<div align="center">

# 爆枪英雄私服

Flash game private server compatible with the 4399 game client

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Release](https://img.shields.io/badge/release-v1.2.0-e94560.svg)](https://github.com/XiciStudio/bqhero-server/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Features

- User authentication with password hashing (werkzeug PBKDF2)
- Login/register with tab separation, client-side validation, CSRF protection
- Rate limiting (5 attempts/60s per IP) and XSS sanitization
- Profile page with user info, union, registration time
- Change password with old-password verification
- Auto-register with initial balance (5000 gold)
- Online user count tracking (5-minute window)
- Game save/load with 8 slots per user
- In-game economy (money encryption via ECB DES)
- Union (guild) system with 11 endpoints
- Player ranking system
- Exchange code redemption with history
- Web admin panel (`/admin`) — user/code/union management, password reset
- CDN auto-download for missing game assets
- AMF3 data serialization (Flash compatible)
- Game updated to v3621 with loading progress bar

## Quick Start

```bash
cd server
pip install -r requirements.txt
python init_db.py --all
python run.py
```

Server starts at `http://localhost:8080`.

## Project Structure

```
.
├── server/
│   ├── run.py                 # Entry point
│   ├── config.py              # All configuration
│   ├── requirements.txt       # Python dependencies
│   ├── init_db.py             # Database setup & seeding
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── extensions.py      # Database connection pool
│   │   ├── models/
│   │   │   ├── user.py        # User CRUD
│   │   │   ├── union.py       # Union CRUD
│   │   │   ├── rank.py        # Ranking CRUD
│   │   │   └── exchange_code.py
│   │   ├── routes/
│   │   │   ├── auth.py        # Login, register, logout, profile
│   │   │   ├── save.py        # Game save/load
│   │   │   ├── economy.py     # Money, recharge, shop
│   │   │   ├── union.py       # Guild management
│   │   │   ├── rank.py        # Leaderboard
│   │   │   ├── exchange.py    # Code redemption
│   │   │   ├── admin.py        # Admin panel
│   │   │   ├── amf_utils.py   # AMF3 encode/decode
│   │   │   ├── mall.py        # In-game mall (stub)
│   │   │   ├── thrift.py      # Thrift API (stub)
│   │   │   └── misc.py        # Static files, CDN fallback
│   │   └── utils/
│   │       ├── crypto.py      # DES encryption
│   │       ├── amf3.py        # AMF3 ByteArray
│   │       ├── helpers.py     # Auth helpers
│   │       └── thrift_stub.py # Thrift client stub
│   ├── templates/
│   │   ├── index.html         # Login/register page
│   │   ├── home.html          # User dashboard
│   │   ├── profile.html       # User profile + change password
│   │   ├── bqv3621.html       # Game page (SWF embed + JS bridge)
│   │   └── admin/             # Admin panel pages
│   └── modified_scripts/      # ActionScript patches (reference)
├── game_files/                # Game SWF assets
├── schema.sql                 # Database schema
└── legacy_server.txt          # Original monolithic backend
```

## API Overview

| Prefix | Purpose |
|--------|---------|
| `/` `/register` `/Exit` | Web login/register/logout |
| `/api/login` `/api/register` | API authentication |
| `/profile` `/change-password` | User profile |
| `/redeem` | Exchange code redemption |
| `/_4399/Save` `/_4399/GetData` `/_4399/GetList` | Game saves |
| `/_4399/GetMoney` `/_4399/FlashStoreApi` | Economy |
| `/_4399/submit` `/_4399/getRankingByPage` | Rankings |
| `/_4399/union*` (11 endpoints) | Union system |
| `/admin` `/admin/users` `/admin/codes` `/admin/unions` | Admin panel |
| `/api/4399/Datadecode` `/api/4399/Dataencode` | AMF3 utilities |

## Game Assets

Missing SWF resource files are automatically downloaded from the official 4399 CDN on first request and cached in `game_files/`. The main game SWF (`v3621.swf`) and `local3621.swf` are included in this repository.

## Configuration

Key environment variables (see `server/config.py` for full list):

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | `8080` | Listen port |
| `SERVER_HOST` | `0.0.0.0` | Listen address |
| `DB_PATH` | `server/bqtjsf.db` | SQLite database path |
| `GAME_FILES_DIR` | `game_files/` | Game assets directory |
| `SECRET_KEY` | (built-in) | Flask session secret |
| `CDN_BASE_URL` | (4399 CDN) | Fallback CDN for missing files |

## License

MIT

## Disclaimer

本项目仅供学习研究使用。详见 [DISCLAIMER.md](DISCLAIMER.md)。
