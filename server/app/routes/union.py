"""Union/guild routes — 11 endpoints for guild management."""

import json
import time
import uuid

from flask import Blueprint, request

from app.models.union import (
    get_all_unions, get_union_by_id, create_union, update_union_info,
    update_union_members, update_union_applications,
    get_union_members, get_union_applications,
)
from app.models.user import (
    get_save_metadata, deduct_money, get_money, set_union, get_union_id,
    set_union_by_uid,
)
from app.utils.helpers import get_user_from_cookies

union_bp = Blueprint("union", __name__)

# Union level-up table: contribution required per level (94 levels)
UNION_LEVEL_TABLE = [
    0, 10000, 20000, 30000, 40000, 50000, 60000, 180000, 300000, 420000,
    540000, 660000, 780000, 910000, 1050000, 1200000, 1360000, 1530000,
    1710000, 1900000, 2100000, 2310000, 2530000, 2760000, 3000000, 5250000,
    5510000, 5780000, 6060000, 7350000, 7650000, 7960000, 8280000, 8610000,
    9950000, 10300000, 10660000, 11030000, 11410000, 12800000, 13200000,
    13610000, 14030000, 14460000, 14900000, 16350000, 16810000, 17280000,
    17760000, 18250000, 18850000, 19550000, 20350000, 21250000, 22250000,
    23350000, 24550000, 25850000, 27250000, 28750000, 30350000, 32050000,
    33850000, 35750000, 37750000, 39850000, 42050000, 44350000, 46750000,
    49250000, 51850000, 54550000, 57350000, 60250000, 63250000, 66450000,
    69850000, 73450000, 77250000, 81250000, 85450000, 89850000, 94450000,
    99250000, 104250000, 109450000, 114850000, 120450000, 126250000,
    132250000, 138450000, 144850000, 151450000, 158250000, 165250000,
    172450000, 179850000, 187250000, 194650000, 202050000, 209450000,
    216850000, 224250000, 231650000, 239050000,
]


@union_bp.route("/_4399/getUnionList", methods=["POST", "GET"])
def get_list():
    unions = get_all_unions()
    unions = sorted(unions, key=lambda x: x.get("level", 1), reverse=True)
    return json.dumps({"tag": "", "unionList": unions}, ensure_ascii=False)


@union_bp.route("/_4399/getOwnUnion", methods=["POST", "GET"])
def get_mine():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])

    if not union_id:
        return json.dumps({"tag": "", "me": {"unionInfo": None}}, ensure_ascii=False)

    udata = get_union_by_id(union_id)
    if not udata:
        return json.dumps({"tag": "", "me": {"unionInfo": None}}, ensure_ascii=False)

    result = {"tag": "", "me": {"unionInfo": udata["info"]}}
    for member in udata["member"]:
        if str(member.get("uId")) == str(user["uid"]):
            result["me"]["member"] = member
            break

    return json.dumps(result, ensure_ascii=False)


@union_bp.route("/_4399/unionCreate", methods=["POST", "GET"])
def create():
    user = get_user_from_cookies()
    username = user["username"]
    uid = user["uid"]
    idx = int(request.form.get("idx", 0))

    # Cost: 200 money
    deduct_money(username, 200)

    metadata_str = get_save_metadata(username)
    metadata = json.loads(metadata_str) if metadata_str else []
    nick_name = "爆枪小战士 lv.1"
    if idx < len(metadata):
        nick_name = metadata[idx].get("title", nick_name)

    union_id = int(str(uuid.uuid4().int)[0:6])

    # Create member entry
    member = {
        "id": uid,
        "gameId": "100027788",
        "unionId": union_id,
        "uId": uid,
        "userName": username,
        "index": idx,
        "contribution": 0,
        "nickName": nick_name,
        "extra": "",
        "extra2": "",
        "active_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roleId": -1,
        "roleName": "总司令",
    }

    # Create union info
    info = {
        "id": union_id,
        "unionId": union_id,
        "title": request.form.get("title", "新建战队"),
        "userName": username,
        "level": 1,
        "count": 1,
        "extra": {},
        "experience": 0,
        "contribution": 0,
        "nickName": nick_name,
        "uId": uid,
        "index": idx,
        "extra2": "",
        "dissolveDate": "",
        "transfer": "",
        "gameid": "100027788",
    }

    create_union(union_id, info)
    set_union(username, union_id)

    # Add member to newly created union
    update_union_members(union_id, [member])

    return "True"


@union_bp.route("/_4399/setMemberExtra", methods=["POST", "GET"])
def set_member_extra():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    members = get_union_members(union_id)
    idx = int(request.form.get("idx", 0))

    for m in members:
        if str(m.get("uId")) == str(user["uid"]):
            m["extra"] = request.form.get("extra", "")
            break

    update_union_members(union_id, members)
    return "True"


@union_bp.route("/_4399/setUnionExtra", methods=["POST", "GET"])
def set_union_extra():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    udata = get_union_by_id(union_id)
    if not udata:
        return "False"

    info = udata["info"]
    info["extra"] = request.form.get("extra", "")
    update_union_info(union_id, info)
    return "True"


@union_bp.route("/_4399/getUnionMembers", methods=["POST", "GET"])
def get_members():
    union_id = int(request.form.get("unionId", 0))
    members = get_union_members(union_id)
    return json.dumps({"tag": "", "memberList": members}, ensure_ascii=False)


@union_bp.route("/_4399/applyUnion", methods=["POST", "GET"])
def apply():
    user = get_user_from_cookies()
    username = user["username"]
    uid = user["uid"]
    union_id = int(request.form.get("unionId", 0))
    idx = int(request.form.get("idx", 0))

    metadata_str = get_save_metadata(username)
    metadata = json.loads(metadata_str) if metadata_str else []
    nick_name = "爆枪小战士 lv.1"
    if idx < len(metadata):
        nick_name = metadata[idx].get("title", nick_name)

    application = {
        "id": uid,
        "gameId": "100027788",
        "unionId": union_id,
        "uId": uid,
        "userName": username,
        "index": idx,
        "contribution": 0,
        "nickName": nick_name,
        "extra": request.form.get("extra", ""),
        "extra2": "",
        "active_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roleId": 0,
        "roleName": "",
    }

    apps = get_union_applications(union_id)
    apps = [a for a in apps
            if not (str(a.get("uId")) == str(uid) and a.get("index") == idx)]
    apps.append(application)
    update_union_applications(union_id, apps)
    return "True"


@union_bp.route("/_4399/getApplyList", methods=["POST", "GET"])
def get_applications():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return json.dumps({"tag": "", "applyList": None}, ensure_ascii=False)

    apps = get_union_applications(union_id)
    return json.dumps({"tag": "", "applyList": apps}, ensure_ascii=False)


@union_bp.route("/_4399/auditMember", methods=["POST", "GET"])
def audit():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    applicant_uid = request.form.get("userId", "")
    user_index = int(request.form.get("userIndex", 0))
    audit_result = int(request.form.get("auditResult", 0))

    apps = get_union_applications(union_id)
    approved_app = None

    # Find and remove from applications
    new_apps = []
    for a in apps:
        if str(a.get("uId")) == applicant_uid and a.get("index") == user_index:
            approved_app = a
        else:
            new_apps.append(a)
    update_union_applications(union_id, new_apps)

    if audit_result and approved_app:
        # Approve — add to members
        set_union_by_uid(applicant_uid, union_id)
        members = get_union_members(union_id)
        members.append(approved_app)
        update_union_members(union_id, members)

        # Update count
        udata = get_union_by_id(union_id)
        if udata:
            info = udata["info"]
            info["count"] = len(members)
            update_union_info(union_id, info)

    return "True"


@union_bp.route("/_4399/doTask", methods=["POST", "GET"])
def do_task():
    """Union task: +100 contribution, check level-up."""
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    udata = get_union_by_id(union_id)
    if not udata:
        return "False"

    idx = int(request.form.get("idx", 0))
    members = udata["member"]
    info = udata["info"]

    # Add contribution to member
    for m in members:
        if str(m.get("uId")) == str(user["uid"]) and m.get("index") == idx:
            m["contribution"] = m.get("contribution", 0) + 100
            break

    info["contribution"] = info.get("contribution", 0) + 100
    info["experience"] = info.get("experience", 0) + 100

    # Check level-up
    current_level = info.get("level", 1)
    if current_level < len(UNION_LEVEL_TABLE):
        if info["contribution"] >= UNION_LEVEL_TABLE[current_level]:
            info["contribution"] -= UNION_LEVEL_TABLE[current_level]
            info["level"] = current_level + 1

    update_union_members(union_id, members)
    update_union_info(union_id, info)
    return "True"


@union_bp.route("/_4399/doExchange", methods=["POST", "GET"])
def do_exchange():
    """Exchange money for union contribution. 10 money = 100 contribution."""
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    money = int(request.form.get("money", 0))
    idx = int(request.form.get("idx", 0))

    deduct_money(user["username"], money)
    gongxian = int(money / 10 * 100)

    udata = get_union_by_id(union_id)
    if not udata:
        return "False"

    members = udata["member"]
    info = udata["info"]

    for m in members:
        if str(m.get("uId")) == str(user["uid"]) and m.get("index") == idx:
            m["contribution"] = m.get("contribution", 0) + gongxian
            break

    info["contribution"] = info.get("contribution", 0) + gongxian
    info["experience"] = info.get("experience", 0) + gongxian

    # Check level-up
    current_level = info.get("level", 1)
    if current_level < len(UNION_LEVEL_TABLE):
        if info["contribution"] >= UNION_LEVEL_TABLE[current_level]:
            info["level"] = current_level + 1

    update_union_members(union_id, members)
    update_union_info(union_id, info)
    return "True"


@union_bp.route("/_4399/removeMember", methods=["POST", "GET"])
def remove_member():
    """Kick a member from the union."""
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    target_uid = request.form.get("userId", "")
    target_index = int(request.form.get("userIndex", 0))

    members = get_union_members(union_id)
    members = [m for m in members
               if not (str(m.get("uId")) == target_uid and m.get("index") == target_index)]
    update_union_members(union_id, members)

    udata = get_union_by_id(union_id)
    if udata:
        info = udata["info"]
        info["count"] = len(members)
        update_union_info(union_id, info)

    set_union_by_uid(target_uid, None)
    return "True"


@union_bp.route("/_4399/dissolveUnion", methods=["POST", "GET"])
def dissolve():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    udata = get_union_by_id(union_id)
    if not udata:
        return "False"

    for member in udata["member"]:
        set_union_by_uid(str(member.get("uId")), 0)

    from app.extensions import execute
    execute("DELETE FROM union_data WHERE id = ?", (union_id,))
    return "True"


@union_bp.route("/_4399/transferUnion", methods=["POST", "GET"])
def transfer():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    target_uid = request.form.get("userId", "")
    target_index = int(request.form.get("userIndex", 0))

    udata = get_union_by_id(union_id)
    if not udata:
        return "False"

    info = udata["info"]
    members = udata["member"]

    for m in members:
        if str(m.get("uId")) == target_uid and m.get("index") == target_index:
            info["userName"] = m.get("userName", "")
            info["nickName"] = m.get("nickName", "")
            info["uId"] = target_uid
            info["index"] = target_index
            m["roleId"] = -1
            m["roleName"] = "总司令"
            break

    for m in members:
        if str(m.get("uId")) == str(user["uid"]):
            m["roleId"] = 0
            m["roleName"] = ""
            break

    update_union_info(union_id, info)
    update_union_members(union_id, members)
    return "True"


@union_bp.route("/_4399/setRole", methods=["POST", "GET"])
def set_role():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    target_uid = request.form.get("userId", "")
    target_index = int(request.form.get("userIndex", 0))
    role_id = int(request.form.get("roleId", 0))

    members = get_union_members(union_id)
    for m in members:
        if str(m.get("uId")) == target_uid and m.get("index") == target_index:
            m["roleId"] = role_id
            break

    update_union_members(union_id, members)
    return "True"


@union_bp.route("/_4399/useUnionContribution", methods=["POST", "GET"])
def use_contribution():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    amount = int(request.form.get("contribution", 0))
    idx = int(request.form.get("idx", 0))

    udata = get_union_by_id(union_id)
    if not udata:
        return "False"

    members = udata["member"]
    info = udata["info"]

    for m in members:
        if str(m.get("uId")) == str(user["uid"]) and m.get("index") == idx:
            current = m.get("contribution", 0)
            if current >= amount:
                m["contribution"] = current - amount
                info["contribution"] = info.get("contribution", 0) - amount
            break

    update_union_members(union_id, members)
    update_union_info(union_id, info)
    return "True"


@union_bp.route("/_4399/applyMultiAudit", methods=["POST", "GET"])
def multi_audit():
    user = get_user_from_cookies()
    union_id = get_union_id(user["username"])
    if not union_id:
        return "False"

    target_uid = request.form.get("userId", "")
    target_index = int(request.form.get("userIndex", 0))
    result = int(request.form.get("result", 0))

    apps = get_union_applications(union_id)
    approved_app = None
    new_apps = []
    for a in apps:
        if str(a.get("uId")) == target_uid and a.get("index") == target_index:
            approved_app = a
        else:
            new_apps.append(a)
    update_union_applications(union_id, new_apps)

    if result and approved_app:
        set_union_by_uid(target_uid, union_id)
        members = get_union_members(union_id)
        members.append(approved_app)
        update_union_members(union_id, members)

        udata = get_union_by_id(union_id)
        if udata:
            info = udata["info"]
            info["count"] = len(members)
            update_union_info(union_id, info)

    return "True"
