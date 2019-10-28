import os


def mkdir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

def chmod(file):
    os.chmod(file, 0o777)
