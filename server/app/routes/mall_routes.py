"""Mall/Shop management API endpoints.

The game uses /mall/index.php/Api/* for the web-based shop management console.
The in-game store uses /_4399/FlashStoreApi instead.
These endpoints provide the management API for admins to configure shop items.
"""

import hashlib
import json
import time

from flask import Blueprint, request

import config
from app.utils.crypto import md5_hash, get_sign

mall_bp = Blueprint("mall", __name__)

# In-memory store for mall items (in production, use a database table)
_mall_items = []
_mall_config = {
    "notice": "",
    "types": [
        {"id": 1, "name": "武器"},
        {"id": 2, "name": "装备"},
        {"id": 3, "name": "道具"},
        {"id": 4, "name": "宝石"},
    ]
}


@mall_bp.route("/mall/index.php/Api/GetToken", methods=["POST", "GET"])
def get_token():
    """Generate a mall API token."""
    ts = str(int(time.time()))
    token = md5_hash(ts + config.SECRET_KEY)
    return json.dumps({
        "code": "10000",
        "message": "1",
        "data": {"token": token, "time": ts}
    })


@mall_bp.route("/mall/index.php/Api/GetMall", methods=["POST", "GET"])
def get_mall():
    """Get mall items list."""
    gameid = request.form.get("gameid", "")
    item_type = request.form.get("type", "")
    page = int(request.form.get("p", 1))
    show = int(request.form.get("show", 20))

    items = _mall_items
    if item_type:
        items = [i for i in items if i.get("type") == item_type]

    start = (page - 1) * show
    end = start + show

    return json.dumps({
        "code": "10000",
        "message": "1",
        "data": {
            "list": items[start:end],
            "total": len(items),
            "page": page,
        }
    })


@mall_bp.route("/mall/index.php/Api/GetConfig", methods=["POST", "GET"])
def get_config():
    """Get mall configuration."""
    return json.dumps({
        "code": "10000",
        "message": "1",
        "data": _mall_config
    })


@mall_bp.route("/mall/index.php/Api/AddTool", methods=["POST", "GET"])
def add_tool():
    """Add item to user's backpack."""
    # For private server, items are handled client-side via save data
    return json.dumps({"code": "10000", "message": "1", "data": {}})


@mall_bp.route("/mall/index.php/Api/GetTools", methods=["POST", "GET"])
def get_tools():
    """Get user's backpack items."""
    # Items are stored in save data on the client side
    return json.dumps({"code": "10000", "message": "1", "data": {"list": [], "total": 0}})


@mall_bp.route("/mall/index.php/Api/DeleteTool", methods=["POST", "GET"])
def delete_tool():
    """Delete/consume item from user's backpack."""
    return json.dumps({"code": "10000", "message": "1", "data": {}})


@mall_bp.route("/mall/index.php/Api/SetProperty", methods=["POST", "GET"])
def set_property():
    """Update item property."""
    return json.dumps({"code": "10000", "message": "1", "data": {}})


@mall_bp.route("/mall/index.php/Api/SetExtend", methods=["POST", "GET"])
def set_extend():
    """Update item extended data."""
    return json.dumps({"code": "10000", "message": "1", "data": {}})


@mall_bp.route("/mall/index.php/Api/EmptyUser", methods=["POST", "GET"])
def empty_user():
    """Clear items by type."""
    return json.dumps({"code": "10000", "message": "1", "data": {}})
