"""Thrift RPC endpoint routes.

The game client uses Apache Thrift TBinaryProtocol for these endpoints.
The private server client has been modified to use /_4399/ REST endpoints
instead, but these Thrift stubs handle any remaining Thrift calls.
"""

from flask import Blueprint, request, Response

from app.utils.thrift_stub import handle_thrift_request, is_thrift_request

thrift_bp = Blueprint("thrift", __name__)


def _handle(endpoint_type: str):
    """Common handler for Thrift endpoints."""
    data = request.get_data()
    if not data:
        return "1"
    try:
        result = handle_thrift_request(data, endpoint_type)
        return Response(result, content_type="application/x-thrift")
    except Exception:
        return "1"


@thrift_bp.route("/score/DevScore.php", methods=["POST", "GET"])
def score():
    return _handle("score")


@thrift_bp.route("/rank/FlashScoreApi", methods=["POST", "GET"])
def rank_flash():
    return _handle("rank")


@thrift_bp.route("/union/MemberApi", methods=["POST", "GET"])
def union_member():
    return _handle("union_member")


@thrift_bp.route("/union/VisitorApi", methods=["POST", "GET"])
def union_visitor():
    return _handle("union_visitor")


@thrift_bp.route("/union/MasterApi", methods=["POST", "GET"])
def union_master():
    return _handle("union_master")


@thrift_bp.route("/union/GrowApi", methods=["POST", "GET"])
def union_grow():
    return _handle("union_grow")


@thrift_bp.route("/union/RoleApi", methods=["POST", "GET"])
def union_role():
    return _handle("union_role")
