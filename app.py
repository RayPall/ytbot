import os
from flask import Flask, request, render_template_string, send_file
from pytube import YouTube

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
        app.run(debug=True)
        
