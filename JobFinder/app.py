import streamlit as st
import fitz
import os
from euriai import EuriaiClient
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

euriai_client = EuriaiClient(
    api_key=os.getenv("EURI_API_KEY"),
    model="gpt-4.1-nano"
)

apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))


def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_euriai(prompt, max_tokens=500):
    response = euriai_client.generate_completion(prompt=prompt, temperature=0.5, max_tokens=max_tokens)
    if isinstance(response, dict) and 'choices' in response:
        return response['choices'][0]['message']['content']
    return response

def fetch_linkedin_jobs(search_query, location="India", rows=60):
    run_input = {
        "title": search_query,
        "location": location,
        "rows": rows,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        }
    }
    run = apify_client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs

def fetch_naukri_jobs(search_query, max_jobs=60):
    run_input = {
        "keyword": search_query,
        "maxJobs": 60,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
    }
    run = apify_client.actor("alpcnRV9YI9lYVPWk").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs

st.set_page_config(page_title="AI Resume Analyzer + Job Finder", layout="wide")
st.title("📄 AI Resume Analyzer & Career Growth Advisor")
st.markdown("Upload your Resume and get career insights + live job recommendations from LinkedIn & Naukri! 🚀")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("📚 Extracting text from resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    # Call Euriai for different tasks
    with st.spinner("✍️ Summarizing Resume..."):
        summarize_text = ask_euriai(f"Summarize this resume highlighting skills, education, and experience:\n\n{resume_text}", max_tokens=500)

    with st.spinner("🔎 Finding Skill Gaps..."):
        gap = ask_euriai(f"Analyze this resume and highlight missing skills, certifications, or experiences needed for better job opportunities:\n\n{resume_text}", max_tokens=400)

    with st.spinner("🚀 Creating Future Roadmap..."):
        roadmap = ask_euriai(f"Based on this resume, suggest a future roadmap to improve this person's career prospects (skills to learn, certifications needed, industry exposure):\n\n{resume_text}", max_tokens=400)

    # Display nicely formatted results
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{summarize_text}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{gap}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🚀 Future Roadmap")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{roadmap}</div>", unsafe_allow_html=True)

    st.success("✅ Analysis Completed Successfully!")

    # Button to Fetch Jobs
    st.markdown("---")
    st.header("🚀 Live Job Recommendations")
    with st.spinner("🚀 Fetching Jobs from LinkedIn and Naukri..."):
        linkedin_jobs = fetch_linkedin_jobs(search_query=roadmap, location="India", rows=60)
        naukri_jobs = fetch_naukri_jobs(search_query=roadmap, max_jobs=60)
    
    st.markdown("---")
    st.header("💼 Top LinkedIn Jobs (INDIA)")

    if linkedin_jobs:
        for job in linkedin_jobs:
            st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
            st.markdown(f"- 📍 {job.get('location')}")
            st.markdown(f"- 🔗 [View Job]({job.get('link')})")
            st.markdown("---")
    else:
        st.warning("No LinkedIn jobs found.")

    st.markdown("---")
    st.header("💼 Top Naukri Jobs (INDIA)")

    if naukri_jobs:
        for job in naukri_jobs:
            st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
            st.markdown(f"- 📍 {job.get('location')}")
            st.markdown(f"- 🔗 [View Job]({job.get('url')})")
            st.markdown("---")
    else:
        st.warning("No Naukri jobs found.")