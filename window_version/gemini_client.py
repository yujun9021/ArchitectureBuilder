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
    
    def generate_response(self, prompt, chat_history=None):
        """Gemini API를 호출하여 응답 생성"""
        try:
            if not self.model:
                return "❌ Gemini API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 추가해주세요."
            
            # 채팅 히스토리가 있으면 컨텍스트로 사용
            if chat_history:
                # 채팅 히스토리를 Gemini 형식으로 변환
                chat = self.model.start_chat(history=[])
                for message in chat_history[-10:]:  # 최근 10개 메시지만 사용
                    if message["role"] == "user":
                        chat.send_message(message["content"])
                    # Gemini는 자동으로 응답을 기록하므로 사용자 메시지만 전송
                
                response = chat.send_message(prompt)
            else:
                # 단일 메시지 요청
                response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"❌ Gemini API 호출 중 오류가 발생했습니다: {str(e)}"
    
    def is_ready(self):
        """Gemini API가 준비되었는지 확인"""
        return self.model is not None
