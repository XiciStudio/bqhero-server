"""Save/Load game data routes.

The game client sends/retrieves base64+zlib+AMF3 encoded game state.
We store the raw encoded data directly — no need to decode/re-encode.
"""

import json
import time

from flask import Blueprint, request, make_response

from app.models.user import (
    get_save_metadata, update_save_metadata, save_game_data,
    get_game_data,
)
from app.utils.helpers import get_user_from_cookies

save_bp = Blueprint("save", __name__)


@save_bp.route("/_4399/Save", methods=["POST", "GET"])
def save():
    user = get_user_from_cookies()
    username = user["username"]

    index_str = request.form.get("index", "0")
    index = int(index_str)
    title = request.form.get("title", "")
    raw_data = request.form.get("data", "")
    # NOTE: Flask already URL-decodes form data. Do NOT use unquote()
    # here — it would corrupt base64 '+' characters into spaces.

    # Update save slot metadata
    metadata_str = get_save_metadata(username)
    metadata = json.loads(metadata_str) if metadata_str else []

    # Ensure list has enough slots
    while len(metadata) <= index:
        metadata.append({})

    metadata[index]["index"] = index_str
    metadata[index]["title"] = title
    metadata[index]["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S")
    metadata[index]["status"] = 0

    update_save_metadata(username, json.dumps(metadata, ensure_ascii=False))

    # Store actual game data
    save_game_data(username, index, raw_data)

    resp = make_response("1")
    resp.set_cookie("index", index_str, max_age=2592000)
    return resp


@save_bp.route("/_4399/GetData", methods=["POST", "GET"])
def get_data():
    user = get_user_from_cookies()
    username = user["username"]
    index = int(request.form.get("index", 0))

    metadata_str = get_save_metadata(username)
    metadata = json.loads(metadata_str) if metadata_str else []

    if index >= len(metadata):
        return "十年老兵禁止进入"

    slot = metadata[index]
    if slot.get("status", 0) != 0:
        return "十年老兵禁止进入"

    raw_data = get_game_data(username, index) or ""

    # Clean and return
    if "datetime" in slot:
        del slot["datetime"]
    if "status" in slot:
        del slot["status"]
    slot["update_times"] = 5
    slot["create_time"] = "2024-07-16 11:45:14"
    slot["data"] = raw_data

    return slot


@save_bp.route("/_4399/GetList", methods=["POST", "GET"])
def get_list():
    user = get_user_from_cookies()
    username = user["username"]
    return get_save_metadata(username)
