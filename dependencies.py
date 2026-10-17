from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import connection

bearer_scheme = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = creds.credentials

    conn = connection()
    try:
        row = conn.execute("select * from users where ApiToken = ?", (token,)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="Invalid Token.")
        return dict(row)
    finally:
        conn.close()

def require_admin(user = Depends(get_current_user)):
    if not user.get("IsAdmin"):
        raise HTTPException(status_code=403, detail="Admins only.")
    return user