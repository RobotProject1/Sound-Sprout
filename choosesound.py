import time
import os
# This code reads from a file every second and writes to it in another script.

last_mtime = 0
while True:
    mtime = os.path.getmtime('path_list.txt')
    if mtime != last_mtime:
        f = open('path_list.txt', 'r')
        line = f.readline()
        print(line)
        f.close()
        last_mtime = mtime
    else:
        pass
        # If the file has not changed, wait for a short time before checking again.
        # This prevents the script from using too much CPU while waiting for changes.
    time.sleep(1)