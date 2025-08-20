"""
UI 컴포넌트 모듈
"""
import streamlit as st
import re
from config import SUPPORTED_PLATFORMS

def extract_code_from_gemini_response(response):
    """Gemini AI 응답에서 Python 코드 추출"""
    
    # Python 코드 블록 찾기 (```python ... ```)
    if "```python" in response:
        code_start = response.find("```python") + 9
        code_end = response.find("```", code_start)
        if code_end != -1:
            return response[code_start:code_end].strip()
    
    # Python 코드 블록 찾기 (``` ... ```) - 언어 지정 없음
    elif "```" in response:
        code_start = response.find("```") + 3
        code_end = response.find("```", code_start)
        if code_end != -1:
            code_content = response[code_start:code_end].strip()
            # Python 코드인지 확인 (import, from, with 등 키워드 포함)
            if any(keyword in code_content for keyword in ['import', 'from', 'with', 'def', 'class', 'Diagram']):
                return code_content
    
    # 코드가 없는 경우
    return None

class UIComponents:
    """UI 컴포넌트들"""
    
    @staticmethod
    def render_setup_guide():
        """설정 안내 섹션 렌더링"""
        with st.expander("⚙️ 설정 안내"):
            st.markdown("""
            ### 환경 설정
            `.env` 파일에 다음 설정을 추가하세요:
            
            ```bash
            # Gemini API 키 (필수)
            GOOGLE_API_KEY=your_gemini_api_key_here
            
            # Amazon Q CLI 경로 (선택사항, 기본값: 'q')
            AMAZON_Q_PATH=/path/to/q
            ```
            
            ### Amazon Q CLI 설치
            - **Windows**: `winget install Amazon.AmazonQ` 또는 [공식 사이트](https://aws.amazon.com/ko/amazon-q/)에서 다운로드
            - **Linux/Mac**: `curl -fsSL https://aws.amazon.com/ko/amazon-q/install.sh | sh`
            
            ### 지원 플랫폼
            """ + '\n'.join([f"- ✅ {platform}: {desc}" for platform, desc in SUPPORTED_PLATFORMS.items()]))
    
    @staticmethod
    def render_requirement_input():
        """요구사항 입력 섹션 렌더링"""
        st.header("📝 요구사항 입력")
        
        requirement = st.text_area(
            "클라우드 아키텍처 요구사항을 자세히 설명해주세요:",
            height=200,
            placeholder="예시: 웹 애플리케이션을 위한 고가용성 아키텍처가 필요합니다..."
        )
        
        return requirement
    
    @staticmethod
    def render_diagram_display(diagram_image):
        """다이어그램 표시 섹션 렌더링"""
        st.header("📊 생성된 다이어그램")
        
        if diagram_image:
            st.image(diagram_image, use_column_width=True)
            
            with open(diagram_image, "rb") as file:
                st.download_button(
                    label="📥 다이어그램 다운로드",
                    data=file.read(),
                    file_name="cloud_architecture.png",
                    mime="image/png"
                )
        else:
            st.info("👈 왼쪽에서 요구사항을 입력하고 다이어그램을 생성해보세요.")
    
    @staticmethod
    def render_code_display(diagram_code):
        """코드 표시 섹션 렌더링 (expander 형태)"""
        if diagram_code:
            with st.expander("💻 생성된 Python 코드", expanded=False):
                # 코드 블록의 높이를 고정 (300px)
                st.markdown(f"""
                <div style="height: 700px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; background-color: #f8f9fa;">
                    <pre style="margin: 0; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4;">
{diagram_code}
                    </pre>
                </div>
                """, unsafe_allow_html=True)
                
                col_download1, col_download2 = st.columns([1, 3])
                with col_download1:
                    st.download_button(
                        label="📥 Python 코드 다운로드",
                        data=diagram_code,
                        file_name="cloud_architecture.py",
                        mime="text/plain"
                    )
        else:
            # 코드가 없을 때는 접을 수 없는 형태로 표시
            st.info("💻 생성된 Python 코드가 여기에 표시됩니다.")
    
    @staticmethod
    def render_chatbot_toggle():
        """챗봇 토글 버튼 렌더링 (우측 상단용)"""
        # 우측 상단에 배치하기 위해 더 작은 버튼으로 변경
        button_text = "🤖 챗봇" if not st.session_state.get('chat_open', False) else "❌ 닫기"
        button_type = "secondary" if not st.session_state.get('chat_open', False) else "primary"
        
        if st.button(button_text, type=button_type, use_container_width=True):
            st.session_state.chat_open = not st.session_state.get('chat_open', False)
            st.rerun()
    
    @staticmethod
    def render_chatbot(chat_history, gemini_client):
        """챗봇 렌더링"""
        if st.session_state.get('chat_open', False):
            st.markdown("---")
            st.header("🤖 클라우드 아키텍처 설계 전문가")
            st.markdown("""
            **역할**: 클라우드 아키텍처 설계 전문가입니다.
            
            **작동 방식**:
            - 사용자의 요청에 따라 클라우드 아키텍처를 트리 형태로 설계합니다
            - AWS, Azure, GCP 등 주요 클라우드 플랫폼의 서비스를 활용합니다
            - 이전에 설계한 아키텍처를 기억하고 수정 요청에 참조합니다
            """)
            
            # 저장된 아키텍처 상태 표시
            if gemini_client.get_current_architecture():
                st.caption("💾 아키텍처가 저장되어 있습니다")
            
            # 챗봇 컨테이너
            chat_container = st.container()
            
            with chat_container:
                # 채팅 히스토리 표시
                for message in chat_history:
                    if message["role"] == "user":
                        st.chat_message("user").write(message["content"])
                    else:
                        st.chat_message("assistant").write(message["content"])
                
                # 사용자 입력
                if prompt := st.chat_input("질문을 입력하세요..."):
                    # 사용자 메시지 추가
                    chat_history.append({"role": "user", "content": prompt})
                    st.chat_message("user").write(prompt)
                    
                    # Gemini 응답 생성
                    with st.chat_message("assistant"):
                        with st.spinner("Gemini가 응답을 생성하고 있습니다..."):
                            response = gemini_client.generate_response(prompt, chat_history)
                            st.write(response)
                    
                    # 어시스턴트 메시지 추가
                    chat_history.append({"role": "assistant", "content": response})
                    
                    # 응답에서 아키텍처 추출 및 저장
                    if gemini_client.save_architecture(response):
                        st.success("✅ 아키텍처가 저장되었습니다!")
                    
                    # Gemini 응답에서 Python 코드 파싱하여 코드 블록에 표시
                    parsed_code = extract_code_from_gemini_response(response)
                    if parsed_code:
                        st.session_state.diagram_code = parsed_code
                        st.success("✅ Python 코드가 감지되어 코드 블록에 표시됩니다!")
            
            # 채팅 히스토리 초기화 버튼
            col_reset1, col_reset2 = st.columns([1, 4])
            with col_reset1:
                if st.button("🗑️ 대화 기록 초기화"):
                    chat_history.clear()
                    gemini_client.clear_architecture()  # 저장된 아키텍처도 초기화
                    st.rerun()
