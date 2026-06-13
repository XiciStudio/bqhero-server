"""Exchange code routes."""

from flask import Blueprint, request

from app.models.exchange_code import (
    get_code_by_id, create_code, mark_code_used, is_code_used,
)
from app.models.user import add_money
from app.utils.helpers import get_user_from_cookies
from app.utils.crypto import decrypt_exchange_code
import config

exchange_bp = Blueprint("exchange", __name__)


@exchange_bp.route("/admin/add_code", methods=["POST", "GET"])
def add_code():
    """Admin: create a new exchange code."""
    if request.form.get("adminkey") != config.ADMIN_KEY:
        return "", 404

    code_type = request.form.get("type", "Money")
    num = int(request.form.get("num", 0))
    code = create_code(code_type, num)
    return code


@exchange_bp.route("/api/exchange_code", methods=["POST", "GET"])
def redeem():
    """Redeem an exchange code."""
    user = get_user_from_cookies()
    code_str = request.form.get("code", "")

    try:
        decrypted = decrypt_exchange_code(code_str)
        parts = decrypted.split("&")
        code_id = parts[0]
        num = int(parts[1])
        code_type = parts[2]
    except Exception:
        return "The code is used", 404

    if is_code_used(code_id):
        return "The code is used", 404

    if code_type == "Money":
        username = user["username"]
        mark_code_used(code_id)
        new_balance = add_money(username, num)
        return str(new_balance)

    return "Unknown code type", 404
