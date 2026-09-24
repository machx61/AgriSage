"""Per-browser identity shared by all pages."""

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

_STATE_KEY = "agrisage_device_id"

_DEVICE_ID_JS = """
    (function() {
        var id = localStorage.getItem('agrisage_device_id');
        if (!id) { id = crypto.randomUUID(); localStorage.setItem('agrisage_device_id', id); }
        return id;
    })()
"""


def get_device_id(key: str) -> str:
    """Return a device ID kept in the browser's localStorage.

    The browser answers on a later rerun, so the page stops here until it
    does. That way nothing is saved under a throwaway ID.
    """
    # Stored under its own key: reusing the component's widget key would let
    # Streamlit delete it on runs where the component isn't drawn, which
    # remounts the component and triggers an endless rerun loop.
    if st.session_state.get(_STATE_KEY):
        return st.session_state[_STATE_KEY]

    device_id = streamlit_js_eval(js_expressions=_DEVICE_ID_JS, key=key)
    if not device_id:
        st.caption("Loading…")
        st.stop()
    st.session_state[_STATE_KEY] = device_id
    return device_id
