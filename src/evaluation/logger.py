import csv
from datetime import datetime

LOG_FILE = "data/logs/auth_log.csv"

def log_auth(score, result):

    with open(LOG_FILE, "a", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.now(),
            score,
            result
        ])