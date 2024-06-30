import openai
import os
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
import re
import pyperclip

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
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a skilled playwright specializing in role-playing scripts as a teacher. You excel at writing scripts with easy words, especially for elementary school students. You can write engaging role-play scripts using educationally appropriate words and situations that help students learn key expressions in a fun way."},
            {"role": "user", "content": f'''Create a role-play script for grade {grade} Korean elementary school students. The script should play for {duration} seconds. Include {num_people} balanced roles in the script. Include Key phrases: {key_phrases} and Key words: {key_words}. The format of the script is 'name:line' and provide 'name: Korean translation' in the next line. Leave one blank line between lines.
            #script example
            
            jake: Hi, nice to see you.
            (안녕, 만나서 반가워.)
            
            jane: Hi. Watch out!
            (안녕. 조심해!)'''}
        ]
    )

    script = response['choices'][0]['message']['content']
    return script

def remove_korean_translation(script):
    # 한국어 번역을 제거하는 정규 표현식
    script_without_korean = re.sub(r'\n\n.*:.*', '', script)
    return script_without_korean

def download_audio(script):
    script_without_korean = remove_korean_translation(script)
    tts = gTTS(script_without_korean, lang='en')
    audio_file_path = "script_audio.mp3"
    tts.save(audio_file_path)
    return audio_file_path

def download_script(script):
    script_file_path = "script.txt"
    with open(script_file_path, "w", encoding="utf-8") as file:
        file.write(script)
    return script_file_path

# Streamlit UI 구성
st.title("초등 영어 상황극 대본 생성기")
col1, col2, col3 = st.columns(3)

grade = col1.selectbox("학년", ["1", "2", "3", "4", "5", "6"], index=5)
num_people = col2.slider("상황극 인원", min_value=2, max_value=10, value=4)
duration = col3.slider("길이(초)", min_value=10, max_value=300, value=30)
key_phrases = st.text_input("주요 표현 입력")
key_words = st.text_area("주요 단어 입력")

if 'script' not in st.session_state:
    st.session_state['script'] = ""

if st.button("상황극 대본 생성"):
    st.session_state['script'] = generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words)
    st.markdown(f"### 상황극 대본\n\n{st.session_state['script']}")

if st.session_state['script']:
    if st.button("음성파일 생성"):
        audio_file = download_audio(st.session_state['script'])
        with open(audio_file, "rb") as file:
            st.download_button(label="Download audio", data=file, file_name="script_audio.mp3", mime="audio/mp3")

    if st.button("대본 다운로드"):
        script_file = download_script(st.session_state['script'])
        with open(script_file, "rb") as file:
            st.download_button(label="Download script", data=file, file_name="script.txt", mime="text/plain")

    if st.button("스크립트 복사"):
        pyperclip.copy(st.session_state['script'])
        st.success("스크립트가 클립보드에 복사되었습니다.")
