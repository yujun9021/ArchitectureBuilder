import streamlit as st 
import os
import google.generativeai as genai
from dotenv import load_dotenv
import html
import re
import subprocess
import platform
from pathlib import Path
from config import GOOGLE_API_KEY, AMAZON_Q_PATH, DIAGRAM_SETTINGS

# =========================================
# 환경 변수 로드
# =========================================
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# =========================================
# Amazon Q CLI 클라이언트 클래스
# =========================================
class AmazonQClient:
    """Amazon Q CLI 클라이언트"""
    
    def __init__(self):
        self.platform = platform.system()
    
    def generate_diagram_prompt(self, tree_structure):
        """트리 구조를 기반으로 다이어그램 생성 프롬프트 생성"""
        return f"""
다음 클라우드 아키텍처 트리 구조를 기반으로 다이어그램을 생성해주세요:

아키텍처 구조:
{tree_structure}

작업 내용:
1. "graph_attr={"dpi": "300", "size": "6.4,3.6"}" 비율로 다이어그램 생성
2. 실제 다이어그램 이미지 파일(.png)을 './generated-diagrams' 폴더에 저장
3. AWS 서비스 아이콘과 연결 관계를 포함한 시각적 아키텍처 다이어그램 생성
4. 중복된 파일이있다면 V2 파일명으로 저장

응답 형식:

파일 정보:
- 파일명: [생성된_파일명.png]
- 저장 경로: ./generated-diagrams/[생성된_파일명.png]
- 상태: 완료

아키텍처 설명:
[생성된 아키텍처에 대한 간단한 설명]
"""
    
    def execute_command(self, prompt):
        """플랫폼별 명령어 실행"""
        try:
            if self.platform == "Windows":
                return self._execute_windows(prompt)
            else:
                return self._execute_unix(prompt)
        except Exception as e:
            st.error(f"Amazon Q CLI 실행 오류: {str(e)}")
            return None
    
    def _execute_windows(self, prompt):
        """Windows에서 명령어 실행"""
        try:
            # WSL이 설치되어 있는지 확인
            wsl_check = subprocess.run(['wsl', '--version'], capture_output=True, text=True)
            if wsl_check.returncode == 0:
                # WSL 사용
                home_dir = os.path.expanduser("~")
                local_bin = os.path.join(home_dir, ".local", "bin")
                cmd = f'source ~/.bashrc && export PATH=$PATH:{local_bin} && printf "y\\ny\\ny\\n" | {AMAZON_Q_PATH} chat "{prompt}"'
                
                return subprocess.run([
                    'wsl', '-e', 'bash', '-c', cmd
                ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
            else:
                # WSL이 없으면 직접 실행 시도
                cmd = f'{AMAZON_Q_PATH} chat "{prompt}"'
                return subprocess.run([
                    'cmd', '/c', cmd
                ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
                
        except FileNotFoundError:
            # WSL 명령어를 찾을 수 없으면 직접 실행
            cmd = f'{AMAZON_Q_PATH} chat "{prompt}"'
            return subprocess.run([
                'cmd', '/c', cmd
            ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
    
    def _execute_unix(self, prompt):
        """Linux/Mac에서 명령어 실행"""
        home_dir = os.path.expanduser("~")
        local_bin = os.path.join(home_dir, ".local", "bin")
        cmd = f'source ~/.bashrc && export PATH=$PATH:{local_bin} && printf "y\\ny\\ny\\n" | {AMAZON_Q_PATH} chat "{prompt}"'
        
        return subprocess.run([
            'bash', '-c', cmd
        ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
    
    def generate_diagram(self, tree_structure):
        """Amazon Q CLI를 통해 다이어그램 생성 요청"""
        try:
            prompt = self.generate_diagram_prompt(tree_structure)
            result = self.execute_command(prompt)
            
            if result and result.returncode == 0:
                return result.stdout or ""
            else:
                if result:
                    st.error(f"Amazon Q CLI 오류: {result.stderr}")
                return None
                
        except Exception as e:
            st.error(f"Amazon Q CLI 실행 오류: {str(e)}")
            return None

# =========================================
# 다이어그램 관리 클래스
# =========================================
class DiagramManager:
    """다이어그램 파일 관리"""
    
    def __init__(self):
        self.diagram_folder = Path('./generated-diagrams')
        self.diagram_folder.mkdir(parents=True, exist_ok=True)
    
    def find_latest_diagram(self):
        """최신 다이어그램 파일 찾기"""
        png_files = list(self.diagram_folder.glob('*.png'))
        if png_files:
            latest_file = max(png_files, key=lambda x: x.stat().st_mtime)
            return latest_file
        return None
    
    def get_folder_contents(self):
        """다이어그램 폴더 내용 반환"""
        if self.diagram_folder.exists():
            return [f.name for f in self.diagram_folder.glob('*')]
        return []

# =========================================
# Gemini API 초기화
# =========================================
def initialize_gemini():
    """Gemini API 초기화"""
    try:
        if not GOOGLE_API_KEY:
            return False, None
        
        # Gemini API 설정
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # 모델 초기화 (최신 모델명 사용)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        return True, model
        
    except Exception as e:
        st.error(f"Gemini API 초기화 실패: {str(e)}")
        return False, None

# API 초기화 실행
api_ready, model = initialize_gemini()

# Amazon Q 클라이언트 초기화
amazon_q_client = AmazonQClient()

# 다이어그램 매니저 초기화
diagram_manager = DiagramManager()

# =========================================
# 트리 구조 추출 함수
# =========================================
def extract_tree_structure(text):
    """텍스트에서 트리 구조를 추출합니다."""
    # 트리 구조 패턴들
    tree_patterns = [
        r'```tree\s*\n(.*?)\n```',  # ```tree ... ``` 형태
        r'```\s*\n(.*?)\n```',      # ``` ... ``` 형태
        r'^\s*[├└│─]+.*$',          # 트리 문자로 시작하는 줄들
        r'^\s*[┌└├│─]+.*$',          # 다른 트리 문자들
        r'^\s*[│├└─]+.*$',           # 기본 트리 문자들
    ]
    
    for pattern in tree_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        if matches:
            return matches[0].strip()
    
    # 트리 구조가 없으면 전체 텍스트 반환
    return text

# =========================================
# 챗봇 응답 생성 함수
# =========================================
def generate_chatbot_response(user_message):
    """사용자 메시지에 대한 챗봇 응답을 생성합니다."""
    if not api_ready or not model:
        return "❌ API가 준비되지 않았습니다. GEMINI_API_KEY를 확인해주세요."
    
    try:
        # 기존 트리 아키텍처 컨텍스트 가져오기
        existing_tree = ss.get("current_tree", "")
        context_info = ""
        
        if existing_tree:
            context_info = f"""

기존 아키텍처 구조 (참고용):
{existing_tree}

위 구조를 기반으로 사용자의 새로운 요청을 처리해주세요. 
기존 구조와 일관성을 유지하면서 요청사항을 반영하거나 확장하세요.
"""
        
        # 클라우드 아키텍처 설계를 위한 프롬프트
        enhanced_prompt = f"""
사용자 요청: {user_message}

AWS 클라우드 아키텍처 전문가로서 답변해주세요. {context_info}

요청사항:
1. 사용자의 요청에 맞는 클라우드 아키텍처를 설계해주세요
2. 반드시 트리 구조로 표현해주세요 (예: ├─, │, └─ 문자 사용)
3. 트리구조는 응답에 1회만 표시해주세요
4. 각 컴포넌트의 역할과 연결 관계를 명확히 표시해주세요
5. 필요시 사용자에게 다시 질문하여 명확하게 하세요

중요 규칙:
- 모든 AWS 서비스와 리소스는 반드시 공식 영어 명칭을 사용하세요
- 예: EC2, S3, RDS, VPC, IAM, CloudFront, Lambda, ECS, EKS 등
- 한국어 설명은 가능하지만, 서비스명은 영어로 표기하세요
- 트리 구조에서 각 노드는 AWS 공식 서비스명을 사용하세요
- 기존 아키텍처가 있다면 일관성을 유지하면서 요청사항을 반영하세요

"""
        
        response = model.generate_content(enhanced_prompt)
        return response.text if response.text else "죄송합니다. 응답을 생성할 수 없습니다."
        
    except Exception as e:
        return f"❌ 오류가 발생했습니다: {str(e)}"

# =========================================
# 트리 구조 추출 및 저장 함수
# =========================================
def update_tree_structure(bot_response):
    """봇 응답에서 트리 구조를 추출하고 저장합니다."""
    tree_structure = extract_tree_structure(bot_response)
    if tree_structure:
        ss["current_tree"] = tree_structure
        return True
    return False

# =========================================
# 트리 구조 초기화 함수
# =========================================
def clear_tree_structure():
    """트리 구조를 초기화합니다."""
    ss["current_tree"] = ""
    st.success("트리 구조가 초기화되었습니다!")

# =========================================
# 다이어그램 생성 함수
# =========================================
def create_diagram_from_tree():
    """현재 트리 구조를 기반으로 Amazon Q를 통해 다이어그램 생성"""
    current_tree = ss.get("current_tree", "")
    
    if not current_tree:
        st.warning("⚠️ 다이어그램을 생성할 트리 구조가 없습니다. 먼저 아키텍처를 설계해주세요.")
        return
    
    try:
        with st.spinner("🎨 Amazon Q를 통해 다이어그램을 생성하고 있습니다..."):
            result = amazon_q_client.generate_diagram(current_tree)
            
            if result:
                st.success("✅ 다이어그램 생성 요청이 완료되었습니다!")
                st.info("📝 Amazon Q 응답:")
                st.code(result, language="text")
                
                # 생성된 다이어그램 파일 확인
                latest_diagram = diagram_manager.find_latest_diagram()
                if latest_diagram:
                    st.success(f"🎉 다이어그램 파일이 생성되었습니다: {latest_diagram.name}")
                    # 다이어그램을 세션 상태에 저장
                    ss["current_diagram"] = str(latest_diagram)
                    # 다이어그램 생성 완료 플래그 설정
                    ss["diagram_created"] = True
                    # 페이지 새로고침하여 다이어그램 표시
                    st.rerun()
                else:
                    st.info("📁 다이어그램 파일을 확인 중입니다...")
                    
            else:
                st.error("❌ 다이어그램 생성에 실패했습니다.")
                
    except Exception as e:
        st.error(f"❌ 다이어그램 생성 중 오류가 발생했습니다: {str(e)}")

# =========================================
# 다이어그램 표시 함수
# =========================================
def display_diagram():
    """현재 다이어그램을 표시합니다."""
    current_diagram = ss.get("current_diagram", "")
    
    if current_diagram and os.path.exists(current_diagram):
        try:
            # 다이어그램 이미지를 지정된 공간 크기에 맞춰 표시
            st.image(current_diagram, caption="생성된 아키텍처 다이어그램", use_container_width=True)
                    
        except Exception as e:
            st.error(f"❌ 다이어그램 표시 중 오류가 발생했습니다: {str(e)}")
            # 오류 발생 시 다이어그램 정보 초기화
            ss["current_diagram"] = ""
    else:
        # 다이어그램이 없을 때 기본 메시지 표시
        st.markdown(
            '<div class="card" style="height:460px; display:flex; align-items:center; justify-content:center; color:#888;">'
            '여기에 다이어그램이 표시됩니다.'
            '</div>',
            unsafe_allow_html=True
        )

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

.tree-display {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
    overflow-x: auto;
}

.tree-controls {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #dee2e6;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# 세션 상태 초기화
# =========================================
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 클라우드 아키텍처 설계를 도와드릴 수 있어요. 예를 들어 '서울 리전에 EC2 두 대 설치' 같은 요청을 주시면, 아키텍처 구조를 트리 형태로 만들어드릴 수 있습니다. 무엇을 도와드릴까요? 😊"}
    ]

if "current_tree" not in st.session_state:
    st.session_state["current_tree"] = ""

if "current_diagram" not in st.session_state:
    st.session_state["current_diagram"] = ""

if "diagram_created" not in st.session_state:
    st.session_state["diagram_created"] = False

ss = st.session_state

# =========================================
# 클라우드 아키텍처 다이어그램
# =========================================
st.markdown("<h3 style='text-align:left;'>Cloud Architecture Diagrams</h3>", unsafe_allow_html=True)

colA, colB = st.columns(2, gap="large")
with colA:
    # 제목(왼쪽) + 제작하기 버튼(오른쪽)을 한 줄에 배치
    _title_col, _btn_col = st.columns([0.8, 0.2])
    with _title_col:
        st.markdown('<div class="title">🌳 아키텍처 트리 구조</div>', unsafe_allow_html=True)
    with _btn_col:
        if st.button("제작하기", key="create_diagram_button", use_container_width=True):
            create_diagram_from_tree()
    
    # 트리 구조 표시 영역
    tree_placeholder = st.empty()
    with tree_placeholder.container():
        if ss.get("current_tree"):
            st.markdown(
                f'<div class="card" style="height:440px; overflow-y:auto; white-space:pre-wrap; color:#000; padding:15px; font-family: monospace; font-size:14px; line-height:1.6;">{ss["current_tree"]}</div>',
                unsafe_allow_html=True
            )
            

        else:
            st.markdown(
                '<div class="card" style="height:400px; display:flex; align-items:center; justify-content:center; color:#888;">'
                '여기에 아키텍처 트리 구조가 표시됩니다.' 
                '</div>',
                unsafe_allow_html=True
            )

with colB:
    st.markdown('<div class="title">🔐 보안 적용 다이어그램</div>', unsafe_allow_html=True)
    secure_placeholder = st.empty()
    with secure_placeholder.container():
        # 제작하기 버튼을 누르기 전에는 챗봇을 여기에 표시
        if not ss.get("diagram_created", False):
            # 챗봇을 보안 적용 다이어그램 공간에 표시
            st.markdown('<div class="chat-title">💬 챗봇</div>', unsafe_allow_html=True)
            with st.expander("아키텍처 설계 챗봇", expanded=True):
                # 챗봇 상태 표시 (에러일 때만 표시)
                if not api_ready:
                    st.error("❌ Gemini API가 준비되지 않았습니다.")
                    st.info("📝 .env 파일에 GEMINI_API_KEY=your_api_key_here 를 추가하세요.")
                
                # 챗봇 내용 렌더링
                chat_html = '<div class="chat-container">'
                for chat in ss["messages"]:
                    role = chat["role"]
                    content = chat["content"]
                    if role == "user":
                        chat_html += f"<div class='chat-bubble-wrapper user-bubble-wrapper'><div class='chat-bubble user-bubble'>{html.escape(content)}</div></div>"
                    else:
                        chat_html += f"<div class='chat-bubble-wrapper bot-bubble-wrapper'><div class='chat-bubble bot-bubble'>{html.escape(content)}</div></div>"
                chat_html += '</div>'
                st.markdown(chat_html, unsafe_allow_html=True)
                st.markdown('<div class="chat-input-spacer"></div>', unsafe_allow_html=True)

                # 입력창
                prompt = st.chat_input("아키텍처 요청사항을 입력하세요")
                if prompt and api_ready:
                    # 사용자 메시지 추가
                    ss["messages"].append({"role": "user", "content": prompt})
                    
                    # 챗봇 응답 생성
                    with st.spinner("🤔 아키텍처 설계 중..."):
                        bot_response = generate_chatbot_response(prompt)
                        ss["messages"].append({"role": "assistant", "content": bot_response})
                        
                        # 트리 구조 추출 및 저장
                        update_tree_structure(bot_response)
                    
                    # 페이지 새로고침
                    st.rerun()
                elif prompt and not api_ready:
                    st.error("API가 준비되지 않았습니다. 환경변수를 확인해주세요.")
        else:
            # 제작하기 버튼을 누른 후에는 다이어그램 표시
            display_diagram()

# 체크 리스트와 보안 요소 설명서를 한 줄에 배치
col1, col2 = st.columns(2, gap="large")

with col1:
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

with col2:
    with st.expander("✨ 보안 요소 설명서", expanded=False):
        recs = st.text_area(
            "추가 고려 사항 입력", 
            value=ss.get("board_suggestions", ""), 
            height=200, 
            label_visibility="collapsed"
        )
        ss["board_suggestions"] = recs

# 챗봇 영역 (제작하기 버튼을 누른 후에만 표시)
if ss.get("diagram_created", False):
    st.markdown('<div class="chat-title">💬 챗봇</div>', unsafe_allow_html=True)
    with st.expander("아키텍처 설계 챗봇", expanded=True):
        # 챗봇 상태 표시 (에러일 때만 표시)
        if not api_ready:
            st.error("❌ Gemini API가 준비되지 않았습니다.")
            st.info("📝 .env 파일에 GEMINI_API_KEY=your_api_key_here 를 추가하세요.")
        
        # 챗봇 내용 렌더링
        chat_html = '<div class="chat-container">'
        for chat in ss["messages"]:
            role = chat["role"]
            content = chat["content"]
            if role == "user":
                chat_html += f"<div class='chat-bubble-wrapper user-bubble-wrapper'><div class='chat-bubble user-bubble'>{html.escape(content)}</div></div>"
            else:
                chat_html += f"<div class='chat-bubble-wrapper bot-bubble-wrapper'><div class='chat-bubble bot-bubble'>{html.escape(content)}</div></div>"
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown('<div class="chat-input-spacer"></div>', unsafe_allow_html=True)

        # 입력창
        prompt = st.chat_input("아키텍처 요청사항을 입력하세요")
        if prompt and api_ready:
            # 사용자 메시지 추가
            ss["messages"].append({"role": "user", "content": prompt})
            
            # 챗봇 응답 생성
            with st.spinner("🤔 아키텍처 설계 중..."):
                bot_response = generate_chatbot_response(prompt)
                ss["messages"].append({"role": "assistant", "content": bot_response})
                
                # 트리 구조 추출 및 저장
                update_tree_structure(bot_response)
            
            # 페이지 새로고침
            st.rerun()
        elif prompt and not api_ready:
            st.error("API가 준비되지 않았습니다. 환경변수를 확인해주세요.")

