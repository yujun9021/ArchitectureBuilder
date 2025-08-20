"""
클라우드 아키텍처 다이어그램 생성기 - 메인 애플리케이션
"""
import streamlit as st
from config import PAGE_CONFIG
from gemini_client import GeminiClient
from amazon_q_client import AmazonQClient
from response_parser import ResponseParser
from diagram_manager import DiagramManager
from ui_components import UIComponents

# 페이지 설정
st.set_page_config(**PAGE_CONFIG)

# 세션 상태 초기화
if 'diagram_code' not in st.session_state:
    st.session_state.diagram_code = ""
if 'diagram_image' not in st.session_state:
    st.session_state.diagram_image = None

def main():
    """메인 애플리케이션"""
    st.title("☁️ 클라우드 아키텍처 다이어그램 생성기")
    st.markdown("Amazon Q와 DiagramMCP를 사용하여 클라우드 아키텍처 다이어그램을 생성합니다.")
    
    # 클라이언트 초기화
    gemini_client = GeminiClient()
    amazon_q_client = AmazonQClient()
    diagram_manager = DiagramManager()
    
    # 설정 안내
    UIComponents.render_setup_guide()
    
    # 메인 컨텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        requirement = UIComponents.render_requirement_input()
        
        if st.button("🚀 아키텍처 다이어그램 생성", type="primary"):
            if requirement:
                with st.spinner("Amazon Q CLI를 통해 다이어그램을 생성하고 있습니다..."):
                    q_response = amazon_q_client.generate_diagram(requirement)
                    
                    if q_response:
                        # Amazon Q 응답 파싱
                        parsed_response = ResponseParser.parse_response(q_response)
                        
                        # 파싱 결과 표시
                        st.info(f"📄 응답 상태: {parsed_response['status']}")
                        if parsed_response['filename']:
                            st.info(f"📄 추출된 파일명: {parsed_response['filename']}")
                        if parsed_response['description']:
                            st.info(f"📝 아키텍처 설명: {parsed_response['description']}")
                        
                        # 다이어그램 파일 찾기
                        if parsed_response['filename']:
                            target_file, exists = diagram_manager.find_diagram_file(parsed_response['filename'])
                            
                            if exists:
                                st.success("✅ 다이어그램 생성 완료")
                                st.session_state.diagram_image = str(target_file)
                            else:
                                st.warning(f"⚠️ 파일을 찾을 수 없습니다: {parsed_response['filename']}")
                                diagram_manager.display_debug_info(parsed_response['filename'])
                        else:
                            # 폴더 내 최신 PNG 파일 찾기
                            latest_file = diagram_manager.find_latest_diagram()
                            if latest_file:
                                st.success("✅ 다이어그램 생성 완료")
                                st.session_state.diagram_image = str(latest_file)
                            else:
                                st.error("❌ 다이어그램 파일을 찾을 수 없습니다.")
                        
                        # Python 코드 저장
                        if parsed_response['code']:
                            st.session_state.diagram_code = parsed_response['code']
                        else:
                            st.session_state.diagram_code = q_response
                    else:
                        st.error("❌ 다이어그램 생성 실패")
            else:
                st.warning("⚠️ 요구사항을 입력해주세요.")
    
    with col2:
        UIComponents.render_diagram_display(st.session_state.diagram_image)
    
    # 생성된 코드 표시
    UIComponents.render_code_display(st.session_state.diagram_code)
    
    # 챗봇 토글 버튼
    UIComponents.render_chatbot_toggle()
    
    # 챗봇 렌더링
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    UIComponents.render_chatbot(st.session_state.chat_history, gemini_client)

if __name__ == "__main__":
    main()
