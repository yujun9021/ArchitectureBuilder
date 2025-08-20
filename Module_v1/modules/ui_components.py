"""
UI 컴포넌트 모듈
Streamlit UI 관련 컴포넌트들
"""

import streamlit as st
import json
import pyperclip
from datetime import datetime
from typing import Dict, Any, List


class UIComponents:
    """Streamlit UI 컴포넌트들"""
    
    @staticmethod
    def render_header():
        """헤더 렌더링"""
        st.title("⚡ AWS JSON Converter & Diagram Generator")
        st.markdown("**Gemini + Amazon Q CLI (실제 연동)**로 자연어를 JSON으로 구조화하고 실제 Amazon Q CLI가 다이어그램을 생성합니다.")
    
    @staticmethod
    def render_system_status(gemini_ready: bool, cli_status: Dict[str, Any]):
        """시스템 상태 표시"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if gemini_ready:
                st.success("✅ Gemini API 연결됨")
            else:
                st.error("❌ Gemini API 연결 실패")
        
        with col2:
            if cli_status["available"]:
                st.success(f"✅ Amazon Q CLI 연결됨")
                st.caption(f"버전: {cli_status['version']}")
            else:
                st.error("❌ Amazon Q CLI 연결 실패")
                st.caption(f"오류: {cli_status.get('error', '알 수 없음')}")
        
        with col3:
            st.info("🔄 CLI 우선, 실패 시 안전한 대체")
    
    @staticmethod
    def render_info_section():
        """정보 섹션 렌더링"""
        with st.expander("⚡ 빠른 Amazon Q 다이어그램 생성 (보안 제외)"):
            st.markdown("""
            ### 🎯 빠른 고품질 다이어그램 생성
            1. **실제 CLI 우선**: Amazon Q CLI와 실제로 대화하여 다이어그램 생성 시도
            2. **Amazon Q 역할 직접 수행**: CLI 실패 시 제가 Amazon Q 역할을 해서 빠른 다이어그램 생성
            3. **보안 요소 제외**: IAM, KMS, Security Groups 등 제외로 더 빠른 생성
            4. **핵심 요소 집중**: 고가용성, 모니터링, 네트워킹, 기업급 아키텍처에만 집중
            
            ### 🔄 빠른 처리 과정
            1. **🔄 프롬프트 최적화 (10%)**: Gemini가 빠른 생성용 JSON 생성
            2. **🤖 CLI 연결 (20%)**: Amazon Q CLI 프로세스 시작
            3. **💬 대화 시작 (30%)**: Amazon Q와 실제 대화 시도
            4. **⚡ 빠른 코드 생성 (40-70%)**: 보안 제외한 핵심 아키텍처 코드 작성
            5. **⚙️ 빠른 실행 (80-90%)**: 간소화된 코드로 빠른 다이어그램 생성
            6. **✅ 완료 (100%)**: 빠른 고품질 다이어그램 완성
            
            ### ⚡ 빠른 생성 특징
            - **보안 요소 제외**: IAM, KMS, Security Groups 등 제거로 빠른 생성
            - **핵심 요소 집중**: 고가용성, 모니터링, 네트워킹만 포함
            - **간소화된 구조**: 복잡한 보안 연결 제거로 깔끔한 다이어그램
            - **빠른 실행**: 적은 컴포넌트로 더 빠른 렌더링
            - **기업급 품질**: 보안 제외해도 프로덕션 수준의 아키텍처
            
            ### 🎯 포함되는 요소
            - ✅ **고가용성**: Multi-AZ, Auto Scaling, Load Balancer
            - ✅ **모니터링**: CloudWatch 메트릭, 로그, 성능 인사이트
            - ✅ **네트워킹**: VPC, 서브넷, 라우팅, DNS
            - ✅ **기업급 아키텍처**: 실제 프로덕션 환경 구조
            - ❌ **보안 요소**: IAM, KMS, Security Groups 제외
            """)
    
    @staticmethod
    def render_input_section() -> str:
        """입력 섹션 렌더링"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_area(
                "AWS 리소스 요청을 자연어로 입력하세요:",
                placeholder="예: EC2 인스턴스 3개를 생성해주세요",
                height=120,
                key="main_input"
            )
        
        with col2:
            st.markdown("### 💡 예시")
            st.markdown("""
            - "EC2 인스턴스 3개를 생성해주세요"
            - "S3 버킷을 만들고 암호화를 활성화해주세요"
            - "MySQL RDS 데이터베이스를 설정하고 싶어요"
            - "Lambda 함수로 API를 만들어주세요"
            - "VPC와 서브넷을 구성해주세요"
            - "고가용성 웹 서버 아키텍처를 구성해주세요"
            """)
        
        return user_input
    
    @staticmethod
    def render_generate_button() -> bool:
        """생성 버튼 렌더링"""
        return st.button("⚡ 빠른 Amazon Q 다이어그램 생성 (보안 제외)", type="primary", use_container_width=True)
    
    @staticmethod
    def render_json_copy_button(json_data: Dict[str, Any]):
        """JSON 복사 버튼 렌더링"""
        if st.button("📋 JSON 복사"):
            try:
                pyperclip.copy(json.dumps(json_data, indent=2, ensure_ascii=False))
                st.success("JSON이 클립보드에 복사되었습니다!")
            except:
                st.warning("클립보드 복사에 실패했습니다.")
    
    @staticmethod
    def render_diagram_result(diagram_path: str, method_used: str):
        """다이어그램 결과 렌더링"""
        if diagram_path:
            st.header("🖼️ 생성된 다이어그램")
            
            try:
                st.image(diagram_path, 
                        caption=f"AWS 아키텍처 다이어그램 ({method_used})", 
                        use_column_width=True)
                
                # 다운로드 버튼
                with open(diagram_path, "rb") as file:
                    st.download_button(
                        label="📥 다이어그램 다운로드",
                        data=file.read(),
                        file_name=f"aws_diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png"
                    )
                    
                # 파일 정보
                import os
                file_size = os.path.getsize(diagram_path)
                st.caption(f"파일 크기: {file_size:,} bytes | 생성 방식: {method_used}")
                
            except Exception as e:
                st.error(f"다이어그램 표시 실패: {str(e)}")
    
    @staticmethod
    def render_history(history: List[Dict[str, Any]]):
        """히스토리 렌더링"""
        if not history:
            return
        
        st.header("📚 생성 히스토리")
        
        # 최근 5개만 표시
        recent_history = list(reversed(history[-5:]))
        
        for i, item in enumerate(recent_history):
            if item.get("fallback_used", False):
                badge = "🔄 CLI→안전한대체"
            elif item.get("cli_used", False):
                badge = "🤖 실제 Amazon Q CLI"
            else:
                badge = "⚡ 안전한 대체"
            
            method_badge = item.get("diagram_method", "기본")
            
            with st.expander(f"{badge} ({method_badge}) #{len(history)-i} - {item['timestamp'][:19]}"):
                st.write("**입력:**")
                st.write(item['input'])
                
                st.write("**JSON 출력:**")
                try:
                    parsed = json.loads(item['json_output'])
                    st.json(parsed)
                except:
                    st.text(item['json_output'])
                
                # Amazon Q 응답 표시
                if item.get("amazon_q_response"):
                    with st.expander("📝 Amazon Q CLI 응답 보기"):
                        st.text_area("", item["amazon_q_response"], height=200, key=f"response_{i}")
                
                # 다이어그램 경로 표시
                if item.get("diagram_path"):
                    st.write(f"**다이어그램:** {item['diagram_path'].split('/')[-1]}")
                
                # 재사용 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🔄 다시 생성", key=f"retry_{i}"):
                        st.session_state.main_input = item['input']
                        st.rerun()
                
                with col2:
                    if st.button(f"📋 JSON 복사", key=f"copy_{i}"):
                        try:
                            pyperclip.copy(item['json_output'])
                            st.success("복사되었습니다!")
                        except:
                            st.warning("복사에 실패했습니다.")
        
        # 히스토리 삭제 버튼
        if st.button("🗑️ 히스토리 삭제", type="secondary"):
            return True  # 삭제 요청 신호
        
        return False
    
    @staticmethod
    def render_sidebar(gemini_handler, cli_generator):
        """사이드바 렌더링"""
        st.sidebar.header("🔧 설정")
        
        # 캐시 상태 표시
        cache_size = gemini_handler.get_cache_size()
        if cache_size > 0:
            st.sidebar.info(f"💾 캐시된 항목: {cache_size}개")
            if st.sidebar.button("🗑️ 캐시 삭제"):
                gemini_handler.clear_cache()
                st.sidebar.success("캐시가 삭제되었습니다!")
                st.rerun()
        
        # Amazon Q CLI 테스트 버튼
        if st.sidebar.button("🧪 Amazon Q CLI 기본 테스트"):
            with st.spinner("Amazon Q CLI 기본 테스트 중..."):
                test_result = cli_generator.test_cli()
                
                if test_result["success"]:
                    st.sidebar.success("✅ Amazon Q CLI 기본 테스트 성공!")
                    st.sidebar.text(f"버전: {test_result['version']}")
                    st.sidebar.caption(test_result['message'])
                else:
                    st.sidebar.error("❌ Amazon Q CLI 기본 테스트 실패")
                    st.sidebar.text(f"오류: {test_result['message']}")
        
        # 빠른 다이어그램 생성 테스트
        if st.sidebar.button("⚡ 빠른 다이어그램 생성 테스트"):
            with st.spinner("빠른 다이어그램 생성 테스트 중..."):
                test_result = cli_generator.quick_test_generation()
                
                if test_result["success"]:
                    st.sidebar.success("✅ 빠른 다이어그램 생성 성공!")
                    st.sidebar.text(f"파일 크기: {test_result['file_size']} bytes")
                    st.sidebar.caption(test_result['message'])
                else:
                    st.sidebar.error("❌ 빠른 다이어그램 생성 실패")
                    st.sidebar.text(f"오류: {test_result['message']}")
        
        # CLI 설정 정보
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ CLI 최적화 설정")
        st.sidebar.info("""
        **개선된 기능:**
        - 45초 타임아웃 (기존 30초)
        - 최적화된 간단한 프롬프트
        - 빠른 코드 추출 및 실행
        - 자동 코드 정리 및 보완
        - 직접 생성 대체 방법
        """)
        
        # 성능 팁
        st.sidebar.markdown("### 💡 성능 팁")
        st.sidebar.info("""
        **빠른 생성을 위한 팁:**
        - 간단한 요청 사용
        - 인스턴스 개수 3개 이하
        - 명확한 서비스명 명시
        - 복잡한 요구사항 피하기
        """)
    
    @staticmethod
    def render_footer():
        """푸터 렌더링"""
        st.markdown("---")
        st.markdown("""
        ### ⚡ 실제 Amazon Q CLI 다이어그램 생성 시스템의 특징
        - **🤖 실제 CLI**: Amazon Q CLI가 직접 다이어그램 생성 (모방이 아님)
        - **🔄 자동 대체**: CLI 실패 시 안정화된 생성기로 즉시 전환
        - **🛡️ 확실한 결과**: 어떤 상황에서도 다이어그램 생성 보장
        - **📊 투명성**: 사용된 생성 방식 명확히 표시
        - **⚡ 모듈화**: 기능별로 분리된 깔끔한 코드 구조
        - **👥 사용자 친화적**: 복잡한 선택 없이 자동으로 최적 방법 사용

        ### 💡 사용 팁
        - **실제 CLI 우선**: Amazon Q의 진짜 AI 기능 활용
        - **간단한 요청**: "EC2 3개", "S3 버킷" 등 명확하게 요청하세요
        - **즉시 결과**: 복잡한 설정 없이 바로 다이어그램 확인
        - **안정성 보장**: CLI 문제가 있어도 확실하게 다이어그램 생성
        - **투명한 과정**: 어떤 방식으로 생성되었는지 명확히 표시

        ### 🔧 모듈 구조
        - **GeminiHandler**: Gemini API 처리
        - **CLIDiagramGenerator**: 실제 Amazon Q CLI 다이어그램 생성
        - **SafeDiagramGenerator**: 안전한 대체 다이어그램 생성
        - **UIComponents**: 사용자 인터페이스 컴포넌트
        """)
    
    @staticmethod
    def show_success_message(message: str):
        """성공 메시지 표시"""
        st.success(message)
        st.balloons()
    
    @staticmethod
    def show_warning_message(message: str):
        """경고 메시지 표시"""
        st.warning(message)
    
    @staticmethod
    def show_error_message(message: str):
        """오류 메시지 표시"""
        st.error(message)
