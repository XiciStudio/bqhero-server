"""AMF3 encoder/decoder for Flash game data compatibility.

The game client uses AMF3 (Action Message Format 3) for serializing
complex data structures. Save data is zlib-compressed AMF3 encoded.

This module provides basic AMF3 readObject/writeObject sufficient for
the game's data interchange format.
"""

import base64
import zlib
import json


class AMF3ByteArray:
    """Minimal AMF3 serializer/deserializer.

    For the server-side, we primarily need to handle:
    - decodeObject: base64 → AMF3 → Python dict/list
    - encodeObject: Python dict/list → AMF3 → base64

    Since we're dealing with data that's already been serialized by
    the client (and we just store/retrieve it), we can use a simpler
    JSON-based intermediate format when needed.
    """

    def __init__(self):
        self._buffer = bytearray()
        self._position = 0

    def append(self, data: bytes):
        self._buffer.extend(data)
        self._position = 0

    def encode(self) -> bytes:
        return bytes(self._buffer)

    def readObject(self):
        """Read AMF3 object and return Python dict/list/primitive."""
        if len(self._buffer) == 0:
            return None
        try:
            return self._read_amf3_value()
        except Exception:
            # Fallback: try to interpret as JSON string
            try:
                return json.loads(bytes(self._buffer).decode("utf-8"))
            except Exception:
                return bytes(self._buffer).decode("utf-8", errors="replace")

    def writeObject(self, obj):
        """Write Python object as AMF3."""
        self._buffer = bytearray()
        self._write_amf3_value(obj)

    def _read_amf3_value(self):
        """Read next AMF3 value from buffer."""
        if self._position >= len(self._buffer):
            return None
        type_byte = self._buffer[self._position]
        self._position += 1
        return self._read_type(type_byte)

    def _read_type(self, type_byte: int):
        if type_byte == 0x01:  # null
            return None
        elif type_byte == 0x02:  # false
            return False
        elif type_byte == 0x03:  # true
            return True
        elif type_byte == 0x04:  # integer
            return self._read_integer()
        elif type_byte == 0x05:  # double
            return self._read_double()
        elif type_byte == 0x06:  # string
            return self._read_string()
        elif type_byte == 0x09:  # array
            return self._read_array()
        elif type_byte == 0x0A:  # object
            return self._read_object()
        else:
            # For unrecognized types, return the raw remaining bytes as string
            remaining = bytes(self._buffer[self._position - 1:])
            return remaining.decode("utf-8", errors="replace")

    def _read_integer(self) -> int:
        """Read AMF3 variable-length unsigned integer (U29)."""
        result = 0
        for i in range(4):
            if self._position >= len(self._buffer):
                break
            byte = self._buffer[self._position]
            self._position += 1
            result = (result << 7) | (byte & 0x7F)
            if not (byte & 0x80):
                break
        return result

    def _read_double(self) -> float:
        import struct
        raw = bytes(self._buffer[self._position:self._position + 8])
        self._position += 8
        return struct.unpack(">d", raw)[0]

    def _read_string(self) -> str:
        ref = self._read_integer()
        if ref & 0x01:  # Not a reference
            length = ref >> 1
            raw = bytes(self._buffer[self._position:self._position + length])
            self._position += length
            return raw.decode("utf-8", errors="replace")
        return ""

    def _read_array(self):
        ref = self._read_integer()
        if ref & 0x01:
            count = ref >> 1
            result = []
            # Read key (usually empty string for dense arrays)
            key = self._read_string()
            while key:
                result[key] = self._read_amf3_value()
                key = self._read_string()
            for _ in range(count):
                result.append(self._read_amf3_value())
            return result
        return []

    def _read_object(self):
        ref = self._read_integer()
        if ref & 0x01:
            result = {}
            while True:
                key = self._read_string()
                if not key:
                    break
                result[key] = self._read_amf3_value()
            return result
        return {}

    def _write_amf3_value(self, obj):
        if obj is None:
            self._buffer.append(0x01)
        elif isinstance(obj, bool):
            self._buffer.append(0x03 if obj else 0x02)
        elif isinstance(obj, int):
            self._buffer.append(0x04)
            self._write_integer(obj)
        elif isinstance(obj, float):
            self._buffer.append(0x05)
            self._write_double(obj)
        elif isinstance(obj, str):
            self._buffer.append(0x06)
            self._write_string(obj)
        elif isinstance(obj, (list, tuple)):
            self._buffer.append(0x09)
            self._write_array(obj)
        elif isinstance(obj, dict):
            self._buffer.append(0x0A)
            self._write_object(obj)
        else:
            # Fallback: write as string
            self._buffer.append(0x06)
            self._write_string(str(obj))

    def _write_integer(self, value: int):
        if value < 0 or value > 0x1FFFFFFF:
            value = value & 0x1FFFFFFF
        if value < 0x80:
            self._buffer.append(value)
        elif value < 0x4000:
            self._buffer.append((value >> 7) | 0x80)
            self._buffer.append(value & 0x7F)
        elif value < 0x200000:
            self._buffer.append((value >> 14) | 0x80)
            self._buffer.append(((value >> 7) & 0x7F) | 0x80)
            self._buffer.append(value & 0x7F)
        else:
            self._buffer.append((value >> 22) | 0x80)
            self._buffer.append(((value >> 15) & 0x7F) | 0x80)
            self._buffer.append(((value >> 8) & 0x7F) | 0x80)
            self._buffer.append(value & 0xFF)

    def _write_double(self, value: float):
        import struct
        self._buffer.extend(struct.pack(">d", value))

    def _write_string(self, s: str):
        data = s.encode("utf-8")
        self._write_integer((len(data) << 1) | 0x01)  # Not a reference
        self._buffer.extend(data)

    def _write_array(self, arr):
        self._write_integer((len(arr) << 1) | 0x01)
        self._buffer.append(0x01)  # Empty key (dense array)
        for item in arr:
            self._write_amf3_value(item)

    def _write_object(self, obj: dict):
        self._write_integer(0x0B)  # Dynamic object, not a reference
        self._buffer.append(0x01)  # Empty class name
        for key, value in obj.items():
            self._write_string(key)
            self._write_amf3_value(value)
        self._buffer.append(0x01)  # End marker
