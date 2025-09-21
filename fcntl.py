LOCK_EX = 2
LOCK_UN = 8
LOCK_NB = 4

def fcntl(*args, **kwargs): return 0
def ioctl(*args, **kwargs): return 0
def flock(*args, **kwargs): return 0
