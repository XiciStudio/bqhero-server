"""Minimal Thrift binary protocol handler.

The game client uses Apache Thrift (TBinaryProtocol) for RPC calls to
score, rank, and union endpoints. This module provides:
 - Thrift message parsing (TBinaryProtocol strict/old-style)
 - Serialization helpers for building valid struct replies
 - Endpoint-specific response handling

TBinaryProtocol type codes:
  0=STOP  2=BOOL  3=BYTE  4=DOUBLE  6=I16  8=I32  10=I64
  11=STRING  12=STRUCT  13=MAP  14=SET  15=LIST
"""

import struct
import json


# ═══════════════════════════════════════════════════════════════
#  Message parsing
# ═══════════════════════════════════════════════════════════════

def read_thrift_message(data: bytes) -> dict:
    """Parse a Thrift TBinaryProtocol message header.

    Returns dict with: version, name, type, seqid, body_offset
    """
    if len(data) < 4:
        return None

    version = struct.unpack(">i", data[0:4])[0]
    strict = bool(version & 0x80000000)

    if strict:
        name_len = version & 0x7FFFFFFF
        offset = 4
    else:
        name_len = data[4] if len(data) > 4 else 0
        offset = 5

    if offset + name_len > len(data):
        return None

    name = data[offset:offset + name_len].decode("utf-8", errors="replace")
    offset += name_len

    if offset + 5 > len(data):
        return None

    msg_type = struct.unpack(">b", data[offset:offset + 1])[0]
    offset += 1
    seqid = struct.unpack(">i", data[offset:offset + 4])[0]
    offset += 4

    return {
        "version": version,
        "name": name,
        "type": msg_type,
        "seqid": seqid,
        "body_offset": offset,
    }


# ═══════════════════════════════════════════════════════════════
#  Serialization helpers
# ═══════════════════════════════════════════════════════════════

def _write_i16(v: int) -> bytes:
    return struct.pack(">h", v)


def _write_i32(v: int) -> bytes:
    return struct.pack(">i", v)


def _write_string(v: str) -> bytes:
    data = v.encode("utf-8")
    return _write_i32(len(data)) + data


def _write_field(ftype: int, fid: int, value: bytes) -> bytes:
    """Encode a single struct field: type_byte + field_id(i16) + value."""
    return bytes([ftype]) + _write_i16(fid) + value


def _write_struct(fields: list[tuple[int, int, bytes]]) -> bytes:
    """Encode a struct from (type, field_id, value) tuples. Adds STOP."""
    buf = bytearray()
    for ftype, fid, value in fields:
        buf.extend(_write_field(ftype, fid, value))
    buf.append(0)  # STOP
    return bytes(buf)


def _write_list(elem_type: int, items: list[bytes]) -> bytes:
    """Encode a list: elem_type + count(i32) + items."""
    buf = bytearray([elem_type])
    buf.extend(_write_i32(len(items)))
    for item in items:
        buf.extend(item)
    return bytes(buf)


# ═══════════════════════════════════════════════════════════════
#  Struct builders — Score (DevScoreImpl)
# ═══════════════════════════════════════════════════════════════

# ScoreInfo struct: uId(string,1) userName(string,2) score(i32,3) rank(i32,4)
# Using common game-industry field IDs for score entries.

def _build_score_info(uid: str, username: str, score: int, rank: int) -> bytes:
    return _write_struct([
        (11, 1, _write_string(uid)),       # STRING uId
        (11, 2, _write_string(username)),  # STRING userName
        (8,  3, _write_i32(score)),         # I32 score
        (8,  4, _write_i32(rank)),          # I32 rank
    ])


def _build_return_score_top(top_list: list[dict]) -> bytes:
    """Build ReturnScoreTop struct: topList(list,1) rankNum(i32,2)."""
    items = [_build_score_info(
        e.get("uId", ""),
        e.get("userName", ""),
        e.get("score", 0),
        e.get("rank", 0),
    ) for e in top_list]
    return _write_struct([
        (15, 1, _write_list(12, items)),     # LIST<STRUCT> topList
        (8,  2, _write_i32(len(top_list))),  # I32 rankNum
    ])


def _build_return_submit_score(rank: int, score: int) -> bytes:
    """Build ReturnSubmitScore struct: rank(i32,1) score(i32,2)."""
    return _write_struct([
        (8, 1, _write_i32(rank)),   # I32 rank
        (8, 2, _write_i32(score)),  # I32 score
    ])


# ═══════════════════════════════════════════════════════════════
#  Message builders
# ═══════════════════════════════════════════════════════════════

def _build_reply_message(method_name: str, seqid: int, body: bytes) -> bytes:
    """Build a complete Thrift REPLY message with the given body."""
    msg = bytearray()

    # TMessage header (strict mode)
    result_name = method_name + "_result"
    name_bytes = result_name.encode("utf-8")
    msg.extend(_write_i32(0x80010000 | len(name_bytes)))
    msg.extend(name_bytes)
    msg.append(2)  # REPLY
    msg.extend(_write_i32(seqid))

    # Body: success field (id 0, type STRUCT) wrapping the result
    msg.extend(_write_field(12, 0, body))
    msg.append(0)  # STOP (end of outer struct)

    return bytes(msg)


def make_thrift_reply(method_name: str, seqid: int, result_data: bytes = b"") -> bytes:
    """Build a Thrift REPLY with optional result data.

    If result_data is empty, returns an empty struct (all fields default).
    This is safe — the client's generated code uses defaults for missing fields.
    """
    if not result_data:
        # Empty struct: just STOP. The client's generated reader will see no
        # success field and use default values (0 / empty string / empty list).
        result_data = b"\x00"
    return _build_reply_message(method_name, seqid, result_data)


def make_thrift_error(seqid: int, message: str = "") -> bytes:
    """Build a Thrift EXCEPTION message (TApplicationException)."""
    body = _write_struct([
        (11, 1, _write_string(message or "Internal error")),  # STRING message
        (8,  2, _write_i32(0)),                                 # I32 type (UNKNOWN)
    ])
    msg = bytearray()
    msg.extend(_write_i32(0x80010000))  # zero-length name
    msg.append(3)  # EXCEPTION
    msg.extend(_write_i32(seqid))
    msg.extend(body)
    return bytes(msg)


# ═══════════════════════════════════════════════════════════════
#  Request dispatcher
# ═══════════════════════════════════════════════════════════════

def handle_thrift_request(data: bytes, endpoint_type: str) -> bytes:
    """Process a Thrift binary request and return a valid response.

    endpoint_type: 'score', 'rank', 'union_member', 'union_visitor',
                   'union_master', 'union_grow', 'union_role'
    """
    parsed = read_thrift_message(data)
    if not parsed:
        return make_thrift_error(0, "Invalid thrift message")

    if parsed["type"] != 1:  # CALL
        return make_thrift_error(parsed["seqid"], "Unsupported message type")

    method = parsed["name"]
    seqid = parsed["seqid"]

    # Build endpoint-specific response structs
    if endpoint_type == "score":
        return _handle_score(method, seqid)
    elif endpoint_type == "rank":
        return _handle_rank(method, seqid)
    elif endpoint_type.startswith("union_"):
        return _handle_union(method, seqid, endpoint_type)

    # Generic: return empty struct
    return make_thrift_reply(method, seqid)


def _handle_score(method: str, seqid: int) -> bytes:
    """Handle DevScoreImpl RPC methods.

    Methods: getTop → ReturnScoreTop, submitScore → ReturnSubmitScore, test → void
    """
    if method == "getTop":
        # Return empty leaderboard (valid but no entries)
        result = _build_return_score_top([])
        return make_thrift_reply(method, seqid, result)
    elif method == "submitScore":
        # Return rank=1, score=0 (placeholder — real scores use /_4399/submit)
        result = _build_return_submit_score(1, 0)
        return make_thrift_reply(method, seqid, result)
    elif method == "test":
        # void return — empty struct is correct
        return make_thrift_reply(method, seqid)
    return make_thrift_error(seqid, f"Unknown method: {method}")


def _handle_rank(method: str, seqid: int) -> bytes:
    """Handle FlashScoreApi RPC methods.

    RankListProxy in the game uses HTTP /_4399/ endpoints directly, so
    this Thrift endpoint is typically unused. Return empty valid responses.
    """
    return make_thrift_reply(method, seqid)


def _handle_union(method: str, seqid: int, endpoint_type: str) -> bytes:
    """Handle Union*Api RPC methods.

    Union data is managed through /_4399/ REST endpoints. These Thrift
    stubs return valid empty responses.
    """
    return make_thrift_reply(method, seqid)


def is_thrift_request(request) -> bool:
    """Check if the incoming request is a Thrift binary request."""
    ct = request.content_type or ""
    return "application/x-thrift" in ct or "application/octet-stream" in ct
