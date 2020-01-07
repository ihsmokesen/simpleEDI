import time
from SimpleEDI.AppCore import AppCore


core = AppCore()
core.start_realtime_observer()
while True:
    time.sleep(5)
