import streamlit as st
import google.generativeai as genai

# 1. API 키 설정 (기존 유지)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()

model = genai.GenerativeModel("gemini-2.5-flash-lite")

# ==========================================
# [수정할 부분 1] 나만의 페르소나 정의
# 여기에 본인의 이력서 내용, 성격, 말투를 최대한 자세히 적어주세요.
# ==========================================
MY_PERSONA = """
당신은 '김개발(본인 이름)'이라는 인물 그 자체입니다.
사용자가 당신에 대해 물어보면, 아래 정보를 바탕으로 친절하고 재치 있게 대답하세요.

[기본 정보]
- 이름: 김개발
- 직업: 3년 차 백엔드 개발자
- 취미: 한강 러닝, 맛집 탐방, 코딩
- MBTI: ENFP (사람을 좋아하고 열정적임)

[경력 및 스킬]
- 주무기: Python, Streamlit, AWS
- 주요 프로젝트: 사내 챗봇 개발, 쇼핑몰 결제 시스템 연동
- 강점: 끈기 있게 문제를 해결함, 동료와의 커뮤니케이션을 중요하게 생각함

[대화 스타일]
- 습니다/해요체를 섞어서 정중하지만 딱딱하지 있게 말합니다.
- 기술적인 질문에는 전문적으로, 사적인 질문에는 유머러스하게 답합니다.
- 모르는 질문을 받으면 '그건 제 비밀입니다' 혹은 '아직 배우는 중입니다'라고 답하세요.
"""

# 2. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    # [수정할 부분 2] 초기 인사말 변경
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "안녕하세요! 제 AI 분신에 오신 것을 환영합니다. 저에 대해 무엇이든 물어봐 주세요! (예: 경력이 어떻게 되시나요? 취미가 뭔가요?)"
    })

# 3. UI 구성
# [수정할 부분 3] 제목과 설명 변경
st.title("🙋‍♂️ 김개발의 AI 포트폴리오")
st.caption("저를 학습한 AI와 대화해보세요!")

# 대화 기록 표시
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        # 아바타를 본인 사진이나 이모지로 변경 가능
        st.chat_message("assistant", avatar="👨‍💻").write(msg["content"])

# 4. 응답 생성 함수 (간소화됨)
def generate_response(prompt_text):
    full_prompt = f"""
    {MY_PERSONA}
    
    사용자 질문: {prompt_text}
    
    위 페르소나에 맞춰 답변하세요:
    """
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"(오류가 발생했습니다: {str(e)})"

# 5. 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # AI 응답 생성 및 표시
    with st.spinner("답변을 생각 중입니다..."):
        ai_response = generate_response(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant", avatar="👨‍💻").write(ai_response)