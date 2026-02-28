"""
Gunicorn Configuration File
Production WSGI server configuration.

Usage:
    gunicorn -c scripts/gunicorn.conf.py config.wsgi:application

Or with environment variables:
    WORKERS=4 BIND=0.0.0.0:8000 gunicorn -c scripts/gunicorn.conf.py config.wsgi:application
"""

import multiprocessing
import os

# =============================================================================
# Server Socket
# =============================================================================

# The socket to bind
bind = os.getenv("BIND", "0.0.0.0:8000")

# Backlog - number of pending connections
backlog = int(os.getenv("BACKLOG", "2048"))

# =============================================================================
# Worker Processes
# =============================================================================

# Number of worker processes
# Recommended: (2 x $num_cores) + 1
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Worker class - sync is recommended for Django
worker_class = os.getenv("WORKER_CLASS", "sync")

# Number of worker threads (for gthread worker class)
threads = int(os.getenv("THREADS", "1"))

# Maximum number of simultaneous clients
worker_connections = int(os.getenv("WORKER_CONNECTIONS", "1000"))

# Maximum number of requests a worker will process before restarting
max_requests = int(os.getenv("MAX_REQUESTS", "1000"))

# Jitter to add to max_requests to prevent all workers from restarting at once
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "50"))

# Timeout for worker processes
timeout = int(os.getenv("TIMEOUT", "30"))

# Graceful timeout for worker shutdown
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))

# Keepalive timeout
keepalive = int(os.getenv("KEEPALIVE", "2"))

# =============================================================================
# Server Mechanics
# =============================================================================

# Daemon mode - run in background
daemon = os.getenv("DAEMON", "False").lower() == "true"

# Process ID file
pidfile = os.getenv("PIDFILE", "/tmp/gunicorn.pid")

# User and group to run as (set to None to not change)
user = os.getenv("USER", None)
group = os.getenv("GROUP", None)

# =============================================================================
# Logging
# =============================================================================

# Access log - "-" means stdout
accesslog = os.getenv("ACCESS_LOG", "-")

# Error log - "-" means stderr
errorlog = os.getenv("ERROR_LOG", "-")

# Log level
loglevel = os.getenv("LOG_LEVEL", "info")

# Access log format
access_log_format = os.getenv(
    "ACCESS_LOG_FORMAT",
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
)

# =============================================================================
# Process Naming
# =============================================================================

# Process name
proc_name = os.getenv("PROC_NAME", "django_ecommerce")

# =============================================================================
# Server Hooks
# =============================================================================

def on_starting(server):
    """Called just before the master process is initialized."""
    pass


def on_reload(server):
    """Called when receiving SIGHUP signal."""
    pass


def when_ready(server):
    """Called just after the server is started."""
    pass


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    pass


def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    pass
