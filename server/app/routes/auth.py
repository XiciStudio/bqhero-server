"""Authentication routes — login, register, logout, user info."""

import uuid
from urllib.parse import parse_qs

from flask import Blueprint, request, render_template, make_response, redirect, url_for

from app.models.user import (
    get_user_by_username, get_uid_by_username, create_user,
    verify_password, check_user_exists, get_money, add_money,
)
from app.utils.helpers import get_user_from_cookies, require_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST", "GET"])
def user_login():
    if request.method != "POST":
        return "请使用POST请求", 404

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return "温馨提示：账号和密码是必填"

    if verify_password(username, password):
        # Existing user — login success
        uid = get_uid_by_username(username)
        money = get_money(username)
        resp = make_response(render_template("home.html", Money=money))
        resp.set_cookie("uid", uid, max_age=2592000)
        resp.set_cookie("uuid", str(uuid.uuid4()), max_age=2592000)
        resp.set_cookie("username", username, max_age=2592000)
        return resp

    elif check_user_exists(username):
        # User exists but wrong password
        return "温馨提示：密码错误，请输入正确密码"

    else:
        # Auto-register new user
        uid = create_user(username, password)
        add_money(username, 5000)
        resp = make_response(render_template("home.html", Money=5000))
        resp.set_cookie("uid", uid, max_age=2592000)
        resp.set_cookie("uuid", str(uuid.uuid4()), max_age=2592000)
        resp.set_cookie("username", username, max_age=2592000)
        return resp


@auth_bp.route("/api/register", methods=["POST", "GET"])
def register():
    if request.method != "POST":
        return "请使用POST请求", 404

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return "温馨提示：账号和密码是必填"

    if check_user_exists(username):
        return "温馨提示：用户已存在，请直接登录"

    uid = create_user(username, password)
    # Return encrypted "username&password&uid" with key "userkey"
    from app.utils.crypto import encrypt_userkey
    return encrypt_userkey(f"{username}&{password}&{uid}")


@auth_bp.route("/Exit", methods=["POST", "GET"])
def logout():
    resp = make_response(render_template("index.html"))
    resp.delete_cookie("uid")
    resp.delete_cookie("uuid")
    resp.delete_cookie("username")
    return resp


@auth_bp.route("/api/Get_Uid", methods=["POST", "GET"])
def get_uid_by_name():
    """Get UID from username (form field)."""
    username = request.form.get("username", "")
    uid = get_uid_by_username(username)
    return uid or ""


@auth_bp.route("/User/GetUid", methods=["POST", "GET"])
def get_uid_cookie():
    """Get UID from cookie."""
    return request.cookies.get("uid", "")


@auth_bp.route("/User/GetUname", methods=["POST", "GET"])
def get_uname_cookie():
    """Get username from cookie."""
    return request.cookies.get("username", "")
