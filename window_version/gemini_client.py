"""
Gemini API 클라이언트 모듈
"""
import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY

class GeminiClient:
    """Gemini API 클라이언트"""
    
    # 클래스 변수로 system_prompt 정의
    SYSTEM_PROMPT = """당신은 클라우드 아키텍처 설계 전문가입니다.

**역할:**
- 사용자의 요청에 따라 AWS 클라우드 아키텍처를 트리 형태로 설계하고 수정합니다

**출력 규칙:**
- 항상 tree 코드 블록 안에 트리 구조만 출력합니다.
- 트리에는 사용자 요구사항에서 등장한 서비스와 구성 요소만 포함합니다.
- 다른 문장, 설명, 예시, 주석은 절대 출력하지 않습니다.
- **중요**: 아키텍처를 출력할 때는 반드시 완성된 하나의 트리만 출력합니다
- 매 응답마다 하나의 완성된 트리 전체만 출력합니다.
- 사용자의 요청을 그대로 트리형태의 아키텍처로로 생성합니다

**수정 요청 처리:**
- "추가" 요청 시: 기존 수량 + 추가 수량으로 정확히 계산
- "변경" 요청 시: 기존 아키텍처를 기반으로 정확히 수정
- "설치" 요청 시: 기존 아키텍처에 새로운 구성요소를 추가
- 수량 계산을 명확히 하고 오류를 방지합니다
"""
    
    def __init__(self):
        """클라이언트 초기화"""
        self.model = None  # Gemini 모델
        self.current_architecture = None  # 현재 아키텍처 저장
        self.initialize_gemini()  # Gemini API 초기화
    
    def initialize_gemini(self):
        """Gemini API 초기화"""
        try:
            # API 키 확인
            if not GOOGLE_API_KEY:
                return False
            
            # Gemini API 설정
            genai.configure(api_key=GOOGLE_API_KEY)
            
            # 클래스 변수 SYSTEM_PROMPT를 사용하여 모델 초기화
            self.model = genai.GenerativeModel('gemini-2.0-flash', 
                                             system_instruction=self.SYSTEM_PROMPT)
            
            return True
            
        except Exception as e:
            st.error(f"Gemini API 초기화 실패: {str(e)}")
            return False
    
    def _get_current_context(self):
        """현재 아키텍처 컨텍스트 생성"""
        if self.current_architecture:
            return f"""
**현재 아키텍처:**
다음은 이전에 설계한 아키텍처입니다. 수정 요청 시 이를 기반으로 응답하세요:

```tree
{self.current_architecture}
```"""
        return ""
    
    def generate_response(self, prompt, chat_history=None):
        """Gemini API를 호출하여 응답 생성"""
        try:
            # API 키 설정 확인
            if not self.model:
                return "❌ Gemini API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 추가해주세요."
            
            # 현재 컨텍스트 가져오기
            current_context = self._get_current_context()
            
            # 채팅 히스토리가 있는 경우
            if chat_history:
                # 새로운 채팅 세션 시작
                chat = self.model.start_chat(history=[])
                # 시스템 프롬프트와 현재 컨텍스트를 첫 메시지로 전송
                chat.send_message(self.SYSTEM_PROMPT + current_context)
                
                # 최근 20개 메시지만 처리하여 컨텍스트 유지
                for message in chat_history[-20:]:
                    if message["role"] == "user":
                        # 사용자 메시지 전송
                        chat.send_message(message["content"])
                    elif message["role"] == "assistant":
                        # 어시스턴트 응답 전송
                        chat.send_message(message["content"])
                
                # 현재 프롬프트에 대한 응답 생성
                response = chat.send_message(prompt)
            else:
                # 채팅 히스토리가 없는 경우 단일 요청으로 처리
                full_prompt = f"{self.SYSTEM_PROMPT}\n\n{current_context}\n\n사용자: {prompt}"
                response = self.model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            return f"❌ Gemini API 호출 중 오류가 발생했습니다: {str(e)}"
    
    def save_architecture(self, response_text):
        """응답에서 아키텍처를 추출하고 저장"""
        import re
        
        # 트리 형태 아키텍처 추출
        tree_pattern = r'```tree\s*\n(.*?)\n```'
        tree_blocks = re.findall(tree_pattern, response_text, re.DOTALL)
        
        if tree_blocks:
            # 가장 최근 트리 블록을 현재 아키텍처로 저장
            self.current_architecture = tree_blocks[-1].strip()
            return True
        return False
    
    def get_current_architecture(self):
        """현재 저장된 아키텍처 반환"""
        return self.current_architecture
    
    def clear_architecture(self):
        """저장된 아키텍처 초기화"""
        self.current_architecture = None
    
    def is_ready(self):
        """Gemini API가 준비되었는지 확인"""
        return self.model is not None
