import streamlit as st
import requests
import types
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter

st.set_page_config(page_title="YouTube → SRT via Webshare")
st.title("Fetch Auto-CC via Webshare and Send to Make")

# ─── STEP 1: Webshare credentials ───
# Replace the following four values with your Webshare “Endpoints” row exactly:
proxy_ip   = "207.244.217.165"
proxy_port = 6712
proxy_user = "qjmegaso"
proxy_pass = "4bscke4bszee"

# Build a single proxy URL string:
proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
proxies = {
    "http":  proxy_url,
    "https": proxy_url
}
st.write("Debug: proxies dictionary = ", proxies)  # *** DEBUG ***

# ─── STEP 2: Your Make webhook (replace with your actual webhook URL) ───
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/9jk9doqnef2cubutr9tqn1uprylnf162"
st.write("Debug: Make webhook URL = ", MAKE_WEBHOOK_URL)  # *** DEBUG ***

video_input = st.text_input(
    "Enter a YouTube video URL or just the ID:",
    placeholder="e.g. dQw4w9WgXcQ"
)

# ─── STEP 3: When the button is pressed ───
if st.button("Fetch via proxy and send to Make"):
    st.write("✅ Button was pressed!")               # *** DEBUG ***
    st.write("Video input is:", video_input)         # *** DEBUG ***

    # 3.1) Extract video_id
    raw = video_input.strip()
    if raw.lower().startswith("http"):
        # If it’s a full URL, parse out the v= param or youtu.be/
        if "v=" in raw:
            video_id = raw.split("v=")[1].split("&")[0]
        elif "youtu.be/" in raw:
            video_id = raw.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Couldn’t parse the URL. Paste the watch?v= link or just the ID.")
            st.stop()
    else:
        video_id = raw
    st.write("Debug: Parsed video_id =", video_id)   # *** DEBUG ***

    # 3.2) Fetch transcript via proxy
    try:
        st.write("Debug: about to call get_transcript() via proxy...")  # *** DEBUG ***
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=["en", "cs"],
            proxies=proxies
        )
        st.write("Debug: get_transcript returned", transcript_list[:2], "...")  # *** DEBUG ***
    except Exception as e:
        st.error(f"Could not fetch transcript via proxy:\n{e}")
        st.stop()

    # 3.3) If empty list, bail
    if not transcript_list:
        st.error("No transcript was found for this video (empty list).")
        st.stop()

    # 3.4) Convert dicts → objects
    formatted_items = []
    for chunk in transcript_list:
        st.write("Debug: chunk =", chunk)          # *** DEBUG ***
        item = types.SimpleNamespace(
            text=chunk["text"],
            start=chunk["start"],
            duration=chunk["duration"]
        )
        formatted_items.append(item)
    st.write("Debug: formatted_items[0] =", formatted_items[0])  # *** DEBUG ***

    # 3.5) Format into SRT
    formatter = SRTFormatter()
    try:
        srt_text = formatter.format_transcript(formatted_items)
        st.write("Debug: srt_text[:200] =", srt_text[:200])  # *** DEBUG ***
    except Exception as e:
        st.error(f"Error formatting transcript into SRT:\n{e}")
        st.write("DEBUG transcript_list:", transcript_list)
        st.stop()

    # 3.6) Show a preview
    st.success("Transcript fetched and formatted (via Webshare proxy)! Preview:")
    st.text_area("SRT Preview", value=srt_text[:500] + "\n…", height=300)

    # 3.7) POST to Make
    payload = {
        "video_id": video_id,
        "srt_contents": srt_text
    }
    st.write("Debug: About to POST to Make with payload keys:", payload.keys())  # *** DEBUG ***
    try:
        resp = requests.post(MAKE_WEBHOOK_URL, json=payload)
        st.write("Debug: Make responded with status", resp.status_code)         # *** DEBUG ***
        if resp.status_code == 200:
            st.success("✅ Sent to Make successfully!")
        else:
            st.error(f"Make webhook returned HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"Failed to POST to Make webhook: {e}")
