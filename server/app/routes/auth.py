"""Authentication routes — login, register, logout, user info."""

import re
import time
import uuid
from collections import defaultdict
from html import escape as html_escape

from flask import Blueprint, request, render_template, make_response, redirect, url_for, flash, session

from app.models.user import (
    get_user_by_username, get_uid_by_username, create_user,
    verify_password, check_user_exists, get_money, add_money,
    update_password, get_user_info, get_total_recharge, update_last_active,
)
from app.models.union import get_union_by_id
from app.utils.helpers import get_user_from_cookies, require_user

auth_bp = Blueprint("auth", __name__)

# ---- Rate limiting (in-memory, per IP) ----
_login_attempts = defaultdict(list)
_RATE_LIMIT = 5  # max attempts
_RATE_WINDOW = 60  # seconds


def _check_rate_limit(ip):
    """Return True if request is allowed, False if rate-limited."""
    now = time.time()
    attempts = _login_attempts[ip]
    # Prune old entries
    _login_attempts[ip] = [t for t in attempts if now - t < _RATE_WINDOW]
    if len(_login_attempts[ip]) >= _RATE_LIMIT:
        return False
    _login_attempts[ip].append(now)
    return True


def _sanitize_username(raw):
    """Strip HTML tags and escape special chars for safe rendering."""
    cleaned = re.sub(r'[<>"\'&]', '', raw)
    return cleaned.strip()


def _check_csrf():
    """Validate CSRF token from form. Returns True if valid."""
    token = request.form.get("_csrf", "")
    return token and token == session.get("_csrf")


def _new_csrf():
    """Generate and store a new CSRF token in session."""
    token = uuid.uuid4().hex
    session["_csrf"] = token
    return token


@auth_bp.route("/api/login", methods=["POST", "GET"])
def user_login():
    if request.method != "POST":
        return redirect("/")

    # Rate limiting
    if not _check_rate_limit(request.remote_addr):
        flash("登录尝试过于频繁，请稍后再试", "error")
        return redirect("/")

    # CSRF check
    if not _check_csrf():
        flash("请求无效，请刷新页面重试", "error")
        return redirect("/")

    username = _sanitize_username(request.form.get("username", ""))
    password = request.form.get("password", "").strip()

    if not username or not password:
        flash("账号和密码是必填项", "error")
        return redirect("/")

    if not check_user_exists(username):
        flash("账号不存在，请先注册", "error")
        return redirect("/#register")

    if verify_password(username, password):
        # Login success
        uid = get_uid_by_username(username)
        money = get_money(username)
        total_recharge = get_total_recharge(username)
        update_last_active(username)
        resp = make_response(render_template("home.html", Money=money, username=username, uid=uid, TotalRecharge=total_recharge))
        resp.set_cookie("uid", uid, max_age=2592000)
        resp.set_cookie("uuid", str(uuid.uuid4()), max_age=2592000, httponly=True)
        resp.set_cookie("username", username, max_age=2592000)
        return resp
    else:
        flash("密码错误，请输入正确密码", "error")
        return redirect("/")


@auth_bp.route("/register", methods=["POST"])
def web_register():
    """Web-facing registration with validation and flash messages."""
    # Rate limiting
    if not _check_rate_limit(request.remote_addr):
        flash("操作过于频繁，请稍后再试", "error")
        return redirect("/#register")

    # CSRF check
    if not _check_csrf():
        flash("请求无效，请刷新页面重试", "error")
        return redirect("/#register")

    username = _sanitize_username(request.form.get("username", ""))
    password = request.form.get("password", "").strip()
    confirm = request.form.get("confirm_password", "").strip()

    if not username or not password or not confirm:
        flash("所有字段都是必填项", "error")
        return redirect("/#register")

    if len(username) < 3 or len(username) > 16:
        flash("账号长度需要 3-16 位", "error")
        return redirect("/#register")

    if not username.isalnum():
        flash("账号只能包含字母和数字", "error")
        return redirect("/#register")

    if len(password) < 4:
        flash("密码长度不能少于 4 位", "error")
        return redirect("/#register")

    if password != confirm:
        flash("两次输入的密码不一致", "error")
        return redirect("/#register")

    if check_user_exists(username):
        flash("该账号已被注册", "error")
        return redirect("/#register")

    # Create user and auto-login
    uid = create_user(username, password)
    add_money(username, 5000)
    update_last_active(username)
    resp = make_response(render_template("home.html", Money=5000, username=username, uid=uid, TotalRecharge=5000))
    resp.set_cookie("uid", uid, max_age=2592000)
    resp.set_cookie("uuid", str(uuid.uuid4()), max_age=2592000, httponly=True)
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
    session.clear()
    resp = make_response(redirect("/"))
    resp.delete_cookie("uid")
    resp.delete_cookie("uuid")
    resp.delete_cookie("username")
    return resp


@auth_bp.route("/profile", methods=["GET"])
def profile():
    user = require_user()
    if not user:
        return redirect("/")

    info = get_user_info(user["username"])
    if not info:
        return redirect("/")

    # Resolve union name
    union_name = None
    if info["inunion_id"]:
        union = get_union_by_id(info["inunion_id"])
        if union:
            import json
            try:
                union_info = json.loads(union["info"])
                union_name = union_info.get("name", f"工会#{info['inunion_id']}")
            except Exception:
                union_name = f"工会#{info['inunion_id']}"

    return render_template("profile.html", user=info, union_name=union_name, csrf=_new_csrf())


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    user = require_user()
    if not user:
        return redirect("/")

    if not _check_csrf():
        flash("请求无效，请刷新页面重试", "error")
        return redirect("/profile")

    old_pw = request.form.get("old_password", "").strip()
    new_pw = request.form.get("new_password", "").strip()
    confirm_pw = request.form.get("confirm_password", "").strip()

    if not old_pw or not new_pw or not confirm_pw:
        flash("所有字段都是必填项", "error")
        return redirect("/profile")

    if new_pw != confirm_pw:
        flash("两次输入的新密码不一致", "error")
        return redirect("/profile")

    if len(new_pw) < 4:
        flash("新密码长度不能少于4位", "error")
        return redirect("/profile")

    if not verify_password(user["username"], old_pw):
        flash("当前密码错误", "error")
        return redirect("/profile")

    update_password(user["username"], new_pw)
    flash("密码修改成功", "success")
    return redirect("/profile")


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
