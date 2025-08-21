# AWS Diagram Generator (Amazon Q CLI 전용)

자연어로 AWS 아키텍처를 설명하면 자동으로 전문적인 다이어그램을 생성해주는 도구입니다.

## 🚀 주요 기능

- **자연어 입력**: 복잡한 AWS 아키텍처를 자연어로 설명
- **JSON 구조화**: Gemini AI가 자연어를 구조화된 JSON으로 변환
- **Amazon Q CLI 연동**: 실제 Amazon Q CLI를 활용한 전문적인 다이어그램 생성
- **실시간 진행상황**: 다이어그램 생성 과정을 실시간으로 확인
- **다양한 AWS 서비스 지원**: EC2, RDS, S3, Lambda, VPC 등 주요 서비스 지원

## 📋 사전 요구사항

### 1. Python 환경
- Python 3.8 이상

### 2. Amazon Q CLI 설치
```bash
# Amazon Q CLI 설치 (필수)
# 설치 방법: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/cli-install.html
```

### 3. Gemini API 키
- Google AI Studio에서 API 키 발급: https://makersuite.google.com/app/apikey

## 🛠️ 설치 및 실행

### 1. 프로젝트 클론/다운로드
```bash
# 이 폴더를 원하는 위치에 복사
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어서 Gemini API 키 입력
# GEMINI_API_KEY=your_actual_api_key_here
```

### 5. 애플리케이션 실행
```bash
streamlit run main_app.py
```

브라우저에서 `http://localhost:8501`로 접속

## 🧪 테스트 프롬프트 예시

### 간단한 테스트
```
EC2 인스턴스 하나와 S3 버킷을 연결한 간단한 아키텍처 그려줘
```

### 복잡한 테스트
```
서울리전에 3-tier 웹 애플리케이션을 구축하고 싶어. 2개의 가용영역을 사용해서 고가용성으로 만들어줘. 각 AZ에 퍼블릭 서브넷과 프라이빗 서브넷을 만들고, 퍼블릭 서브넷에는 웹 서버용 EC2 인스턴스들을 배치하고 Application Load Balancer로 트래픽을 분산시켜줘. 프라이빗 서브넷에는 애플리케이션 서버용 EC2와 PostgreSQL RDS를 Multi-AZ로 구성해줘. 그리고 정적 파일 저장용 S3 버킷도 포함시켜줘.
```

## 📁 프로젝트 구조

```
aws-diagram-generator-team/
├── main_app.py              # 메인 애플리케이션
├── requirements.txt         # Python 의존성
├── .env.example            # 환경변수 예시
├── README.md               # 이 파일
└── modules/                # 핵심 모듈들
    ├── __init__.py
    ├── gemini_handler.py    # Gemini API 처리
    ├── cli_diagram_generator.py  # Amazon Q CLI 다이어그램 생성
    └── ui_components.py     # Streamlit UI 컴포넌트
```

## 🔧 지원하는 AWS 서비스

- **컴퓨팅**: EC2, Lambda, Auto Scaling
- **네트워킹**: VPC, 서브넷, Load Balancer, Internet Gateway, NAT Gateway
- **데이터베이스**: RDS (MySQL, PostgreSQL, Oracle), DynamoDB
- **스토리지**: S3, EFS
- **모니터링**: CloudWatch, X-Ray
- **보안**: Security Groups, NACLs

## 🎯 사용 팁

1. **리전 지정**: "서울리전", "오사카리전", "버지니아리전" 등으로 명시
2. **가용영역**: "2개의 AZ", "3개의 가용영역" 등으로 지정
3. **고가용성**: "고가용성", "Multi-AZ" 키워드 사용
4. **서브넷 구분**: "퍼블릭 서브넷", "프라이빗 서브넷" 명시
5. **서비스 연결**: "EC2에서 RDS로", "로드밸런서 뒤에" 등 관계 설명

## ❗ 문제 해결

### Amazon Q CLI 관련
- Amazon Q CLI가 설치되어 있는지 확인: `q --version`
- AWS 자격 증명이 설정되어 있는지 확인

### Gemini API 관련
- API 키가 올바르게 설정되어 있는지 확인
- API 키에 충분한 할당량이 있는지 확인

### 다이어그램 생성 실패
- Python diagrams 패키지가 설치되어 있는지 확인
- Graphviz가 시스템에 설치되어 있는지 확인

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. 모든 의존성이 올바르게 설치되었는지
2. 환경변수가 올바르게 설정되었는지
3. Amazon Q CLI가 정상 작동하는지

---

**Made with ❤️ for AWS Architecture Visualization**
