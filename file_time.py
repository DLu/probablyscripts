import os
import datetime


def _time_accessor(path, attr):
    file_stats = os.stat(path)
    seconds = int(getattr(file_stats, attr))
    return datetime.datetime.fromtimestamp(seconds)


def get_access_time(path):
    # Time of most recent access
    return _time_accessor(path, 'st_atime')


def get_modification_time(path):
    # Time of most recent content modification
    return _time_accessor(path, 'st_mtime')


def get_ctime(path):
    # Time of most recent metadata change on Unix and creation time on Windows
    return _time_accessor(path, 'st_ctime')
