import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import speech_recognition as sr  # For Speech-to-Text
import pyaudio  # Ensure you have pyaudio installed

# Load environment variables from .env file
load_dotenv()

# Configure the API key for Gemini 1.5 Flash
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Function to summarize the URL content
def summarize_audio_or_text(url):
    """Summarize content from the URL using Google's Gemini 1.5 Flash."""
    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")  # Use Gemini model
        response = model.generate_content(
            [
                f"Please summarize the content from the following URL: {url}"
            ]
        )
        return response.text
    except Exception as e:
        st.error(f"Error during summarization: {str(e)}")
        return None

# Function to answer questions based on the URL content
def answer_question(url, question):
    """Answer a question based on the content of the URL using Google's Gemini 1.5 Flash."""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(
            [
                f"Based on the content from the following URL: {url}, answer the question: {question}"
            ]
        )
        return response.text
    except Exception as e:
        st.error(f"Error during Q&A: {str(e)}")
        return None

# Function to convert voice input to text
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening for your question... Speak now.")
        audio = recognizer.listen(source)
    try:
        question_text = recognizer.recognize_google(audio)
        st.write(f"Question: {question_text}")  # Display the recognized text
        return question_text
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition service.")
        return None

# Initialize session state to store history
if 'history' not in st.session_state:
    st.session_state.history = {}

# Title and Sidebar setup
st.markdown("""
<div style="text-align: center;">
    <h1>Welcome to QuickURL 🌐</h1>
<h5><i>Simplify Research and Amplify Understanding with Q&A 📚💡</i></h5>
</div>
""", unsafe_allow_html=True)

with st.expander("About this app"):
    st.write("""
        This app uses Google's Gemini 1.5 Flash Model to:
        - Insert and process website URLs to extract relevant content.
        - Provides precise answers to questions based on the content.
        - Eliminates the need to read entire webpages.
        - Saves time and effort by offering quick, targeted insights.
    """)

st.sidebar.title("Insert URLs Here")

# URL inputs on the sidebar
urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i + 1}", placeholder="Enter a URL here")
    urls.append(url)

# Submit button for processing the URLs
process_url_clicked = st.sidebar.button("Process URLs")

# Process URLs when button is clicked
if process_url_clicked:
    for i, url in enumerate(urls):
        if url:
            # Check if the URL has already been processed
            if url not in st.session_state.history:
                summary = summarize_audio_or_text(url)
                if summary:
                    # Store summary in session state
                    st.session_state.history[url] = {'summary': summary, 'qa': []}
            else:
                st.info(f"URL {i + 1} has already been processed.")

# Display summaries and allow Q&A
for i, url in enumerate(urls):
    if url in st.session_state.history:
        # Display Summary of URL
        st.subheader(f"Summary of URL {i + 1}:")
        st.write(st.session_state.history[url]['summary'])

        # Input for asking a question
        st.subheader(f"Ask a question for URL {i + 1}:")
        question = st.text_input(f"Enter your question for URL {i + 1}:", key=f"question_{url}")

        if st.button(f"Ask with Voice for URL {i + 1}", key=f"voice_{url}"):
            # Capture the question using speech-to-text if the user presses the button
            question = speech_to_text()

        if question:
            with st.spinner(f"Fetching answer for URL {i + 1}..."):
                answer = answer_question(url, question)
                if answer:
                    # Store question and answer in session state
                    st.session_state.history[url]['qa'].append({'question': question, 'answer': answer})
                    st.success(f"Answer for your question '{question}' has been generated.")

        # Display Q&A History
        st.subheader(f"Questions and Answers for URL {i + 1}:")
        for idx, qa in enumerate(st.session_state.history[url]['qa']):
            st.write(f"Q{idx + 1}: {qa['question']}")
            st.write(f"A{idx + 1}: {qa['answer']}")
