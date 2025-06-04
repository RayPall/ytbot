import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import requests

st.set_page_config(page_title="YouTube → Make Transcript Uploader")

st.title("YouTube Transcripts → Make")

video_input = st.text_input(
    "Enter YouTube video ID or URL:",
    placeholder="e.g. dQw4w9WgXcQ"
)

if st.button("Fetch transcript and send to Make"):
    # Extract just the video ID (strip full URL if given)
    if "youtube.com" in video_input or "youtu.be" in video_input:
        # naive extraction: split on “v=” or “youtu.be/”
        if "v=" in video_input:
            video_id = video_input.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_input:
            video_id = video_input.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Unrecognized YouTube format")
            st.stop()
    else:
        video_id = video_input.strip()

    try:
        # 1) Fetch raw transcript (auto or manual, whichever exists)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en","cs"])
        # 2) Convert to SRT
        srt_formatter = SRTFormatter()
        srt_text = srt_formatter.format_transcript(transcript_list)
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        st.stop()

    st.success("Transcript fetched! Preview:")
    st.text_area("SRT Preview", value=srt_text[:500] + "\n…", height=200)

    # 3) POST the SRT to your Make webhook
    make_webhook_url = "https://hook.eu2.make.com/9jk9doqnef2cubutr9tqn1uprylnf162"  # ← paste your Custom Webhook URL here
    payload = {
        "video_id": video_id,
        "srt_contents": srt_text
    }
    # You can send as JSON or as multipart form-data; we’ll send JSON.
    resp = requests.post(make_webhook_url, json=payload)
    if resp.status_code == 200:
        st.success("Sent to Make successfully!")
        st.write("Make responded:", resp.text)
    else:
        st.error(f"Make webhook returned HTTP {resp.status_code}: {resp.text}")
