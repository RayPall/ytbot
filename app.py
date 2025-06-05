import streamlit as st
import requests
import types
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from youtube_transcript_api.proxies import WebshareProxyConfig

st.set_page_config(page_title="YouTube → SRT via Webshare")
st.title("Fetch Auto-CC via Webshare and Send to Make")

# ──────────── WEBSHARE PROXY CONFIG ────────────
# Copy these values exactly from your Webshare Dashboard → Endpoints
proxy_host     = "proxy.webshare.io"
proxy_port     = 6712
proxy_username = "qjmegaso"
proxy_password = "4bscke4bszee"

# Build the WebshareProxyConfig for youtube_transcript_api
proxy_config = WebshareProxyConfig(
    proxy_host=proxy_host,
    proxy_port=proxy_port,
    proxy_username=proxy_username,
    proxy_password=proxy_password
)
# ────────────────────────────────────────────────

# Replace this with your actual Make webhook URL:
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/9jk9doqnef2cubutr9tqn1uprylnf162"

video_input = st.text_input(
    "Enter a YouTube video URL or just the ID:",
    placeholder="e.g. dQw4w9WgXcQ"
)

if st.button("Fetch via proxy and send to Make"):
    # ─── 1) Extract video_id from URL or bare ID ───
    raw = video_input.strip()
    if raw.startswith("http"):
        if "v=" in raw:
            video_id = raw.split("v=")[1].split("&")[0]
        elif "youtu.be/" in raw:
            video_id = raw.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Couldn’t parse the URL. Paste the watch?v= link or just the ID.")
            st.stop()
    else:
        video_id = raw

    # ─── 2) Fetch transcript via Webshare proxy ───
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=["en", "cs"],
            proxies=proxy_config.get_requests_proxies()
        )
    except Exception as e:
        st.error(f"Could not fetch transcript via proxy:\n{e}")
        st.stop()

    # ─── 3) If empty, no captions exist ───
    if not transcript_list:
        st.error("No transcript was found for this video (empty list).")
        st.stop()

    # ─── 4) Convert each dict into an object with .start, .duration, .text ───
    formatted_items = []
    for chunk in transcript_list:
        # chunk is a dict: {'text': ..., 'start': ..., 'duration': ...}
        item = types.SimpleNamespace(
            text=chunk["text"],
            start=chunk["start"],
            duration=chunk["duration"]
        )
        formatted_items.append(item)

    # ─── 5) Format those objects into a single SRT string ───
    formatter = SRTFormatter()
    try:
        srt_text = formatter.format_transcript(formatted_items)
    except Exception as e:
        st.error(f"Error formatting transcript into SRT:\n{e}")
        st.write("DEBUG transcript_list:", transcript_list)
        st.stop()

    # ─── 6) Preview the first 500 characters in Streamlit ───
    st.success("Transcript fetched and formatted (via proxy)! Preview:")
    st.text_area("SRT Preview", value=srt_text[:500] + "\n…", height=300)

    # ─── 7) POST the SRT text to your Make webhook ───
    payload = {
        "video_id": video_id,
        "srt_contents": srt_text
    }
    try:
        resp = requests.post(MAKE_WEBHOOK_URL, json=payload)
        if resp.status_code == 200:
            st.success("✅ Sent to Make successfully!")
        else:
            st.error(f"Make webhook returned HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"Failed to POST to Make webhook: {e}")
