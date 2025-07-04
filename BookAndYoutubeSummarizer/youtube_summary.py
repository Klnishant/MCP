import os
from dotenv import load_dotenv
from euriai import EuriaiClient
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

load_dotenv()

api_key = os.getenv("EURI_API_KEY")
client = EuriaiClient(api_key=api_key, model="gpt-4.1-nano")

def extract_video_id(youtube_url: str):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
    if not match:
        raise ValueError("❌ Invalid YouTube URL format.")
    return match.group(1)

def  summarize_youtube_video(url: str):
    try:
        video_id = extract_video_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        clipped_text = transcript[:6000]

        summary_prompt = f"""
You are an AI content expert. Watch this YouTube video transcript and generate the following:
1. Timestamped and formatted summary of the video (with key sections and timestamps).
2. 5 SEO-friendly YouTube title suggestions (separated by new lines).
3. Comma-separated video tags for SEO.
4. A short thumbnail title for this video.

Transcript:
{clipped_text}
"""

        response = client.generate_completion(
            prompt=summary_prompt,
            temperature=0.6,

        )

        return {
            "video_id": video_id,
            "video_url": url,
            "response": response
        }
    except Exception as e:
        return {"error": str(e)}