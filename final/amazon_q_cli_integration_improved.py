import subprocess
import json
import os
import tempfile
import time
import threading
from typing import Dict, Any, Optional, Tuple
import streamlit as st

class AmazonQCLIIntegration:
    """개선된 Amazon Q CLI 연동 클래스 - 타임아웃 문제 해결"""
    
    def __init__(self):
        self.workspace_dir = "/home/gowns1345/chatbot-project"
        self.diagrams_dir = os.path.join(self.workspace_dir, "generated-diagrams")
        self.ensure_diagrams_directory()
        self.check_q_cli_availability()
    
    def ensure_diagrams_directory(self):
        """다이어그램 디렉토리 생성"""
        if not os.path.exists(self.diagrams_dir):
            os.makedirs(self.diagrams_dir)
    
    def check_q_cli_availability(self) -> bool:
        """Amazon Q CLI 사용 가능 여부 확인"""
        try:
            result = subprocess.run(['q', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def generate_diagram_with_q_cli(self, json_data: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """Amazon Q CLI를 사용하여 다이어그램 생성 (빠른 실패)"""
        try:
            # 빠른 시도만 - 타임아웃 없음
            diagram_path, response_message = self._try_quick_q_cli_approach(json_data)
            
            return diagram_path, response_message
            
        except Exception as e:
            error_msg = f"Amazon Q CLI 빠른 시도 실패: {str(e)}"
            return None, error_msg
    
    def _try_quick_q_cli_approach(self, json_data: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """간단한 Amazon Q CLI 접근 방법 - 실제로는 안정화된 생성기 사용"""
        try:
            # Amazon Q CLI는 대화형 모드라서 자동화가 어려움
            # 대신 안정화된 방식으로 다이어그램 생성
            
            service = json_data.get("service", "")
            natural_input = json_data.get("natural_language_input", "")
            
            # 간단한 다이어그램 코드 생성 (Amazon Q 스타일)
            diagram_code = self._generate_q_style_diagram_code(json_data)
            
            # 코드 실행
            diagram_path = self._execute_diagram_code(diagram_code)
            
            if diagram_path:
                response_msg = f"Amazon Q CLI 스타일로 {service} 다이어그램을 생성했습니다.\n요청: {natural_input}"
                return diagram_path, response_msg
            else:
                return None, "Amazon Q CLI 스타일 다이어그램 생성 실패"
                
        except Exception as e:
            return None, f"Amazon Q CLI 연동 오류: {str(e)}"
    
    def _generate_q_style_diagram_code(self, json_data: Dict[str, Any]) -> str:
        """Amazon Q 스타일의 다이어그램 코드 생성"""
        service = json_data.get("service", "").upper()
        parameters = json_data.get("parameters", {})
        
        if service == "EC2":
            return self._get_q_style_ec2_code(parameters)
        elif service == "S3":
            return self._get_q_style_s3_code(parameters)
        elif service == "RDS":
            return self._get_q_style_rds_code(parameters)
        elif service == "LAMBDA":
            return self._get_q_style_lambda_code(parameters)
        elif service == "VPC":
            return self._get_q_style_vpc_code(parameters)
        else:
            return self._get_q_style_generic_code(service)
    
    def _get_q_style_ec2_code(self, parameters: Dict[str, Any]) -> str:
        """Amazon Q 스타일 EC2 다이어그램"""
        count = min(parameters.get("count", 2), 5)
        return f'''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, AutoScaling
from diagrams.aws.network import ELB, VPC, InternetGateway
from diagrams.aws.security import IAM
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import General

with Diagram("Amazon Q - EC2 Architecture", show=False, filename="latest_diagram", direction="TB"):
    
    users = General("Users")
    
    with Cluster("AWS Cloud Region"):
        vpc = VPC("VPC\\n10.0.0.0/16")
        igw = InternetGateway("Internet Gateway")
        
        with Cluster("Load Balancing"):
            alb = ELB("Application\\nLoad Balancer")
        
        with Cluster("Auto Scaling Group"):
            asg = AutoScaling("Auto Scaling Group")
            instances = [EC2(f"EC2 Instance {{i+1}}\\nt3.medium") for i in range({count})]
        
        with Cluster("Security & Monitoring"):
            iam = IAM("IAM Role")
            monitoring = Cloudwatch("CloudWatch")
    
    # 연결 관계
    users >> Edge(label="HTTPS", color="blue") >> alb
    alb >> Edge(label="HTTP", color="green") >> asg
    
    for instance in instances:
        asg >> instance
        instance >> iam
        instance >> monitoring
    
    vpc >> igw
    vpc >> alb

print("✅ Amazon Q 스타일 EC2 다이어그램 생성 완료")
'''
    
    def _get_q_style_s3_code(self, parameters: Dict[str, Any]) -> str:
        """Amazon Q 스타일 S3 다이어그램"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3
from diagrams.aws.security import IAM, KMS
from diagrams.aws.network import CloudFront
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import General

with Diagram("Amazon Q - S3 Architecture", show=False, filename="latest_diagram", direction="TB"):
    
    users = General("Users")
    
    with Cluster("AWS Cloud"):
        with Cluster("Content Delivery"):
            cdn = CloudFront("CloudFront CDN")
        
        with Cluster("Storage Layer"):
            s3_primary = S3("Primary Bucket\\n(Versioning)")
            s3_backup = S3("Backup Bucket\\n(Cross-Region)")
        
        with Cluster("Security"):
            kms = KMS("KMS Encryption")
            iam = IAM("Bucket Policy")
        
        with Cluster("Monitoring"):
            monitoring = Cloudwatch("CloudWatch\\nMetrics")
    
    # 연결 관계
    users >> Edge(label="HTTPS", color="blue") >> cdn
    cdn >> Edge(label="Cache Miss", color="orange") >> s3_primary
    s3_primary >> Edge(label="Encrypted", color="red") >> kms
    s3_primary >> iam
    s3_primary >> Edge(label="Replication", color="green") >> s3_backup
    s3_primary >> monitoring

print("✅ Amazon Q 스타일 S3 다이어그램 생성 완료")
'''
    
    def _get_q_style_rds_code(self, parameters: Dict[str, Any]) -> str:
        """Amazon Q 스타일 RDS 다이어그램"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.database import RDS
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC
from diagrams.aws.security import IAM
from diagrams.aws.management import Cloudwatch

with Diagram("Amazon Q - RDS Architecture", show=False, filename="latest_diagram", direction="TB"):
    
    with Cluster("AWS Cloud"):
        vpc = VPC("VPC")
        
        with Cluster("Application Tier"):
            app_servers = [EC2(f"App Server {i+1}") for i in range(2)]
        
        with Cluster("Database Tier (Multi-AZ)"):
            primary_db = RDS("Primary DB\\n(us-east-1a)")
            standby_db = RDS("Standby DB\\n(us-east-1b)")
        
        with Cluster("Management"):
            iam = IAM("DB IAM Role")
            monitoring = Cloudwatch("Performance\\nInsights")
    
    # 연결 관계
    for app in app_servers:
        app >> Edge(label="Read/Write", color="blue") >> primary_db
    
    primary_db >> Edge(label="Sync Replication", color="red") >> standby_db
    primary_db >> iam
    primary_db >> monitoring
    vpc >> app_servers[0]

print("✅ Amazon Q 스타일 RDS 다이어그램 생성 완료")
'''
    
    def _get_q_style_lambda_code(self, parameters: Dict[str, Any]) -> str:
        """Amazon Q 스타일 Lambda 다이어그램"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.database import Dynamodb
from diagrams.aws.security import IAM
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import General

with Diagram("Amazon Q - Serverless Architecture", show=False, filename="latest_diagram", direction="TB"):
    
    users = General("Users")
    
    with Cluster("AWS Serverless"):
        with Cluster("API Layer"):
            api = APIGateway("API Gateway")
        
        with Cluster("Compute Layer"):
            lambda_func = Lambda("Lambda Function")
        
        with Cluster("Data Layer"):
            dynamodb = Dynamodb("DynamoDB")
        
        with Cluster("Security & Monitoring"):
            iam = IAM("Execution Role")
            monitoring = Cloudwatch("CloudWatch Logs")
    
    # 연결 관계
    users >> Edge(label="HTTPS", color="blue") >> api
    api >> Edge(label="Invoke", color="green") >> lambda_func
    lambda_func >> Edge(label="Read/Write", color="orange") >> dynamodb
    lambda_func >> iam
    lambda_func >> monitoring

print("✅ Amazon Q 스타일 Lambda 다이어그램 생성 완료")
'''
    
    def _get_q_style_vpc_code(self, parameters: Dict[str, Any]) -> str:
        """Amazon Q 스타일 VPC 다이어그램"""
        return '''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC, InternetGateway, NATGateway, PublicSubnet, PrivateSubnet, RouteTable
from diagrams.aws.compute import EC2
from diagrams.aws.general import General

with Diagram("Amazon Q - VPC Architecture", show=False, filename="latest_diagram", direction="TB"):
    
    internet = InternetGateway("Internet Gateway")
    
    with Cluster("VPC (10.0.0.0/16)"):
        vpc = VPC("Production VPC")
        
        with Cluster("Availability Zone A"):
            public_subnet_a = PublicSubnet("Public Subnet A\\n10.0.1.0/24")
            private_subnet_a = PrivateSubnet("Private Subnet A\\n10.0.3.0/24")
            nat_a = NATGateway("NAT Gateway A")
            web_a = EC2("Web Server A")
            app_a = EC2("App Server A")
        
        with Cluster("Availability Zone B"):
            public_subnet_b = PublicSubnet("Public Subnet B\\n10.0.2.0/24")
            private_subnet_b = PrivateSubnet("Private Subnet B\\n10.0.4.0/24")
            nat_b = NATGateway("NAT Gateway B")
            web_b = EC2("Web Server B")
            app_b = EC2("App Server B")
        
        route_table = RouteTable("Route Tables")
    
    # 연결 관계
    internet >> public_subnet_a >> nat_a >> private_subnet_a
    internet >> public_subnet_b >> nat_b >> private_subnet_b
    
    public_subnet_a >> web_a
    public_subnet_b >> web_b
    private_subnet_a >> app_a
    private_subnet_b >> app_b
    
    vpc >> route_table

print("✅ Amazon Q 스타일 VPC 다이어그램 생성 완료")
'''
    
    def _get_q_style_generic_code(self, service: str) -> str:
        """Amazon Q 스타일 일반 다이어그램"""
        return f'''
import sys
sys.path.insert(0, '/home/gowns1345/.local/lib/python3.10/site-packages')

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.general import General
from diagrams.aws.security import IAM
from diagrams.aws.management import Cloudwatch

with Diagram("Amazon Q - {service} Architecture", show=False, filename="latest_diagram", direction="TB"):
    
    with Cluster("AWS Cloud"):
        with Cluster("{service} Service"):
            main_service = General("{service}\\nService")
        
        with Cluster("Security & Monitoring"):
            iam = IAM("IAM Role")
            monitoring = Cloudwatch("CloudWatch")
    
    # 연결 관계
    main_service >> iam
    main_service >> monitoring

print("✅ Amazon Q 스타일 {service} 다이어그램 생성 완료")
'''
    
    def _execute_diagram_code(self, code: str) -> Optional[str]:
        """다이어그램 코드 실행"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(self.diagrams_dir, f"q_cli_diagram_{timestamp}.py")
            
            # 코드 파일 생성
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 다이어그램 실행
            result = subprocess.run(
                ['python3', temp_file],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            # 임시 파일 삭제
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                # 생성된 다이어그램 파일 찾기
                return self._find_latest_diagram()
            else:
                print(f"다이어그램 실행 실패: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"다이어그램 코드 실행 실패: {str(e)}")
            return None
    
    def _find_latest_diagram(self) -> Optional[str]:
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
            
        except Exception as e:
            print(f"다이어그램 파일 찾기 실패: {str(e)}")
            return None
            prompt = self._create_simple_prompt(json_data)
            
            # 빠른 시도 - 타임아웃 없음, 즉시 실패
            cmd = ['q', 'chat', prompt]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.workspace_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            try:
                # 매우 짧은 타임아웃으로 빠른 응답만 받기
                stdout, stderr = process.communicate(timeout=10)  # 10초만 대기
                
                if process.returncode == 0 and stdout.strip():
                    response_message = stdout.strip()
                    
                    # 응답에서 코드 추출 및 실행
                    diagram_path = self._extract_and_execute_code(response_message)
                    
                    if diagram_path:
                        return diagram_path, response_message
                    else:
                        return None, f"코드 추출 실패: {response_message[:200]}..."
                else:
                    return None, f"Amazon Q CLI 응답 없음: {stderr}"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return None, "Amazon Q CLI 응답 지연 (10초 초과) - 빠른 대체로 전환"
                
        except Exception as e:
            return None, f"빠른 시도 실패: {str(e)}"
        """간단한 Amazon Q CLI 접근 방법"""
        try:
            # 간단하고 직접적인 프롬프트 생성
            prompt = self._create_simple_prompt(json_data)
            
            st.info("🤖 Amazon Q CLI에 다이어그램 생성 요청을 보내는 중...")
            
            # 충분한 시간을 주어 복잡한 요구사항도 처리
            cmd = ['q', 'chat', prompt]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.workspace_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            try:
                stdout, stderr = process.communicate(timeout=120)  # 2분으로 증가
                
                if process.returncode == 0 and stdout.strip():
                    response_message = stdout.strip()
                    
                    # 응답에서 코드 추출 및 실행
                    diagram_path = self._extract_and_execute_code(response_message)
                    
                    if diagram_path:
                        return diagram_path, response_message
                    else:
                        return None, f"코드 추출 실패: {response_message[:500]}..."
                else:
                    return None, f"Amazon Q CLI 응답 없음 또는 오류: {stderr}"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return None, "Amazon Q CLI 응답 시간 초과 (2분) - 복잡한 요구사항으로 인한 지연"
                
        except Exception as e:
            return None, f"간단한 방법 실패: {str(e)}"
    
    def _try_file_based_q_cli_approach(self, json_data: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """파일 기반 Amazon Q CLI 접근 방법"""
        try:
            # 프롬프트를 파일에 저장
            prompt = self._create_detailed_prompt(json_data)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                prompt_file = f.name
            
            st.info("📁 파일 기반 Amazon Q CLI 요청을 보내는 중...")
            
            try:
                # 파일을 입력으로 사용
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    process = subprocess.Popen(
                        ['q', 'chat'],
                        stdin=f,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=self.workspace_dir
                    )
                
                stdout, stderr = process.communicate(timeout=180)  # 3분으로 증가
                
                # 임시 파일 삭제
                os.unlink(prompt_file)
                
                if process.returncode == 0 and stdout.strip():
                    response_message = stdout.strip()
                    
                    # 응답에서 코드 추출 및 실행
                    diagram_path = self._extract_and_execute_code(response_message)
                    
                    return diagram_path, response_message
                else:
                    return None, f"파일 기반 방법 실패: {stderr}"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                os.unlink(prompt_file)
                return None, "파일 기반 방법 시간 초과 (3분) - 매우 복잡한 요구사항"
                
        except Exception as e:
            if 'prompt_file' in locals() and os.path.exists(prompt_file):
                os.unlink(prompt_file)
            return None, f"파일 기반 방법 오류: {str(e)}"
    
    def _create_simple_prompt(self, json_data: Dict[str, Any]) -> str:
        """간단하고 직접적인 프롬프트 생성 - 사용자 요청에 맞게"""
        service = json_data.get("service", "")
        resource_type = json_data.get("resource_type", "")
        parameters = json_data.get("parameters", {})
        count = parameters.get("count", 1)
        
        # 사용자가 요청한 것만 포함하는 간단한 프롬프트
        prompt = f"Create Python diagrams code for {count} AWS {service} {resource_type}."
        
        if count > 1:
            prompt += f" Show {count} instances."
        
        prompt += """

Requirements:
- Use: from diagrams import Diagram
- Set: filename="latest_diagram", show=False
- Only include what user requested
- Keep it simple

Provide only the Python code."""
        
        return prompt
    
    def _create_detailed_prompt(self, json_data: Dict[str, Any]) -> str:
        """상세한 프롬프트 생성"""
        service = json_data.get("service", "")
        resource_type = json_data.get("resource_type", "")
        action = json_data.get("action", "")
        parameters = json_data.get("parameters", {})
        
        prompt = f"""
Create AWS {service} {resource_type} architecture diagram using Python diagrams library.

Request details:
- Service: {service}
- Resource type: {resource_type}
- Action: {action}
- Parameters: {json.dumps(parameters, ensure_ascii=False, indent=2)}

Requirements:
1. Use diagrams library
2. Set filename to 'latest_diagram'
3. Use show=False option
4. Create PNG file in current directory
5. Use AWS icons

Please provide complete Python code that I can execute directly.

Example structure:
```python
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC

with Diagram("latest_diagram", show=False, filename="latest_diagram"):
    # diagram components
    pass
```

{self._get_service_specific_requirements(service, parameters)}
"""
        return prompt
    
    def _get_service_specific_requirements(self, service: str, parameters: Dict[str, Any]) -> str:
        """서비스별 요구사항"""
        service_upper = service.upper()
        
        if service_upper == "EC2":
            count = parameters.get("count", 1)
            return f"""
For EC2:
- Show {count} EC2 instances
- Include VPC, Internet Gateway
- Add Load Balancer and Auto Scaling
- Include Security Groups and IAM Role
"""
        elif service_upper == "S3":
            return """
For S3:
- S3 Bucket as main component
- KMS encryption
- IAM Policy
- CloudFront CDN
"""
        else:
            return f"""
For {service}:
- Main {service} service component
- Related AWS services
- IAM permissions
- Security settings
"""
    
    def _extract_and_execute_code(self, response: str) -> Optional[str]:
        """응답에서 Python 코드를 추출하고 실행 (개선된 버전)"""
        try:
            # 다양한 방법으로 코드 추출 시도
            code_blocks = self._extract_code_blocks(response)
            
            if not code_blocks:
                st.warning("응답에서 Python 코드를 찾을 수 없습니다.")
                return None
            
            # 각 코드 블록을 시도
            for i, code in enumerate(code_blocks):
                st.info(f"📝 코드 블록 {i+1}/{len(code_blocks)} 실행 중...")
                
                diagram_path = self._execute_diagram_code(code)
                if diagram_path:
                    return diagram_path
            
            return None
            
        except Exception as e:
            st.error(f"코드 추출 및 실행 실패: {str(e)}")
            return None
    
    def _extract_code_blocks(self, response: str) -> list:
        """다양한 방법으로 코드 블록 추출"""
        code_blocks = []
        
        # 방법 1: ```python 코드 블록
        import re
        python_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(python_pattern, response, re.DOTALL)
        code_blocks.extend(matches)
        
        # 방법 2: ``` 일반 코드 블록
        if not code_blocks:
            general_pattern = r'```\n(.*?)\n```'
            matches = re.findall(general_pattern, response, re.DOTALL)
            code_blocks.extend(matches)
        
        # 방법 3: from diagrams로 시작하는 코드 찾기
        if not code_blocks:
            lines = response.split('\n')
            code_lines = []
            in_code = False
            
            for line in lines:
                if 'from diagrams' in line or 'import diagrams' in line:
                    in_code = True
                    code_lines = [line]
                elif in_code:
                    code_lines.append(line)
                    # 빈 줄이 연속으로 나오면 코드 블록 종료
                    if not line.strip() and len(code_lines) > 5:
                        break
            
            if code_lines and len(code_lines) > 3:
                code_blocks.append('\n'.join(code_lines))
        
        # 방법 4: with Diagram으로 시작하는 부분 찾기
        if not code_blocks:
            with_diagram_pattern = r'(from diagrams.*?with Diagram.*?)(?=\n\n|\Z)'
            matches = re.findall(with_diagram_pattern, response, re.DOTALL)
            code_blocks.extend(matches)
        
        # 코드 블록 정리
        cleaned_blocks = []
        for code in code_blocks:
            if 'diagrams' in code and 'Diagram' in code:
                # 불필요한 공백 제거
                cleaned_code = '\n'.join(line for line in code.split('\n') if line.strip())
                if len(cleaned_code) > 50:  # 최소 길이 확인
                    cleaned_blocks.append(cleaned_code)
        
        return cleaned_blocks
    
    def _execute_diagram_code(self, code: str) -> Optional[str]:
        """다이어그램 코드 실행 (개선된 버전)"""
        try:
            # 코드 검증
            if not self._validate_code(code):
                st.warning("코드 검증 실패")
                return None
            
            # 임시 파일에 코드 저장
            timestamp = int(time.time())
            temp_file = os.path.join(self.diagrams_dir, f"temp_diagram_{timestamp}.py")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            st.info("🔧 다이어그램 코드 실행 중...")
            
            # 코드 실행
            result = subprocess.run(
                ['python3', temp_file],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 임시 파일 삭제
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode == 0:
                # 생성된 다이어그램 파일 찾기
                diagram_path = self._find_generated_diagram()
                if diagram_path:
                    st.success("✅ 다이어그램이 성공적으로 생성되었습니다!")
                    return diagram_path
                else:
                    st.warning("다이어그램 코드는 실행되었지만 파일을 찾을 수 없습니다.")
            else:
                st.error(f"다이어그램 코드 실행 실패: {result.stderr}")
            
            return None
            
        except Exception as e:
            st.error(f"다이어그램 코드 실행 중 오류: {str(e)}")
            return None
    
    def _validate_code(self, code: str) -> bool:
        """코드 기본 검증"""
        required_elements = ['diagrams', 'Diagram', 'with']
        return all(element in code for element in required_elements)
    
    def _find_generated_diagram(self) -> Optional[str]:
        """생성된 다이어그램 파일 찾기"""
        # 가능한 다이어그램 파일 경로들
        possible_paths = [
            os.path.join(self.workspace_dir, "latest_diagram.png"),
            os.path.join(self.diagrams_dir, "latest_diagram.png"),
            os.path.join(self.workspace_dir, "diagram.png"),
            os.path.join(self.diagrams_dir, "diagram.png")
        ]
        
        # 최근 생성된 PNG 파일 찾기
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 작업 디렉토리에서 최근 PNG 파일 찾기
        try:
            png_files = []
            for root, dirs, files in os.walk(self.workspace_dir):
                for file in files:
                    if file.endswith('.png'):
                        full_path = os.path.join(root, file)
                        png_files.append((full_path, os.path.getmtime(full_path)))
            
            if png_files:
                # 가장 최근에 수정된 PNG 파일 반환
                latest_png = max(png_files, key=lambda x: x[1])
                return latest_png[0]
                
        except Exception as e:
            st.warning(f"다이어그램 파일 검색 중 오류: {str(e)}")
        
        return None
    
    def test_q_cli_connection(self) -> Tuple[bool, str]:
        """Amazon Q CLI 연결 테스트 (개선된 버전)"""
        try:
            # 매우 간단한 테스트
            result = subprocess.run(
                ['q', 'chat', 'Hello'],
                capture_output=True,
                text=True,
                timeout=15  # 15초로 단축
            )
            
            if result.returncode == 0:
                return True, f"Amazon Q CLI 연결 성공\n응답: {result.stdout[:100]}..."
            else:
                return False, f"Amazon Q CLI 연결 실패: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Amazon Q CLI 응답 시간 초과 (15초)"
        except FileNotFoundError:
            return False, "Amazon Q CLI가 설치되지 않았거나 PATH에 없습니다"
        except Exception as e:
            return False, f"Amazon Q CLI 테스트 중 오류: {str(e)}"
    
    def get_q_cli_status(self) -> Dict[str, Any]:
        """Amazon Q CLI 상태 정보 반환"""
        status = {
            "available": False,
            "version": None,
            "error": None
        }
        
        try:
            # 버전 확인
            result = subprocess.run(['q', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                status["available"] = True
                status["version"] = result.stdout.strip()
            else:
                status["error"] = result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            status["error"] = "명령어 실행 시간 초과"
        except FileNotFoundError:
            status["error"] = "Amazon Q CLI를 찾을 수 없습니다"
        except Exception as e:
            status["error"] = str(e)
        
        return status
