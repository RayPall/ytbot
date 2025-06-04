import streamlit as st
import requests

st.title("Trigger Make’s Timed-text→SRT flow")

video_input = st.text_input("YouTube video URL or ID:")
if st.button("Run Make scenario"):
    # extract ID (same logic as before)
    if "youtube.com" in video_input or "youtu.be" in video_input:
        if "v=" in video_input:
            video_id = video_input.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_input:
            video_id = video_input.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Unrecognized YouTube URL format")
            st.stop()
    else:
        video_id = video_input.strip()

    make_webhook_url = "https://hook.eu2.make.com/9jk9doqnef2cubutr9tqn1uprylnf162"  # your webhook URL
    payload = {"video_id": video_id}
    try:
        r = requests.post(make_webhook_url, json=payload)
        if r.status_code == 200:
            st.success("Make scenario triggered successfully!")
            st.text(r.text)  # Make usually returns a small JSON with “id” or a confirmation
        else:
            st.error(f"Make returned HTTP {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"Error calling Make webhook: {e}")
