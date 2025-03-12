import time
import TexUI
import sys
import os

(
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 
                ".."
            )
        )
    )
)

def test_time(function, params, count=10000):
    time_start = time.time()
    for _ in range(count):
        function(*params)
    delta = (time.time() - time_start) / count * 1000

    print(f"total time for {function!r} -> {delta:.2f}ms @ {count}x")

test_time(TexUI.Display, (256, 256, "!", True))

display = TexUI.Display(256, 256, "!", True)

test_time(display.fill, (0, 0, "#"))
