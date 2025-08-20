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
        self.architectures = []  # 아키텍처 저장소
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
   - 아키텍처 출력 시 ```tree 코드 블록으로 트리 구조를 생성합니다
   - 아키텍처 설명과 함께 제공합니다

4. **지속적 개선**: 사용자 피드백을 받아 아키텍처를 지속적으로 개선합니다

**아키텍처 기억 및 수정:**
- 이전에 설계한 아키텍처를 항상 기억하고 참조합니다
- 사용자가 "수정해줘", "변경해줘" 등의 요청을 할 때 이전 아키텍처를 기반으로 수정합니다
- 아키텍처 수정 시 "기존 아키텍처를 기반으로 다음과 같이 수정했습니다:" 형태로 명확히 표시합니다
- 트리 형태 아키텍처를 수정할 때는 전체 아키텍처를 다시 출력합니다

**응답 형식:**
- 일반 대화: 자연스러운 대화로 진행
- 아키텍처 출력: 명확한 요청이 있을 때만 트리 형태로 출력:
  **트리 형태 아키텍처**: ```tree로 시작하는 코드 블록으로 트리 구조 출력

**트리 형태 아키텍처 예시:**
```tree
REGION: ap-northeast-2 (Seoul)
└── [Regional Service] S3 Bucket  ──(정적 파일 저장; VPC 바깥에 존재)

VPC: 10.0.0.0/16
├── Internet Gateway (IGW)  ──(외부에서 VPC로 진입)
├── Application Load Balancer (ALB)  ──(퍼블릭 서브넷 A/C에 연결됨; 들어오는 트래픽 분산)
│
├─ AZ: ap-northeast-2a
│  ├─ Public Subnet A (10.0.1.0/24)
│  │   ├─ [ALB Attachment]
│  │   ├─ NAT Gateway A
│  │   └─ Web EC2 (ASG) : web-a-1, web-a-2  ──(퍼블릭; ALB가 타깃으로 트래픽 전달)
│  │
│  ├─ Private-App Subnet A (10.0.11.0/24)
│  │   └─ App EC2 (ASG) : app-a-1, app-a-2  ──(프라이빗; Web에서 내부 호출)
│  │
│  └─ Private-DB Subnet A (10.0.21.0/24)
│      └─ RDS for PostgreSQL (Primary)  ──(Multi-AZ의 주 인스턴스)
│
└─ AZ: ap-northeast-2c
   ├─ Public Subnet C (10.0.2.0/24)
   │   ├─ [ALB Attachment]
   │   ├─ NAT Gateway C
   │   └─ Web EC2 (ASG) : web-c-1, web-c-2
   │
   ├─ Private-App Subnet C (10.0.12.0/24)
   │   └─ App EC2 (ASG) : app-c-1, app-c-2
   │
   └─ Private-DB Subnet C (10.0.22.0/24)
       └─ RDS for PostgreSQL (Standby)  ──(Multi-AZ 대기 인스턴스; Primary와 동기화)
```

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

            # 저장된 아키텍처 정보를 시스템 프롬프트에 추가
            architecture_context = self.get_architecture_context()
            if architecture_context:
                system_prompt += architecture_context

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
    
    def extract_and_store_architecture(self, response_text):
        """응답에서 아키텍처를 추출하고 저장"""
        import re
        from datetime import datetime
        
        # 트리 형태 아키텍처 추출
        tree_pattern = r'```tree\s*\n(.*?)\n```'
        tree_blocks = re.findall(tree_pattern, response_text, re.DOTALL)
        
        if tree_blocks:
            for tree_block in tree_blocks:
                tree_block = tree_block.strip()
                if tree_block:  # 빈 블록이 아닌 경우만 저장
                    architecture_info = {
                        'content': tree_block,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'tree'
                    }
                    self.architectures.append(architecture_info)
            
            # 최대 5개까지만 유지 (메모리 효율성)
            if len(self.architectures) > 5:
                self.architectures = self.architectures[-5:]
            
            return True
        return False
    
    def get_architecture_context(self):
        """저장된 아키텍처를 시스템 프롬프트용 컨텍스트로 변환"""
        if not self.architectures:
            return ""
        
        context = "\n\n**📋 이전에 설계된 아키텍처 정보:**\n"
        context += "다음은 이전 대화에서 설계한 아키텍처입니다. 이를 참조하여 수정 요청에 응답하세요:\n\n"
        
        # 최근 2개 아키텍처만 사용 (시스템 프롬프트 길이 제한 고려)
        recent_architectures = self.architectures[-2:]
        
        for i, arch in enumerate(recent_architectures, 1):
            context += f"**아키텍처 {i} (생성: {arch['timestamp'][:19]}):**\n"
            context += f"```tree\n{arch['content']}\n```\n\n"
        
        return context
    
    def clear_architectures(self):
        """저장된 아키텍처 초기화"""
        self.architectures.clear()
    
    def is_ready(self):
        """Gemini API가 준비되었는지 확인"""
        return self.model is not None
