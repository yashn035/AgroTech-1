import os
import json
import hashlib
import streamlit as st

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

USERS_FILE = os.path.join("data", "users.json")

def _load_users_db() -> dict:
    """Loads users database from JSON file."""
    if not os.path.exists(USERS_FILE):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        # Create default demo user
        demo_db = {
            "farmer_demo": {
                "password_hash": _hash_password("agro123"),
                "preferences": {"language": "en"}
            }
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(demo_db, f, indent=2)
        return demo_db
        
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users_db(db: dict):
    """Saves users database to JSON file."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def _hash_password(password: str) -> str:
    """Hashes password using bcrypt or SHA-256 fallback."""
    if HAS_BCRYPT:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    else:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _verify_password(password: str, hashed: str) -> bool:
    """Verifies plaintext password against stored hash."""
    if HAS_BCRYPT and hashed.startswith("$2b$"):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    else:
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == hashed

def register_user(username: str, password: str) -> tuple:
    """
    Registers a new user.
    
    Returns:
        tuple: (success_bool, message_str)
    """
    username = username.strip().lower()
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long."
        
    db = _load_users_db()
    if username in db:
        return False, f"Username '{username}' already exists."
        
    db[username] = {
        "password_hash": _hash_password(password),
        "preferences": {"language": "en"}
    }
    _save_users_db(db)
    return True, f"User '{username}' registered successfully! You can now log in."

def login_user(username: str, password: str) -> tuple:
    """
    Authenticates a user.
    
    Returns:
        tuple: (success_bool, message_str)
    """
    username = username.strip().lower()
    db = _load_users_db()
    
    if username not in db:
        return False, "Invalid username or password."
        
    user_data = db[username]
    if _verify_password(password, user_data.get("password_hash", "")):
        st.session_state["authenticated_user"] = username
        st.session_state["user_prefs"] = user_data.get("preferences", {"language": "en"})
        return True, f"Welcome back, {username}!"
    else:
        return False, "Invalid username or password."

def logout_user():
    """Logs out the current user."""
    if "authenticated_user" in st.session_state:
        del st.session_state["authenticated_user"]
    if "user_prefs" in st.session_state:
        del st.session_state["user_prefs"]

def get_current_user():
    """Returns current logged-in username or None."""
    return st.session_state.get("authenticated_user", None)
