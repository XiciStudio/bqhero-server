"""Miscellaneous routes — index, game page, tokens, server time, static files,
secondary password, payment redirect, feedback, crossdomain.xml, etc."""

import hashlib
import json
import logging
import os
import sys
import time
import urllib.request

from flask import (Blueprint, request, render_template, send_from_directory,
                   make_response, redirect, Response)

logger = logging.getLogger("bqtj")

from app.models.user import get_save_metadata, get_game_data, get_money, get_total_recharge
from app.utils.helpers import get_user_from_cookies
from app.utils.crypto import encrypt_money
import config

misc_bp = Blueprint("misc", __name__)


# ═══════════════════════════════════════════════════════════════
#  Pages
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/", methods=["POST", "GET"])
def index():
    username = request.cookies.get("username")
    if username:
        money = get_money(username)
        return render_template("home.html", Money=money)
    return render_template("index.html")


@misc_bp.route("/BQTJ", methods=["POST", "GET"])
def play():
    username = request.cookies.get("username")
    if username:
        return render_template("bqv3241.html")
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════════
#  Core game tokens
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/_4399/play", methods=["POST", "GET"])
def api_play():
    """Game play tracking / heartbeat.

    RedeemTaskProxy expects: {"code": "1", "result": {"time": <seconds>}}
    The `time` value is used to start a heartbeat timer.
    """
    return {"code": "1", "result": {"time": 1800}}


@misc_bp.route("/_4399/auth", methods=["POST", "GET"])
def api_auth():
    """User authentication verification.

    MainProxy calls this with uid/username/gameid. The callback ignores
    the response body entirely, so any response works. Returning standard
    format for compatibility.
    """
    return {"code": "10000", "message": "1"}


@misc_bp.route("/_4399/VariableApi", methods=["POST", "GET"])
def api_variable():
    """Union variable API — returns hardcoded token.

    Used by union/guild system to get a verification token.
    """
    return config.TOKEN_VALUE


@misc_bp.route("/_4399/get_time", methods=["POST", "GET"])
def server_time():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    return {"time": now}


@misc_bp.route("/_4399/get_token", methods=["POST", "GET"])
def get_token():
    return config.TOKEN_VALUE


@misc_bp.route("/_4399/get_session", methods=["POST", "GET"])
def get_session():
    return config.SESSION_VALUE


@misc_bp.route("/_4399/get_token_save", methods=["POST", "GET"])
def save_token():
    return config.SAVE_TOKEN_VALUE


@misc_bp.route("/_4399/check_session", methods=["POST", "GET"])
def check_session():
    return "1"


# ═══════════════════════════════════════════════════════════════
#  Player data (arena / PvP opponent lookup)
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/_4399/GetOther", methods=["POST", "GET"])
def get_other_player():
    target_uid = request.form.get("uid", "")
    index = int(request.form.get("index", 0))

    from app.models.user import get_user_by_uid
    target = get_user_by_uid(target_uid)
    if not target:
        return "十年老兵禁止进入"

    username = target["username"]
    metadata_str = get_save_metadata(username)
    metadata = json.loads(metadata_str) if metadata_str else []

    if index >= len(metadata):
        return "十年老兵禁止进入"

    slot = metadata[index]
    if slot.get("status", 0) != 0:
        return "十年老兵禁止进入"

    raw_data = get_game_data(username, index) or ""

    if "datetime" in slot:
        del slot["datetime"]
    if "status" in slot:
        del slot["status"]
    slot["update_times"] = 5
    slot["create_time"] = "2024-07-16 11:25:00"
    slot["data"] = raw_data

    return slot


# ═══════════════════════════════════════════════════════════════
#  Money / Payment
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/_4399/GetTotalPay", methods=["POST", "GET"])
def total_pay():
    """Get total pay amount (same as TotalRecharge for private server)."""
    user = get_user_from_cookies()
    username = user["username"]
    timestamp = request.form.get("time", "0")
    total = get_total_recharge(username)
    return encrypt_money(total, timestamp)


@misc_bp.route("/_4399/Pay", methods=["POST", "GET"])
def pay_redirect():
    """Payment redirect — opens external browser for real-money payment.
    On a private server, simply redirect to a page showing payment is disabled.
    """
    gameid = request.args.get("gameid", "")
    money = request.args.get("money", "0")
    userid = request.args.get("userid", "")
    username = request.args.get("username", "")
    return f'<html><body style="background:#1a1a2e;color:#eee;font-family:sans-serif;text-align:center;padding-top:100px"><h2>充值功能</h2><p>私服不支持真实货币充值</p><p>游戏ID: {gameid} | 用户: {username}</p><p><a href="/" style="color:#e94560">返回主页</a></p></body></html>'


# ═══════════════════════════════════════════════════════════════
#  Ranking extras
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/_4399/getRankingByArounds", methods=["POST", "GET"])
def ranking_arounds():
    """Get rankings around the current user's position within a sub-category.

    Client sends:
      rankListId — the rank list ID (e.g. 1501)
      idx       — sub-category index (0-7, matches the `index` field in rank entries)
      rankNum   — how many entries to return around the user

    The server filters entries to those with `index == idx`, finds the current
    user's rank position within that filtered list, and returns `rankNum`
    entries centered around that position.
    """
    rank_list_id = int(request.form.get("rankListId", 1501))
    idx = int(request.form.get("idx", 0))
    rank_num = int(request.form.get("rankNum", 5))
    user = get_user_from_cookies()

    from app.models.rank import get_rank_data

    data = get_rank_data(rank_list_id)
    result = {"code": "10000", "message": "1", "data": []}

    if data:
        # Filter to same sub-category index
        filtered = [item for item in data if item.get("index") == idx]

        # Find the current user's position in the filtered list
        user_pos = None
        for i, item in enumerate(filtered):
            if str(item.get("uId")) == str(user["uid"]):
                user_pos = i
                break

        if user_pos is not None:
            half = rank_num // 2
            start = max(0, user_pos - half)
            end = min(len(filtered), start + rank_num)
            result["data"] = filtered[start:end]

    return result


@misc_bp.route("/Login/get_token_rank", methods=["POST", "GET"])
def rank_token():
    """Get token for rank data reading. Returns hardcoded value."""
    return config.TOKEN_VALUE


# ═══════════════════════════════════════════════════════════════
#  Secondary password (stub — private server skips this)
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/secondary.php", methods=["POST", "GET"])
def secondary():
    """Secondary password endpoint. All actions return success/empty."""
    ac = request.args.get("ac", request.form.get("ac", ""))

    if ac == "check_privilege":
        # Return that user does NOT need secondary password
        return '{"code":"10000","message":"1","data":{"status":0}}'

    elif ac == "login":
        # Secondary login always succeeds
        return "1"

    elif ac == "save":
        # Delegate to normal save
        from app.routes.save import save
        return save()

    elif ac == "get":
        # Delegate to normal get
        from app.routes.save import get_data
        return get_data()

    elif ac == "get_list":
        # Delegate to normal get list
        from app.routes.save import get_list
        return get_list()

    elif ac == "get_captcha":
        return ""

    return "1"


# ═══════════════════════════════════════════════════════════════
#  Feedback / Report redirects
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/auth/r.php", methods=["POST", "GET"])
def feedback():
    app = request.args.get("app", "")
    return f'<html><body style="background:#1a1a2e;color:#eee;font-family:sans-serif;text-align:center;padding-top:100px"><h2>{"申诉" if "feedback" in app and "report" not in app else "举报"}</h2><p>请联系管理员处理</p><p><a href="/" style="color:#e94560">返回主页</a></p></body></html>'


# ═══════════════════════════════════════════════════════════════
#  Flash crossdomain policy (critical for SWF cross-domain requests)
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/crossdomain.xml")
def crossdomain():
    """Flash cross-domain policy file."""
    xml = '''<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
    <allow-access-from domain="*" />
    <site-control permitted-cross-domain-policies="all"/>
    <allow-http-request-headers-from domain="*" headers="*"/>
</cross-domain-policy>'''
    return Response(xml, mimetype="text/xml")


# ═══════════════════════════════════════════════════════════════
#  Game recommendations (stub for recommend/api.php)
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/recommend/api.php", methods=["POST", "GET"])
def recommend():
    """Game recommendation API stub."""
    ac = request.args.get("ac", "")
    if ac == "recommend":
        return json.dumps({"code": "10000", "message": "1", "data": {"list": [], "ad": []}})
    elif ac == "go":
        return redirect("/")
    return json.dumps({"code": "10000", "message": "1", "data": {}})


# ═══════════════════════════════════════════════════════════════
#  Admin
# ═══════════════════════════════════════════════════════════════

@misc_bp.route("/_4399/init_sql", methods=["POST", "GET"])
def init_rank_tables():
    if request.form.get("adminkey") != config.ADMIN_KEY:
        return "", 404

    from app.extensions import execute
    for rid in range(800, 2501):
        execute("INSERT OR IGNORE INTO top (rid, data) VALUES (?, ?)", (rid, "[]"))
    return "1"


@misc_bp.route("/admin/test", methods=["POST", "GET"])
def admin_test():
    return "test ok"


@misc_bp.route("/MD5", methods=["POST", "GET"])
def md5_api():
    data = request.form.get("data", "")
    return hashlib.md5(data.encode("utf-8")).hexdigest()


@misc_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "time": time.strftime("%Y-%m-%d %H:%M:%S")}


# ═══════════════════════════════════════════════════════════════
#  Static file serving (must be last — catches unmatched paths)
# ═══════════════════════════════════════════════════════════════
#
#  The game SWF files are stored under GAME_FILES_DIR/files/gun/swf/
#  but the client may request them from various paths:
#    /swf/local3241.swf       (absolute from domain root)
#    /swf/enemy/ArgonShip.swf (sub-SWFs, relative to local3241.swf)
#    /files/gun/v3241.swf     (main container, via template embed)
#    /files/ctrl_mo_v5.swf    (top-level modified client)
#
#  Strategy: try exact path first, then common alternate locations,
#  then a filename-only search under GAME_FILES_DIR.

# Pre-built filename → full path cache (lazy, populated on first miss)
_filename_cache = None


def _build_filename_cache():
    """Walk GAME_FILES_DIR and map filename → (base, rel_path).

    Uses forward slashes in rel_path for Flask's send_from_directory.
    """
    global _filename_cache
    _filename_cache = {}
    base = config.GAME_FILES_DIR
    for root, dirs, files in os.walk(base):
        for f in files:
            if f not in _filename_cache:
                full = os.path.join(root, f)
                rel_path = os.path.relpath(full, base)
                # Flask requires forward slashes
                rel_path = rel_path.replace(os.sep, "/")
                _filename_cache[f] = (base, rel_path)


def _find_file(path: str) -> tuple[str, str] | None:
    """Find a game file by request path.

    Returns (directory, filename) or None.

    Search order:
      1. Exact path under GAME_FILES_DIR
      2. Path under GAME_FILES_DIR/files/ (common nested prefix)
      3. Filename-only search (ignores directory structure)
    """
    base = config.GAME_FILES_DIR

    # 1. Exact match
    exact = os.path.join(base, path)
    if os.path.isfile(exact):
        return (base, path)

    # 2. Try under files/
    under_files = os.path.join(base, "files", path)
    if os.path.isfile(under_files):
        return (os.path.join(base, "files"), path)

    # 3. Filename-only search (lazy cache)
    global _filename_cache
    if _filename_cache is None:
        _build_filename_cache()
    fname = os.path.basename(path)
    if fname in _filename_cache:
        return _filename_cache[fname]

    # 4. Cache miss — search filesystem directly (handles newly added files)
    for root, dirs, files in os.walk(base):
        if fname in files:
            full = os.path.join(root, fname)
            rel_path = os.path.relpath(full, base).replace(os.sep, "/")
            _filename_cache[fname] = (base, rel_path)
            return (base, rel_path)

    return None


def _log(msg):
    """Write debug message to stderr AND a log file."""
    ts = time.strftime("%H:%M:%S")
    line = f"{ts} {msg}\n"
    # Direct write to stderr fd (bypasses all buffering)
    os.write(2, line.encode("utf-8"))
    # Also append to log file as backup
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cdn_log.txt"), "a", encoding="utf-8") as lf:
            lf.write(line)
    except:
        pass


def _cdn_download(path):
    """Try to download a missing file from CDN. Returns file data or None."""
    _log(f"CDN_START path={path}")

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
        cdn_url = config.CDN_BASE_URL + cdn_path
        _log(f"CDN_TRY {cdn_url}")
        try:
            req = urllib.request.Request(cdn_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    data = resp.read()
                    local_dir = os.path.join(config.GAME_FILES_DIR, os.path.dirname(path))
                    local_path = os.path.join(config.GAME_FILES_DIR, path)
                    os.makedirs(local_dir, exist_ok=True)
                    with open(local_path, "wb") as f:
                        f.write(data)
                    _log(f"CDN_OK size={len(data)} -> {local_path}")
                    return data
        except Exception as e:
            _log(f"CDN_ERR {e}")
    _log(f"CDN_FAIL all attempts exhausted")
    return None


@misc_bp.route("/<path:path>")
def serve_file(path):
    """Serve static game files, with CDN fallback for missing resources."""
    _log(f"SRV_ENTER {path}")

    result = _find_file(path)
    if result:
        _log(f"SRV_FOUND {result[0]} / {result[1]}")
        return send_from_directory(result[0], result[1])

    _log(f"SRV_MISS {path} — starting CDN download")

    # Try CDN download
    data = _cdn_download(path)
    if data is not None:
        local_dir = os.path.join(config.GAME_FILES_DIR, os.path.dirname(path))
        local_path = os.path.join(config.GAME_FILES_DIR, path)
        os.makedirs(local_dir, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        global _filename_cache
        if _filename_cache is not None:
            fname = os.path.basename(path)
            _filename_cache[fname] = (config.GAME_FILES_DIR, path.replace(os.sep, "/"))
        return send_from_directory(config.GAME_FILES_DIR, path.replace(os.sep, "/"))

    _log(f"SRV_404 {path}")
    return "哥们你走错地了QAQ", 404
