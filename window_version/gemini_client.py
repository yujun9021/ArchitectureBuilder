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
        self.current_architecture = None  # 현재 아키텍처 저장
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
    
    def generate_response(self, prompt, chat_history=None):
        """Gemini API를 호출하여 응답 생성"""
        try:
            if not self.model:
                return "❌ Gemini API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 추가해주세요."
            
            # 클라우드 아키텍처 전문가 시스템 프롬프트
            system_prompt = """당신은 클라우드 아키텍처 설계 전문가입니다.

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

            # 현재 저장된 아키텍처가 있으면 시스템 프롬프트에 추가
            if self.current_architecture:
                system_prompt += f"""

**현재 아키텍처:**
다음은 이전에 설계한 아키텍처입니다. 수정 요청 시 이를 기반으로 응답하세요:

```tree
{self.current_architecture}
```"""
            


            # 채팅 히스토리가 있으면 컨텍스트로 사용
            if chat_history:
                # 채팅 히스토리를 Gemini 형식으로 변환
                chat = self.model.start_chat(history=[])
                
                # 첫 번째 메시지로 시스템 프롬프트 전송
                chat.send_message(system_prompt)
                
                # 전체 대화 기록을 전송 (최근 20개 메시지로 확장)
                for message in chat_history[-20:]:  # 최근 20개 메시지로 확장
                    if message["role"] == "user":
                        chat.send_message(message["content"])
                    elif message["role"] == "assistant":
                        # 어시스턴트 응답도 명시적으로 전송하여 컨텍스트 유지
                        chat.send_message(message["content"])
                
                response = chat.send_message(prompt)
            else:
                # 단일 메시지 요청 (시스템 프롬프트 포함)
                full_prompt = f"{system_prompt}\n\n사용자: {prompt}"
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
            # 가장 최근 트리 블록을 저장
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
