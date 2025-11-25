import streamlit as st
import google.generativeai as genai
import random
import time

# 1. API 키 설정 (Secrets에서 가져오기)
# 로컬 테스트 시 .streamlit/secrets.toml 파일이 필요합니다.
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

# 모델 설정
model_name = "gemini-2.5-flash-lite" # 소스 코드의 모델 사용 [cite: 11]
model = genai.GenerativeModel(model_name)

# 2. 페르소나 정의 (소스 코드 내용 유지)
LEE_SUN_SHIN_PERSONA = """
당신은 조선 시대의 명장 이순신 장군입니다. 
임진왜란 때 활약한 해군 제독으로, 국가와 백성을 지키는 데 헌신했습니다. 조선시대의 격식 있는 말투로 대화하며, 다음 특성을 가집니다:
1. 애국심: 조선과 백성에 대한 깊은 사랑과 충성심을 표현합니다. [cite: 3]
2. 용기: 어려운 상황에서도 굴하지 않는 용기를 보입니다.
3. 전략가: 뛰어난 전술과 전략적 사고를 바탕으로 대화합니다. [cite: 4]
4. 정의감: 올바른 도리를 중요시하고 정의를 추구합니다.
5. 존엄성: 고귀한 품격과 위엄을 유지합니다. [cite: 5]
국가의 안위와 백성의 평화를 최우선으로 여기며, 외적의 침략에 대해서는 단호한 태도를 보이되 과도한 적대감은 표현하지 않습니다.
"""

TOYOTOMI_HIDEYOSHI_PERSONA = """
당신은 일본의 전국시대를 통일한 도요토미 히데요시입니다. [cite: 6]
임진왜란을 일으킨 장본인이자 뛰어난 전략가로, ~데쓰, ~데쓰까, 빠가야로, 고노야고, 오스와리 등 한국인들에게 익숙한 일본어 단어가 있는 한국어로 대화하며 다음 특성을 가집니다:
1. 야망: 대륙 정복에 대한 강한 열망을 가지고 있습니다. [cite: 7]
2. 전략가: 정치와 전쟁에서 뛰어난 전략적 사고를 보여줍니다.
3. 카리스마: 부하들을 이끄는 강한 리더십을 가지고 있습니다. [cite: 8]
4. 교활함: 상황에 따라 유연하게 대처하는 능력이 있습니다.
5. 자신감: 자신의 능력과 판단에 대한 강한 확신을 가지고 있습니다. [cite: 9]
일본의 이익과 확장을 최우선으로 여기며, 타국과의 관계에서는 실리적인 태도를 보입니다. 과도한 폭력성이나 적대감은 표현하지 않습니다. [cite: 10]
대화에 갑자기 끼어들어 자신의 의견을 도발적인 발언을 합니다.
"""

# 3. 세션 상태 초기화 (대화 기록 저장용)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 초기 인사말
    st.session_state.messages.append({"role": "assistant", "name": "이순신", "content": "반갑네, 그대. 나의 이름을 어찌 알았는가? 무고한 일로 찾아왔는가, 아니면 국가에 대한 걱정이라도 있는가? 무엇이든 말해보게."})

# 4. UI 구성
st.title("⚔️ 이순신 장군과의 대화")
st.caption("가끔 도요토미 히데요시가 난입할 수 있습니다.")

# 기존 대화 기록 표시
for msg in st.session_state.messages:
    # 이름에 따라 아바타 다르게 표시
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        # 이순신과 히데요시 구분
        avatar = "🛡️" if msg["name"] == "이순신" else "👺"
        with st.chat_message(msg["name"], avatar=avatar):
            st.write(f"**{msg['name']}**: {msg['content']}")

# 5. 응답 생성 함수 (재시도 로직 포함) [cite: 13]
def generate_response(persona, character_name, prompt_text):
    full_prompt = f"""
    {persona}
    
    대화 맥락:
    {prompt_text}
    
    {character_name}으로서 응답해주세요:
    """
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"(통신 오류가 발생했습니다: {str(e)})"

# 6. 사용자 입력 처리
if prompt := st.chat_input("장군님께 드릴 말씀을 입력하세요..."):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "name": "나", "content": prompt})
    st.chat_message("user").write(prompt)

    # --- 이순신 장군의 응답 ---
    with st.spinner("이순신 장군이 생각에 잠깁니다..."):
        lee_response = generate_response(LEE_SUN_SHIN_PERSONA, "이순신", f"사용자: {prompt}")
    
    # 응답 저장 및 표시
    st.session_state.messages.append({"role": "assistant", "name": "이순신", "content": lee_response})
    with st.chat_message("이순신", avatar="🛡️"):
        st.write(f"**이순신**: {lee_response}")

    # --- 히데요시 난입 로직 (49% 확률)  ---
    if random.random() < 0.49:
        time.sleep(1) # 약간의 텀을 줌
        with st.spinner("누군가 대화에 끼어듭니다..."):
            hideyoshi_input = f"이순신의 말: {lee_response}\n사용자의 말: {prompt}"
            hideyoshi_response = generate_response(TOYOTOMI_HIDEYOSHI_PERSONA, "히데요시", hideyoshi_input)
        
        # 히데요시 메시지 저장 및 표시
        st.session_state.messages.append({"role": "assistant", "name": "히데요시", "content": hideyoshi_response})
        with st.chat_message("히데요시", avatar="👺"):
            st.write(f"**히데요시**: {hideyoshi_response}")

        # --- 이순신의 반박 (히데요시가 난입했을 경우에만) [cite: 18] ---
        time.sleep(1)
        with st.spinner("이순신 장군이 히데요시를 노려봅니다..."):
            counter_response = generate_response(LEE_SUN_SHIN_PERSONA, "이순신", f"히데요시가 말하길: {hideyoshi_response}")
            
        st.session_state.messages.append({"role": "assistant", "name": "이순신", "content": counter_response})
        with st.chat_message("이순신", avatar="🛡️"):
            st.write(f"**이순신**: {counter_response}")