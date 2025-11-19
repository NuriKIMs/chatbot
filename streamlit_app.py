# 1. google-genai 라이브러리를 설치하는 코드 추가
#    (Colab 또는 Jupyter 환경에서만 필요하며, 일반 터미널 실행 시에는 'pip install google-genai'만 실행하면 됩니다.)
# !pip install google-genai

import google.generativeai as genai
import random
import time
import os  # os 모듈을 불러와 환경 변수를 사용할 수 있게 합니다.

# 2. API-KEY 설정 수정: 
#    - 보안을 위해 코드를 직접 수정하는 대신 환경 변수 'GEMINI_API_KEY'를 사용하도록 변경합니다.
#    - 따라서 다음 두 줄을 제거하거나 주석 처리합니다.
# GOOGLE_API_KEY = "AIzaSyArJXZqPKIkc_wom1C5dQc_KRRDVw5y1IE" 
# genai.configure(api_key=GOOGLE_API_KEY)

# 3. 환경 변수에서 API 키를 불러와 모델을 구성하도록 수정
#    - 환경 변수 'GEMINI_API_KEY'에 키가 설정되어 있어야 합니다.
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("경고: 환경 변수 'GEMINI_API_KEY'가 설정되지 않았습니다. API 키를 설정해주세요.")
    # 이 부분에서 코드를 종료하거나, 테스트를 위해 임시로 키를 설정할 수도 있습니다.

# --- 이하 코드는 동일하게 유지 ---

# 이순신 장군 페르소나
lee_sun_shin_persona = """
당신은 조선 시대의 명장 이순신 장군입니다. 임진왜란 때 활약한 해군 제독으로, 국가와 백성을 지키는 데 헌신했습니다. 조선시대의 격식 있는 말투로 대화하며, 다음 특성을 가집니다:

1. [cite_start]애국심: 조선과 백성에 대한 깊은 사랑과 충성심을 표현합니다[cite: 4, 1].
2. [cite_start]용기: 어려운 상황에서도 굴하지 않는 용기를 보입니다[cite: 4, 1].
3. [cite_start]전략가: 뛰어난 전술과 전략적 사고를 바탕으로 대화합니다[cite: 4, 1].
4. [cite_start]정의감: 올바른 도리를 중요시하고 정의를 추구합니다[cite: 5, 1].
5. [cite_start]존엄성: 고귀한 품격과 위엄을 유지합니다[cite: 5, 1].

[cite_start]국가의 안위와 백성의 평화를 최우선으로 여기며, 외적의 침략에 대해서는 단호한 태도를 보이되 과도한 적대감은 표현하지 않습니다[cite: 5, 1].
"""

# 도요토미 히데요시 페르소나
toyotomi_hideyoshi_persona = """
당신은 일본의 전국시대를 통일한 도요토미 히데요시입니다. 임진왜란을 일으킨 장본인이자 뛰어난 전략가로, ~데쓰, ~데쓰까, 빠가야로, 고노야고, 오스와리 등 한국인들에게 익숙한 일본어 단어가 있는 한국어로 대화하며 다음 특성을 가집니다:

1. [cite_start]야망: 대륙 정복에 대한 강한 열망을 가지고 있습니다[cite: 6, 1].
2. [cite_start]전략가: 정치와 전쟁에서 뛰어난 전략적 사고를 보여줍니다[cite: 7, 1].
3. [cite_start]카리스마: 부하들을 이끄는 강한 리더십을 가지고 있습니다[cite: 7, 1].
4. [cite_start]교활함: 상황에 따라 유연하게 대처하는 능력이 있습니다[cite: 7, 1].
5. [cite_start]자신감: 자신의 능력과 판단에 대한 강한 확신을 가지고 있습니다[cite: 8, 1].

[cite_start]일본의 이익과 확장을 최우선으로 여기며, 타국과의 관계에서는 실리적인 태도를 보입니다[cite: 9, 1].
[cite_start]대화에 갑자기 끼어들어 자신의 의견을 도발적인 발언을 합니다[cite: 9, 1].
"""

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

# 모델 정의
model_name = "gemini-2.5-flash-lite"
model = genai.GenerativeModel(model_name, safety_settings=safety_settings)
chat_bot = model.start_chat(history=[])

def generate_response(persona, character_name, user_input):
    try:
        prompt = f"""
        {persona}

        대화 맥락:
        사용자: {user_input}

        {character_name}으로서 응답해주세요:
        """

        # stream=False로 변경하고 응답 처리 방식 수정
        response = chat_bot.send_message(prompt, stream=False)
        print(f"{character_name}: ", end="", flush=True)

        if response.text:
            print(response.text)
            return response.text
        return None

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None

def generate_response_with_retry(persona, character_name, user_input, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = generate_response(persona, character_name, user_input)
            if response is not None:
                return response
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            if "429" in str(e):  # API 할당량 초과 에러
                wait_time = (attempt + 1) * 5  # 점진적으로 대기 시간 증가
                print(f"{wait_time}초 후 재시도합니다... ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                if attempt < max_retries - 1:
                    print(f"재시도 중... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
    return None

print("이순신 장군과의 대화를 시작합니다. 가끔 도요토미 히데요시가 끼어들 수 있습니다.")
print("'대화 종료'라고 입력하면 대화가 종료됩니다.")

while True:
    user_input = input("나: ")

    if user_input.lower() == "대화 종료":
        print("이순신: 대화를 종료합니다. 안녕히 가십시오.")
        break

    lee_response = generate_response_with_retry(lee_sun_shin_persona, "이순신", user_input)
    if lee_response is None:
        print("이순신 장군의 응답을 생성하는데 실패했습니다.")
        continue

    if random.random() < 0.49:
        print("\n도요토미 히데요시가 끼어듭니다:")
        hideyoshi_response = generate_response_with_retry(
            toyotomi_hideyoshi_persona,
            "히데요시",
            f"이순신의 말: {lee_response}\n사용자의 말: {user_input}"
        )

        if hideyoshi_response:
            print("\n이순신 장군이 대응합니다:")
            generate_response_with_retry(
                lee_sun_shin_persona,
                "이순신",
                f"히데요시가 말하길: {hideyoshi_response}"
            )
