"""
Gemini API 클라이언트 모듈
"""
import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY

class GeminiClient:
    """Gemini API 클라이언트"""
    
    def __init__(self):
        self.model = None
        self.initialize_gemini()
    
    def initialize_gemini(self):
        """Gemini API 초기화"""
        try:
            if not GOOGLE_API_KEY:
                return False
            
            # Gemini API 설정
            genai.configure(api_key=GOOGLE_API_KEY)
            
            # 모델 초기화 (최신 모델명 사용)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            return True
            
        except Exception as e:
            st.error(f"Gemini API 초기화 실패: {str(e)}")
            return False
    
    def generate_response(self, prompt, chat_history=None, selected_security=None):
        """Gemini API를 호출하여 응답 생성"""
        try:
            if not self.model:
                return "❌ Gemini API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 추가해주세요."
            
            # 클라우드 아키텍처 전문가 시스템 프롬프트
            system_prompt = """당신은 클라우드 아키텍처 설계 전문가입니다. 

**역할과 책임:**
- 사용자와 소통하며 완성된 클라우드 아키텍처를 단계별로 설계합니다
- 사용자의 요청이 모호하거나 불완전하면 추가 질문으로 명확히 합니다
- 변경점이 명확하고 구체적일 때만 클라우드 아키텍처를 출력합니다
- AWS, Azure, GCP 등 주요 클라우드 플랫폼의 서비스와 아키텍처 패턴에 전문성을 가집니다

**작동 원칙:**
1. **명확성 확보**: 요청이 모호하면 구체적인 질문으로 명확히 합니다
   - 예: "어떤 규모의 시스템인가요?", "예상 트래픽은 얼마나 되나요?", "보안 요구사항은 무엇인가요?"

2. **단계별 설계**: 아키텍처를 한 번에 완성하지 말고 단계별로 발전시킵니다
   - 1단계: 기본 요구사항 파악
   - 2단계: 아키텍처 구성요소 설계
   - 3단계: 상세 아키텍처 다이어그램 생성

3. **명확한 출력**: 변경점이 명확할 때만 아키텍처를 출력합니다
   - 아키텍처 출력 시 ```python 코드 블록으로 diagrams 라이브러리 코드를 생성합니다
   - 아키텍처 설명과 함께 제공합니다

4. **지속적 개선**: 사용자 피드백을 받아 아키텍처를 지속적으로 개선합니다

**응답 형식:**
- 일반 대화: 자연스러운 대화로 진행
- 아키텍처 출력: 명확한 요청이 있을 때만 ```python 코드 블록으로 출력

이제 사용자와 함께 완성된 클라우드 아키텍처를 설계해보겠습니다."""
            
            # 선택된 보안 요소가 있으면 시스템 프롬프트에 추가
            if selected_security:
                # 다이어그램에 포함 가능한 보안 요소와 설정 기반 요소 분리
                diagram_security = [item for item in selected_security if item.get('다이어그램_포함', False)]
                config_security = [item for item in selected_security if not item.get('다이어그램_포함', False)]
                
                security_context = "\n\n**🔒 선택된 보안 요구사항:**\n"
                
                # 다이어그램에 포함 가능한 요소들
                if diagram_security:
                    security_context += "\n**🏗️ 아키텍처 다이어그램에 포함할 보안 요소:**\n"
                    for item in diagram_security:
                        security_context += f"- **{item['서비스']} ({item['카테고리']})**: {item['설명']}\n"
                        security_context += f"  - 적용방법: {item['적용방법']}\n"
                
                # 설정/정책 기반 요소들
                if config_security:
                    security_context += "\n**⚙️ 설정/정책 기반 보안 요소 (다이어그램 외 별도 적용):**\n"
                    for item in config_security:
                        security_context += f"- **{item['서비스']} ({item['카테고리']})**: {item['설명']}\n"
                        security_context += f"  - 적용방법: {item['적용방법']}\n"
                
                security_context += "\n**중요**: 🏗️ 표시된 요소들은 아키텍처 다이어그램에 반영하고, ⚙️ 표시된 요소들은 별도 설정으로 적용해주세요."
                system_prompt += security_context

            # 채팅 히스토리가 있으면 컨텍스트로 사용
            if chat_history:
                # 채팅 히스토리를 Gemini 형식으로 변환
                chat = self.model.start_chat(history=[])
                
                # 첫 번째 메시지로 시스템 프롬프트 전송
                chat.send_message(system_prompt)
                
                for message in chat_history[-10:]:  # 최근 10개 메시지만 사용
                    if message["role"] == "user":
                        chat.send_message(message["content"])
                    # Gemini는 자동으로 응답을 기록하므로 사용자 메시지만 전송
                
                response = chat.send_message(prompt)
            else:
                # 단일 메시지 요청 (시스템 프롬프트 포함)
                full_prompt = f"{system_prompt}\n\n사용자: {prompt}"
                response = self.model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            return f"❌ Gemini API 호출 중 오류가 발생했습니다: {str(e)}"
    
    def is_ready(self):
        """Gemini API가 준비되었는지 확인"""
        return self.model is not None
