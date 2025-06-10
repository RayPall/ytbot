import streamlit as st
from pytube import YouTube
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

st.title("YouTube Subtitle Extractor")

def clean_youtube_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    # Only keep the video id parameter
    if "v" in query:
        cleaned_query = urlencode({"v": query["v"][0]})
        cleaned_parsed = parsed._replace(query=cleaned_query)
        return urlunparse(cleaned_parsed)
    return url

yt_url = st.text_input("Enter YouTube Video Link:")

if st.button("Download"):
    if not yt_url:
        st.error("Please enter a YouTube URL.")
    elif not (yt_url.startswith("https://") or yt_url.startswith("http://")):
        st.error("Invalid URL. Please enter a valid YouTube link.")
    else:
        try:
            cleaned_url = clean_youtube_url(yt_url)
            yt = YouTube(cleaned_url)
            caption = yt.captions.get_by_language_code('en')
            if not caption:
                st.error("No English auto-generated subtitles found.")
            else:
                srt_captions = caption.generate_srt_captions()
                filename = "subtitles.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_captions)
                with open(filename, "rb") as f:
                    st.download_button("Download Subtitles", f, file_name=filename, mime="text/plain")
        except Exception as e:
            st.error(f"Error: {str(e)}")
