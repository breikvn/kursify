import os
import time

import oracledb


HOST = os.environ.get("ORACLE_HOST", "db")
PORT = int(os.environ.get("ORACLE_PORT", "1521"))
SERVICE_NAME = os.environ.get("ORACLE_SERVICE_NAME", "xepdb1")
USER = os.environ.get("ORACLE_USER", "SYSTEM")
PASSWORD = os.environ.get("ORACLE_PASSWORD", "oracle")
TIMEOUT_SECONDS = int(os.environ.get("ORACLE_WAIT_TIMEOUT", "180"))
SLEEP_SECONDS = int(os.environ.get("ORACLE_WAIT_INTERVAL", "5"))


def main() -> int:
    deadline = time.time() + TIMEOUT_SECONDS
    dsn = f"{HOST}:{PORT}/{SERVICE_NAME}"

    while time.time() < deadline:
        try:
            with oracledb.connect(user=USER, password=PASSWORD, dsn=dsn):
                print(f"Oracle is ready at {dsn}")
                return 0
        except oracledb.Error as exc:
            print(f"Waiting for Oracle at {dsn}: {exc}")
            time.sleep(SLEEP_SECONDS)

    print(f"Timed out waiting for Oracle at {dsn}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
