import openai
import os
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정 (환경 변수에서 가져오기)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

def generate_script_with_gpt_stream(grade, num_people, duration, key_phrases, key_words):
    prompt = (
        f"Create a role-play script for {grade} grade Korean elementary school students. "
        f"The script should play for {duration} seconds (a line in the script takes 4~5 seconds). "
        f"Include {num_people} balanced roles in the script. Include Key phrases: {key_phrases} and Key words: {key_words}."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response:
        if "choices" in chunk:
            yield chunk['choices'][0]['delta'].get('content', '')

st.title("Role-Play Script Generator")

grade = st.text_input("Grade", value="5")
num_people = st.text_input("Number of People", value="3")
duration = st.text_input("Duration (in seconds)", value="60")
key_phrases = st.text_input("Key Phrases", value="Hello, Thank you")
key_words = st.text_input("Key Words", value="School, Friends")

if st.button("Generate Script"):
    script_placeholder = st.empty()
    script_text = ""
    for chunk in generate_script_with_gpt_stream(grade, num_people, duration, key_phrases, key_words):
        script_text += chunk
        script_placeholder.text_area("Generated Script", script_text, height=400)

    st.success("Script generation complete")
