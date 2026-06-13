"""Flask application factory with CORS, logging, and error handling."""

import os
import sys
import time
import logging
import urllib.request

from flask import Flask, request, g, send_from_directory, Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    force=True,
)
logger = logging.getLogger("bqtj")

GAME_FILES_DIR = None
CDN_BASE_URL = None


def create_app():
    global GAME_FILES_DIR, CDN_BASE_URL
    app = Flask(__name__, template_folder="../templates", static_folder=None)
    app.config.from_object("config")
    GAME_FILES_DIR = app.config.get("GAME_FILES_DIR", "")
    CDN_BASE_URL = app.config.get("CDN_BASE_URL", "")

    # Initialize database (lazy)
    from app.extensions import init_db
    init_db()

    # Register middleware
    _setup_middleware(app)

    # Register all blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    logger.info("爆枪英雄私服 backend started, %d routes", len(app.url_map._rules))
    logger.info("CDN base: %s", CDN_BASE_URL)
    return app


def _setup_middleware(app: Flask):
    """Register before/after request handlers."""

    @app.before_request
    def before():
        g.start_time = time.time()
        logger.debug("→ %s %s from %s", request.method, request.path, request.remote_addr)

    @app.after_request
    def after(response):
        # CORS headers for Flash cross-domain requests
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"

        # Prevent caching for API responses
        if request.path.startswith("/_4399") or request.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        # Log response
        elapsed = (time.time() - g.get("start_time", time.time())) * 1000
        logger.info("%s %s → %d (%.1fms)", request.method, request.path, response.status_code, elapsed)

        return response

    @app.route("/flash_ctrl_version.xml")
    def flash_ctrl_version():
        """Serve flash_ctrl_version.xml locally with absolute paths.

        The platform SWF fetches this from stat.api.4399.com, but the
        returned relative paths break when the SWF isn't at domain root.
        We intercept and return absolute paths so ctrl_mo_v5.swf and
        A4399dv_base.swf load from our local server instead of CDN.
        """
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<root>\n"
            '    <ctrl_v5>/files/ctrl_mo_v5.swf</ctrl_v5>\n'
            "    <zwsf></zwsf>\n"
            '    <ads>/files/A4399dv_base.swf</ads>\n'
            "</root>\n"
        )
        return Response(xml, mimetype="application/xml")

    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 — try CDN download for missing game resources."""
        path = request.path.lstrip("/")
        sys.stderr.write(f"[404] {path} — trying CDN\n")
        sys.stderr.flush()

        if GAME_FILES_DIR and CDN_BASE_URL and path:
            candidates = [path]
            for prefix in ["files/gun/", "gun/"]:
                if path.startswith(prefix):
                    candidates.append(path[len(prefix):])
            candidates.append(os.path.basename(path))

            seen = set()
            for cdn_path in candidates:
                if cdn_path in seen:
                    continue
                seen.add(cdn_path)
                cdn_url = CDN_BASE_URL + cdn_path
                sys.stderr.write(f"[CDN] Try: {cdn_url}\n")
                sys.stderr.flush()
                try:
                    req = urllib.request.Request(cdn_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        if resp.status == 200:
                            data = resp.read()
                            local_dir = os.path.join(GAME_FILES_DIR, os.path.dirname(path))
                            local_path = os.path.join(GAME_FILES_DIR, path)
                            os.makedirs(local_dir, exist_ok=True)
                            with open(local_path, "wb") as f:
                                f.write(data)
                            sys.stderr.write(f"[CDN] OK {len(data)}b -> {local_path}\n")
                            sys.stderr.flush()
                            mimetype = None
                            if path.endswith(".swf"):
                                mimetype = "application/x-shockwave-flash"
                            elif path.endswith(".mp3"):
                                mimetype = "audio/mpeg"
                            elif path.endswith(".png"):
                                mimetype = "image/png"
                            return send_from_directory(GAME_FILES_DIR, os.path.relpath(local_path, GAME_FILES_DIR).replace(os.sep, "/"), mimetype=mimetype)
                except Exception as ex:
                    sys.stderr.write(f"[CDN] ERR: {ex}\n")
                    sys.stderr.flush()

        return "", 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error("500: %s %s — %s", request.method, request.path, str(e))
        return "Internal Server Error", 500
