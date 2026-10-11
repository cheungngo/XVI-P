import os, sys
_LOG = os.environ.get("XVIP_TRACE_LOG")
if _LOG:
    _fd = os.open(_LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    _seen = set()
    def _hook(ev, args):
        if ev != "open":
            return
        try:
            p, mode = args[0], args[1]
            if not isinstance(p, (str, bytes, os.PathLike)):
                return
            p = os.fsdecode(p)
            if isinstance(mode, int):
                w = bool(mode & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC))
            else:
                w = mode is not None and any(c in str(mode) for c in "wax+")
            ap = os.path.abspath(p)
            key = (ap, w)
            if key in _seen:
                return
            _seen.add(key)
            os.write(_fd, (("W " if w else "R ") + ap + "\n").encode())
        except Exception:
            pass
    sys.addaudithook(_hook)
