import os
import platform

def list_drives():
    system = platform.system()
    drives = []

    if system == "Windows":
        import string
        from ctypes import windll

        bitmask = windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                drives.append(f"{string.ascii_uppercase[i]}:\\")
    else:  # Linux / macOS
        drives.append("/")
        mounts = ["/mnt", "/media", "/Volumes"]
        for mount in mounts:
            if os.path.exists(mount):
                for name in os.listdir(mount):
                    drives.append(os.path.join(mount, name))
    return drives
