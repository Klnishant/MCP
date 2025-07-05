import streamlit as st
import os
from euriai import EuriaiClient
from dotenv import load_dotenv

load_dotenv()

euri_client = EuriaiClient(
    api_key = os.getenv("EURI_API_KEY"),
    model = "gemini-2.0-flash"
)

euri_client1 = EuriaiClient(
    api_key = os.getenv("EURI_API_KEY"),
    model = "gpt-4.1-mini"
)

def fetch_news(query):
    """
    Fetch realtime latest news based on user query
    """
    prompt = f"""
You are a professional live news reporter with realtime access.
find and report the latest-real-world news updates about '{query}'.
keep it factual, current and professional.
summarize it arround 150-200 words.
start immediately with news content. No greetings.
If no recent news is available, say: "No recent updates found on [query]".
"""
    try:
        response = euri_client.generate_completion(
            prompt=prompt,
            temperature=0.4,
            max_tokens=400
        )

        if isinstance(response,dict):
            if 'content' in response:
                return response['content'].strip()
            elif 'choices' in response and isinstance(response['choices'],list):
                return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"❌ Error fetching news: {e}")
        return None
    
def generate_video_transcription(news_text):
    """
    Generate an engaging video script based on the news text.
    """
    prompt = f"""
You are a creative scriptwriter.
Turn this real-time news into an engaging short video script (YouTube Shorts or Instagram Reels).
Write in a natural, speaking style, with a hook at the beginning and a CTA at the end.
Keep it around 100–120 words:

{news_text}
"""
    try:
        response = euri_client1.generate_completion(
            prompt=prompt,
            temperature=0.6,
            max_tokens=300
        )

        if isinstance(response,dict):
            if 'content' in response:
                return response['content'].strip()
            elif 'choices' in response and isinstance(response['choices'],list):
                return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"❌ Error fetching news: {e}")
        return None
    
def main():
    st.set_page_config(page_title="AI News & Script Generator", page_icon="📰")
    st.title("📰 AI News & Video Script Generator")

    st.markdown(
        "Type any **topic, keyword, or phrase** and get the latest news about it!\n\n"
        "Then optionally create a **video script** out of that news 🚀"
    )

    query = st.text_input("🔎 Enter your topic:")

    if query:
        with st.spinner('Fetching the latest news...'):
            news = fetch_news(query)
        
        if news:
            st.success('✅ News fetched successfully!')
            st.subheader("📰 Latest News:")
            st.write(news)

            generate_script = st.radio(
                "🎬 Would you like to generate a video transcription?",
                ("No", "Yes"),
                index=0,
                horizontal=True
            )

            if generate_script == "Yes":
                with st.spinner('Generating video transcription...'):
                    script = generate_video_transcription(news)

                if script:
                    st.success("✅ Video transcription ready!")
                    st.subheader("🎥 Video Script:")
                    st.write(script)

                    # Download button
                    st.download_button(
                        label="📥 Download Script as TXT",
                        data=script,
                        file_name="video_script.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("⚠️ Could not generate transcription.")
        else:
            st.warning("⚠️ No valid news found. Please try a different topic.")

    st.markdown("---")
    st.caption("Made with ❤️ using EURI AI and Streamlit.")

if __name__ == "__main__":
    main()