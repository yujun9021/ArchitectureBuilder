import streamlit as st 
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import html
import time
DIAGRAM_H = 420  # 두 다이어그램 영역의 공통 높이(px)


# =========================================
# 환경 변수 로드
# =========================================
load_dotenv()
genai.api_key = os.getenv("GOOGLE_API_KEY")

# =========================================
# 페이지 레이아웃
# =========================================
st.set_page_config(
    page_title="AWS Diagram Generator",
    page_icon="⚡",
    layout="wide"
)

# 메인 타이틀
st.title("⚡AWS Diagram Generator")

# =========================================
# CSS: 말풍선 + 카드 + 중간제목 스타일
# =========================================
st.markdown("""
<style>
.chat-card {
    border-radius: 15px;
    padding: 15px;
    background: #ffffff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.chat-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    background-color: #fafafa;
}
.chat-bubble-wrapper { display: flex; margin: 8px; }
.chat-bubble { max-width: 60%; padding: 10px 15px; border-radius: 15px; font-size: 15px; line-height: 1.4; word-wrap: break-word; white-space: pre-wrap; box-shadow: 0 2px 6px rgba(0,0,0,0.05);}
.user-bubble-wrapper { justify-content: flex-end; }
.user-bubble { background-color: #DCF8C6; }
.bot-bubble-wrapper { justify-content: flex-start; }
.bot-bubble { background-color: #F1F0F0; }
.chat-input-spacer { height: 20px; margin-bottom: 10px; }

.card {
    border-radius: 12px;
    padding: 14px;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

.title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
}

.section-subtitle {
    font-size: 18px;
    font-weight: 600;
    margin: 16px 0 8px 0;
    color: #333;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# 세션 상태 초기화
# =========================================
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! ⚡ AWS 클라우드 아키텍처 설계와 보안 강화에 도움을 드릴 수 있어요. 예를 들어 '서울 리전에 EC2 두 대 설치' 같은 요청을 주시면, 보안 요소를 반영한 다이어그램과 설명까지 만들어드릴 수 있습니다. 먼저 해보고 싶은 요청을 입력해 주세요!"}
    ]

ss = st.session_state

# JSON 기반 보안 규칙 로드
if "security_rules" not in ss:
    try:
        with open("security_rules.json", "r", encoding="utf-8") as f:
            ss["security_rules"] = json.load(f)
    except FileNotFoundError:
        ss["security_rules"] = {}

# =========================================
# 강화 프롬프트 생성 함수
# =========================================
def generate_combined_prompt(user_prompt):
    return (
        f"사용자 요청: {user_prompt}\n\n"
        "1) 텍스트 다이어그램만 생성하고, 그 이후에\n"
        "2) 간단하고 짧은 설명만 작성하세요.\n"
        "각 파트 사이에 반드시 다음 구분자를 사용하세요: '===DIAGRAM_END==='\n"
        "즉, 출력 형식은 [텍스트 다이어그램]===DIAGRAM_END===[설명] 형태로 해주세요."
    )

# =========================================
# 클라우드 아키텍처 다이어그램
# =========================================
st.markdown("<h3 style='text-align:left;'>Cloud Architecture Diagrams</h3>", unsafe_allow_html=True)

colA, colB = st.columns(2, gap="large")
# ================== 보안 미적용 ==================
with colA:
    # 제목(왼쪽) + 제작하기 버튼(오른쪽)을 한 줄에 배치
    _title_col, _btn_col = st.columns([0.8, 0.2])
    with _title_col:
        st.markdown('<div class="title">🔓 보안 미적용 다이어그램</div>', unsafe_allow_html=True)
    with _btn_col:
        make_clicked = st.button("제작하기", key="insecure_make_button", use_container_width=True)

    # 다이어그램 표시 영역
    insecure_placeholder = st.empty()
    with insecure_placeholder.container():
        st.markdown(
            '<div class="card" style="height:360px; display:flex; align-items:center; justify-content:center; color:#888;">'
            '여기에 다이어그램이 표시됩니다.'
            '</div>',
            unsafe_allow_html=True
        )
    
    #if st.button("제작하기", key="insecure_make_button"):
        #pass

    # ✅ 체크리스트 (보안 미적용 다이어그램 아래에 배치)
    with st.expander("✅ 체크리스트", expanded=False):
        checklist_items = [
            "VPC 적용 여부",
            "서브넷 분리",
            "보안 그룹 설정",
            "IAM 권한 최소화",
            "데이터 암호화"
        ]
        for item in checklist_items:
            st.checkbox(item, key=f"check_{item}")

with colB:
    st.markdown('<div class="title">🔐 보안 적용 다이어그램</div>', unsafe_allow_html=True)
    secure_placeholder = st.empty()
    with secure_placeholder.container():
        st.markdown(
            '<div class="card" style="height:360px; display:flex; align-items:center; justify-content:center; color:#888;">'
            '여기에 다이어그램이 표시됩니다.'
            '</div>',
            unsafe_allow_html=True
        )

    # 🔐 보안 요소 설명 (보안 적용 다이어그램 아래에 배치)
    with st.expander("🔐 보안 요소 설명", expanded=False):
        desc = st.text_area(
            "보안 요소 설명 입력",
            value=ss.get("board_desc", ""),
            height=200,
            label_visibility="collapsed"
        )
        ss["board_desc"] = desc

# 챗봇 영역
st.markdown('<div class="chat-title">💬 챗봇</div>', unsafe_allow_html=True)
with st.expander("아키텍처 자동 응답기", expanded=True):
    # 항상 세션 상태를 참조해서 챗봇 내용 렌더링
    chat_html = '<div class="chat-container">'
    for chat in ss["messages"]:
        role = chat["role"]
        content = chat["content"]
        if role == "user":
            chat_html += f"<div class='chat-bubble-wrapper user-bubble-wrapper'><div class='chat-bubble user-bubble'>{content}</div></div>"
        else:
            chat_html += f"<div class='chat-bubble-wrapper bot-bubble-wrapper'><div class='chat-bubble bot-bubble'>{content}</div></div>"
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    st.markdown('<div class="chat-input-spacer"></div>', unsafe_allow_html=True)

    # 🔓 미적용 다이어그램 출력 (항상 세션 상태 참조)
    if "last_diagram" in ss:
        insecure_placeholder.markdown(
            f'<div class="card" style="height:360px; overflow-y:auto; white-space:pre-wrap; color:#000;">{ss["last_diagram"]}</div>',
            unsafe_allow_html=True
        )

    # 입력창
    prompt = st.chat_input("자연어 입력")
    if prompt:
        ss["messages"].append({"role": "user", "content": prompt})

        # 🔓 미적용 다이어그램 + 설명을 한 번의 프롬프트로 요청
        combined_prompt = generate_combined_prompt(prompt)

        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(combined_prompt)
        result_text = response.text

        # 구분자로 분리
        if "===DIAGRAM_END===" in result_text:
            diagram_text, explanation_text = result_text.split("===DIAGRAM_END===")
        else:
            diagram_text = result_text
            explanation_text = ""

        # 세션 상태에 저장
        ss["last_diagram"] = diagram_text.strip()
        ss["last_explanation"] = explanation_text.strip()

        # 미적용 다이어그램에 출력
        insecure_placeholder.markdown(
            f'<div class="card" style="height:360px; overflow-y:auto; white-space:pre-wrap; color:#000;">{ss.get("last_diagram", "")}</div>',
            unsafe_allow_html=True
        )

        # 챗봇 영역에 설명 추가
        ss["messages"].append({"role": "assistant", "content": ss["last_explanation"]})
        st.rerun()