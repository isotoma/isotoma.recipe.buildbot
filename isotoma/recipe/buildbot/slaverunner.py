import sys, os, subprocess
from buildslave.scripts.runner import run as base_run

def run(base_directory, usesyslog=None):
    if usesyslog:
        from twisted.python import log,syslog
        syslog.startLogging(prefix=usesyslog)

    if len(sys.argv) <= 1 or not sys.argv[1] in ("start", "stop", "tail"):
        print "Huh?"
        print "(start|stop|tail)"
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

    base_run()

