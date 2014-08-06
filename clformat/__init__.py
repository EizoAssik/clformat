from .parser import parse_ctrl


def clformat(dest, ctrl_str, *args, **kwargs):
    """
    This is the wapper to
    """
    _string = _clformat(ctrl_str, *args, **kwargs)
    if dest is False or dest is None:
        return _string
    if dest is True:
        print(_string)
        return _string


def _clformat(ctrl_str, *args, **kwargs):
    """
    Format the string here.
    """
    _fn = parse_ctrl(ctrl_str)
    _string = _fn(*args, **kwargs)
    return _string
