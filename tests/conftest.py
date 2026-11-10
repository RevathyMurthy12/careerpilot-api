import os

# main.py reads DATABASE_URL once, at import time. If it is set (for example,
# the production PostgreSQL URL in your shell), the app would use PostgreSQL.
# pytest loads this file before any test module, so removing the variable here
# guarantees the tests use the temporary SQLite database instead.
os.environ.pop("DATABASE_URL", None)