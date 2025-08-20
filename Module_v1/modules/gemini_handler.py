"""
Gemini API 처리 모듈
자연어를 구조화된 JSON으로 변환
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
import google.generativeai as genai
import streamlit as st


class GeminiHandler:
    """Gemini API를 사용한 자연어 처리 및 JSON 구조화"""
    
    def __init__(self):
        self.api_key = None
        self.model = None
        self.cache = {}
        self.initialize_gemini()
    
    def initialize_gemini(self) -> bool:
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
    
    def is_ready(self) -> bool:
        """Gemini API 사용 가능 여부 확인"""
        return self.model is not None
    
    def _generate_cache_key(self, natural_language: str) -> str:
        """입력 텍스트에 대한 캐시 키 생성"""
        normalized = natural_language.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def generate_aws_json(self, natural_language: str) -> Optional[Dict[str, Any]]:
        """자연어를 AWS JSON으로 구조화"""
        try:
            # 캐시 확인
            cache_key = self._generate_cache_key(natural_language)
            if cache_key in self.cache:
                st.info("🔄 캐시된 결과를 사용합니다.")
                return self.cache[cache_key]
            
            # 프롬프트 생성
            prompt = self._create_prompt(natural_language)
            
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
            st.error(f"Gemini JSON 생성 실패: {str(e)}")
            return None
    
    def _create_prompt(self, natural_language: str) -> str:
        """Amazon Q CLI용 최적화된 프롬프트 생성 - 모든 자연어 요구사항 처리"""
        return f"""
사용자의 자연어 요청을 Amazon Q CLI가 이해하기 쉬운 최적화된 AWS 아키텍처 JSON으로 변환해주세요.

입력: "{natural_language}"

Amazon Q CLI가 빠르고 정확하게 다이어그램을 생성할 수 있도록 다음 JSON 스키마를 따라 응답해주세요:

{{
    "request_type": "AWS Architecture Request for Amazon Q CLI",
    "natural_language_input": "{natural_language}",
    "architecture": {{
        "type": "vpc|serverless|container|hybrid|simple 중 하나",
        "complexity": "simple|medium|complex",
        "region": "리전명 (예: ap-northeast-1, us-east-1)",
        "availability_zones": 숫자 (AZ 개수, 1-3)
    }},
    "networking": {{
        "vpc": {{
            "enabled": true/false,
            "cidr": "10.0.0.0/16",
            "subnets": [
                {{
                    "type": "public|private",
                    "az": "a|b|c",
                    "cidr": "10.0.x.0/24",
                    "name": "서브넷명"
                }}
            ]
        }},
        "internet_gateway": true/false,
        "nat_gateway": true/false,
        "load_balancer": {{
            "enabled": true/false,
            "type": "application|network|classic"
        }}
    }},
    "compute": {{
        "ec2": {{
            "enabled": true/false,
            "instances": [
                {{
                    "name": "인스턴스명",
                    "type": "t3.micro|t3.small|m5.large 등",
                    "subnet_type": "public|private",
                    "az": "a|b|c",
                    "count": 숫자
                }}
            ]
        }},
        "lambda": {{
            "enabled": true/false,
            "functions": ["함수명들"]
        }},
        "ecs": {{
            "enabled": true/false,
            "services": ["서비스명들"]
        }}
    }},
    "database": {{
        "rds": {{
            "enabled": true/false,
            "engine": "mysql|postgresql|oracle|sqlserver",
            "multi_az": true/false,
            "subnet_type": "private",
            "instances": [
                {{
                    "name": "DB명",
                    "engine": "mysql|postgresql 등",
                    "instance_class": "db.t3.micro 등",
                    "az": "a|b|c"
                }}
            ]
        }},
        "dynamodb": {{
            "enabled": true/false,
            "tables": ["테이블명들"]
        }}
    }},
    "storage": {{
        "s3": {{
            "enabled": true/false,
            "buckets": ["버킷명들"]
        }},
        "efs": {{
            "enabled": true/false,
            "file_systems": ["파일시스템명들"]
        }}
    }},
    "security": {{
        "security_groups": true/false,
        "nacl": true/false,
        "waf": true/false,
        "cloudtrail": true/false
    }},
    "monitoring": {{
        "cloudwatch": true/false,
        "cloudtrail": true/false,
        "x_ray": true/false
    }},
    "diagram_description": "Amazon Q CLI가 생성할 상세한 다이어그램 설명",
    "optimization_hints": {{
        "complexity": "simple|medium|complex",
        "focus_areas": ["보안", "고가용성", "비용최적화", "성능", "확장성"] 중 선택,
        "preferred_services": ["사용자가 언급한 서비스들"],
        "exclude_security": false,
        "fast_generation": true
    }}
}}

분석 규칙:
1. 사용자가 언급한 모든 AWS 서비스와 리소스를 정확히 파악
2. 리전, AZ, 서브넷 정보를 명확히 구조화
3. 네트워킹 요구사항 (VPC, 서브넷, 게이트웨이) 상세 분석
4. 컴퓨팅, 데이터베이스, 스토리지 요구사항 분리
5. 보안 및 모니터링 요구사항 식별
6. 사용자가 명시하지 않은 내용은 기본값 사용
7. 반드시 유효한 JSON 형식으로만 응답
8. 추가 설명이나 마크다운 없이 JSON만 반환

예시 분석:
- "오사카리전에 VPC생성" → region: "ap-northeast-1", vpc.enabled: true
- "2개의 AZ영역" → availability_zones: 2
- "프라이빗/퍼블릭 서브넷" → subnets 배열에 각각 추가
- "EC2 인스턴스" → compute.ec2.enabled: true
- "MySQL RDS" → database.rds.enabled: true, engine: "mysql"

JSON:
"""
    
    def _parse_and_validate_json(self, response_text: str, original_input: str) -> Optional[Dict[str, Any]]:
        """JSON 파싱 및 검증"""
        try:
            clean_json = self._extract_json(response_text)
            if not clean_json:
                raise ValueError("JSON을 찾을 수 없습니다.")
            
            parsed_json = json.loads(clean_json)
            validated_json = self._validate_schema(parsed_json, original_input)
            
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
    
    def _validate_schema(self, data: Dict[str, Any], original_input: str) -> Dict[str, Any]:
        """강화된 스키마 검증 및 보정 - 모든 자연어 요구사항 처리"""
        # 필수 필드 확인 및 보정
        if "request_type" not in data:
            data["request_type"] = "AWS Architecture Request for Amazon Q CLI"
        
        if "natural_language_input" not in data:
            data["natural_language_input"] = original_input
        
        # 아키텍처 기본 구조 보정
        if "architecture" not in data:
            data["architecture"] = {}
        
        arch = data["architecture"]
        if "type" not in arch:
            arch["type"] = self._detect_architecture_type(original_input)
        if "complexity" not in arch:
            arch["complexity"] = self._detect_complexity(original_input)
        if "region" not in arch:
            arch["region"] = self._detect_region(original_input)
        if "availability_zones" not in arch:
            arch["availability_zones"] = self._detect_az_count(original_input)
        
        # 네트워킹 구조 보정
        if "networking" not in data:
            data["networking"] = {}
        
        net = data["networking"]
        if "vpc" not in net:
            net["vpc"] = {
                "enabled": self._detect_vpc_needed(original_input),
                "cidr": "10.0.0.0/16",
                "subnets": self._generate_subnets(original_input, arch["availability_zones"])
            }
        
        if "internet_gateway" not in net:
            net["internet_gateway"] = self._detect_igw_needed(original_input)
        if "nat_gateway" not in net:
            net["nat_gateway"] = self._detect_nat_needed(original_input)
        if "load_balancer" not in net:
            net["load_balancer"] = {
                "enabled": self._detect_lb_needed(original_input),
                "type": "application"
            }
        
        # 컴퓨팅 구조 보정
        if "compute" not in data:
            data["compute"] = {}
        
        comp = data["compute"]
        if "ec2" not in comp:
            comp["ec2"] = {
                "enabled": self._detect_ec2_needed(original_input),
                "instances": self._generate_ec2_instances(original_input)
            }
        if "lambda" not in comp:
            comp["lambda"] = {
                "enabled": self._detect_lambda_needed(original_input),
                "functions": []
            }
        if "ecs" not in comp:
            comp["ecs"] = {
                "enabled": self._detect_ecs_needed(original_input),
                "services": []
            }
        
        # 데이터베이스 구조 보정
        if "database" not in data:
            data["database"] = {}
        
        db = data["database"]
        if "rds" not in db:
            db["rds"] = {
                "enabled": self._detect_rds_needed(original_input),
                "engine": self._detect_db_engine(original_input),
                "multi_az": arch["availability_zones"] > 1,
                "subnet_type": "private",
                "instances": self._generate_rds_instances(original_input)
            }
        if "dynamodb" not in db:
            db["dynamodb"] = {
                "enabled": self._detect_dynamodb_needed(original_input),
                "tables": []
            }
        
        # 스토리지 구조 보정
        if "storage" not in data:
            data["storage"] = {}
        
        stor = data["storage"]
        if "s3" not in stor:
            stor["s3"] = {
                "enabled": self._detect_s3_needed(original_input),
                "buckets": []
            }
        if "efs" not in stor:
            stor["efs"] = {
                "enabled": self._detect_efs_needed(original_input),
                "file_systems": []
            }
        
        # 보안 및 모니터링 구조 보정
        if "security" not in data:
            data["security"] = {
                "security_groups": True,
                "nacl": False,
                "waf": False,
                "cloudtrail": False
            }
        
        if "monitoring" not in data:
            data["monitoring"] = {
                "cloudwatch": True,
                "cloudtrail": False,
                "x_ray": False
            }
        
        # 다이어그램 설명 생성
        if "diagram_description" not in data:
            data["diagram_description"] = self._generate_diagram_description(data)
        
        # 최적화 힌트 보정
        if "optimization_hints" not in data:
            data["optimization_hints"] = {
                "complexity": arch["complexity"],
                "focus_areas": ["고가용성", "성능"],
                "preferred_services": self._extract_services(original_input),
                "exclude_security": False,
                "fast_generation": True
            }
        
        return data
    
    def _detect_architecture_type(self, text: str) -> str:
        """아키텍처 타입 감지"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["vpc", "서브넷", "subnet", "네트워크"]):
            return "vpc"
        elif any(word in text_lower for word in ["lambda", "서버리스", "serverless"]):
            return "serverless"
        elif any(word in text_lower for word in ["container", "ecs", "fargate", "컨테이너"]):
            return "container"
        else:
            return "simple"
    
    def _detect_complexity(self, text: str) -> str:
        """복잡도 감지"""
        text_lower = text.lower()
        complex_indicators = ["multi", "여러", "다중", "고가용성", "로드밸런서", "오토스케일링"]
        simple_indicators = ["간단", "simple", "기본", "테스트"]
        
        if any(word in text_lower for word in complex_indicators):
            return "complex"
        elif any(word in text_lower for word in simple_indicators):
            return "simple"
        else:
            return "medium"
    
    def _detect_region(self, text: str) -> str:
        """리전 감지"""
        text_lower = text.lower()
        region_map = {
            "오사카": "ap-northeast-3",
            "osaka": "ap-northeast-3",
            "도쿄": "ap-northeast-1",
            "tokyo": "ap-northeast-1",
            "서울": "ap-northeast-2",
            "seoul": "ap-northeast-2",
            "버지니아": "us-east-1",
            "virginia": "us-east-1",
            "오레곤": "us-west-2",
            "oregon": "us-west-2"
        }
        
        for region_name, region_code in region_map.items():
            if region_name in text_lower:
                return region_code
        
        return "us-east-1"  # 기본값
    
    def _detect_az_count(self, text: str) -> int:
        """AZ 개수 감지"""
        text_lower = text.lower()
        if "2개" in text or "두개" in text or "2 az" in text_lower:
            return 2
        elif "3개" in text or "세개" in text or "3 az" in text_lower:
            return 3
        elif any(word in text_lower for word in ["고가용성", "multi-az", "다중"]):
            return 2
        else:
            return 1
    
    def _detect_vpc_needed(self, text: str) -> bool:
        """VPC 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["vpc", "서브넷", "subnet", "네트워크", "프라이빗", "퍼블릭"])
    
    def _detect_igw_needed(self, text: str) -> bool:
        """Internet Gateway 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["퍼블릭", "public", "인터넷", "internet", "웹"])
    
    def _detect_nat_needed(self, text: str) -> bool:
        """NAT Gateway 필요 여부 감지"""
        text_lower = text.lower()
        return "프라이빗" in text_lower and ("퍼블릭" in text_lower or "public" in text_lower)
    
    def _detect_lb_needed(self, text: str) -> bool:
        """Load Balancer 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["로드밸런서", "load balancer", "alb", "elb", "분산"])
    
    def _detect_ec2_needed(self, text: str) -> bool:
        """EC2 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["ec2", "인스턴스", "instance", "서버", "server"])
    
    def _detect_lambda_needed(self, text: str) -> bool:
        """Lambda 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["lambda", "람다", "서버리스", "serverless", "함수"])
    
    def _detect_ecs_needed(self, text: str) -> bool:
        """ECS 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["ecs", "fargate", "컨테이너", "container", "docker"])
    
    def _detect_rds_needed(self, text: str) -> bool:
        """RDS 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["rds", "mysql", "postgresql", "oracle", "데이터베이스", "database", "db"])
    
    def _detect_dynamodb_needed(self, text: str) -> bool:
        """DynamoDB 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["dynamodb", "다이나모", "nosql"])
    
    def _detect_s3_needed(self, text: str) -> bool:
        """S3 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["s3", "스토리지", "storage", "버킷", "bucket", "파일"])
    
    def _detect_efs_needed(self, text: str) -> bool:
        """EFS 필요 여부 감지"""
        text_lower = text.lower()
        return any(word in text_lower for word in ["efs", "파일시스템", "file system", "공유"])
    
    def _detect_db_engine(self, text: str) -> str:
        """데이터베이스 엔진 감지"""
        text_lower = text.lower()
        if "mysql" in text_lower:
            return "mysql"
        elif "postgresql" in text_lower or "postgres" in text_lower:
            return "postgresql"
        elif "oracle" in text_lower:
            return "oracle"
        elif "sqlserver" in text_lower or "sql server" in text_lower:
            return "sqlserver"
        else:
            return "mysql"  # 기본값
    
    def _generate_subnets(self, text: str, az_count: int) -> list:
        """서브넷 구성 생성"""
        subnets = []
        text_lower = text.lower()
        
        has_public = any(word in text_lower for word in ["퍼블릭", "public"])
        has_private = any(word in text_lower for word in ["프라이빗", "private"])
        
        if not has_public and not has_private:
            has_public = has_private = True  # 둘 다 없으면 둘 다 생성
        
        az_letters = ['a', 'b', 'c']
        cidr_base = 10
        
        for i in range(az_count):
            if has_public:
                subnets.append({
                    "type": "public",
                    "az": az_letters[i],
                    "cidr": f"10.0.{cidr_base}.0/24",
                    "name": f"public-subnet-{az_letters[i]}"
                })
                cidr_base += 1
            
            if has_private:
                subnets.append({
                    "type": "private",
                    "az": az_letters[i],
                    "cidr": f"10.0.{cidr_base}.0/24",
                    "name": f"private-subnet-{az_letters[i]}"
                })
                cidr_base += 1
        
        return subnets
    
    def _generate_ec2_instances(self, text: str) -> list:
        """EC2 인스턴스 구성 생성"""
        if not self._detect_ec2_needed(text):
            return []
        
        instances = []
        text_lower = text.lower()
        
        # 퍼블릭 서브넷에 EC2가 있는지 확인
        if "퍼블릭" in text_lower and "ec2" in text_lower:
            instances.append({
                "name": "web-server",
                "type": "t3.micro",
                "subnet_type": "public",
                "az": "a",
                "count": 1
            })
        
        # 프라이빗 서브넷에 EC2가 있는지 확인
        if "프라이빗" in text_lower and "ec2" in text_lower:
            instances.append({
                "name": "app-server",
                "type": "t3.micro",
                "subnet_type": "private",
                "az": "a",
                "count": 1
            })
        
        # 일반적인 경우
        if not instances:
            instances.append({
                "name": "ec2-instance",
                "type": "t3.micro",
                "subnet_type": "public",
                "az": "a",
                "count": 1
            })
        
        return instances
    
    def _generate_rds_instances(self, text: str) -> list:
        """RDS 인스턴스 구성 생성"""
        if not self._detect_rds_needed(text):
            return []
        
        return [{
            "name": "main-database",
            "engine": self._detect_db_engine(text),
            "instance_class": "db.t3.micro",
            "az": "a"
        }]
    
    def _generate_diagram_description(self, data: Dict[str, Any]) -> str:
        """다이어그램 설명 생성"""
        arch = data.get("architecture", {})
        region = arch.get("region", "us-east-1")
        az_count = arch.get("availability_zones", 1)
        
        description = f"{region} 리전에 {az_count}개 AZ를 사용한 AWS 아키텍처"
        
        # VPC 정보 추가
        if data.get("networking", {}).get("vpc", {}).get("enabled"):
            description += ", VPC 기반"
        
        # 주요 서비스 추가
        services = []
        if data.get("compute", {}).get("ec2", {}).get("enabled"):
            services.append("EC2")
        if data.get("database", {}).get("rds", {}).get("enabled"):
            services.append("RDS")
        if data.get("storage", {}).get("s3", {}).get("enabled"):
            services.append("S3")
        
        if services:
            description += f", {', '.join(services)} 포함"
        
        return description
    
    def _extract_services(self, text: str) -> list:
        """텍스트에서 AWS 서비스 추출"""
        text_lower = text.lower()
        services = []
        
        service_map = {
            "ec2": ["ec2", "인스턴스", "instance"],
            "rds": ["rds", "mysql", "postgresql", "데이터베이스"],
            "s3": ["s3", "스토리지", "버킷"],
            "lambda": ["lambda", "람다", "서버리스"],
            "vpc": ["vpc", "네트워크"],
            "elb": ["로드밸런서", "load balancer", "alb", "elb"]
        }
        
        for service, keywords in service_map.items():
            if any(keyword in text_lower for keyword in keywords):
                services.append(service.upper())
        
        return services
    
    def clear_cache(self):
        """캐시 삭제"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """캐시 크기 반환"""
        return len(self.cache)
