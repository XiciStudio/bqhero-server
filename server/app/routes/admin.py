"""Admin panel routes — session-based auth, independent of game cookies."""

from functools import wraps
from flask import Blueprint, session, redirect, url_for, render_template, request, flash

from config import ADMIN_KEY
from app.models.user import (
    get_user_count, get_all_users, search_users,
    delete_user, update_user_money, get_recent_users,
)
from app.models.exchange_code import get_code_count, get_all_codes, create_code
from app.models.rank import get_rank_count
from app.models.union import get_all_unions, get_union_by_id

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


# ---- Login / Logout ----

@admin_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("adminkey") == ADMIN_KEY:
            session["admin_authenticated"] = True
            return redirect(url_for("admin.dashboard"))
        flash("管理员密钥错误", "error")
    return render_template("admin/login.html")


@admin_bp.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


# ---- Dashboard ----

@admin_bp.route("/admin")
@admin_required
def dashboard():
    stats = {
        "users": get_user_count(),
        "codes": get_code_count(),
        "unions": len(get_all_unions()),
        "ranks": get_rank_count(),
    }
    recent_users = get_recent_users(5)
    recent_codes, _ = get_all_codes(page=1, per_page=5)
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        recent_codes=recent_codes,
    )


# ---- User Management ----

@admin_bp.route("/admin/users")
@admin_required
def users():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    if q:
        user_list = search_users(q)
        total = len(user_list)
        pages = 1
    else:
        user_list, total = get_all_users(page=page, per_page=20)
        pages = (total + 19) // 20 if total > 0 else 1

    return render_template(
        "admin/users.html",
        users=user_list,
        page=page,
        pages=pages,
        total=total,
        query=q,
    )


@admin_bp.route("/admin/users/<username>/edit", methods=["POST"])
@admin_required
def user_edit(username):
    try:
        money = int(request.form.get("money", 0))
        recharge = int(request.form.get("total_recharge", 0))
        if money < 0 or recharge < 0:
            flash("金币和充值金额不能为负数", "error")
        else:
            update_user_money(username, money, recharge)
            flash(f"已更新 {username}：金币={money}，充值={recharge}", "success")
    except ValueError:
        flash("无效的数值", "error")
    return redirect(url_for("admin.users"))


@admin_bp.route("/admin/users/<username>/delete", methods=["POST"])
@admin_required
def user_delete(username):
    delete_user(username)
    flash(f'用户 "{username}" 已删除', "success")
    return redirect(url_for("admin.users"))


# ---- Exchange Code Management ----

@admin_bp.route("/admin/codes")
@admin_required
def codes():
    page = request.args.get("page", 1, type=int)
    code_list, total = get_all_codes(page=page, per_page=20)
    pages = (total + 19) // 20 if total > 0 else 1
    return render_template(
        "admin/codes.html",
        codes=code_list,
        page=page,
        pages=pages,
        total=total,
    )


@admin_bp.route("/admin/codes/create", methods=["POST"])
@admin_required
def code_create():
    code_type = request.form.get("type", "Money")
    num = int(request.form.get("num", 0))
    encrypted = create_code(code_type, num)
    flash(encrypted, "code_created")
    return redirect(url_for("admin.codes"))


# ---- Union Management ----

@admin_bp.route("/admin/unions")
@admin_required
def unions():
    union_list = get_all_unions()
    return render_template("admin/unions.html", unions=union_list)


@admin_bp.route("/admin/unions/<int:union_id>")
@admin_required
def union_detail(union_id):
    union = get_union_by_id(union_id)
    if not union:
        flash("工会不存在", "error")
        return redirect(url_for("admin.unions"))
    return render_template("admin/unions.html", union=union, show_detail=True)
