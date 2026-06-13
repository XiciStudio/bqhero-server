"""Common helper functions for route handlers."""

from flask import request


def get_user_from_cookies():
    """Extract user identity from cookies."""
    return {
        "username": request.cookies.get("username", ""),
        "uid": request.cookies.get("uid", ""),
        "uuid": request.cookies.get("uuid", ""),
    }


def require_user():
    """Get user from cookies or return None."""
    user = get_user_from_cookies()
    if not user["username"] or not user["uid"]:
        return None
    return user


def json_response(data, status=200):
    """Return JSON response with proper headers."""
    from flask import jsonify
    return jsonify(data), status, {"Content-Type": "application/json; charset=utf-8"}


def text_response(text, status=200):
    """Return plain text response."""
    from flask import make_response
    resp = make_response(str(text), status)
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    return resp
