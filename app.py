import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import requests

st.set_page_config(page_title="YouTube → SRT Uploader")

st.title("Fetch Auto-CC & Push to Make")

video_input = st.text_input(
    "Enter a YouTube video URL or just the ID:",
    placeholder="e.g. dQw4w9WgXcQ"
)

if st.button("Fetch transcript and send to Make"):
    # 1) Extract the video_id
    if "youtube.com" in video_input or "youtu.be" in video_input:
        # crude parsing of a URL
        if "v=" in video_input:
            video_id = video_input.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_input:
            video_id = video_input.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Couldn’t parse the URL. Just paste the ID or a watch?v= URL.")
            st.stop()
    else:
        video_id = video_input.strip()

    # 2) Use youtube-transcript-api to get auto/manual CC as a list of dicts
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en","cs"]  # try English first, fall back to Czech
        )
    except Exception as e:
        st.error(f"Could not fetch transcript: {e}")
        st.stop()

    # 3) Format that list into SRT text
    formatter = SRTFormatter()
    srt_text = formatter.format_transcript(transcript_list)

    st.success("Transcript fetched! Preview below:")
    st.text_area("SRT Preview (first 500 chars)", value=srt_text[:500] + "\n…", height=200)

    # 4) POST it to your Make webhook
    make_webhook_url = "https://hook.eu2.make.com/9jk9doqnef2cubutr9tqn1uprylnf162"  # replace with your actual webhook
    payload = {
        "video_id": video_id,
        "srt_contents": srt_text
    }
    resp = requests.post(make_webhook_url, json=payload)

    if resp.status_code == 200:
        st.success("✅ Sent to Make successfully!")
    else:
        st.error(f"Make webhook returned HTTP {resp.status_code}: {resp.text}")
