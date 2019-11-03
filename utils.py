import os


def mkdir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass


def chmod(file):
    os.chmod(file, 0o777)


def dirname(file):
    path_list = file.split('/')
    if len(path_list == 1):
        return ""

    return "/".join(path_list[:-1])
