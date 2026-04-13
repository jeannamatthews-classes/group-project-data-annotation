"""
Utility for serializing / deserializing Python dataclass objects to JSON.
"""

import dataclasses
import json
from datetime import date, datetime
from pathlib import Path


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def _from_dict(cls, data):
    import typing
    try:
        type_hints = typing.get_type_hints(cls)
    except Exception:
        type_hints = {f.name: f.type for f in dataclasses.fields(cls)}

    kwargs = {}
    for field_name, raw_value in data.items():
        if field_name in type_hints:
            kwargs[field_name] = _coerce(type_hints[field_name], raw_value)

    return cls(**kwargs)


def _coerce(tp, value):
    if value is None:
        return None

    origin = getattr(tp, "__origin__", None)
    args = getattr(tp, "__args__", ())

    # Optional[X]
    if origin is __import__("typing").Union and type(None) in args:
        tp = next(a for a in args if a is not type(None))
        return _coerce(tp, value)

    if origin is list and args:
        return [_coerce(args[0], item) for item in value]

    if origin is dict and len(args) == 2:
        return {k: _coerce(args[1], v) for k, v in value.items()}

    if dataclasses.is_dataclass(tp) and isinstance(value, dict):
        return _from_dict(tp, value)

    if tp is datetime and isinstance(value, str):
        return datetime.fromisoformat(value)
    if tp is date and isinstance(value, str):
        return date.fromisoformat(value)

    return value


def write(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, cls=DataclassEncoder, ensure_ascii=False)


def read(cls, path):
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        raise ValueError("File contains a list — use read_list() instead.")
    return _from_dict(cls, data)


def read_list(cls, path):
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("File contains a single object — use read() instead.")
    return [_from_dict(cls, item) for item in data]


def to_json(obj):
    return json.dumps(obj, cls=DataclassEncoder, ensure_ascii=False)


def from_json(cls, json_str):
    return _from_dict(cls, json.loads(json_str))


# Run Tests

if __name__ == "__main__":
    import sys, os
    sys.path.append(".")
    from widgets.commentsWidget import CommentEntry
    
    # ---- single object ----
    testComment = CommentEntry(
        timestamp_ms=1024,
        data_point="a point in time",
        comment="At this time in history..."
    )

    write(testComment, "singleCommentTest.json")
    comment = read(CommentEntry, "singleCommentTest.json")
    assert testComment == comment, "Single-object round-trip failed!"
    print("Single object round-trip: OK")
    print(to_json(comment))

    # ---- list of objects ----
    testComment2 = CommentEntry(timestamp_ms=2048, data_point="a different point in time", comment="An event at some other time in history")
    write([testComment, testComment2], "/tmp/commentsTest.json")
    comments_read = read_list(CommentEntry, "/tmp/commentsTest.json")
    assert [testComment, testComment2] == comments_read, "List round-trip failed!"
    print("\nList round-trip: OK")