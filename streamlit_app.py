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
            {"role": "user", "content": f'''Create a role-play script for grade {grade} Korean elementary school students. The script should play for {duration} seconds. Include {num_people} balanced roles in the script. Include Key phrases: {key_phrases} and Key words: {key_words}. The format of the script is 'name:line' and provide 'name: Korean translation' in the next line. Leave one blank line between lines. return scripts only.
            #script example
            Characters:
            1. Sumi: An active and curious student. [활발하고 호기심이 많은 학생]
            2. Jin: A calm and inquisitive student. [차분하고 질문을 잘하는 학생]
            3. Minho: A student interested in history. [역사에 관심이 많은 학생]
            4. Hana: A responsible student who takes care of her friends. [책임감 있고 친구들을 잘 챙기는 학생]
            
            Background:
            Elementary school students are getting ready for a field trip to the museum. They are discussing what they want to see and are excited about the trip. [초등학교 학생들이 박물관으로 소풍을 가기 위해 준비하고 있습니다. 아이들은 무엇을 보고 싶은지 이야기하며 소풍을 기대하고 있습니다.]
            
            ---
            scripts:
            
            Sumi: Hello, everyone! How are you today?
            [안녕하세요, 여러분! 오늘 기분이 어떠세요?]
            
            Jin: I am good, thank you. How about you, Sumi?
            [저는 좋아요, 감사합니다. 수미는요?]
            
            Minho: I am excited! We have a field trip today.
            [저는 신나요! 오늘 소풍 가잖아요.]
            
            Hana: Yes, we are going to the museum. What do you want to see first?
            [맞아요, 우리 박물관에 가잖아요. 뭐부터 보고 싶어요?]
            
            Sumi: I want to see the dinosaur bones!
            [저는 공룡 뼈를 보고 싶어요!]
            
            Jin: Me too! Dinosaurs are so cool.
            [저도요! 공룡은 정말 멋져요.]
            
            Minho: I want to see the ancient artifacts. They have stories.
            [저는 고대 유물을 보고 싶어요. 그들은 이야기가 있어요.]
            
            Hana: Don’t forget to bring your notebooks. We need to write about what we see.
            [노트북 가져오는 것 잊지 마세요. 우리가 본 것에 대해 써야 해요.]
            
            Sumi: I have my notebook and a pen ready!
            [저는 노트북과 펜을 준비했어요!]
            
            Jin: Let’s go to the bus. We don’t want to be late.
            [버스로 가요. 늦지 않도록 해요.]
            
            Minho: Yes, let’s go! I can’t wait to explore.
            [네, 가요! 빨리 탐험하고 싶어요.]
            
            Hana: Remember to stay with the group and listen to the teacher.
            [그룹과 함께 다니고 선생님 말씀 잘 들어요.]
            
            Sumi: Okay, let's have fun and learn a lot!
            [네, 재미있게 놀고 많이 배워요!]
            
            Jin: Yes, let's go!
            [네, 가요!]
            
            ---
            make script like an example above. start_marker = "scripts:". you must include it.
            '''}
        ]
    )

    script = response['choices'][0]['message']['content']
    
    if not script:
        raise ValueError("Generated script is empty")
    
    return script

def remove_korean_translation(script):
    # Extract lines after 'scripts:'
    start_marker = "scripts:"
    
    # Find the start position of the marker
    start_pos = script.find(start_marker)
    
    # Check if the start_marker exists in the script
    if start_pos == -1:
        raise ValueError("The marker 'scripts:' not found in the script")

    start_pos += len(start_marker)
    
    # Extract the lines after the marker
    script_lines = script[start_pos:].strip().split("\n")
    
    # Remove the lines with Korean translations and character names
    english_lines = []
    for line in script_lines:
        if ":" in line and "[" in line:
            parts = line.split(":")
            if len(parts) > 1:
                english_line = parts[1].split("[")[0].strip()
                if english_line:  # Ensure the line is not empty
                    english_lines.append(english_line)
    
    # Join the English lines into the final script
    final_script = "\n".join(english_lines).strip()
    
    if not final_script:
        raise ValueError("Final script after removing Korean translation is empty")
    
    return final_script


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
    with st.spinner("Generating script..."):
        try:
            st.session_state['script'] = generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words)
            st.markdown(f"### 상황극 대본\n\n{st.session_state['script']}")
        except ValueError as e:
            st.error(str(e))

if st.session_state['script']:
    if st.button("음성파일 생성"):
        try:
            audio_file = download_audio(st.session_state['script'])
            with open(audio_file, "rb") as file:
                st.download_button(label="Download audio", data=file, file_name="script_audio.mp3", mime="audio/mp3")
        except ValueError as e:
            st.error(str(e))

    if st.button("대본 다운로드"):
        script_file = download_script(st.session_state['script'])
        with open(script_file, "rb") as file:
            st.download_button(label="Download script", data=file, file_name="script.txt", mime="text/plain")

    if st.button("스크립트 복사"):
        pyperclip.copy(st.session_state['script'])
        st.success("스크립트가 클립보드에 복사되었습니다.")
