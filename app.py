import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import requests
import types

st.set_page_config(page_title="YouTube → SRT Uploader")
st.title("Fetch Auto-CC & Push to Make")

video_input = st.text_input(
    "Enter a YouTube video URL or just the ID:",
    placeholder="e.g. dQw4w9WgXcQ"
)

if st.button("Fetch transcript and send to Make"):
    # 1) Extract video_id from URL or bare ID
    if "youtube.com" in video_input or "youtu.be" in video_input:
        if "v=" in video_input:
            video_id = video_input.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_input:
            video_id = video_input.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Couldn’t parse the URL. Paste the ID or a watch?v= URL.")
            st.stop()
    else:
        video_id = video_input.strip()

    # 2) Try to fetch the transcript (auto or manual)
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=["en", "cs"]  # try English first, then Czech
        )
    except Exception as e:
        st.error(f"Could not fetch transcript: {e}")
        st.stop()

    # 3) If empty, bail out
    if not transcript_list:
        st.error("No transcript was found for this video (empty list).")
        st.stop()

    # 4) Convert each dict into a SimpleNamespace so SRTFormatter can see .start/.duration/.text
    formatted_items = [
        types.SimpleNamespace(
            text=chunk["text"],
            start=chunk["start"],
            duration=chunk["duration"]
        )
        for chunk in transcript_list
    ]

    # 5) Now format to SRT
    formatter = SRTFormatter()
    try:
        srt_text = formatter.format_transcript(formatted_items)
    except Exception as e:
        st.error(f"Error while formatting SRT: {e}")
        st.write("DEBUG transcript_list:", transcript_list)
        st.stop()

    # 6) Show a preview in Streamlit
    st.success("Transcript fetched and formatted! Preview:")
    st.text_area("SRT preview (first 500 chars)", value=srt_text[:500] + "\n…", height=200)

    # 7) POST to your Make webhook
    make_webhook_url = "https://hook.integromat.com/abcd1234xyz"  # ← your webhook here
    payload = {"video_id": video_id, "srt_contents": srt_text}
    resp = requests.post(make_webhook_url, json=payload)

    if resp.status_code == 200:
        st.success("✅ Sent to Make successfully!")
    else:
        st.error(f"Make webhook returned HTTP {resp.status_code}: {resp.text}")
