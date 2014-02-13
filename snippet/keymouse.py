import ctypes
import subprocess
import time

MOUSEEVENTF_MOVE = 0x0001  # mouse move
MOUSEEVENTF_ABSOLUTE = 0x8000  # absolute move
MOUSEEVENTF_MOVEABS = MOUSEEVENTF_MOVE + MOUSEEVENTF_ABSOLUTE

MOUSEEVENTF_LEFTDOWN = 0x0002  # left button down
MOUSEEVENTF_LEFTUP = 0x0004  # left button up
MOUSEEVENTF_CLICK = MOUSEEVENTF_LEFTDOWN + MOUSEEVENTF_LEFTUP

def wait_timeout(proc, seconds):
    """Wait for a process to finish, or raise exception after timeout"""
    start = time.time()
    end = start + seconds
    interval = min(seconds / 1000.0, .25)

    print("DBG wait for: %s sec" % seconds)
    while True:
        result = proc.poll()
        if result is not None:
            return result
        if time.time() >= end:
            proc.kill()
            print("DBG Process timed out, killed")
            break
        time.sleep(interval)

def _click_mouse(self, x, y):
# move first
    x = 65536L * x / ctypes.windll.user32.GetSystemMetrics(0) + 1
    y = 65536L * y / ctypes.windll.user32.GetSystemMetrics(1) + 1
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVEABS, x, y, 0, 0)
    # then click
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_CLICK, 0, 0, 0, 0)

def _trigger_sync(self, timeout=10):
    subp = subprocess.Popen(['keyinject.exe'])
    wait_timeout(subp, timeout)


for tries in range(1, 10):
    print("- Upgrade, Trigger sync for 30 seconds, try %s" % tries)
    _trigger_sync(timeout=30)

    print("- Upgrade, wait for 1 minute: %s" % time.ctime())
    time.sleep(60 * 1)

    #upgraded, got_level = self._check_upgraded(instance_id)
    #if upgraded:
    #    break

    for i in range(10):
        _click_mouse(100 + i, 0)