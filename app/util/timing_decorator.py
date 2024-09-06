import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        original_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        print("time elapsed in ", func.__name__, ": ", "%.3f" % (end - start), " seconds", sep='')
        return original_return_val

    return wrapper

def async_timing_decorator(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        original_return_val = await func(*args, **kwargs)
        end = time.perf_counter()
        print("time elapsed in ", func.__name__, ": ", "%.3f" % (end - start), " seconds", sep='')
        return original_return_val

    return wrapper