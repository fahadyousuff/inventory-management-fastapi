from database import connection
from security import hash_password

# edit this dict — map Id → chosen password
PASSWORDS = {
    1: "admin123",      # Fahad
    2: "user123",       # Ahmed
    3: "bilawal123",    # Bilawal
    5: "osama123",      # Osama
    6: "waseem123",     # Waseem
    7: "bilal123",      # Bilal
    8: "shafeeq123",    # Shafeeq
}

conn = connection()
try:
    rows = conn.execute("SELECT Id, name, PasswordHash FROM users").fetchall()
    print(f"Found {len(rows)} users.\n")

    for row in rows:
        uid = row["Id"]
        name = row["name"]

        if row["PasswordHash"]:
            print(f"  [skip] Id {uid} ({name}) — already has a password")
            continue

        if uid not in PASSWORDS:
            print(f"  [MISS] Id {uid} ({name}) — no password in script, skipping")
            continue

        hashed = hash_password(PASSWORDS[uid])
        conn.execute(
            "UPDATE users SET PasswordHash = ? WHERE Id = ?",
            (hashed, uid),
        )
        print(f"  [ok]   Id {uid} ({name}) — password set")

    conn.commit()
    print("\nDone.")
finally:
    conn.close()