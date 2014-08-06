#encoding=utf-8
from parser import parse_ctrl


def _clformat(ctrl_str, *args, **kwargs):
    _fn = parse_ctrl(ctrl_str)
    _string = _fn(*args, **kwargs)
    return _string


def clformat(dest, ctrl_str, *args, **kwargs):
    _string = _clformat(ctrl_str, *args, **kwargs)
    if dest is False or dest is None:
        return _string
    if dest is True:
        print(_string)
        return _string
