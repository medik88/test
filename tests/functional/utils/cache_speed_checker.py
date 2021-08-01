import time

from settings import settings


async def check_cache_speed(func, *args, **kwargs):
    time1_start = time.time()
    result1 = await func(*args, **kwargs)
    time1_end = time.time()
    result2 = await func(*args, **kwargs)
    time2_end = time.time()

    time1 = time1_end - time1_start
    time2 = time2_end - time1_end

    # check that second run is faster than first
    assert time2 * settings.CACHE_BOOST_RATIO < time1
    return (result1, result2)
