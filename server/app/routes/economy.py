"""Economy routes — money, store purchases."""

from flask import Blueprint, request

from app.models.user import get_money, get_total_recharge, deduct_money
from app.utils.helpers import get_user_from_cookies
from app.utils.crypto import encrypt_money

economy_bp = Blueprint("economy", __name__)


@economy_bp.route("/_4399/GetMoney", methods=["POST", "GET"])
def money_get():
    user = get_user_from_cookies()
    username = user["username"]
    timestamp = request.form.get("time", "0")
    balance = get_money(username)
    return encrypt_money(balance, timestamp)


@economy_bp.route("/_4399/GetTotalRecharge", methods=["POST", "GET"])
def total_recharge_get():
    user = get_user_from_cookies()
    username = user["username"]
    timestamp = request.form.get("time", "0")
    total = get_total_recharge(username)
    return encrypt_money(total, timestamp)


@economy_bp.route("/_4399/FlashStoreApi", methods=["POST", "GET"])
def mall():
    """In-game store purchase. Deducts money and returns updated balance."""
    user = get_user_from_cookies()
    username = user["username"]

    prop_id = request.form.get("propId", "0")
    prop_count = request.form.get("propCount", "1")
    prop_price = request.form.get("propPrice", "0")

    total_cost = int(prop_price) * int(prop_count)
    new_balance = deduct_money(username, total_cost)

    return {
        "propId": prop_id,
        "count": prop_count,
        "balance": new_balance,
        "tag": "",
    }


@economy_bp.route("/_4399/Dec", methods=["POST", "GET"])
def dec_money():
    """Deduct money endpoint (used by payment flow)."""
    user = get_user_from_cookies()
    username = user["username"]

    money_val = int(request.form.get("money", 0))
    new_balance = deduct_money(username, money_val)

    timestamp = request.form.get("time", "0")
    return encrypt_money(new_balance, timestamp)
