"""
UI 컴포넌트 모듈
"""
import streamlit as st
from config import SUPPORTED_PLATFORMS

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
        """코드 표시 섹션 렌더링"""
        if diagram_code:
            st.header("💻 생성된 Python 코드")
            st.code(diagram_code, language="python")
            
            st.download_button(
                label="📥 Python 코드 다운로드",
                data=diagram_code,
                file_name="cloud_architecture.py",
                mime="text/plain"
            )
    
    @staticmethod
    def render_chatbot_toggle():
        """챗봇 토글 버튼 렌더링"""
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🤖 챗봇 열기" if not st.session_state.get('chat_open', False) else "❌ 챗봇 닫기"):
                st.session_state.chat_open = not st.session_state.get('chat_open', False)
                st.rerun()
    
    @staticmethod
    def render_chatbot(chat_history, gemini_client):
        """챗봇 렌더링"""
        if st.session_state.get('chat_open', False):
            st.markdown("---")
            st.header("🤖 Gemini AI 챗봇")
            st.markdown("클라우드 아키텍처에 대해 질문하거나 대화해보세요.")
            
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
            
            # 채팅 히스토리 초기화 버튼
            col_reset1, col_reset2 = st.columns([1, 4])
            with col_reset1:
                if st.button("🗑️ 대화 기록 초기화"):
                    chat_history.clear()
                    st.rerun()
