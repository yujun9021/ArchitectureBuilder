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

def extract_code_blocks(response):
    """응답에서 코드 블록만 추출"""
    import re
    
    # 코드 블록 패턴 찾기 (```python 또는 ``` 으로 시작하고 ``` 으로 끝나는 부분)
    code_pattern = r'```(?:python)?\s*\n(.*?)\n```'
    matches = re.findall(code_pattern, response, re.DOTALL)
    
    # 추출된 코드 블록들 반환
    return [match.strip() for match in matches if match.strip()]

def get_security_requirements():
    """보안 요구사항 체크박스 렌더링 및 선택된 항목 반환"""
    st.markdown("### 🛡️ 보안 요구사항 선택")
    st.markdown("아키텍처 설계 시 적용할 보안 요소들을 선택하세요:")
    
    # 보안 요소 데이터 (아키텍처 다이어그램 포함 가능성에 따라 분류)
    security_elements = {
        "🏗️ 아키텍처에 포함 가능": {
            "VPC": {
                "네트워크": [
                    {"설명": "Public/Private Subnet 분리", "필수": True, "적용방법": "외부 접근 최소화 구조 설계", "다이어그램_포함": True},
                    {"설명": "NACL 최소 권한 적용", "필수": True, "적용방법": "불필요한 트래픽 차단", "다이어그램_포함": True},
                    {"설명": "VPC 엔드포인트 사용", "필수": True, "적용방법": "S3, DynamoDB 등 안전 접근", "다이어그램_포함": True}
                ]
            },
            "EC2": {
                "네트워크": [
                    {"설명": "퍼블릭 서브넷 사용 자제", "필수": True, "적용방법": "사설 서브넷에 배치하여 외부 노출 최소화", "다이어그램_포함": True},
                    {"설명": "보안 그룹 최소화", "필수": True, "적용방법": "필요한 포트와 IP만 허용", "다이어그램_포함": True}
                ],
                "암호화": [
                    {"설명": "EBS 볼륨 암호화 활성화", "필수": True, "적용방법": "KMS 기반 암호화 적용", "다이어그램_포함": True}
                ]
            },
            "S3": {
                "접근제어": [
                    {"설명": "퍼블릭 접근 차단", "필수": True, "적용방법": "버킷 퍼블릭 액세스 차단 설정", "다이어그램_포함": True}
                ],
                "암호화": [
                    {"설명": "서버측 암호화(SSE) 활성화", "필수": True, "적용방법": "버킷 기본 암호화 적용", "다이어그램_포함": True}
                ]
            },
            "RDS": {
                "네트워크": [
                    {"설명": "퍼블릭 접근 차단", "필수": True, "적용방법": "VPC 서브넷 그룹 내에서만 접근 허용", "다이어그램_포함": True}
                ],
                "암호화": [
                    {"설명": "저장소 및 백업 암호화 활성화", "필수": True, "적용방법": "KMS 기반 암호화 적용", "다이어그램_포함": True}
                ]
            },
            "Lambda": {
                "암호화": [
                    {"설명": "환경 변수 암호화 적용", "필수": True, "적용방법": "민감 정보 KMS로 암호화 저장", "다이어그램_포함": True}
                ]
            },
            "CloudFront_ALB_API": {
                "네트워크": [
                    {"설명": "TLS/HTTPS 적용", "필수": True, "적용방법": "모든 엔드포인트 HTTPS 사용", "다이어그램_포함": True}
                ]
            },
            "EFS_FSx": {
                "암호화": [
                    {"설명": "파일 스토리지 암호화", "필수": True, "적용방법": "KMS 기반 암호화 적용", "다이어그램_포함": True},
                    {"설명": "VPC 내 접근 제한", "필수": True, "적용방법": "VPC 보안 그룹 및 NACL을 통한 접근 제어", "다이어그램_포함": True}
                ]
            },
            "ELB": {
                "보안": [
                    {"설명": "HTTP → HTTPS 리디렉션 적용", "필수": True, "적용방법": "ALB의 모든 HTTP 리스너에 대해 HTTPS 리디렉션 구성", "다이어그램_포함": True},
                    {"설명": "HTTPS/TLS 리스너 구성", "필수": True, "적용방법": "CLB 및 ALB 프런트엔드 리스너를 HTTPS 또는 TLS로 설정", "다이어그램_포함": True},
                    {"설명": "가용 영역 분산", "필수": True, "적용방법": "ELB를 최소 2개 이상의 AZ에 걸쳐 구성", "다이어그램_포함": True}
                ]
            }
        },
        "⚙️ 설정/정책 기반": {
            "IAM": {
                "접근제어": [
                    {"설명": "사용자, 그룹, 역할 최소 권한 적용", "필수": True, "적용방법": "원하는 권한만 IAM 정책에 부여", "다이어그램_포함": False},
                    {"설명": "MFA(다중 인증) 활성화", "필수": True, "적용방법": "루트 계정 및 중요한 사용자 계정에 MFA 적용", "다이어그램_포함": False},
                    {"설명": "루트 계정 사용 최소화", "필수": True, "적용방법": "일상적 운영은 IAM 계정 사용, 루트 계정은 긴급 시만 사용", "다이어그램_포함": False},
                    {"설명": "Access Key 관리 및 주기적 교체", "필수": True, "적용방법": "키 주기적 회전 및 불필요한 키 삭제", "다이어그램_포함": False}
                ]
            },
            "EC2": {
                "접근제어": [
                    {"설명": "IAM 역할 기반 접근", "필수": True, "적용방법": "EC2 인스턴스마다 최소 권한 IAM 역할 연결", "다이어그램_포함": False},
                    {"설명": "인스턴스 프로파일 권한 최소화", "필수": True, "적용방법": "필요한 권한만 IAM 역할에 부여", "다이어그램_포함": False}
                ]
            },
            "S3": {
                "접근제어": [
                    {"설명": "버킷 정책 최소 권한 적용", "필수": True, "적용방법": "권한이 필요한 사용자/서비스만 접근", "다이어그램_포함": False}
                ]
            },
            "RDS": {
                "접근제어": [
                    {"설명": "IAM 인증 및 DB 사용자 최소 권한", "필수": True, "적용방법": "DB 계정과 IAM 권한 최소화", "다이어그램_포함": False},
                    {"설명": "보안 그룹 최소 권한 적용", "필수": True, "적용방법": "DB 전용 보안 그룹 적용", "다이어그램_포함": False}
                ]
            },
            "Lambda": {
                "접근제어": [
                    {"설명": "IAM 역할 최소 권한 적용", "필수": True, "적용방법": "Lambda 함수별 최소 권한 역할 연결", "다이어그램_포함": False}
                ]
            },
            "ELB": {
                "보안": [
                    {"설명": "인증서 관리", "필수": True, "적용방법": "ACM 인증서를 HTTPS/SSL 리스너에 적용", "다이어그램_포함": False}
                ]
            }
        },
        "📊 모니터링/로깅": {
            "CloudTrail": {
                "모니터링": [
                    {"설명": "계정 활동 로깅", "필수": True, "적용방법": "모든 리전에서 CloudTrail 활성화", "다이어그램_포함": False},
                    {"설명": "감사 및 이상 탐지용", "필수": True, "적용방법": "로그를 CloudWatch와 연계하여 모니터링", "다이어그램_포함": False},
                    {"설명": "S3와 연계하여 로그 안전하게 보관", "필수": True, "적용방법": "버킷 정책과 암호화 적용", "다이어그램_포함": False}
                ]
            }
        },
        "🔐 보안 서비스": {
            "SecretsManager": {
                "암호화": [
                    {"설명": "민감 정보 안전 저장 및 자동 암호화", "필수": True, "적용방법": "Secrets Manager 또는 Parameter Store 사용, KMS 기반 암호화 적용", "다이어그램_포함": True}
                ]
            }
        }
    }
    
    selected_security = []
    
    # 분류별로 체크박스 렌더링
    for category_name, services in security_elements.items():
        with st.expander(f"{category_name}", expanded=False):
            for service, categories in services.items():
                st.markdown(f"**🔒 {service}:**")
                for category, items in categories.items():
                    st.markdown(f"*{category}:*")
                    for item in items:
                        key = f"{category_name}_{service}_{category}_{item['설명']}"
                        checkbox_text = f"✅ {item['설명']}"
                        if item.get('다이어그램_포함', False):
                            checkbox_text += " 🏗️"
                        else:
                            checkbox_text += " ⚙️"
                        
                        if st.checkbox(checkbox_text, key=key, value=False):
                            selected_security.append({
                                "서비스": service,
                                "카테고리": category,
                                "설명": item['설명'],
                                "적용방법": item['적용방법'],
                                "다이어그램_포함": item.get('다이어그램_포함', False)
                            })
    
    return selected_security

def main():
    """메인 애플리케이션"""
    # 제목과 챗봇 버튼을 한 줄에 배치
    col_title, col_chat = st.columns([4, 1])
    
    with col_title:
        st.title("☁️ 클라우드 아키텍처 다이어그램 생성기")
        st.markdown("Amazon Q와 DiagramMCP를 사용하여 클라우드 아키텍처 다이어그램을 생성합니다.")
    
    with col_chat:
        st.markdown("")  # 여백 추가
        st.markdown("")  # 여백 추가
        UIComponents.render_chatbot_toggle()
    
    # 클라이언트 초기화
    gemini_client = GeminiClient()
    amazon_q_client = AmazonQClient()
    diagram_manager = DiagramManager()
    
    # 코드 블록과 다이어그램 공간
    col_code, col_diagram = st.columns([1, 1])
    
    with col_code:
        st.subheader("💻 아키텍처 설계")
        
        # Gemini AI 응답의 아키텍처 텍스트가 있으면 표시
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            # 가장 최근 Gemini AI 응답에서 아키텍처 관련 텍스트 찾기
            latest_response = None
            for message in reversed(st.session_state.chat_history):
                if message["role"] == "assistant":
                    latest_response = message["content"]
                    break
            
            if latest_response:
                # 아키텍처 관련 키워드가 포함된 응답인지 확인
                architecture_keywords = ['아키텍처', 'architecture', 'AWS', '클라우드', 'cloud', '서비스', 'service', 'VPC', 'EC2', 'S3', 'Lambda']
                if any(keyword in latest_response for keyword in architecture_keywords):
                    # 코드 블록만 추출
                    code_blocks = extract_code_blocks(latest_response)
                    
                    if code_blocks:
                        st.markdown("**🤖 Gemini AI가 설계한 아키텍처 코드:**")
                        for i, code_block in enumerate(code_blocks):
                            # 코드 블록의 높이를 고정 (400px)
                            st.markdown(f"""
                            <div style="height: 400px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; background-color: #f8f9fa;">
                                <pre style="margin: 0; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4;">
{code_block}
                                </pre>
                            </div>
                            """, unsafe_allow_html=True)
                            if i < len(code_blocks) - 1:  # 마지막이 아니면 구분선 추가
                                st.divider()
                    else:
                        st.info("👈 Gemini AI 응답에 코드 블록이 없습니다.")
                else:
                    st.info("👈 Gemini AI와 아키텍처 설계에 대해 대화해보세요.")
            else:
                st.info("👈 Gemini AI와 아키텍처 설계에 대해 대화해보세요.")
        else:
            st.info("👈 Gemini AI와 아키텍처 설계에 대해 대화해보세요.")
    
    with col_diagram:
        st.subheader("🖼️ 다이어그램 예시")
        # 기존 다이어그램 표시 공간을 여기로 이동
        if st.session_state.diagram_image:
            st.image(st.session_state.diagram_image, use_column_width=True)
            
            with open(st.session_state.diagram_image, "rb") as file:
                st.download_button(
                    label="📥 다이어그램 다운로드",
                    data=file.read(),
                    file_name="cloud_architecture.png",
                    mime="image/png"
                )
        else:
            st.info("👈 다이어그램을 생성하면 여기에 표시됩니다.")
    
    # 보안 요구사항 선택 (코드 블록과 챗봇 사이)
    selected_security = get_security_requirements()
    
    # 선택된 보안 요소들을 세션 상태에 저장
    st.session_state.selected_security = selected_security
    
    # 챗봇 렌더링 (보안 요구사항 아래)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    UIComponents.render_chatbot(st.session_state.chat_history, gemini_client, selected_security)
    
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
        st.subheader("📊 생성된 다이어그램")
        st.info("👈 왼쪽에서 요구사항을 입력하고 다이어그램을 생성해보세요.")
    
    # 생성된 코드 표시 (간단하게)
    if 'diagram_code' in st.session_state and st.session_state.diagram_code:
        if "```python" in st.session_state.diagram_code or "import" in st.session_state.diagram_code:
            st.code(st.session_state.diagram_code, language="python", line_numbers=True)

if __name__ == "__main__":
    main()
