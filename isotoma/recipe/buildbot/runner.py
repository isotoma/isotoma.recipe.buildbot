import sys, os, subprocess, signal
from buildbot.scripts.runner import run as base_run

try:
    from buildbot.scripts import start
    class Follower(start.Follower):
        def follow(self, basedir):
            return 0
    start.Follower = Follower
except ImportError:
    pass


def send_signal(base_directory, master_cfg, sig):
    pidfile = os.path.join(base_directory, "twistd.pid")
    try:
        with open(pidfile, "rt") as f:
            pid = int(f.read().strip())
    except:
        return 0

    try:
        os.kill(pid, sig)
    except OSError, e:
        if e.errno != errno.ESRCH:
            raise
        return 0

    return 0


def run(base_directory, master_cfg):
    if len(sys.argv) <= 1 or not sys.argv[1] in ("start", "stop", "check", "reconfig", "tail", "graceful-stop", "logrotate"):
        print "Huh?"
        print "(start|stop|check|reconfig|tail|graceful-stop|logrotate)"
        return 1

    if sys.argv[1] == "tail":
        try:
            return subprocess.call(["tail", "-f", os.path.join(base_directory, "twistd.log")])
        except KeyboardInterrupt:
            return 0

    if sys.argv[1] == "graceful-stop":
        return send_signal(base_directory, master_cfg, signal.SIGUSR1)

    if sys.argv[1] == "logrotate":
        return send_signal(base_directory, master_cfg, signal.SIGUSR2)

    if sys.argv[1] == "start":
        sys.argv[1:] = ["start", base_directory]
    elif sys.argv[1] == "stop":
        sys.argv[1:] = ["stop", base_directory]
    elif sys.argv[1] == "check":
        sys.argv[1:] = ["checkconfig", master_cfg]
    elif sys.argv[1] == "reconfig":
        sys.argv[1:] = ["reconfig", base_directory]

    base_run()

