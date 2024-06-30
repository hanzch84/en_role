import openai
import os
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정 (환경 변수에서 가져오기)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# ChatGPT API 호출 함수
def generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "You are a skilled playwright specializing in role-playing scripts as a teacher. You excel at writing scripts with easy words, especially for elementary school students. You can write engaging role-play scripts using educationally appropriate words and situations that help students learn key expressions in a fun way."},
            {"role": "user", "content": f"Create a role-play script for grade {grade} Korean elementary school students. The script should play for {duration} seconds. Include {num_people} balanced roles in the script. Key phrases: {key_phrases}. Key words: {key_words}. The format of the script is 'name:line' and provide Korean translation in the next line."}
        ]
    )

    script = response['choices'][0]['message']['content']
    return script

def download_audio(script):
    tts = gTTS(script, lang='ko')
    audio_file_path = "script_audio.mp3"
    tts.save(audio_file_path)
    return audio_file_path

def download_script(script):
    script_file_path = "script.txt"
    with open(script_file_path, "w", encoding="utf-8") as file:
        file.write(script)
    return script_file_path

# Streamlit UI 구성
st.title("상황극 대본 생성기")

grade = st.selectbox("학년", ["1", "2", "3", "4", "5", "6"])
num_people = st.slider("상황극 인원", min_value=2, max_value=10, value=4)
duration = st.slider("길이(초)", min_value=30, max_value=300, value=30)
key_phrases = st.text_input("주요 표현 입력")
key_words = st.text_area("주요 단어 입력")

if st.button("상황극 대본 생성"):
    script = generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words)
    st.text_area("상황극 대본", script, height=300)

    if st.button("음성파일 다운로드"):
        audio_file = download_audio(script)
        with open(audio_file, "rb") as file:
            st.download_button(label="Download audio", data=file, file_name="script_audio.mp3", mime="audio/mp3")

    if st.button("대본 다운로드"):
        script_file = download_script(script)
        with open(script_file, "rb") as file:
            st.download_button(label="Download script", data=file, file_name="script.txt", mime="text/plain")
