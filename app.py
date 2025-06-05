from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_transcript_api.formatters import SRTFormatter
import types

# 1) Copy these four values straight from your Webshare Dashboard:
proxy_host     = "proxy.webshare.io"
proxy_port     = 6712
proxy_username = "qjmegaso"
proxy_password = "4bscke4bszee"

# 2) Create a WebshareProxyConfig object:
config = WebshareProxyConfig(
    proxy_host=proxy_host,
    proxy_port=proxy_port,
    proxy_username=proxy_username,
    proxy_password=proxy_password
)

# 3) When you call get_transcript, pass config.get_requests_proxies():
video_id = "E61n0RKttQA"
transcript_list = YouTubeTranscriptApi.get_transcript(
    video_id,
    languages=["en"],  # or ['en','cs'], etc.
    proxies=config.get_requests_proxies()
)

# 4) Convert each dict into a minimal object so SRTFormatter can see .start/.duration/.text
formatted_items = [
    types.SimpleNamespace(text=d["text"], start=d["start"], duration=d["duration"])
    for d in transcript_list
]

# 5) Format to SRT
formatter = SRTFormatter()
srt_text = formatter.format_transcript(formatted_items)
print(srt_text)
