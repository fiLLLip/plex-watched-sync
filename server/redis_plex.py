# redis_plex.py

import redis as redis_lib

_connection = None


def connection():
    """Return the Redis connection to the URL given by the environment
    variable REDIS_URL, creating it if necessary."""

    global _connection

    if _connection is None:
        _connection = redis_lib.StrictRedis(host='localhost', port=6379, db=0)
    return _connection
