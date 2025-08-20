"""
AWS JSON Converter & Diagram Generator (모듈화 버전)
실제 Amazon Q CLI를 사용한 다이어그램 생성기

모듈 구조:
- GeminiHandler: Gemini API 처리
- CLIDiagramGenerator: 실제 Amazon Q CLI 다이어그램 생성
- UIComponents: 사용자 인터페이스 컴포넌트
"""

import streamlit as st
import json
import os
import traceback
from datetime import datetime
from dotenv import load_dotenv

# 모듈 import (안전한 대체 생성기 제거)
from modules import GeminiHandler, CLIDiagramGenerator, UIComponents

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AWS Diagram Generator (모듈화)",
    page_icon="⚡",
    layout="wide"
)


class DiagramGeneratorApp:
    """AWS 다이어그램 생성기 메인 애플리케이션"""
    
    def __init__(self):
        self.initialize_components()
        self.initialize_session_state()
    
    def initialize_components(self):
        """컴포넌트 초기화 (안전한 대체 생성기 제거)"""
        if 'gemini_handler' not in st.session_state:
            st.session_state.gemini_handler = GeminiHandler()
        
        if 'cli_generator' not in st.session_state:
            st.session_state.cli_generator = CLIDiagramGenerator()
        
        if 'ui_components' not in st.session_state:
            st.session_state.ui_components = UIComponents()
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'conversion_history' not in st.session_state:
            st.session_state.conversion_history = []
        
        if 'latest_diagram' not in st.session_state:
            st.session_state.latest_diagram = None
    
    def run(self):
        """메인 애플리케이션 실행"""
        # 제목 및 설명
        st.session_state.ui_components.render_header()
        
        # 상태 정보 표시
        st.session_state.ui_components.render_status_info(
            gemini_ready=st.session_state.gemini_handler.is_ready(),
            cli_available=st.session_state.cli_generator.is_available(),
            cli_status=st.session_state.cli_generator.get_status()
        )
        
        # 메인 입력 및 처리
        self.render_main_interface()
        
        # 최신 다이어그램 표시
        if st.session_state.latest_diagram:
            st.session_state.ui_components.render_latest_diagram(st.session_state.latest_diagram)
        
        # 히스토리 표시
        if st.session_state.ui_components.render_history(st.session_state.conversion_history):
            st.session_state.conversion_history.clear()
            st.rerun()
    
    def render_main_interface(self):
        """메인 인터페이스 렌더링"""
        st.subheader("🎯 자연어 입력")
        
        # 사용자 입력
        user_input = st.text_area(
            "AWS 아키텍처 요구사항을 자연어로 입력하세요:",
            height=100,
            placeholder="예: 서울리전에 고가용성 웹 애플리케이션을 만들고 싶어요. 로드밸런서와 EC2 인스턴스, RDS 데이터베이스를 포함해서 구성해주세요."
        )
        
        # 생성 버튼
        if st.button("🚀 다이어그램 생성", type="primary", use_container_width=True):
            if user_input.strip():
                self.process_user_input(user_input.strip())
            else:
                st.warning("⚠️ 요구사항을 입력해주세요.")
    
    def process_user_input(self, user_input: str):
        """사용자 입력 처리"""
        try:
            # Gemini API 사용 가능 여부 확인
            if not st.session_state.gemini_handler.is_ready():
                st.error("❌ Gemini API가 준비되지 않았습니다. API 키를 확인해주세요.")
                return
            
            # JSON 구조화
            with st.spinner("🔄 자연어를 AWS JSON으로 구조화 중..."):
                json_result = st.session_state.gemini_handler.generate_aws_json(user_input)
            
            if not json_result:
                st.error("❌ JSON 구조화에 실패했습니다.")
                return
            
            # JSON 결과 표시
            st.session_state.ui_components.render_json_result(json_result)
            
            # 다이어그램 생성
            with st.spinner("🎨 다이어그램 생성 중..."):
                diagram_path = None
                response_message = ""
                method_used = ""
                
                # Amazon Q CLI만 사용 (안전한 대체 생성기 제거)
                if st.session_state.cli_generator.is_available():
                    st.subheader("🤖 Amazon Q CLI 다이어그램 생성 (실시간 진행상황)")
                    
                    try:
                        # 진행상황 표시와 함께 실제 CLI 사용
                        diagram_path, response_message = st.session_state.cli_generator.generate_diagram_with_progress(json_result)
                        
                        if response_message:
                            with st.expander("📝 Amazon Q CLI 응답 보기"):
                                st.text_area("Amazon Q CLI 응답:", response_message, height=200)
                        
                        if diagram_path:
                            st.session_state.ui_components.show_success_message("✅ Amazon Q CLI가 다이어그램을 생성했습니다!")
                            method_used = "Amazon Q CLI"
                        else:
                            st.session_state.ui_components.show_error_message("❌ Amazon Q CLI 다이어그램 생성에 실패했습니다.")
                            method_used = "실패"
                            
                    except Exception as e:
                        st.session_state.ui_components.show_error_message(f"❌ Amazon Q CLI 오류: {str(e)}")
                        method_used = "오류"
                else:
                    st.error("❌ Amazon Q CLI를 사용할 수 없습니다. CLI가 설치되어 있는지 확인해주세요.")
                    method_used = "CLI 사용 불가"
                
                # 결과 저장
                if diagram_path and os.path.exists(diagram_path):
                    st.session_state.latest_diagram = diagram_path
                    st.session_state.last_method_used = method_used
                
                # 히스토리에 추가
                self.add_to_history(
                    user_input=user_input,
                    json_result=json_result,
                    diagram_path=diagram_path,
                    response_message=response_message,
                    method_used=method_used
                )
                
        except Exception as e:
            st.session_state.ui_components.show_error_message(f"처리 중 오류가 발생했습니다: {str(e)}")
            st.error(f"상세 오류: {traceback.format_exc()}")
    
    def add_to_history(self, user_input: str, json_result: dict, diagram_path: str, 
                      response_message: str, method_used: str):
        """히스토리에 추가 (used_fallback 제거)"""
        st.session_state.conversion_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "json_output": json.dumps(json_result, ensure_ascii=False),
            "diagram_method": method_used,
            "diagram_path": diagram_path,
            "amazon_q_response": response_message,
            "cli_used": st.session_state.cli_generator.is_available(),
            "version": "Amazon Q CLI Only"
        })


def main():
    """메인 함수"""
    app = DiagramGeneratorApp()
    app.run()


if __name__ == "__main__":
    main()
