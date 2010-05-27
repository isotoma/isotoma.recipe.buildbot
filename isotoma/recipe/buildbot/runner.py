import sys, os, subprocess
from buildbot.scripts.runner import run as base_run

def run(base_directory, master_cfg):
    if len(sys.argv) <= 1 or not sys.argv[1] in ("start", "stop", "check", "reconfig", "tail"):
        print "Huh?"
        print "(start|stop|check|reconfig|tail)"
        return 1

    if sys.argv[1] == "tail":
        try:
            return subprocess.call(["tail", "-f", os.path.join(base_directory, "twistd.log")])
        except KeyboardInterrupt:
            return 0

    if sys.argv[1] == "start":
        sys.argv[1:] = ["start", base_directory]
    elif sys.argv[1] == "stop":
        sys.argv[1:] = ["stop", base_directory]
    elif sys.argv[1] == "check":
        sys.argv[1:] = ["checkconfig", master_cfg]
    elif sys.argv[1] == "reconfig":
        sys.argv[1:] = ["reconfig", base_directory]

    base_run()

