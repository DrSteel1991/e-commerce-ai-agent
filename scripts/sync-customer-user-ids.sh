#!/usr/bin/env bash
# Links business_db.customers.user_id to auth_db.users.id
# for seed users like user1@example.com -> customer id 1.
set -euo pipefail

python3 <<'PY'
import re
import subprocess


def psql(db: str, sql: str) -> str:
    return subprocess.check_output(
        ["psql", "-d", db, "-t", "-A", "-c", sql],
        text=True,
    ).strip()


rows = [line for line in psql("auth_db", "SELECT id, email FROM users").splitlines() if "|" in line]

linked = 0
for row in rows:
    user_id, email = row.split("|", 1)
    match = re.match(r"user(\d+)@example\.com$", email.strip())
    if not match:
        continue

    customer_id = int(match.group(1))
    subprocess.run(
        [
            "psql",
            "-d",
            "business_db",
            "-c",
            f"UPDATE customers SET user_id = '{user_id}' WHERE id = {customer_id};",
        ],
        check=True,
    )
    print(f"Linked customer #{customer_id} → {email} ({user_id})")
    linked += 1

subprocess.run(
    [
        "psql",
        "-d",
        "business_db",
        "-c",
        "UPDATE orders SET customer_id = 1 WHERE id = 1;",
    ],
    check=True,
)

print(f"Done. Linked {linked} customers. Order #1 assigned to customer #1.")
PY
