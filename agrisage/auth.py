"""Username + password accounts with a login that survives page refreshes.

The first half is plain logic (hashing, signup, login, session tokens). The
second half is the Streamlit glue: reading the saved token from the browser's
localStorage, the login form, and logout.
"""

import hashlib
import hmac
import re
import secrets
import time

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from agrisage import db

MAX_FAILED_ATTEMPTS = 5
LOCK_SECONDS = 10 * 60
SESSION_DAYS = 30
MIN_PASSWORD_LENGTH = 8

_USERNAME_RE = re.compile(r"[a-z0-9_]{3,30}")
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1


# --- Passwords ---

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p))
    except ValueError:
        return False
    return hmac.compare_digest(digest, bytes.fromhex(digest_hex))


_DUMMY_HASH = hash_password("not-a-real-password")  # keeps unknown-user logins as slow as real ones


# --- Signup and login ---

def normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def signup(username: str, password: str) -> tuple[dict | None, str | None]:
    """Create an account. Returns (user, None) or (None, error message)."""
    username = normalize_username(username)
    if not _USERNAME_RE.fullmatch(username):
        return None, "Username must be 3-30 characters: letters, numbers or underscore."
    if len(password) < MIN_PASSWORD_LENGTH:
        return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    user_id = db.create_user(username, hash_password(password))
    if user_id is None:
        return None, "That username is taken."
    return {"id": user_id, "username": username}, None


def login(username: str, password: str) -> tuple[dict | None, str | None]:
    """Check credentials. Returns (user, None) or (None, error message)."""
    username = normalize_username(username)
    row = db.get_user_by_username(username)
    if row is None:
        verify_password(password, _DUMMY_HASH)
        return None, "Wrong username or password."

    wait = row["locked_until"] - int(time.time())
    if wait > 0:
        return None, f"Too many failed attempts. Try again in {-(-wait // 60)} minute(s)."

    if not verify_password(password, row["password_hash"]):
        db.record_failed_login(row["id"], MAX_FAILED_ATTEMPTS, LOCK_SECONDS)
        return None, "Wrong username or password."

    db.reset_failed_logins(row["id"])
    return {"id": row["id"], "username": row["username"]}, None


# --- Session tokens ---

def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_session(user_id: int) -> str:
    """Create a login session. Returns the raw token to keep in the browser; only its hash is stored."""
    token = secrets.token_urlsafe(32)
    db.create_auth_session(_token_hash(token), user_id, int(time.time()) + SESSION_DAYS * 86400)
    return token


def user_from_token(token: str) -> dict | None:
    return db.get_session_user(_token_hash(token)) if token else None


def end_session(token: str):
    if token:
        db.delete_auth_session(_token_hash(token))


# --- Streamlit glue ---

_USER_KEY = "agrisage_user"           # the logged-in user dict, or None for a guest once checked
_TOKEN_KEY = "agrisage_auth_token"
_DEVICE_KEY = "agrisage_legacy_device"
_BROWSER_OP_KEY = "agrisage_browser_op"  # JS still to run in the browser (save or clear the token)

_STORAGE_KEY = "agrisage_auth_token"  # localStorage key
_READ_JS = f"""
    [localStorage.getItem('{_STORAGE_KEY}') || '', localStorage.getItem('agrisage_device_id') || '']
"""


def _browser_op(js: str) -> str:
    return f"(function() {{ {js} return 'ok'; }})()"


def _run_pending_browser_op():
    """Run queued localStorage changes. The component has to be drawn in a run for its JS to execute."""
    op = st.session_state.get(_BROWSER_OP_KEY)
    if op and streamlit_js_eval(js_expressions=op, key="agrisage_auth_browser_op") == "ok":
        del st.session_state[_BROWSER_OP_KEY]


def get_current_user(key: str = "agrisage_auth_boot") -> dict | None:
    """Return {"id", "username"} for the logged-in user, or None for a guest.

    The browser answers on a later rerun, so the page stops here until it
    does. The answer is kept in session_state under its own keys: reusing the
    component's widget key would let Streamlit delete it on runs where the
    component isn't drawn, which remounts the component and loops forever.
    """
    _run_pending_browser_op()
    if _USER_KEY in st.session_state:
        return st.session_state[_USER_KEY]

    stored = streamlit_js_eval(js_expressions=_READ_JS, key=key)
    if not stored:
        st.caption("Loading…")
        st.stop()
    token, device_id = stored
    user = user_from_token(token)
    st.session_state[_USER_KEY] = user
    st.session_state[_TOKEN_KEY] = token if user else None
    st.session_state[_DEVICE_KEY] = device_id or None
    return user


def _start_session(user: dict):
    token = new_session(user["id"])
    st.session_state[_USER_KEY] = user
    st.session_state[_TOKEN_KEY] = token
    st.session_state[_BROWSER_OP_KEY] = _browser_op(f"localStorage.setItem('{_STORAGE_KEY}', '{token}');")
    # Carry over history saved on this browser before accounts existed
    device_id = st.session_state.get(_DEVICE_KEY)
    if device_id:
        db.claim_device_data(user["id"], device_id)


def logout():
    end_session(st.session_state.get(_TOKEN_KEY))
    st.session_state[_USER_KEY] = None
    st.session_state[_TOKEN_KEY] = None
    st.session_state[_BROWSER_OP_KEY] = _browser_op(f"localStorage.removeItem('{_STORAGE_KEY}');")
    st.session_state.pop("last_analysis", None)
    st.rerun()


def render_login_form(suffix: str = "main"):
    """Log in / Sign up tabs. Starts a session and reruns on success.

    `suffix` keeps widget keys unique if a page shows the form more than once.
    """
    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

    with login_tab:
        with st.form(f"agrisage_login_form_{suffix}"):
            username = st.text_input("Username", placeholder="your username", autocomplete="username")
            password = st.text_input("Password", type="password", placeholder="your password", autocomplete="current-password")
            submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
        if submitted:
            user, error = login(username, password)
            if error:
                st.error(error)
            else:
                _start_session(user)
                st.rerun()

    with signup_tab:
        with st.form(f"agrisage_signup_form_{suffix}"):
            username = st.text_input("Choose a username", placeholder="3-30 letters, numbers or _", autocomplete="off")
            password = st.text_input("Choose a password", type="password", placeholder=f"At least {MIN_PASSWORD_LENGTH} characters", autocomplete="new-password")
            confirm = st.text_input("Repeat password", type="password", placeholder="Type it again", autocomplete="new-password")
            submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
        if submitted:
            if password != confirm:
                st.error("The two passwords don't match.")
            else:
                user, error = signup(username, password)
                if error:
                    st.error(error)
                else:
                    _start_session(user)
                    st.rerun()


def login_prompt(message: str, suffix: str):
    """A note explaining why login is needed, with the form tucked into an expander."""
    st.info(message)
    with st.expander("🔑 Log in or sign up"):
        render_login_form(suffix)
