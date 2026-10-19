from database import connection
from security import hash_password

PASSWORDS = {1: "admin123"}

conn = connection()
try:
    for uid, pw in PASSWORDS.items():
        conn.execute("UPDATE users SET PasswordHash = ? WHERE Id = ?",
                     (hash_password(pw), uid))
    conn.commit()
finally:
    conn.close()
print("done")