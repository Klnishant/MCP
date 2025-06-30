import streamlit as st
import time
import json
import requests
import os
import tempfile
import logging
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# HARDCODED API KEYS - DO NOT SHARE THIS FILE
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CX = os.environ.get("SEARCH_ENGINE_ID", "")

# initialize session state variables
if 'api_server_url' not in st.session_state:
    st.session_state['api_server_url'] = "http://localhost:8085"

# Always use our hardcoded keys - don't get them from session_state
st.session_state['groq_api_key'] = GROQ_API_KEY
st.session_state['google_api_key'] = GOOGLE_API_KEY
st.session_state['google_cx'] = GOOGLE_CX

# Function to call API tools
def call_api_tool(tool_name, data):
    """Call a tool on the API server with hardcoded API keys."""
    url = f"{st.session_state['api_server_url']}/tools/{tool_name}"
    
    # Create a copy of the data
    request_data = data.copy()
    
    # ALWAYS add API keys to EVERY request
    request_data["groq_api_key"] = GROQ_API_KEY
    request_data["google_api_key"] = GOOGLE_API_KEY
    request_data["search_engine_id"] = GOOGLE_CX
    
    try:
        response = requests.post(
            url, 
            json=request_data,
            headers={"Content-Type": "application/json"}, 
            timeout=60
        )
        
        if response.status_code != 200:
                error_message = f"Error {response.status_code} from server: {response.text}"
                
                st.error(error_message)
                return None
                    
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text
            
    except Exception as e:
        error_message = f"Error connecting to server: {str(e)}"
        
        st.error(error_message)
        return None

#set page confiq
st.set_page_config(
    page_title="Assignment Grader",
    page_icon="📝",
    layout="wide"
)

# Main title
st.title("📝 Assignment Grader")
st.markdown("Upload assignments and grade them automatically with AI")
st.info("This version has hardcoded API keys for debugging purposes. API keys are automatically included in all requests.")

# Sidebar configuration
st.sidebar.header("Server Configuration")
with st.sidebar.expander("Server Settings", expanded=True):
    # API server URL
    server_url = st.text_input("API Server URL", value=st.session_state['api_server_url'])
    
    # Save button
    if st.button("Save Server URL"):
        st.session_state['api_server_url'] = server_url
        st.success(f"✅ Server URL updated to {server_url}")

# Check server connection
with st.sidebar:
    st.write("---")
    st.subheader("Server Status")
    if st.button("Check Server Connection"):
        try:
            response = requests.get(f"{st.session_state['api_server_url']}/")
            if response.status_code == 200:
                st.success("✅ Server is online")
            else:
                st.error("❌ Server is offline")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Unable to connect to the server: {str(e)}")

#create tabs
tab1, tab2, tab3 = st.tabs(["Upload Assignment", "Grade Assignment", "Result"])

#Tab 1 upload assignment
with tab1:
    st.header("Upload Assignment")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])

    #save file temporarily
    if uploaded_file is not None:
        # Display file information
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.info(f"File: {uploaded_file.name} ({file_size:.1f} KB)")
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name
        
        st.session_state['file_path'] = file_path
        st.session_state['file_name'] = uploaded_file.name

        # Parse the document
        if st.button("Parse Document"):
            with st.spinner("Processing document..."):
                result = call_api_tool("parse_file", {"file_path": file_path})

                if result is None:
                    st.error("Failed to process document. Check server connection.")
                elif isinstance(result, str):
                    # If result is a string, it's either the document text or an error message
                    st.session_state['document_text'] = result
                    word_count = len(result.split())
                    st.success(f"Document processed successfully!")
                    st.info(f"Document contains {word_count} words.")

                    # Show a preview with word count
                    with st.expander("Document Preview"):
                        preview = result[:1000] + ("..." if len(result) > 1000 else "")
                        st.text_area("Preview", value=preview, height=300, disabled=True)

                    # If document is very long, show a warning
                    if word_count > 5000:
                        st.warning(f"Long document detected ({word_count} words). Processing might take longer.")

                else:
                    # If result is a dict, might be error information
                    st.session_state['document_text'] = str(result)
                    st.success(f"Document processed!")

                    # Show a preview
                    with st.expander("Document Preview"):
                        st.json(result)

# tab2 grad assignment
with tab2:
    st.header("Grading configuration")
    
    # Check if document is loaded
    if 'document_text' not in st.session_state:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        st.success(f"✅ Document loaded: {st.session_state.get('file_name', 'Unknown')}")
    
    # Rubric input
    st.subheader("Grading Rubric")
    
    # Default rubric templates
    rubric_templates = {
        "Default Academic": """Content (40%): The assignment should demonstrate a thorough understanding of the topic.
Structure (20%): The assignment should be well-organized with a clear introduction, body, and conclusion.
Analysis (30%): The assignment should include critical analysis backed by evidence.
Grammar & Style (10%): The assignment should be free of grammatical errors and use appropriate academic language.""",
        "Technical Report": """Accuracy (35%): Technical details should be accurate and well-explained.
Methodology (25%): The methodology should be appropriate and clearly described.
Results (25%): Results should be presented clearly with appropriate visualizations.
Conclusions (15%): Conclusions should be supported by the data and analysis.""",
        "Creative Writing": """Originality (30%): The work should show creative and original thinking.
Language & Style (20%): The language should be engaging, varied, and appropriate.
Structure (20%): The narrative structure should be effective and appropriate.
Character/Scene Development (30%): Characters or scenes should be well-developed.""",
        "Custom": ""
    }

    # Template selector
    template_choice = st.selectbox(
        "Select a template or create your own:", 
        ["Default Academic", "Technical Report", "Creative Writing", "Custom"]
    )
    
    # Get default value based on selection
    default_value = rubric_templates.get(template_choice, "") if template_choice != "Custom" else ""
    
    # Rubric text area
    rubric = st.text_area(
        "Enter your grading rubric here:",
        height=200,
        help="Specify the criteria on which the assignment should be graded",
        value=default_value
    )

    #paligarism check and grading options
    col1, col2 = st.columns(2)
    with col1:
        check_plagiarism = st.checkbox("Check for plagiarism", value=True)
        
        if check_plagiarism:
            similarity_threshold = st.slider(
                "Similarity threshold (%)", 
                min_value=1, 
                max_value=90, 
                value=40,
                help="Select the similarity threshold for plagiarism detection (1-90%)"
            )
            
    with col2:
        grad_model = st.selectbox(
            "Select a grading model",
            ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
            help="Select the model to use for grading"
        )

        #grad assignment
        if st.button("Grade Assignment"):
            progress_bar = st.progress(0)
            progress_bar.progress(20)

            # Call API tool
            result = call_api_tool("grade_assignment", {
                "text": st.session_state['document_text'],
                "rubric": rubric,
                "check_plagiarism": check_plagiarism,
                "similarity_threshold": similarity_threshold if 'similarity_threshold' in locals() else 40,
                "grade_model": grad_model if 'grade_model' in locals() else "llama-3.1-8b-instant"
            })

            progress_bar.progress(50)

            if result is None:
                st.error("Failed to grade assignment. Check server connection.")
            elif isinstance(result, str):
                st.session_state['grade_results'] = result
                st.success("✅ Grading completed!")
                st.balloons()
            else:
                st.session_state['grade_results'] = str(result)
                st.success("✅ Grading completed!")
                st.balloons()

# Tab 3: Results
with tab3:
    st.header("Grading Results")
    
    if all(k in st.session_state for k in ['file_name']):
        st.subheader(f"Results for: {st.session_state['file_name']}")
        
        # Create columns for grade display
        col1, col2 = st.columns([1, 3])
        
        # Display grade in the first column
        with col1:
            if 'grade_results' in st.session_state and st.session_state['grade_results'] is not None:
                if isinstance(st.session_state['grade_results'], dict):
                    grade = st.session_state['grade_results'].get('grade', 'Not available')
                else:
                    # If it's not a dict, just display the raw result
                    grade = str(st.session_state['grade_results'])
                
                # Display grade in large format
                st.markdown(f"## Grade: {grade}")
                
                # Generate a visual indicator based on the grade
                try:
                    # Try to convert to numeric format if it's a percentage or out of 100
                    if '%' in grade:
                        numeric_grade = float(grade.replace('%', ''))
                        st.progress(numeric_grade / 100)
                    elif '/' in grade:
                        parts = grade.split('/')
                        numeric_grade = float(parts[0]) / float(parts[1])
                        st.progress(numeric_grade)
                    elif grade.upper() in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']:
                        grade_values = {
                            'A+': 0.97, 'A': 0.94, 'A-': 0.90,
                            'B+': 0.87, 'B': 0.84, 'B-': 0.80,
                            'C+': 0.77, 'C': 0.74, 'C-': 0.70,
                            'D+': 0.67, 'D': 0.64, 'D-': 0.60,
                            'F': 0.50
                        }
                        numeric_grade = grade_values.get(grade.upper(), 0)
                        st.progress(numeric_grade)
                except:
                    # If we can't convert, just skip the progress bar
                    pass
            else:
                st.warning("Grade information is not available.")
                st.metric("Grade", "Not available")
        
        # Display feedback in the second column
        with col2:
            if 'feedback' in st.session_state and st.session_state['feedback'] is not None:
                st.subheader("Feedback")
                st.markdown(st.session_state['feedback'])
            else:
                st.warning("Feedback is not available.")
        
        # Display plagiarism results if available
        if 'plagiarism_results' in st.session_state and st.session_state['plagiarism_results']:
            st.subheader("Plagiarism Check")
            results = st.session_state['plagiarism_results']
            
            if results is None:
                st.warning("Plagiarism check results are not available.")
            elif isinstance(results, dict) and 'error' in results:
                st.error(f"Plagiarism check error: {results['error']}")
            elif isinstance(results, dict) and 'results' in results:
                # New API format
                st.markdown("**Similarity matches found:**")
                for item in results['results']:
                    url = item.get('url', '')
                    similarity = item.get('similarity', 0)
                    
                    if similarity > 70:
                        st.warning(f"⚠️ High similarity ({similarity}%): [{url}]({url})")
                    elif similarity > 40:
                        st.info(f"ℹ️ Moderate similarity ({similarity}%): [{url}]({url})")
                    else:
                        st.success(f"✅ Low similarity ({similarity}%): [{url}]({url})")
            else:
                # Old API format
                st.markdown("**Similarity matches found:**")
                if isinstance(results, dict):
                    for url, similarity in results.items():
                        if similarity > 70:
                            st.warning(f"⚠️ High similarity ({similarity}%): [{url}]({url})")
                        elif similarity > 40:
                            st.info(f"ℹ️ Moderate similarity ({similarity}%): [{url}]({url})")
                        else:
                            st.success(f"✅ Low similarity ({similarity}%): [{url}]({url})")
                else:
                    st.json(results)  # Display raw results if format is unknown
        
        # Export options
        st.subheader("Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export to PDF"):
                st.info("Creating PDF report...")
                # This is where you would implement PDF export
                st.download_button(
                    label="Download PDF",
                    data=b"Placeholder for PDF content",  # Replace with actual PDF data
                    file_name=f"grading_report_{st.session_state['file_name']}.pdf",
                    mime="application/pdf",
                    disabled=True  # Enable when implemented
                )
                st.info("PDF export functionality would go here")
        
        with col2:
            if st.button("💾 Save to Database"):
                st.info("Saving to database...")
                # This is where you would implement database save
                time.sleep(1)
                st.success("Record saved! (This is a placeholder)")
                st.info("Database save functionality would go here")
    else:
        st.info("No grading results available. Please upload and grade an assignment first.")

# Add footer
st.markdown("---")
st.markdown("© 2025 Assignment Grader | Powered by FastAPI and OpenAI")