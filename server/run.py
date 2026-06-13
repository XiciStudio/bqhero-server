#!/usr/bin/env python3
"""爆枪英雄私服 — Backend Server Entry Point.

Start with:
    python run.py              # Default port 8080
    python run.py --port 9000  # Custom port
    python run.py --debug      # Debug mode

Before first run:
    1. Create MySQL database 'bqtjsf'
    2. Import schema: python init_db.py
    3. Start server: python run.py
"""

import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import config


def print_banner():
    print(r"""
    ╔══════════════════════════════════════╗
    ║       爆枪英雄 · 私服后端           ║
    ║       Bao Qiang Ying Xiong PS       ║
    ╠══════════════════════════════════════╣
    ║  API endpoints: /_4399/*            ║
    ║  Game page:     /BQTJ               ║
    ║  Login:         /                   ║
    ║  Admin key:     (see config.py)     ║
    ╚══════════════════════════════════════╝
    """)


def main():
    print_banner()

    # Parse command line
    port = config.SERVER_PORT
    debug = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif args[i] == "--debug":
            debug = True
            i += 1
        elif args[i] == "--help":
            print(__doc__)
            return
        else:
            i += 1

    app = create_app()
    # SERVER_NAME is only set when needed for URL generation, NOT for
    # localhost dev — otherwise Flask rejects requests with mismatched Host headers.
    if config.SERVER_NAME and config.SERVER_HOST != "0.0.0.0":
        app.config["SERVER_NAME"] = config.SERVER_NAME

    print(f"\n  Database: {config.DB_PATH}")
    print(f"  Server:   http://{config.SERVER_HOST}:{port}")
    print(f"  Game:     http://{config.SERVER_HOST}:{port}/BQTJ")
    print(f"  Debug:    {debug}")
    print()

    app.run(
        host=config.SERVER_HOST,
        port=port,
        debug=debug,
    )


if __name__ == "__main__":
    main()
