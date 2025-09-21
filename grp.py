class _G:
    def __init__(self, name="Users", gid=0):
        self.gr_name = name
        self.gr_gid = gid

def getgrgid(gid):
    return _G()
