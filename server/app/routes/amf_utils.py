"""AMF3 encoding/decoding utility routes.

Used by the game client for encode/decode operations.
"""

import base64
import zlib
import json

from flask import Blueprint, request

from app.utils.amf3 import AMF3ByteArray

amf_bp = Blueprint("amf", __name__)


@amf_bp.route("/api/4399/Datadecode", methods=["POST", "GET"])
def data_decode():
    """Decode base64 + zlib + AMF3 data."""
    data = request.form.get("data", "")
    raw = base64.b64decode(data)
    decompressed = zlib.decompress(raw)
    arr = AMF3ByteArray()
    arr.append(decompressed)
    return arr.readObject()


@amf_bp.route("/api/4399/Dataencode", methods=["POST", "GET"])
def data_encode():
    """Encode data to base64 + zlib + AMF3."""
    data = request.form.get("data", "")
    arr = AMF3ByteArray()
    arr.writeObject(data)
    compressed = zlib.compress(arr.encode())
    return base64.b64encode(compressed).decode("ascii")


@amf_bp.route("/api/4399/bqtj/decodeObject", methods=["POST", "GET"])
def decode_object():
    """Decode base64 + AMF3 object."""
    data = request.form.get("data", "")
    raw = base64.b64decode(data)
    arr = AMF3ByteArray()
    arr.append(raw)
    return arr.readObject()


@amf_bp.route("/api/4399/bqtj/encodeObject", methods=["POST", "GET"])
def encode_object():
    """Encode JSON to AMF3 + base64."""
    data = request.form.get("data", "")
    arr = AMF3ByteArray()
    try:
        obj = json.loads(data)
    except Exception:
        obj = data
    arr.writeObject(obj)
    return base64.b64encode(arr.encode()).decode("ascii")
