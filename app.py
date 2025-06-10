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

# --------------------------------------------------------------------
# Below is the Flask version of the app.
# To run the Flask app, launch this file with an argument "flask":
#   python app.py flask
# --------------------------------------------------------------------

def run_flask():
    import os
    from flask import Flask, request, render_template_string, send_file
    # from pytube import YouTube is already imported above
    from openai import OpenAI  # Ensure you have the OpenAI library installed
    # Ensure you have the pytube library installed  
    flask_app = Flask(__name__)

    HTML_FORM = """
    <!doctype html>
    <title>YouTube Subtitle Extractor</title>
    <h2>Enter YouTube Video Link</h2>
    <form method=post>
        <input type=text name=yt_url style="width:400px">
        <input type=submit value=Download>
    </form>
    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}
    """

    @flask_app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            yt_url = request.form.get('yt_url', '').strip()
            if not yt_url:
                return render_template_string(HTML_FORM, error="Please enter a YouTube URL.")
            try:
                yt = YouTube(yt_url)
                caption = yt.captions.get_by_language_code('en')
                if not caption:
                    return render_template_string(HTML_FORM, error="No English auto-generated subtitles found.")
                srt_captions = caption.generate_srt_captions()
                filename = "subtitles.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_captions)
                return send_file(filename, as_attachment=True)
            except Exception as e:
                return render_template_string(HTML_FORM, error=f"Error: {str(e)}")
        return render_template_string(HTML_FORM)

    flask_app.run(debug=True)

if __name__ == '__main__':
    import sys
    # If "flask" is passed as a command-line argument, run the Flask app.
    if len(sys.argv) > 1 and sys.argv[1] == 'flask':
        run_flask()
