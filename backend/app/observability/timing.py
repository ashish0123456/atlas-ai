import time
from contextlib import contextmanager

@contextmanager
def measure_latency():
    start = time.time()
    yield lambda: time.time() - start