import os, getpass
class _P:
    def __init__(self, name=None, uid=0):
        self.pw_name = name or os.environ.get("USERNAME") or getpass.getuser()
        self.pw_uid = uid

def getpwuid(uid):
    return _P()
