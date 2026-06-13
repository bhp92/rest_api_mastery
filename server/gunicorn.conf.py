# gunicorn.conf.py
# Gunicorn configuration — loaded automatically when run from this directory
# Docs: https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing

# ── Binding ───────────────────────────────────────────────────
bind = "0.0.0.0:5000"
# "0.0.0.0" means listen on all network interfaces.
# Use "127.0.0.1:5000" if you put nginx in front (nginx → gunicorn).

# ── Workers ───────────────────────────────────────────────────
workers = multiprocessing.cpu_count() * 2 + 1
# Rule of thumb: (2 × CPU count) + 1
# For a 1-core VM this = 3 workers.
# Each worker is a separate OS process — handles one request at a time.

worker_class = "sync"
# sync   = standard, one request per worker at a time. Good default.
# gevent = async/greenlet, many concurrent requests per worker.
#          Use for APIs that do lots of external HTTP calls.

threads = 1
# Threads per worker (sync workers). Usually keep at 1.

timeout = 30
# If a worker takes longer than 30s to respond, gunicorn kills and restarts it.
# Prevents hung workers from blocking indefinitely.

keepalive = 2
# Seconds to keep an idle connection alive.

# ── Application ───────────────────────────────────────────────
wsgi_app = "wsgi:app"
# module:variable — gunicorn imports wsgi.py and uses the `app` variable.

chdir = "/home/bpuranik/rest_api_mastery/server"
# ⚠️  CHANGE THIS to your actual path.
# Run `echo $HOME` on the VM to find it.
# Example: chdir = "/home/bharatish/rest_api_mastery/server"

# ── Logging ───────────────────────────────────────────────────
accesslog = "-"
# "-" = stdout. systemd captures this and sends it to the journal.
# View with: journalctl -u rest_api_mastery -f

errorlog = "-"
# "-" = stderr. Same — goes to systemd journal.

loglevel = "info"
# debug | info | warning | error | critical

access_log_format = '%(h)s "%(r)s" %(s)s %(b)sB %(Dms)sms'
# h = remote address, r = request line, s = status, b = bytes, D = duration

# ── Process ───────────────────────────────────────────────────
preload_app = True
# Load the Flask app in the master process BEFORE forking workers.
# Workers inherit it via copy-on-write fork — saves memory.
# Side effect: code changes require a full restart (not just reload).

daemon = False
# CRITICAL: keep False when using systemd.
# systemd tracks the process by PID. If you daemonize, systemd loses track
# and thinks the service failed even if it's running fine.

pidfile = None
# systemd handles PID tracking. No need for a pidfile.

# ── Development overrides ─────────────────────────────────────
# Uncomment these for local dev (not for systemd/production use):
# reload = True      # auto-reload workers when code changes
# workers = 1        # single worker easier to debug
# loglevel = "debug" # verbose logging
