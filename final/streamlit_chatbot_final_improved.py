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
import traceback
from typing import Dict, List, Any
import hashlib
import tempfile
import sys
import logging

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="AWS JSON Converter & Diagram Generator (안정화)",
    page_icon="⚡",
    layout="wide"
)

class SafeDiagramGenerator:
    """Streamlit 환경에서 안전하게 작동하는 다이어그램 생성기"""
    
    def __init__(self):
        self.workspace_dir = "/home/gowns1345/chatbot-project"
        self.diagrams_dir = os.path.join(self.workspace_dir, "generated-diagrams")
        self.ensure_diagrams_directory()
    
    def ensure_diagrams_directory(self):
        """다이어그램 디렉토리 생성"""
        if not os.path.exists(self.diagrams_dir):
            os.makedirs(self.diagrams_dir)
    
    def create_safe_diagram(self, json_data: Dict[str, Any]) -> str:
        """안전한 다이어그램 생성"""
        try:
            service = json_data.get("service", "").upper()
            
            # 서비스별 안전한 다이어그램 코드 생성
            if service == "EC2":
                code = self._get_safe_ec2_code(json_data)
            elif service == "S3":
                code = self._get_safe_s3_code(json_data)
            elif service == "RDS":
                code = self._get_safe_rds_code(json_data)
            elif service == "LAMBDA":
                code = self._get_safe_lambda_code(json_data)
            elif service == "VPC":
                code = self._get_safe_vpc_code(json_data)
            else:
                code = self._get_safe_generic_code(json_data)
            
            # 안전한 실행
            return self._execute_safe_diagram(code)
            
        except Exception as e:
            logger.error(f"다이어그램 생성 실패: {str(e)}")
            # 최후의 수단으로 matplotlib 사용
            return self._create_matplotlib_fallback(json_data)
    
    def _execute_safe_diagram(self, code: str) -> str:
        """안전한 다이어그램 실행"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(self.diagrams_dir, f"safe_diagram_{timestamp}.py")
            
            # 코드 파일 생성
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 별도 프로세스에서 실행
            env = os.environ.copy()
            env['PYTHONPATH'] = ':'.join(sys.path)
            
            result = subprocess.run(
                [sys.executable, temp_file],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=15,
                env=env
            )
            
            # 임시 파일 삭제
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                # 생성된 파일 찾기
                diagram_path = self._find_latest_diagram()
                if diagram_path:
                    return diagram_path
            
            # 실패 시 matplotlib 대체
            return self._create_matplotlib_fallback({})
                
        except Exception as e:
            logger.error(f"다이어그램 실행 실패: {str(e)}")
            return self._create_matplotlib_fallback({})
    
    def _find_latest_diagram(self) -> str:
        """최근 생성된 다이어그램 파일 찾기"""
        try:
            png_files = []
            for root, dirs, files in os.walk(self.workspace_dir):
                for file in files:
                    if file.endswith('.png'):
                        full_path = os.path.join(root, file)
                        png_files.append((full_path, os.path.getmtime(full_path)))
            
            if png_files:
                latest_file = max(png_files, key=lambda x: x[1])
                return latest_file[0]
            
            return None
        except Exception:
            return None
    
    def _get_safe_ec2_code(self, json_data: Dict[str, Any]) -> str:
        """안전한 EC2 다이어그램 코드"""
        parameters = json_data.get("parameters", {})
        count = min(parameters.get("count", 2), 4)
        
        return f'''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import EC2, AutoScaling
    from diagrams.aws.network import ELB, VPC
    from diagrams.aws.security import IAM
    from diagrams.aws.general import General
    
    with Diagram("EC2 Architecture", show=False, filename="latest_diagram"):
        users = General("Users")
        
        with Cluster("AWS Cloud"):
            vpc = VPC("VPC")
            lb = ELB("Load Balancer")
            asg = AutoScaling("Auto Scaling")
            
            instances = [EC2(f"EC2-{{i+1}}") for i in range({count})]
            iam = IAM("IAM Role")
        
        users >> lb >> asg
        for instance in instances:
            asg >> instance
            instance >> iam
        vpc >> lb
    
    print("✅ EC2 다이어그램 생성 완료")
except Exception as e:
    print(f"❌ 오류: {{str(e)}}")
'''
    
    def _get_safe_s3_code(self, json_data: Dict[str, Any]) -> str:
        """안전한 S3 다이어그램 코드"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

try:
    from diagrams import Diagram, Cluster
    from diagrams.aws.storage import S3
    from diagrams.aws.security import IAM, KMS
    from diagrams.aws.network import CloudFront
    from diagrams.aws.general import General
    
    with Diagram("S3 Architecture", show=False, filename="latest_diagram"):
        users = General("Users")
        
        with Cluster("AWS Cloud"):
            cdn = CloudFront("CloudFront")
            s3_main = S3("Main Bucket")
            s3_backup = S3("Backup Bucket")
            kms = KMS("KMS")
            iam = IAM("IAM Policy")
        
        users >> cdn >> s3_main
        s3_main >> kms
        s3_main >> iam
        s3_main >> s3_backup
    
    print("✅ S3 다이어그램 생성 완료")
except Exception as e:
    print(f"❌ 오류: {str(e)}")
'''
    
    def _get_safe_rds_code(self, json_data: Dict[str, Any]) -> str:
        """안전한 RDS 다이어그램 코드"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.database import RDS
    from diagrams.aws.compute import EC2
    from diagrams.aws.network import VPC
    from diagrams.aws.security import IAM
    
    with Diagram("RDS Architecture", show=False, filename="latest_diagram"):
        with Cluster("AWS Cloud"):
            vpc = VPC("VPC")
            app_server = EC2("App Server")
            primary_db = RDS("Primary DB")
            standby_db = RDS("Standby DB")
            iam = IAM("DB IAM Role")
        
        app_server >> primary_db
        primary_db >> Edge(label="Replication") >> standby_db
        primary_db >> iam
        vpc >> app_server
    
    print("✅ RDS 다이어그램 생성 완료")
except Exception as e:
    print(f"❌ 오류: {str(e)}")
'''
    
    def _get_safe_lambda_code(self, json_data: Dict[str, Any]) -> str:
        """안전한 Lambda 다이어그램 코드"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

try:
    from diagrams import Diagram, Cluster
    from diagrams.aws.compute import Lambda
    from diagrams.aws.network import APIGateway
    from diagrams.aws.database import Dynamodb
    from diagrams.aws.security import IAM
    from diagrams.aws.general import General
    
    with Diagram("Lambda Architecture", show=False, filename="latest_diagram"):
        users = General("Users")
        
        with Cluster("AWS Cloud"):
            api = APIGateway("API Gateway")
            lambda_func = Lambda("Lambda Function")
            dynamodb = Dynamodb("DynamoDB")
            iam = IAM("Lambda Role")
        
        users >> api >> lambda_func
        lambda_func >> dynamodb
        lambda_func >> iam
    
    print("✅ Lambda 다이어그램 생성 완료")
except Exception as e:
    print(f"❌ 오류: {str(e)}")
'''
    
    def _get_safe_vpc_code(self, json_data: Dict[str, Any]) -> str:
        """안전한 VPC 다이어그램 코드"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

try:
    from diagrams import Diagram, Cluster
    from diagrams.aws.network import VPC, InternetGateway, NATGateway, PublicSubnet, PrivateSubnet
    from diagrams.aws.compute import EC2
    
    with Diagram("VPC Architecture", show=False, filename="latest_diagram"):
        internet = InternetGateway("Internet Gateway")
        
        with Cluster("VPC"):
            vpc = VPC("Production VPC")
            public_subnet = PublicSubnet("Public Subnet")
            private_subnet = PrivateSubnet("Private Subnet")
            nat_gw = NATGateway("NAT Gateway")
            web_server = EC2("Web Server")
            app_server = EC2("App Server")
        
        internet >> public_subnet >> nat_gw >> private_subnet
        public_subnet >> web_server
        private_subnet >> app_server
        vpc >> public_subnet
        vpc >> private_subnet
    
    print("✅ VPC 다이어그램 생성 완료")
except Exception as e:
    print(f"❌ 오류: {str(e)}")
'''
    
    def _get_safe_generic_code(self, json_data: Dict[str, Any]) -> str:
        """안전한 일반 다이어그램 코드"""
        service = json_data.get("service", "AWS")
        return f'''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

try:
    from diagrams import Diagram, Cluster
    from diagrams.aws.general import General
    from diagrams.aws.security import IAM
    
    with Diagram("{service} Architecture", show=False, filename="latest_diagram"):
        with Cluster("AWS Cloud"):
            service_node = General("{service} Service")
            iam_role = IAM("IAM Role")
            monitoring = General("Monitoring")
        
        service_node >> iam_role
        service_node >> monitoring
    
    print("✅ {service} 다이어그램 생성 완료")
except Exception as e:
    print(f"❌ 오류: {{str(e)}}")
'''
    
    def _create_matplotlib_fallback(self, json_data: Dict[str, Any]) -> str:
        """matplotlib을 사용한 최후의 수단 다이어그램"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            # AWS 색상
            aws_orange = '#FF9900'
            aws_blue = '#232F3E'
            
            service = json_data.get("service", "AWS Service")
            
            # 메인 서비스 박스
            main_box = patches.Rectangle((2, 3), 6, 2, linewidth=2, 
                                       edgecolor=aws_blue, facecolor=aws_orange, alpha=0.8)
            ax.add_patch(main_box)
            ax.text(5, 4, f'{service}\\nService', ha='center', va='center', 
                   fontsize=14, fontweight='bold', color='white')
            
            # 보안 박스
            security_box = patches.Rectangle((1, 1), 3, 1, linewidth=2, 
                                           edgecolor=aws_blue, facecolor='lightblue', alpha=0.7)
            ax.add_patch(security_box)
            ax.text(2.5, 1.5, 'Security\\n(IAM)', ha='center', va='center', fontsize=10)
            
            # 모니터링 박스
            monitor_box = patches.Rectangle((6, 1), 3, 1, linewidth=2, 
                                          edgecolor=aws_blue, facecolor='lightgreen', alpha=0.7)
            ax.add_patch(monitor_box)
            ax.text(7.5, 1.5, 'Monitoring', ha='center', va='center', fontsize=10)
            
            # 연결선
            ax.arrow(4, 3, -1.5, -0.8, head_width=0.1, head_length=0.1, fc=aws_blue, ec=aws_blue)
            ax.arrow(6, 3, 1.5, -0.8, head_width=0.1, head_length=0.1, fc=aws_blue, ec=aws_blue)
            
            # 축 설정
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f'AWS {service} Architecture (Fallback)', fontsize=16, fontweight='bold', pad=20)
            
            # 파일 저장
            fallback_path = os.path.join(self.workspace_dir, "latest_diagram.png")
            plt.savefig(fallback_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return fallback_path
            
        except Exception as e:
            logger.error(f"matplotlib 다이어그램도 실패: {str(e)}")
            return None

class StructuredGeminiConverter:
    """구조화된 출력을 위한 Gemini API 변환기"""
    
    def __init__(self):
        self.api_key = None
        self.model = None
        self.cache = {}
        self.initialize_gemini()
    
    def initialize_gemini(self):
        """Gemini API 초기화"""
        try:
            self.api_key = os.getenv('GEMINI_API_KEY')
            
            if not self.api_key:
                return False
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            return True
            
        except Exception as e:
            st.error(f"Gemini API 초기화 실패: {str(e)}")
            return False
    
    def _generate_cache_key(self, natural_language: str) -> str:
        """입력 텍스트에 대한 캐시 키 생성"""
        normalized = natural_language.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def generate_aws_json_structured(self, natural_language: str) -> Dict[str, Any]:
        """구조화된 AWS JSON 생성"""
        try:
            # 캐시 확인
            cache_key = self._generate_cache_key(natural_language)
            if cache_key in self.cache:
                st.info("🔄 캐시된 결과를 사용합니다.")
                return self.cache[cache_key]
            
            # 구조화된 프롬프트 생성
            prompt = self._create_structured_prompt(natural_language)
            
            if not self.model:
                return None
            
            # Gemini API 호출
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # JSON 파싱 및 검증
            result = self._parse_and_validate_json(response.text, natural_language)
            
            # 캐시에 저장
            if result:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            st.error(f"구조화된 JSON 생성 실패: {str(e)}")
            return None
    
    def _create_structured_prompt(self, natural_language: str) -> str:
        """사용자 요청에 맞는 간단한 구조화 프롬프트 생성"""
        return f"""
사용자의 자연어 요청을 간단하고 정확하게 분석하여 AWS 리소스 요청 JSON으로 변환해주세요.

입력: "{natural_language}"

중요: 사용자가 명시적으로 요청한 내용만 포함하고, 추가적인 정보는 최소화하세요.

다음 JSON 스키마를 따라 응답해주세요:

{{
    "request_type": "AWS 리소스 요청",
    "natural_language_input": "{natural_language}",
    "service": "주요 AWS 서비스명 (EC2, S3, RDS, Lambda, VPC 등)",
    "action": "create|delete|modify|configure|deploy 중 하나",
    "resource_type": "구체적인 리소스 타입 (instance, bucket, database, function 등)",
    "parameters": {{
        "name": "간단한 리소스 이름",
        "count": 숫자 (개수가 명시된 경우만),
        "region": "us-east-1" (기본값, 사용자가 다른 리전을 명시하지 않은 경우)
    }},
    "diagram_description": "간단한 다이어그램 설명"
}}

규칙:
1. 사용자가 명시하지 않은 세부사항(보안그룹, IAM, 비용 등)은 포함하지 마세요
2. parameters에는 사용자가 직접 언급한 내용만 포함하세요
3. 반드시 유효한 JSON 형식으로만 응답하세요
4. 추가 설명이나 마크다운 없이 JSON만 반환하세요

JSON:
"""
    
    def _parse_and_validate_json(self, response_text: str, original_input: str) -> Dict[str, Any]:
        """JSON 파싱 및 검증"""
        try:
            clean_json = self._extract_json(response_text)
            if not clean_json:
                raise ValueError("JSON을 찾을 수 없습니다.")
            
            parsed_json = json.loads(clean_json)
            validated_json = self._validate_and_fix_schema(parsed_json, original_input)
            
            return validated_json
            
        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {str(e)}")
            return None
        except Exception as e:
            st.error(f"JSON 검증 오류: {str(e)}")
            return None
    
    def _extract_json(self, text: str) -> str:
        """텍스트에서 JSON 추출"""
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return text[start:end]
        
        return text.strip()
    
    def _validate_and_fix_schema(self, data: Dict[str, Any], original_input: str) -> Dict[str, Any]:
        """스키마 검증 및 누락된 필드 보정 - 사용자 요청에 맞게 간단하게"""
        # 필수 필드만 확인 및 보정
        if "request_type" not in data:
            data["request_type"] = "AWS 리소스 요청"
        
        if "natural_language_input" not in data:
            data["natural_language_input"] = original_input
        
        if "service" not in data:
            data["service"] = "Unknown"
        
        if "action" not in data:
            data["action"] = "create"
        elif data["action"] not in ["create", "delete", "modify", "configure", "deploy"]:
            data["action"] = "create"
        
        if "resource_type" not in data:
            data["resource_type"] = "resource"
        
        # parameters는 사용자가 명시한 것만 유지
        if "parameters" not in data:
            data["parameters"] = {
                "name": f"{data['service'].lower()}-resource",
                "region": "us-east-1"
            }
        elif not isinstance(data["parameters"], dict):
            data["parameters"] = {
                "name": f"{data['service'].lower()}-resource",
                "region": "us-east-1"
            }
        
        # 기본 필수 필드만 확인
        if "name" not in data["parameters"]:
            data["parameters"]["name"] = f"{data['service'].lower()}-resource"
        
        if "region" not in data["parameters"]:
            data["parameters"]["region"] = "us-east-1"
        
        # 간단한 다이어그램 설명만
        if "diagram_description" not in data:
            data["diagram_description"] = f"{data['service']} {data['resource_type']} 다이어그램"
        
        # 불필요한 복잡한 필드들 제거 (사용자가 요청하지 않은 경우)
        unnecessary_fields = ["estimated_cost", "security_considerations", "best_practices"]
        for field in unnecessary_fields:
            if field in data:
                del data[field]
        
        return data

# 전역 인스턴스 초기화
if 'structured_converter' not in st.session_state:
    st.session_state.structured_converter = StructuredGeminiConverter()

if 'safe_diagram_generator' not in st.session_state:
    st.session_state.safe_diagram_generator = SafeDiagramGenerator()

# 기존 Amazon Q 통합도 유지 (선택적 사용)
try:
    from amazon_q_cli_integration_improved import AmazonQCLIIntegration
    if 'amazon_q_cli_improved' not in st.session_state:
        st.session_state.amazon_q_cli_improved = AmazonQCLIIntegration()
    q_cli_available = True
except ImportError:
    q_cli_available = False

# 세션 상태 초기화
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

if 'latest_diagram' not in st.session_state:
    st.session_state.latest_diagram = None

# API 키 상태 확인
api_ready = st.session_state.structured_converter.model is not None

# 다이어그램 생성기 상태 확인
diagram_generator_ready = st.session_state.safe_diagram_generator is not None

# Amazon Q CLI 상태 확인 (선택적)
if q_cli_available:
    q_cli_status = st.session_state.amazon_q_cli_improved.get_q_cli_status()
else:
    q_cli_status = {"available": False, "error": "모듈 없음"}

# 메인 타이틀
st.title("⚡ AWS JSON Converter & Diagram Generator (안정화)")
st.markdown("**Gemini + 안정화된 다이어그램 생성기**로 Streamlit 환경에서도 확실하게 다이어그램을 생성합니다.")

# 시스템 상태 표시
col1, col2, col3 = st.columns(3)

with col1:
    if api_ready:
        st.success("✅ Gemini API 연결됨")
    else:
        st.error("❌ Gemini API 연결 실패")

with col2:
    if diagram_generator_ready:
        st.success("✅ 안정화된 다이어그램 생성기")
    else:
        st.error("❌ 다이어그램 생성기 오류")

with col3:
    if q_cli_status["available"]:
        st.success(f"✅ Amazon Q CLI 연결됨 ({q_cli_status['version']})")
    else:
        st.info(f"ℹ️ Amazon Q CLI 미사용 (안정화 모드)")

# 빠른 다이어그램 생성 시스템 안내
with st.expander("⚡ 다이어그램 생성 시스템"):
    st.markdown("""
    ### 🎯 자동 생성 방식
    1. **Amazon Q CLI 우선**: 먼저 Amazon Q CLI로 전문적인 다이어그램 시도
    2. **자동 대체**: CLI 실패 시 안정화된 생성기로 자동 전환
    3. **확실한 결과**: 어떤 상황에서도 다이어그램 생성 보장
    
    ### 🔄 처리 순서
    1. **Amazon Q CLI 시도**: 전문적인 아키텍처 다이어그램 생성 시도
    2. **실패 시 자동 전환**: 안정화된 생성기로 즉시 대체
    3. **결과 알림**: 어떤 방식으로 생성되었는지 명확히 표시
    
    ### 🎯 결과 보장
    - **CLI 우선**: Amazon Q의 전문적인 아키텍처 패턴 적용
    - **안정성**: 실패 시 확실한 대체 방법 자동 사용
    - **투명성**: 사용된 생성 방식 명확히 표시
    """)

# 메인 타이틀
st.title("⚡ AWS JSON Converter & Diagram Generator")
st.markdown("**Gemini + Amazon Q CLI (자동 대체)**로 자연어를 JSON으로 구조화하고 최적의 방법으로 다이어그램을 생성합니다.")

if not api_ready:
    st.error("❌ Gemini API 키가 설정되지 않았습니다.")
    st.info("💡 .env 파일에 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

# 사이드바 설정
st.sidebar.header("🔧 설정")

# 캐시 상태 표시
cache_size = len(st.session_state.structured_converter.cache)
if cache_size > 0:
    st.sidebar.info(f"💾 캐시된 항목: {cache_size}개")
    if st.sidebar.button("🗑️ 캐시 삭제"):
        st.session_state.structured_converter.cache.clear()
        st.sidebar.success("캐시가 삭제되었습니다!")
        st.rerun()

# Amazon Q CLI 테스트 버튼
if st.sidebar.button("🧪 Amazon Q CLI 빠른 테스트"):
    with st.spinner("Amazon Q CLI 빠른 테스트 중..."):
        # 간단한 버전 확인만
        try:
            import subprocess
            result = subprocess.run(['q', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                st.sidebar.success("✅ Amazon Q CLI 설치 확인!")
                st.sidebar.text(f"버전: {result.stdout.strip()}")
            else:
                st.sidebar.error("❌ Amazon Q CLI 실행 실패")
        except subprocess.TimeoutExpired:
            st.sidebar.warning("⚠️ Amazon Q CLI 응답 지연")
        except Exception as e:
            st.sidebar.error(f"❌ 오류: {str(e)}")

# 메인 입력 영역
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

# 생성 버튼
if st.button("⚡ 다이어그램 생성", type="primary", use_container_width=True):
    if user_input.strip():
        try:
            with st.spinner("🔄 Gemini로 JSON 구조화 중..."):
                # 1단계: Gemini로 구조화된 JSON 변환
                json_result = st.session_state.structured_converter.generate_aws_json_structured(user_input)
                
                if json_result:
                    # 클립보드 복사 버튼 (JSON은 숨김)
                    if st.button("📋 JSON 복사"):
                        try:
                            pyperclip.copy(json.dumps(json_result, indent=2, ensure_ascii=False))
                            st.success("JSON이 클립보드에 복사되었습니다!")
                        except:
                            st.warning("클립보드 복사에 실패했습니다.")
                    
                    # 다이어그램 생성 - CLI 우선, 실패 시 안정화된 생성기 자동 사용
                    diagram_path = None
                    response_message = ""
                    used_fallback = False
                    
                    # 1단계: Amazon Q CLI 시도 (사용 가능한 경우)
                    if q_cli_available and q_cli_status["available"]:
                        with st.spinner("🤖 Amazon Q CLI로 다이어그램 생성 중..."):
                            st.subheader("🤖 Amazon Q CLI 다이어그램 생성")
                            
                            try:
                                diagram_path, response_message = st.session_state.amazon_q_cli_improved.generate_diagram_with_q_cli(json_result)
                                
                                if response_message:
                                    with st.expander("📝 Amazon Q 응답 보기"):
                                        st.text_area("Amazon Q 응답:", response_message, height=200)
                                
                                if diagram_path:
                                    st.success("✅ Amazon Q CLI로 다이어그램이 생성되었습니다!")
                                else:
                                    st.warning("⚠️ Amazon Q CLI 실패, 안정화된 생성기로 전환합니다.")
                                    used_fallback = True
                                    
                            except Exception as e:
                                st.warning(f"⚠️ Amazon Q CLI 오류: {str(e)}, 안정화된 생성기로 전환합니다.")
                                used_fallback = True
                    else:
                        st.info("ℹ️ Amazon Q CLI를 사용할 수 없어 안정화된 생성기를 사용합니다.")
                        used_fallback = True
                    
                    # 2단계: 안정화된 생성기 사용 (CLI 실패 시 또는 CLI 없는 경우)
                    if not diagram_path or used_fallback:
                        with st.spinner("⚡ 안정화된 다이어그램 생성기로 생성 중..."):
                            if used_fallback:
                                st.subheader("⚡ 안정화된 다이어그램 생성기 (대체)")
                            else:
                                st.subheader("⚡ 안정화된 다이어그램 생성기")
                            
                            diagram_path = st.session_state.safe_diagram_generator.create_safe_diagram(json_result)
                            
                            if diagram_path:
                                if used_fallback:
                                    st.success("✅ Amazon Q CLI 실패로 안정화된 생성기가 다이어그램을 생성했습니다!")
                                    response_message = "Amazon Q CLI 실패 후 안정화된 생성기로 생성됨"
                                else:
                                    st.success("✅ 안정화된 생성기로 다이어그램이 생성되었습니다!")
                                    response_message = "안정화된 생성기로 생성됨"
                            else:
                                st.error("❌ 다이어그램 생성에 실패했습니다.")
                    
                    # 다이어그램 결과 처리
                    if diagram_path and os.path.exists(diagram_path):
                        st.session_state.latest_diagram = diagram_path
                        st.balloons()  # 성공 축하 효과
                    else:
                        if diagram_method == "Amazon Q CLI만":
                            st.warning("⚠️ Amazon Q CLI 전용 모드에서 다이어그램 생성이 실패했습니다.")
                        else:
                            st.error("🚨 다이어그램 생성에 실패했습니다.")
                    
                    # 히스토리에 추가
                    st.session_state.conversion_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "input": user_input,
                        "json_output": json.dumps(json_result, ensure_ascii=False),
                        "diagram_method": "CLI 우선 (대체: 안정화)" if used_fallback else "CLI 우선",
                        "diagram_path": diagram_path,
                        "amazon_q_response": response_message,
                        "q_cli_used": not used_fallback and q_cli_available and q_cli_status["available"],
                        "fallback_used": used_fallback,
                        "version": "안정화"
                    })
                    
                else:
                    st.error("Gemini JSON 구조화에 실패했습니다.")
                    
        except Exception as e:
            st.error(f"처리 중 오류가 발생했습니다: {str(e)}")
            st.error(f"상세 오류: {traceback.format_exc()}")
            
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
        if item.get("fallback_used", False):
            badge = "🔄 CLI→안정화"
        elif item.get("q_cli_used", False):
            badge = "🤖 Amazon Q CLI"
        else:
            badge = "⚡ 안정화"
        
        method_badge = item.get("diagram_method", "기본")
        
        with st.expander(f"{badge} ({method_badge}) 변환 #{len(st.session_state.conversion_history)-i} - {item['timestamp'][:19]}"):
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
                with st.expander("📝 Amazon Q 응답 보기"):
                    st.text_area("", item["amazon_q_response"], height=200, key=f"response_{i}")
            
            # 다이어그램 경로 표시
            if item.get("diagram_path"):
                st.write(f"**다이어그램 경로:** {item['diagram_path']}")
            
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
### ⚡ 자동 다이어그램 생성 시스템의 특징
- **🤖 CLI 우선**: Amazon Q CLI로 전문적인 다이어그램 우선 시도
- **🔄 자동 대체**: CLI 실패 시 안정화된 생성기로 즉시 전환
- **🛡️ 확실한 결과**: 어떤 상황에서도 다이어그램 생성 보장
- **📊 투명성**: 사용된 생성 방식 명확히 표시
- **⚡ 빠른 응답**: 최적화된 처리로 신속한 결과
- **👥 사용자 친화적**: 복잡한 선택 없이 자동으로 최적 방법 사용

### 💡 사용 팁
- **자동 최적화**: 시스템이 자동으로 최적의 생성 방법 선택
- **간단한 요청**: "EC2 3개", "S3 버킷" 등 명확하게 요청하세요
- **즉시 결과**: 복잡한 설정 없이 바로 다이어그램 확인
- **안정성 보장**: CLI 문제가 있어도 확실하게 다이어그램 생성
- **투명한 과정**: 어떤 방식으로 생성되었는지 명확히 표시

### 🔧 문제 해결
- **생성 실패**: 자동으로 대체 방법 시도하므로 재시도 불필요
- **느린 응답**: CLI 타임아웃 시 자동으로 빠른 방법으로 전환
- **오류 발생**: 시스템이 자동으로 복구하여 결과 제공
- **품질 확인**: CLI 성공 시 전문적, 대체 시 안정적 다이어그램 제공
""")
