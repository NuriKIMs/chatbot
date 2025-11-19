# 필요한 라이브러리 설치:
# 터미널: pip install google-genai streamlit
# Streamlit 앱 배포 시, requirements.txt에 'google-genai'와 'streamlit'을 포함해야 합니다.

import streamlit as st # Streamlit 라이브러리 추가
import google.generativeai as genai
import random
import time
import os 
# import os는 Streamlit Secret을 사용해도 안전성을 위해 남겨둡니다.

## --- 환경 설정 및 모델 초기화 ---

try:
    # st.secrets는 로컬에서 secrets.toml을, 클라우드에서 Secrets 메뉴를 읽습니다.
    # 클라우드 배포 시에는 secrets.toml이 아닌 클라우드 Secrets 메뉴에 키를 넣어주어야 합니다.
    api_key = "AIzaSyArJXZqPKIkc_wom1C5dQc_KRRDVw5y1IE" 
    # genai.configure(api_key=api_key) # API 키 설정은 이 코드를 사용합니다.
    # ...
except KeyError:
    st.error("API 키 설정 오류: 'GEMINI_API_KEY'를 secrets.toml 또는 Streamlit Secrets에 설정해주세요.")
    st.stop()

# 안전 설정
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]

# 모델 정의 (Streamlit의 캐싱 기능을 활용하여 초기화 속도를 높입니다.)
@st.cache_resource
def get_model():
    model_name = "gemini-2.5-flash-lite"
    model = genai.GenerativeModel(model_name, safety_settings=safety_settings)
    # history는 세션별로 관리해야 하므로, chat_bot은 아래 메인 로직에서 생성합니다.
    return model

model = get_model()

# 세션 상태 초기화 (대화 기록 및 챗봇 인스턴스)
if "chat_bot" not in st.session_state:
    st.session_state.chat_bot = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

## --- 페르소나 정의 (유지) ---

lee_sun_shin_persona = """
당신은 조선 시대의 명장 이순신 장군입니다. 임진왜란 때 활약한 해군 제독으로, 국가와 백성을 지키는 데 헌신했습니다. 조선시대의 격식 있는 말투로 대화하며, 다음 특성을 가집니다:
... (중략) ...
"""

toyotomi_hideyoshi_persona = """
당신은 일본의 전국시대를 통일한 도요토미 히데요시입니다. 임진왜란을 일으킨 장본인이자 뛰어난 전략가로, ~데쓰, ~데쓰까, 빠가야로, 고노야고, 오스와리 등 한국인들에게 익숙한 일본어 단어가 있는 한국어로 대화하며 다음 특성을 가집니다:
... (중략) ...
"""

## --- 응답 생성 함수 (Streamlit 환경에 맞게 수정) ---

def generate_response(persona, character_name, user_input, chat_instance=None):
    try:
        prompt = f"""
        {persona}

        대화 맥락:
        사용자: {user_input}

        {character_name}으로서 응답해주세요:
        """
        # chat_instance를 사용하거나, 새 메시지를 전송합니다.
        response = chat_instance.send_message(prompt, stream=False)
        return response.text

    except Exception as e:
        st.error(f"{character_name} 응답 오류 발생: {str(e)}")
        return None

def generate_response_with_retry(persona, character_name, user_input, max_retries=3, chat_instance=None):
    for attempt in range(max_retries):
        try:
            response = generate_response(persona, character_name, user_input, chat_instance)
            if response is not None:
                return response
        except Exception as e:
            time.sleep(2) # 재시도 전 잠깐 대기
            if attempt == max_retries - 1:
                st.error(f"{character_name} 응답 생성 최종 실패.")
                return None
    return None

## --- Streamlit UI 및 메인 루프 ---

st.title("이순신 vs 도요토미 히데요시 ⚔️")
st.markdown("이순신 장군과의 대화를 시작합니다. 가끔 도요토미 히데요시가 끼어들 수 있습니다.")

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if user_input := st.chat_input("나:"):
    
    # 1. 사용자 메시지 기록 및 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. 이순신 장군 응답 생성
    with st.spinner("이순신 장군이 생각 중입니다..."):
        lee_response = generate_response_with_retry(
            lee_sun_shin_persona, 
            "이순신", 
            user_input, 
            chat_instance=st.session_state.chat_bot
        )
    
    if lee_response:
        # 이순신 응답 기록 및 표시
        st.session_state.messages.append({"role": "이순신", "content": lee_response})
        with st.chat_message("이순신"):
            st.markdown(lee_response)

        # 3. 도요토미 히데요시 난입 (49% 확률)
        if random.random() < 0.49:
            st.session_state.messages.append({"role": "system", "content": "도요토미 히데요시가 끼어듭니다:"})
            st.info("도요토미 히데요시가 끼어듭니다:")

            # 히데요시 응답 생성
            hideyoshi_prompt = f"이순신의 말: {lee_response}\n사용자의 말: {user_input}"
            with st.spinner("히데요시가 도발할 기회를 엿보고 있습니다..."):
                hideyoshi_response = generate_response_with_retry(
                    toyotomi_hideyoshi_persona,
                    "히데요시",
                    hideyoshi_prompt,
                    chat_instance=st.session_state.chat_bot # 같은 챗봇 인스턴스 사용
                )
            
            if hideyoshi_response:
                # 히데요시 응답 기록 및 표시
                st.session_state.messages.append({"role": "히데요시", "content": hideyoshi_response})
                with st.chat_message("히데요시"):
                    st.markdown(hideyoshi_response)

                st.session_state.messages.append({"role": "system", "content": "이순신 장군이 대응합니다:"})
                st.info("이순신 장군이 대응합니다:")

                # 이순신 대응 응답 생성
                lee_counter_prompt = f"히데요시가 말하길: {hideyoshi_response}"
                with st.spinner("이순신 장군이 엄중히 대응합니다..."):
                    lee_counter_response = generate_response_with_retry(
                        lee_sun_shin_persona,
                        "이순신",
                        lee_counter_prompt,
                        chat_instance=st.session_state.chat_bot
                    )

                if lee_counter_response:
                    # 이순신 대응 기록 및 표시
                    st.session_state.messages.append({"role": "이순신", "content": lee_counter_response})
                    with st.chat_message("이순신"):
                        st.markdown(lee_counter_response)
