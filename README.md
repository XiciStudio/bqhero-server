<div align="center">

# 爆枪英雄私服

Flash game private server compatible with the 4399 game client

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Features

- User authentication with password hashing
- Auto-register with initial balance (5000 gold)
- Game save/load with 8 slots per user
- In-game economy (money encryption via ECB DES)
- Union (guild) system with 11 endpoints
- Player ranking system
- Exchange code redemption
- CDN auto-download for missing game assets
- AMF3 data serialization (Flash compatible)

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
│   │   │   ├── auth.py        # Login, register, logout
│   │   │   ├── save.py        # Game save/load
│   │   │   ├── economy.py     # Money, recharge, shop
│   │   │   ├── union.py       # Guild management
│   │   │   ├── rank.py        # Leaderboard
│   │   │   ├── exchange.py    # Code redemption
│   │   │   ├── amf_utils.py   # AMF3 encode/decode
│   │   │   ├── mall.py        # In-game mall (stub)
│   │   │   ├── thrift.py      # Thrift API (stub)
│   │   │   └── misc.py        # Static files, CDN fallback
│   │   └── utils/
│   │       ├── crypto.py      # DES encryption
│   │       ├── amf3.py        # AMF3 ByteArray
│   │       ├── helpers.py     # Auth helpers
│   │       └── thrift_stub.py # Thrift client stub
│   ├── templates/             # HTML pages
│   └── modified_scripts/      # ActionScript patches (reference)
├── game_files/                # Game SWF assets
├── schema.sql                 # Database schema
└── legacy_server.txt          # Original monolithic backend
```

## API Overview

| Prefix | Purpose |
|--------|---------|
| `/api/login` `/api/register` `/Exit` | Authentication |
| `/_4399/Save` `/_4399/GetData` `/_4399/GetList` | Game saves |
| `/_4399/GetMoney` `/_4399/FlashStoreApi` | Economy |
| `/_4399/submit` `/_4399/getRankingByPage` | Rankings |
| `/_4399/union*` (11 endpoints) | Union system |
| `/api/exchange_code` `/admin/add_code` | Exchange codes |
| `/api/4399/Datadecode` `/api/4399/Dataencode` | AMF3 utilities |

## Game Assets

Missing SWF resource files are automatically downloaded from the official 4399 CDN on first request and cached in `game_files/`. The main game SWF (`v3241.swf`) and `local3241.swf` are included in this repository.

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
