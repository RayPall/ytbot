import streamlit as st
from pytube import YouTube

st.title("YouTube Subtitle Extractor")
st.header("Enter YouTube Video Link")

yt_url = st.text_input("YouTube URL")

if st.button("Download"):
    if not yt_url:
        st.error("Please enter a YouTube URL.")
    else:
        try:
            yt = YouTube(yt_url)
            caption = yt.captions.get_by_language_code('en')
            if not caption:
                st.error("No English auto-generated subtitles found.")
            else:
                srt_captions = caption.generate_srt_captions()
                filename = "subtitles.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_captions)
                with open(filename, "rb") as f:
                    st.download_button("Download Subtitles", f, filename=filename)
        except Exception as e:
            st.error(f"Error: {str(e)}")
