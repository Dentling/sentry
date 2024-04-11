from __future__ import annotations

import re
from hashlib import md5
from typing import TYPE_CHECKING

from django.utils.encoding import force_bytes

from sentry.stacktraces.processing import get_crash_frame_from_event_data
from sentry.utils.safe import get_path

if TYPE_CHECKING:
    from sentry.db.models import NodeData

_fingerprint_var_re = re.compile(r"\{\{\s*(\S+)\s*\}\}")


def parse_fingerprint_var(value: str) -> str | None:
    match = _fingerprint_var_re.match(value)
    if match is not None and match.end() == len(value):
        return match.group(1)
    return None


def is_default_fingerprint_var(value: str) -> bool:
    return parse_fingerprint_var(value) == "default"


def hash_from_values(values: list[str]) -> str:
    result = md5()
    for value in values:
        result.update(force_bytes(value, errors="replace"))
    return result.hexdigest()


def get_rule_bool(value: str) -> bool:
    if value:
        value = value.lower()
        if value in ("1", "yes", "true"):
            return True
        elif value in ("0", "no", "false"):
            return False
    return False  # explicit default


def get_fingerprint_value(var: str, data: NodeData) -> str | None:
    if var == "transaction":
        return data.get("transaction") or "<no-transaction>"
    elif var == "message":
        message = (
            get_path(data, "logentry", "formatted")
            or get_path(data, "logentry", "message")
            or get_path(data, "exception", "values", -1, "value")
        )
        return message or "<no-message>"
    elif var in ("type", "error.type"):
        ty = get_path(data, "exception", "values", -1, "type")
        return ty or "<no-type>"
    elif var in ("value", "error.value"):
        value = get_path(data, "exception", "values", -1, "value")
        return value or "<no-value>"
    elif var in ("function", "stack.function"):
        frame = get_crash_frame_from_event_data(data)
        func = frame.get("function") if frame else None
        return func or "<no-function>"
    elif var in ("path", "stack.abs_path"):
        frame = get_crash_frame_from_event_data(data)
        func = frame.get("abs_path") or frame.get("filename") if frame else None
        return func or "<no-abs-path>"
    elif var == "stack.filename":
        frame = get_crash_frame_from_event_data(data)
        func = frame.get("filename") or frame.get("abs_path") if frame else None
        return func or "<no-filename>"
    elif var in ("module", "stack.module"):
        frame = get_crash_frame_from_event_data(data)
        mod = frame.get("module") if frame else None
        return mod or "<no-module>"
    elif var in ("package", "stack.package"):
        frame = get_crash_frame_from_event_data(data)
        pkg = frame.get("package") if frame else None
        if pkg:
            pkg = pkg.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return pkg or "<no-package>"
    elif var == "level":
        return data.get("level") or "<no-level>"
    elif var == "logger":
        return data.get("logger") or "<no-logger>"
    elif var.startswith("tags."):
        tag = var[5:]
        for t, value in data.get("tags") or ():
            if t == tag:
                return value
        return "<no-value-for-tag-%s>" % tag
    return None


def resolve_fingerprint_values(values: list[str], event_data: NodeData) -> list[str | None]:
    def _get_fingerprint_value(value: str) -> str | None:
        var = parse_fingerprint_var(value)
        if var is None:
            return value
        rv = get_fingerprint_value(var, event_data)
        if rv is None:
            return value
        return rv

    return [_get_fingerprint_value(x) for x in values]


def expand_title_template(template: str, event_data: NodeData) -> str:
    def _handle_match(match: re.Match[str]) -> str:
        var = match.group(1)
        rv = get_fingerprint_value(var, event_data)
        if rv is not None:
            return rv
        return match.group(0)

    return _fingerprint_var_re.sub(_handle_match, template)
