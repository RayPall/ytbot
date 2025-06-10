import streamlit as st
import yt_dlp
import os

def download_captions(video_url):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=True)
            video_title = info['title']
            return video_title
        except Exception as e:
            st.error(f"Error downloading captions: {str(e)}")
            return None

def main():
    st.title("YouTube Caption Extractor")
    
    # Input for YouTube URL
    video_url = st.text_input("Enter YouTube Video URL:")
    
    if st.button("Extract Captions"):
        if video_url:
            with st.spinner("Extracting captions..."):
                video_title = download_captions(video_url)
                
                if video_title:
                    # Find the downloaded subtitle file
                    subtitle_file = None
                    for file in os.listdir():
                        if file.endswith('.vtt'):
                            subtitle_file = file
                            break
                    
                    if subtitle_file:
                        # Read and clean the subtitle file
                        with open(subtitle_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Save to a text file
                        output_file = f"{video_title}_captions.txt"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        # Clean up the VTT file
                        os.remove(subtitle_file)
                        
                        st.success(f"Captions extracted and saved to {output_file}")
                        
                        # Display the content
                        st.text_area("Extracted Captions:", content, height=300)
                    else:
                        st.error("No captions found for this video")
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main()
