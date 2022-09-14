from setting import log_level


def log_debug(msg):
    if log_level >= 0:
        print(msg)


def log_info(msg):
    if log_level >= 1:
        print(msg)


def log_warn(msg):
    if log_level >= 2:
        print(msg)


def log_error(msg):
    if log_level >= 3:
        print(msg)
