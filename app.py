import streamlit as st
import requests
import types
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter

st.set_page_config(page_title="YouTube → SRT via Webshare")
st.title("Fetch Auto-CC via Webshare and Send to Make")

# ─── STEP 1: Webshare credentials ───
#
# Copy these four values *exactly* from your Webshare dashboard’s Endpoints section:
#   • proxy_ip      = the actual numeric IP (e.g. “207.244.217.165”)
#   • proxy_port    = the port (e.g. 6712)
#   • proxy_user    = your Webshare username for that endpoint (e.g. “qjmegaso”)
#   • proxy_pass    = your Webshare password for that endpoint (e.g. “4bscke4bszee”)
#
# (Do not use “proxy.webshare.io” here—use the concrete IP that Webshare shows as “Proxy Address.”)

proxy_ip   = "207.244.217.165"
proxy_port = 6712
proxy_user = "qjmegaso"
proxy_pass = "4bscke4bszee"

# Build the proxy URL in the form "http://user:password@IP:PORT"
# Note: We use the "http://" scheme even for HTTPS requests—requests will
# automatically tunnel HTTPS through this HTTP proxy.
proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"

# Create the `proxies` dict that requests (and youtube_transcript_api) expect:
proxies = {
    "http":  proxy_url,
    "https": proxy_url
}
# ───────────────────────────────────────

# Replace this with your actual Make webhook URL:
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/9jk9doqnef2cubutr9tqn1uprylnf162"

video_input = st.text_input(
    "Enter a YouTube video URL or just the ID:",
    placeholder="e.g. dQw4w9WgXcQ"
)

if st.button("Fetch via proxy and send to Make"):
    # │ STEP 2: Extract the video_id from URL or bare ID
    raw = video_input.strip()
    if raw.lower().startswith("http"):
        if "v=" in raw:
            video_id = raw.split("v=")[1].split("&")[0]
        elif "youtu.be/" in raw:
            video_id = raw.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Couldn’t parse the URL. Paste
