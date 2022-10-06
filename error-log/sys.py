import sys

if sys.platform.startswith("linux"):
    print("linux")
elif sys.platform == "darwin":
    print("mac")
