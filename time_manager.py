from datetime import datetime
import sqlite3
import time

DB_PATH = "database.db"
DECREMENTAL_VALUE = 1  # Seconds
DECREMENT_INTERVAL = 1  # Seconds, how much to decrement every active device each time


def decrement_all_devices():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Subtract 60 seconds from every device that is_active=1 and time_remaining > 0
    cur.execute(
        """
        UPDATE devices
        SET 
            time_remaining = CASE
                WHEN time_remaining <= ? THEN 0
                ELSE time_remaining - ?
            END,
            is_active = CASE
                WHEN time_remaining <= ? THEN 0
                ELSE 1
            END
        WHERE is_active = 1 AND time_remaining > 0;
    """,
        (DECREMENT_INTERVAL, DECREMENT_INTERVAL, DECREMENT_INTERVAL),
    )
    print(f"[{datetime.now()}] Decremented {cur.rowcount} devices")
    conn.commit()
    conn.close()


def main_loop():
    while True:
        start = time.time()
        decrement_all_devices()
        # Sleep until the next interval
        elapsed = time.time() - start
        to_sleep = max(0, DECREMENT_INTERVAL - elapsed)
        time.sleep(to_sleep)


if __name__ == "__main__":
    print(
        f"[{datetime.now()}] Starting time_manager (decrement every {DECREMENT_INTERVAL}s)"
    )
    main_loop()
