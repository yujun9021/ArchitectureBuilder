import streamlit as st
import json
import subprocess
import pyperclip
from datetime import datetime
import os
import platform
import re
import google.generativeai as genai
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AWS JSON Converter & Diagram Generator",
    page_icon="🔄",
    layout="wide"
)

class GeminiAWSConverter:
    """Google Gemini API를 활용한 AWS JSON 변환기"""
    
    def __init__(self):
        self.api_key = None
        self.model = None
        self.initialize_gemini()
    
    def initialize_gemini(self):
        """Gemini API 초기화"""
        try:
            # 환경변수에서 API 키 가져오기
            self.api_key = os.getenv('GEMINI_API_KEY')
            
            if not self.api_key:
                return False
            
            # Gemini API 설정
            genai.configure(api_key=self.api_key)
            
            # 모델 초기화 (최신 모델명 사용)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            return True
            
        except Exception as e:
            st.error(f"Gemini API 초기화 실패: {str(e)}")
            return False
    
    def set_api_key(self, api_key):
        """API 키 설정"""
        self.api_key = api_key
        os.environ['GEMINI_API_KEY'] = api_key
        return self.initialize_gemini()
    
    def generate_aws_json(self, natural_language):
        """자연어를 AWS JSON으로 변환"""
        prompt = f"""
        다음 자연어 요청을 AWS 리소스 요청 JSON으로 변환해주세요.
        
        자연어 입력: "{natural_language}"
        
        반드시 다음 형식의 유효한 JSON만 반환하세요 (다른 설명이나 텍스트 없이):
        
        ```json
        {{
            "request_type": "AWS 리소스 요청",
            "natural_language_input": "{natural_language}",
            "service": "감지된 AWS 서비스 (예: S3, EC2, RDS)",
            "action": "수행할 작업 (예: create, delete, modify)",
            "resource_type": "리소스 타입 (예: bucket, instance, database)",
            "parameters": {{
                "name": "리소스 이름",
                "region": "AWS 리전",
                "size": "크기 또는 용량"
            }},
            "estimated_cost": "예상 비용 정보",
            "security_considerations": ["보안 고려사항1", "보안 고려사항2"],
            "best_practices": ["모범 사례1", "모범 사례2"],
            "diagram_description": "이 요청을 바탕으로 한 AWS 아키텍처 다이어그램 설명"
        }}
        ```
        
        중요: 반드시 유효한 JSON 형식으로만 응답하세요. 추가 설명이나 마크다운은 포함하지 마세요.
        """
        
        try:
            if not self.model:
                return None
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            st.error(f"JSON 변환 실패: {str(e)}")
            return None
    
    def generate_diagram_code(self, json_data):
        """JSON 데이터를 바탕으로 다이어그램 생성 코드 생성"""
        
        # 정확한 AWS 아이콘 이름들 (정확한 이름)
        available_icons = """
        정확한 AWS 아이콘 이름들:
        
        Compute: EC2, Lambda, ECS, EKS, Fargate, AutoScaling, Batch
        Storage: S3, EBS, EFS, S3Glacier (Glacier 아님)
        Database: RDS, Dynamodb (DynamoDB 아님), Aurora, ElastiCache, Redshift
        Network: VPC, ELB, ALB, NLB, CloudFront, Route53, IGW, NATGateway, PrivateSubnet, PublicSubnet
        Security: IAM, KMS, SecretsManager, WAF, Shield
        Analytics: Athena, Kinesis, EMR, Glue, Quicksight
        Integration: SNS, SQS, Eventbridge, StepFunctions, APIGateway
        Management: Cloudwatch, Cloudtrail, Config, SystemsManager
        
        중요한 정확한 이름들:
        - DynamoDB → Dynamodb
        - CloudWatch → Cloudwatch  
        - CloudTrail → Cloudtrail
        - EventBridge → Eventbridge
        - QuickSight → Quicksight
        
        절대 사용하지 말 것: SecurityGroup, VPCSecurityGroup, DynamoDB, CloudWatch, CloudTrail
        """
        
        prompt = f"""
        다음 AWS 리소스 요청 JSON을 바탕으로 Python diagrams 라이브러리를 사용한 AWS 아키텍처 다이어그램 코드를 생성해주세요.
        
        JSON 데이터: {json_data}
        
        {available_icons}
        
        다음 규칙을 따라주세요:
        1. 위에 나열된 아이콘들만 사용하세요
        2. 필요한 import문을 모두 포함하세요
        3. with Diagram()으로 시작하세요
        4. show=False 옵션을 사용하세요
        5. filename을 "latest_diagram"으로 설정하세요
        6. 존재하지 않는 아이콘은 사용하지 마세요
        
        예시 형식:
        ```python
        from diagrams import Diagram
        from diagrams.aws.compute import EC2, Lambda
        from diagrams.aws.storage import S3
        from diagrams.aws.network import ELB, VPC
        
        with Diagram("latest_diagram", show=False):
            # 다이어그램 코드
        ```
        
        완전한 Python 코드만 반환해주세요:
        """
        
        try:
            if not self.model:
                return None
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            st.error(f"다이어그램 코드 생성 실패: {str(e)}")
            return None

# 전역 변환기 인스턴스
if 'gemini_converter' not in st.session_state:
    st.session_state.gemini_converter = GeminiAWSConverter()

# 세션 상태 초기화
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

if 'latest_diagram' not in st.session_state:
    st.session_state.latest_diagram = None

# 사이드바 - API 키 설정
st.sidebar.header("🔑 API 설정")

# API 키 입력
api_key_input = st.sidebar.text_input(
    "Gemini API Key", 
    type="password",
    help="Google AI Studio에서 발급받은 API 키를 입력하세요"
)

if api_key_input:
    if st.session_state.gemini_converter.set_api_key(api_key_input):
        st.sidebar.success("✅ API 키가 설정되었습니다!")
    else:
        st.sidebar.error("❌ API 키 설정에 실패했습니다.")

# API 키 상태 확인
api_ready = st.session_state.gemini_converter.model is not None

# 메인 타이틀
st.title("🔄 AWS JSON Converter & Diagram Generator")
st.markdown("자연어를 AWS 리소스 요청 JSON으로 변환하고 다이어그램을 자동 생성합니다.")

if not api_ready:
    st.warning("⚠️ 먼저 사이드바에서 Gemini API 키를 입력해주세요.")
    st.info("💡 Google AI Studio (https://makersuite.google.com/app/apikey)에서 무료로 API 키를 발급받을 수 있습니다.")
else:
    # 메인 입력 영역
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_area(
            "AWS 리소스 요청을 자연어로 입력하세요:",
            placeholder="예: S3 버킷을 만들고 싶어요. 버전 관리와 암호화를 활성화해주세요.",
            height=120,
            key="main_input"
        )
    
    with col2:
        st.markdown("### 💡 예시")
        st.markdown("""
        - "EC2 인스턴스 3개를 생성해주세요"
        - "RDS MySQL 데이터베이스를 설정하고 싶어요"
        - "Lambda 함수로 S3 이벤트를 처리하고 싶습니다"
        - "VPC와 서브넷을 구성해주세요"
        - "웹 애플리케이션용 3-tier 아키텍처"
        """)
    
    # 변환 버튼
    if st.button("🚀 JSON 변환 & 다이어그램 생성", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("🔄 JSON 변환 중..."):
                # JSON 변환
                json_result = st.session_state.gemini_converter.generate_aws_json(user_input)
                
                if json_result:
                    # JSON 결과 표시
                    st.subheader("📋 변환된 JSON")
                    
                    # 여러 방법으로 JSON 추출 시도
                    clean_json = None
                    parsed_json = None
                    
                    try:
                        # 방법 1: 마크다운 코드 블록에서 추출
                        if '```json' in json_result:
                            start_marker = json_result.find('```json') + 7
                            end_marker = json_result.find('```', start_marker)
                            if end_marker != -1:
                                clean_json = json_result[start_marker:end_marker].strip()
                        
                        # 방법 2: 첫 번째와 마지막 중괄호 사이 추출
                        if not clean_json:
                            json_start = json_result.find('{')
                            json_end = json_result.rfind('}') + 1
                            if json_start != -1 and json_end > json_start:
                                clean_json = json_result[json_start:json_end]
                        
                        # 방법 3: 전체 텍스트가 JSON인지 확인
                        if not clean_json:
                            clean_json = json_result.strip()
                        
                        # JSON 파싱 시도
                        if clean_json:
                            # 일반적인 JSON 오류 수정 시도
                            clean_json = clean_json.replace('\n', ' ')  # 줄바꿈 제거
                            clean_json = re.sub(r',\s*}', '}', clean_json)  # 마지막 쉼표 제거
                            clean_json = re.sub(r',\s*]', ']', clean_json)  # 배열 마지막 쉼표 제거
                            
                            parsed_json = json.loads(clean_json)
                            st.json(parsed_json)
                            
                            # 클립보드 복사 버튼
                            if st.button("📋 JSON 복사"):
                                try:
                                    pyperclip.copy(clean_json)
                                    st.success("JSON이 클립보드에 복사되었습니다!")
                                except:
                                    st.warning("클립보드 복사에 실패했습니다.")
                        else:
                            raise ValueError("JSON을 찾을 수 없습니다.")
                            
                    except json.JSONDecodeError as e:
                        st.error(f"JSON 파싱 실패: {str(e)}")
                        st.subheader("🔧 원본 응답 (디버그용)")
                        st.text_area("원본 응답:", json_result, height=200)
                        
                        # 수동 수정을 위한 입력 필드
                        st.subheader("✏️ 수동 JSON 수정")
                        manual_json = st.text_area(
                            "JSON을 수동으로 수정하세요:",
                            value=clean_json if clean_json else json_result,
                            height=200
                        )
                        
                        if st.button("🔄 수정된 JSON으로 다시 시도"):
                            try:
                                parsed_json = json.loads(manual_json)
                                st.success("✅ JSON 파싱 성공!")
                                st.json(parsed_json)
                                clean_json = manual_json
                            except json.JSONDecodeError as e2:
                                st.error(f"수정된 JSON도 파싱 실패: {str(e2)}")
                        
                    except Exception as e:
                        st.error(f"예상치 못한 오류: {str(e)}")
                        st.subheader("🔧 원본 응답")
                        st.text(json_result)
                    
                    # 다이어그램 생성 (JSON 파싱 성공 시에만)
                    if parsed_json and clean_json:
                        with st.spinner("📊 다이어그램 생성 중..."):
                            diagram_code = st.session_state.gemini_converter.generate_diagram_code(clean_json)
                            
                            if diagram_code:
                                st.subheader("🔧 생성된 다이어그램 코드")
                                st.code(diagram_code, language="python")
                                
                                # 다이어그램 실행
                                try:
                                    # 코드에서 실제 Python 코드 부분만 추출
                                    code_lines = diagram_code.split('\n')
                                    python_code = []
                                    in_code_block = False
                                    
                                    for line in code_lines:
                                        # 마크다운 코드 블록 시작/끝 처리
                                        if line.strip().startswith('```python'):
                                            in_code_block = True
                                            continue
                                        elif line.strip().startswith('```'):
                                            in_code_block = False
                                            continue
                                        
                                        # 코드 블록 내부이거나 일반 Python 코드인 경우
                                        if in_code_block or (line.strip() and not line.strip().startswith('```')):
                                            python_code.append(line)
                                    
                                    # 코드 블록이 없었다면 전체를 코드로 처리
                                    if not python_code:
                                        python_code = [line for line in code_lines if line.strip() and not line.strip().startswith('#')]
                                    
                                    final_code = '\n'.join(python_code)
                                    
                                    # 다이어그램 생성 디렉토리 확인
                                    diagrams_dir = "generated-diagrams"
                                    if not os.path.exists(diagrams_dir):
                                        os.makedirs(diagrams_dir)
                                    
                                    # 임시 파일로 코드 저장
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    temp_file = f"{diagrams_dir}/temp_diagram_{timestamp}.py"
                                    
                                    with open(temp_file, 'w', encoding='utf-8') as f:
                                        f.write(final_code)
                                    
                                    # 디버그: 생성된 코드 확인
                                    st.write("**실행할 코드:**")
                                    st.code(final_code, language="python")
                                    
                                    # 다이어그램 실행
                                    result = subprocess.run(
                                        ['python3', temp_file],
                                        cwd=os.getcwd(),
                                        capture_output=True,
                                        text=True,
                                        timeout=30
                                    )
                                    
                                    if result.returncode == 0:
                                        # latest_diagram.png 파일 찾기
                                        latest_diagram_path = "latest_diagram.png"
                                        if os.path.exists(latest_diagram_path):
                                            st.session_state.latest_diagram = latest_diagram_path
                                            st.success("✅ 다이어그램이 성공적으로 생성되었습니다!")
                                        else:
                                            # 다른 PNG 파일 찾기
                                            png_files = [f for f in os.listdir('.') if f.endswith('.png')]
                                            if png_files:
                                                latest_png = max(png_files, key=os.path.getmtime)
                                                st.session_state.latest_diagram = latest_png
                                                st.success("✅ 다이어그램이 성공적으로 생성되었습니다!")
                                            else:
                                                st.warning("다이어그램 파일을 찾을 수 없습니다.")
                                    else:
                                        st.error(f"다이어그램 생성 실패: {result.stderr}")
                                    
                                    # 임시 파일 삭제
                                    if os.path.exists(temp_file):
                                        os.remove(temp_file)
                                        
                                except Exception as e:
                                    st.error(f"다이어그램 생성 중 오류 발생: {str(e)}")
                            else:
                                st.error("다이어그램 코드 생성에 실패했습니다.")
                        
                        # 히스토리에 추가
                        st.session_state.conversion_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "input": user_input,
                            "json_output": clean_json,
                            "diagram_code": diagram_code if diagram_code else "생성 실패"
                        })
                        
                else:
                    st.error("JSON 변환에 실패했습니다.")
        else:
            st.warning("변환할 텍스트를 입력해주세요.")

# 최신 다이어그램 표시
if st.session_state.latest_diagram and os.path.exists(st.session_state.latest_diagram):
    st.header("🖼️ 최신 생성 다이어그램")
    
    try:
        st.image(st.session_state.latest_diagram, 
                caption="최신 생성된 AWS 아키텍처 다이어그램", 
                use_column_width=True)
        
        # 다운로드 버튼
        with open(st.session_state.latest_diagram, "rb") as file:
            st.download_button(
                label="📥 다이어그램 다운로드",
                data=file.read(),
                file_name=f"aws_diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
    except Exception as e:
        st.error(f"다이어그램 표시 실패: {str(e)}")

# 변환 히스토리 (최근 3개만)
if st.session_state.conversion_history:
    st.header("📚 최근 변환 히스토리")
    
    # 최근 3개만 표시
    recent_history = list(reversed(st.session_state.conversion_history[-3:]))
    
    for i, item in enumerate(recent_history):
        with st.expander(f"변환 #{len(st.session_state.conversion_history)-i} - {item['timestamp'][:19]}"):
            st.write("**입력:**")
            st.write(item['input'])
            
            st.write("**JSON 출력:**")
            try:
                parsed = json.loads(item['json_output'])
                st.json(parsed)
            except:
                st.text(item['json_output'])
            
            # 재사용 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔄 다시 변환", key=f"retry_{i}"):
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
        st.session_state.conversion_history = []
        st.success("히스토리가 삭제되었습니다.")
        st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
### 🚀 사용 방법
1. **사이드바**에서 Gemini API 키를 입력하세요
2. **자연어 요청**을 입력하세요 (AWS 리소스 관련)
3. **변환 버튼**을 클릭하면 JSON과 다이어그램이 자동 생성됩니다
4. **최신 다이어그램**이 자동으로 표시됩니다

### 💡 특징
- 🔄 자연어 → AWS JSON 자동 변환
- 📊 JSON → 다이어그램 자동 생성
- 🖼️ 최신 다이어그램만 표시 (깔끔한 UI)
- 📚 최근 3개 변환 히스토리 관리
- 📥 다이어그램 다운로드 지원
- 🔧 강력한 JSON 파싱 및 오류 수정
""")
