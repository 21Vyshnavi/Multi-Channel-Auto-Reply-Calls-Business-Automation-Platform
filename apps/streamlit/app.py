from __future__ import annotations

import time
from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st


@dataclass(frozen=True)
class InboxItem:
    id: str
    channel: str
    receivedAt: str
    from_: str
    name: Optional[str]
    text: Optional[str]


_session = requests.Session()
_session.trust_env = False  # avoid proxy env vars breaking localhost/127.0.0.1 calls


def apply_ui_styles() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  .stApp {
    background: radial-gradient(1200px 600px at 15% 0%, rgba(124,58,237,.25), transparent 60%),
                radial-gradient(900px 500px at 90% 10%, rgba(34,197,94,.18), transparent 55%),
                #0b1020;
    color: rgba(255,255,255,.92);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji",
      "Segoe UI Emoji";
  }

  /* Hide Streamlit chrome */
  header[data-testid="stHeader"] { background: transparent; }
  div[data-testid="stToolbar"] { visibility: hidden; height: 0; }
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }

  /* Header */
  .mcabap-header {
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 18px;
    padding: 14px 16px;
    background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.03));
    backdrop-filter: blur(10px);
    margin-bottom: 10px;
    position: sticky;
    top: 0.25rem;
    z-index: 5;
  }
  .mcabap-title {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: .2px;
    margin: 0;
  }
  .mcabap-subtitle {
    margin: 6px 0 0 0;
    color: rgba(255,255,255,.68);
    font-size: 13px;
  }

  .mcabap-topbar {
    margin-top: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
  }

  .mcabap-search {
    width: min(560px, 100%);
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(255,255,255,.06);
    border-radius: 14px;
    padding: 10px 12px;
    color: rgba(255,255,255,.92);
    outline: none;
  }
  .mcabap-search::placeholder { color: rgba(255,255,255,.55); }

  .mcabap-kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 12px 0 10px 0;
  }
  @media (max-width: 1100px) { .mcabap-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 600px) { .mcabap-kpis { grid-template-columns: 1fr; } }

  .mcabap-kpi {
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 16px;
    padding: 12px 12px;
    background: rgba(255,255,255,.05);
  }
  .mcabap-kpi-label { color: rgba(255,255,255,.62); font-size: 12px; }
  .mcabap-kpi-value { font-size: 20px; font-weight: 800; margin-top: 6px; letter-spacing: .2px; }
  .mcabap-kpi-sub { color: rgba(255,255,255,.60); font-size: 12px; margin-top: 4px; }

  /* Cards */
  .mcabap-card {
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 16px;
    padding: 12px 12px;
    background: rgba(255,255,255,.05);
    margin-bottom: 10px;
  }
  .mcabap-row {
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 14px;
    padding: 12px 12px;
    background: linear-gradient(180deg, rgba(0,0,0,.20), rgba(0,0,0,.12));
    margin-bottom: 10px;
    transition: transform .08s ease, border-color .08s ease, background .08s ease;
  }
  .mcabap-row:hover {
    transform: translateY(-1px);
    border-color: rgba(124,58,237,.35);
    background: linear-gradient(180deg, rgba(124,58,237,.10), rgba(0,0,0,.12));
  }
  .mcabap-row-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .mcabap-from {
    font-weight: 700;
    color: rgba(255,255,255,.92);
  }
  .mcabap-time {
    color: rgba(255,255,255,.62);
    font-size: 12px;
    white-space: nowrap;
  }
  .mcabap-text {
    margin-top: 8px;
    color: rgba(255,255,255,.84);
    line-height: 1.35;
  }

  /* Channel pill */
  .mcabap-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,.16);
    background: rgba(255,255,255,.06);
    color: rgba(255,255,255,.86);
    font-weight: 650;
  }
  .mcabap-pill.whatsapp { border-color: rgba(34,197,94,.55); background: rgba(34,197,94,.12); }
  .mcabap-pill.instagram { border-color: rgba(236,72,153,.55); background: rgba(236,72,153,.10); }
  .mcabap-pill.facebook { border-color: rgba(59,130,246,.55); background: rgba(59,130,246,.10); }
  .mcabap-pill.linkedin { border-color: rgba(14,165,233,.55); background: rgba(14,165,233,.10); }
  .mcabap-pill.webchat { border-color: rgba(124,58,237,.55); background: rgba(124,58,237,.12); }
  .mcabap-pill.voice { border-color: rgba(245,158,11,.55); background: rgba(245,158,11,.10); }
  .mcabap-pill.generic { border-color: rgba(255,255,255,.20); background: rgba(255,255,255,.06); }

  /* Sidebar polish */
  section[data-testid="stSidebar"] > div {
    background: rgba(255,255,255,.04);
    border-right: 1px solid rgba(255,255,255,.10);
  }

  /* Reduce top padding a bit */
  .block-container { padding-top: 1.0rem; max-width: 1200px; }

  /* Streamlit inputs */
  div[data-baseweb="input"] input, textarea, select {
    border-radius: 14px !important;
  }

</style>
        """,
        unsafe_allow_html=True,
    )


def _api_get_json(url: str, timeout_s: float = 5.0) -> Dict[str, Any]:
    res = _session.get(url, timeout=timeout_s)
    res.raise_for_status()
    return res.json()


def _api_post_json(url: str, payload: Dict[str, Any], timeout_s: float = 8.0) -> Dict[str, Any]:
    res = _session.post(url, json=payload, timeout=timeout_s)
    res.raise_for_status()
    return res.json()


def fetch_inbox(api_base: str) -> List[InboxItem]:
    data = _api_get_json(f"{api_base}/v1/inbox")
    items = data.get("items", []) or []
    parsed: List[InboxItem] = []
    for it in items:
        parsed.append(
            InboxItem(
                id=str(it.get("id", "")),
                channel=str(it.get("channel", "")),
                receivedAt=str(it.get("receivedAt", "")),
                from_=str(it.get("from", "")),
                name=(it.get("name") if it.get("name") is not None else None),
                text=(it.get("text") if it.get("text") is not None else None),
            )
        )
    return parsed


def send_test_enquiry(api_base: str, channel: str, from_value: str, name: str, text: str) -> Dict[str, Any]:
    return _api_post_json(
        f"{api_base}/v1/webhooks/{channel}/inbound",
        {"from": from_value, "name": name, "text": text},
    )


def fetch_rules(api_base: str) -> List[Dict[str, Any]]:
    data = _api_get_json(f"{api_base}/v1/rules")
    return data.get("rules", []) or []


def create_rule(api_base: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _api_post_json(f"{api_base}/v1/rules", payload)


def delete_rule(api_base: str, rule_id: str) -> Dict[str, Any]:
    res = _session.delete(f"{api_base}/v1/rules/{rule_id}", timeout=8.0)
    res.raise_for_status()
    return res.json()


def fetch_leads(api_base: str) -> List[Dict[str, Any]]:
    data = _api_get_json(f"{api_base}/v1/leads")
    return data.get("leads", []) or []


def create_lead(api_base: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _api_post_json(f"{api_base}/v1/leads", payload)


def fetch_appointments(api_base: str) -> List[Dict[str, Any]]:
    data = _api_get_json(f"{api_base}/v1/appointments")
    return data.get("appointments", []) or []


def create_appointment(api_base: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _api_post_json(f"{api_base}/v1/appointments", payload)


def cancel_appointment(api_base: str, appt_id: str) -> Dict[str, Any]:
    return _api_post_json(f"{api_base}/v1/appointments/{appt_id}/cancel", {})


st.set_page_config(page_title="Unified Inbox", layout="wide")

apply_ui_styles()

st.markdown(
    """
<div class="mcabap-header">
  <div class="mcabap-title">Unified Inbox</div>
  <div class="mcabap-subtitle">Multi Channel Auto Reply, Calls &amp; Business Automation Platform</div>
</div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    default_api = os.environ.get("API_BASE_URL")
    if not default_api:
        default_api = "http://127.0.0.1:8080"
    api_base = st.text_input("API base URL", value=default_api).rstrip("/")
    st.caption(f"API: `{api_base}`")
    auto_refresh = st.toggle("Auto-refresh", value=True)
    refresh_seconds = st.slider("Refresh interval (seconds)", 1, 10, 2)
    st.divider()
    st.subheader("Send test enquiry")
    channel = st.selectbox("Channel", options=["webchat", "whatsapp", "instagram", "facebook", "linkedin", "voice", "generic"])
    from_value = st.text_input("From", value="+91-9999999999")
    name = st.text_input("Name", value="Test Lead")
    text = st.text_area("Message", value="Hi, I want to know pricing", height=120)
    if st.button("Send", type="primary"):
        try:
            out = send_test_enquiry(api_base, channel, from_value, name, text)
            st.success(f"Accepted: {out.get('accepted')}  ID: {out.get('id')}")
        except requests.RequestException as e:
            st.error(f"Failed to send: {e}")

    st.divider()
    st.subheader("Filters")
    channel_filter = st.multiselect(
        "Channels",
        options=["webchat", "whatsapp", "instagram", "facebook", "linkedin", "voice", "generic"],
        default=["webchat", "whatsapp", "instagram", "facebook", "linkedin", "voice", "generic"],
    )
    query = st.text_input("Search", placeholder="Name, phone, message…")
    compact = st.toggle("Compact list", value=False)


col1, col2 = st.columns([3, 1], vertical_alignment="top")
with col2:
    if st.button("Refresh now"):
        st.rerun()
    st.write("")
    st.write("API health:")
    try:
        health = _api_get_json(f"{api_base}/health")
        st.code(health, language="json")
    except requests.RequestException as e:
        st.error(f"API not reachable: {e}")

with col1:
    try:
        items = fetch_inbox(api_base)
    except requests.RequestException as e:
        st.error(f"Failed to load inbox: {e}")
        items = []

    total = len(items)
    by_channel: Dict[str, int] = {}
    for it in items:
        by_channel[it.channel] = by_channel.get(it.channel, 0) + 1

    st.markdown(
        f"""
<div class="mcabap-kpis">
  <div class="mcabap-kpi">
    <div class="mcabap-kpi-label">Total enquiries</div>
    <div class="mcabap-kpi-value">{total}</div>
    <div class="mcabap-kpi-sub">In-memory (resets on API restart)</div>
  </div>
  <div class="mcabap-kpi">
    <div class="mcabap-kpi-label">Top channel</div>
    <div class="mcabap-kpi-value">{(max(by_channel, key=by_channel.get) if by_channel else "—")}</div>
    <div class="mcabap-kpi-sub">{(max(by_channel.values()) if by_channel else 0)} message(s)</div>
  </div>
  <div class="mcabap-kpi">
    <div class="mcabap-kpi-label">Auto-refresh</div>
    <div class="mcabap-kpi-value">{("On" if auto_refresh else "Off")}</div>
    <div class="mcabap-kpi-sub">Every {refresh_seconds}s</div>
  </div>
  <div class="mcabap-kpi">
    <div class="mcabap-kpi-label">API base</div>
    <div class="mcabap-kpi-value">:8080</div>
    <div class="mcabap-kpi-sub">{api_base}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    tab_inbox, tab_analytics, tab_rules, tab_leads, tab_appts = st.tabs(
        ["Inbox", "Analytics", "Auto-replies", "Leads", "Appointments"]
    )

    with tab_analytics:
        if items:
            st.markdown('<div class="mcabap-card">', unsafe_allow_html=True)
            st.subheader("Channel distribution")
            st.bar_chart(by_channel)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No data yet.")

    with tab_inbox:
        # Apply filters
        filtered = [it for it in items if it.channel in set(channel_filter)]
        if query.strip():
            q = query.strip().lower()
            def _haystack(it: InboxItem) -> str:
                return " ".join(
                    [
                        it.channel,
                        it.receivedAt,
                        it.from_,
                        it.name or "",
                        it.text or "",
                    ]
                ).lower()
            filtered = [it for it in filtered if q in _haystack(it)]

        st.markdown(
            f"""
<div class="mcabap-topbar">
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
    <div style="font-weight:800;font-size:18px;">Inbox</div>
    <div style="color:rgba(255,255,255,.62);font-size:12px;">Showing {len(filtered)} of {len(items)}</div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        if not filtered:
            st.info("No items match your filters. Use the sidebar to send a test enquiry.")
        else:
            st.markdown('<div class="mcabap-card">', unsafe_allow_html=True)
            for it in filtered:
                from_label = f"{it.name} ({it.from_})" if it.name else it.from_
                text_label = (it.text or "(no text)").replace("<", "&lt;").replace(">", "&gt;")
                if compact:
                    st.markdown(
                        f"""
<div class="mcabap-row">
  <div class="mcabap-row-top">
    <div style="display:flex;align-items:center;gap:10px;">
      <span class="mcabap-pill {it.channel}">{it.channel}</span>
      <span class="mcabap-from">{from_label}</span>
    </div>
    <span class="mcabap-time" title="{it.receivedAt}">{it.receivedAt}</span>
  </div>
</div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
<div class="mcabap-row">
  <div class="mcabap-row-top">
    <div style="display:flex;align-items:center;gap:10px;">
      <span class="mcabap-pill {it.channel}">{it.channel}</span>
      <span class="mcabap-from">{from_label}</span>
    </div>
    <span class="mcabap-time" title="{it.receivedAt}">{it.receivedAt}</span>
  </div>
  <div class="mcabap-text">{text_label}</div>
</div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_rules:
        st.subheader("Auto-reply rules")
        try:
            rule_items = fetch_rules(api_base)
        except requests.RequestException as e:
            st.error(f"Failed to load rules: {e}")
            rule_items = []

        with st.expander("Create new rule", expanded=True):
            r_name = st.text_input("Rule name", value="New rule", key="rule_name")
            r_enabled = st.checkbox("Enabled", value=True, key="rule_enabled")
            r_channel = st.selectbox(
                "Channel (optional)",
                options=["", "webchat", "whatsapp", "instagram", "facebook", "linkedin", "voice", "generic"],
                key="rule_channel",
            )
            r_contains = st.text_input("Contains keyword (optional)", value="pricing", key="rule_contains")
            r_reply = st.text_area(
                "Reply text",
                value="Thanks! Please share your business name and a good time to call.",
                height=90,
                key="rule_reply",
            )
            if st.button("Create rule", type="primary", key="rule_create"):
                try:
                    payload: Dict[str, Any] = {"name": r_name, "enabled": r_enabled, "replyText": r_reply}
                    if r_channel.strip():
                        payload["channel"] = r_channel.strip()
                    if r_contains.strip():
                        payload["contains"] = r_contains.strip()
                    create_rule(api_base, payload)
                    st.success("Rule created.")
                    st.rerun()
                except requests.RequestException as e:
                    st.error(f"Create failed: {e}")

        if not rule_items:
            st.info("No rules yet.")
        else:
            for r in rule_items:
                ch = r.get("channel") or "any"
                contains = r.get("contains") or "—"
                enabled = "enabled" if r.get("enabled") else "disabled"
                st.markdown(
                    f"""
<div class="mcabap-row">
  <div class="mcabap-row-top">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span class="mcabap-pill {(r.get('channel') or 'generic')}">{ch}</span>
      <span class="mcabap-from">{(r.get("name") or "")}</span>
      <span style="color:rgba(255,255,255,.62);font-size:12px;">contains: <code>{contains}</code></span>
      <span style="color:rgba(255,255,255,.62);font-size:12px;">status: <code>{enabled}</code></span>
    </div>
    <span class="mcabap-time" title="{(r.get("createdAt") or "")}">{(r.get("createdAt") or "")}</span>
  </div>
  <div class="mcabap-text">{str(r.get("replyText") or "").replace("<","&lt;").replace(">","&gt;")}</div>
</div>
                    """,
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns([1, 3])
                with c1:
                    if st.button("Delete", key=f"rule_del_{r.get('id')}"):
                        try:
                            delete_rule(api_base, str(r.get("id")))
                            st.success("Deleted.")
                            st.rerun()
                        except requests.RequestException as e:
                            st.error(f"Delete failed: {e}")
                with c2:
                    st.caption(f"Rule id: {r.get('id')}")

    with tab_leads:
        st.subheader("Leads")
        with st.expander("Add lead", expanded=True):
            l_name = st.text_input("Lead name", key="lead_name")
            l_phone = st.text_input("Phone", key="lead_phone")
            l_email = st.text_input("Email", key="lead_email")
            l_source = st.selectbox(
                "Source channel",
                options=["", "webchat", "whatsapp", "instagram", "facebook", "linkedin", "voice", "generic"],
                key="lead_source",
            )
            l_notes = st.text_area("Notes", key="lead_notes", height=90)
            if st.button("Create lead", type="primary", key="lead_create"):
                try:
                    payload: Dict[str, Any] = {}
                    if l_name.strip():
                        payload["name"] = l_name.strip()
                    if l_phone.strip():
                        payload["phone"] = l_phone.strip()
                    if l_email.strip():
                        payload["email"] = l_email.strip()
                    if l_source.strip():
                        payload["sourceChannel"] = l_source.strip()
                    if l_notes.strip():
                        payload["notes"] = l_notes.strip()
                    create_lead(api_base, payload)
                    st.success("Lead created.")
                    st.rerun()
                except requests.RequestException as e:
                    st.error(f"Create failed: {e}")

        try:
            lead_items = fetch_leads(api_base)
        except requests.RequestException as e:
            st.error(f"Failed to load leads: {e}")
            lead_items = []
        if not lead_items:
            st.info("No leads yet.")
        else:
            st.dataframe(lead_items, use_container_width=True, hide_index=True)

    with tab_appts:
        st.subheader("Appointments")
        with st.expander("Book appointment", expanded=True):
            a_name = st.text_input("Name", key="appt_name")
            a_phone = st.text_input("Phone", key="appt_phone")
            a_email = st.text_input("Email", key="appt_email")
            a_start = st.text_input("Start time (ISO)", value="2026-05-26T19:30:00", key="appt_start")
            a_reason = st.text_area("Reason", value="Intro call", height=70, key="appt_reason")
            if st.button("Book", type="primary", key="appt_book"):
                try:
                    payload: Dict[str, Any] = {"startAt": a_start}
                    if a_name.strip():
                        payload["name"] = a_name.strip()
                    if a_phone.strip():
                        payload["phone"] = a_phone.strip()
                    if a_email.strip():
                        payload["email"] = a_email.strip()
                    if a_reason.strip():
                        payload["reason"] = a_reason.strip()
                    create_appointment(api_base, payload)
                    st.success("Booked.")
                    st.rerun()
                except requests.RequestException as e:
                    st.error(f"Book failed: {e}")

        try:
            appt_items = fetch_appointments(api_base)
        except requests.RequestException as e:
            st.error(f"Failed to load appointments: {e}")
            appt_items = []
        if not appt_items:
            st.info("No appointments yet.")
        else:
            for a in appt_items:
                st.markdown(
                    f"""
<div class="mcabap-row">
  <div class="mcabap-row-top">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span class="mcabap-pill generic">{a.get("status","")}</span>
      <span class="mcabap-from">{(a.get("name") or "Unknown")}</span>
      <span style="color:rgba(255,255,255,.62);font-size:12px;"><code>{a.get("startAt","")}</code></span>
    </div>
    <span class="mcabap-time" title="{(a.get("createdAt") or "")}">{(a.get("createdAt") or "")}</span>
  </div>
  <div class="mcabap-text">{str(a.get("reason") or "").replace("<","&lt;").replace(">","&gt;")}</div>
</div>
                    """,
                    unsafe_allow_html=True,
                )
                if a.get("status") != "cancelled":
                    if st.button("Cancel", key=f"appt_cancel_{a.get('id')}"):
                        try:
                            cancel_appointment(api_base, str(a.get("id")))
                            st.success("Cancelled.")
                            st.rerun()
                        except requests.RequestException as e:
                            st.error(f"Cancel failed: {e}")

if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()
