# 爆枪英雄私服

Flash game (爆枪英雄) private server, compatible with the official 4399 game client.

## Architecture

```
server/
├── run.py              # Entry point
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
├── init_db.py          # Database initialization
├── app/
│   ├── __init__.py     # Flask app factory
│   ├── extensions.py   # DB connection pool
│   ├── models/         # Database models (user, union, rank, exchange_code)
│   ├── routes/         # API routes (auth, save, economy, union, rank, etc.)
│   └── utils/          # Encryption, AMF3, helpers
├── templates/          # HTML templates
├── static/             # Static assets
└── modified_scripts/   # ActionScript patches (reference)
```

## Setup

1. Install dependencies:
```bash
cd server
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python init_db.py
```

3. Run the server:
```bash
python run.py
```

The server starts at `http://localhost:8080`.

## Game Files

The game SWF and resource files are served from `game_files/`. On first run, missing resources are automatically downloaded from the official 4399 CDN and cached locally. The main game SWF (`v3241.swf`) is included in this repo.

## Configuration

See `server/config.py` for all settings. Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | `8080` | Listen port |
| `SERVER_HOST` | `0.0.0.0` | Listen address |
| `DB_PATH` | `server/bqtjsf.db` | SQLite database path |
| `GAME_FILES_DIR` | `game_files/` | Game assets directory |
| `SECRET_KEY` | (default) | Flask secret key |
| `CDN_BASE_URL` | (4399 CDN) | CDN for missing files |

## Original Code

`legacy_server.txt` is the original monolithic backend code from which this project was refactored. `schema.sql` contains the original database schema.
