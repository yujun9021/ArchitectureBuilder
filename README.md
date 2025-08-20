# ArchitectureBuilder

AWS 아키텍처 다이어그램을 자동으로 생성하는 Streamlit 애플리케이션입니다.

## 🚀 주요 기능

- **자연어 입력**: AWS 아키텍처 요구사항을 자연어로 입력
- **자동 다이어그램 생성**: Amazon Q CLI와 DiagramMCP를 사용한 자동 다이어그램 생성
- **Gemini AI 챗봇**: 클라우드 아키텍처 관련 질문 답변
- **크로스 플랫폼 지원**: Windows, Linux, macOS 지원
ㄴ
## ⚙️ 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Gemini API 키 (필수)
# Google AI Studio (https://makersuite.google.com/app/apikey)에서 발급받은 API 키
GOOGLE_API_KEY=your_gemini_api_key_here

# Amazon Q CLI 경로 (선택사항)
# 기본값: 'q' (PATH에 설치된 경우)
# 커스텀 경로: '/path/to/amazon-q' 또는 'C:\\Program Files\\Amazon\\AmazonQ\\q.exe'
AMAZON_Q_PATH=q
```

### 3. Amazon Q CLI 설치

#### Windows
```bash
winget install Amazon.AmazonQ
```
또는 [공식 사이트](https://aws.amazon.com/ko/amazon-q/)에서 다운로드

#### Linux/macOS
```bash
curl -fsSL https://aws.amazon.com/ko/amazon-q/install.sh | sh
```

## 🎯 사용 방법

1. **애플리케이션 실행**
   ```bash
   streamlit run app.py
   ```

2. **요구사항 입력**: 클라우드 아키텍처 요구사항을 자연어로 입력

3. **다이어그램 생성**: "아키텍처 다이어그램 생성" 버튼 클릭

4. **결과 확인**: 생성된 다이어그램과 Python 코드 확인

## 📁 프로젝트 구조

```
ArchitectureBuilder/
├── app.py                          # 메인 Streamlit 애플리케이션
├── streamlit_chatbot_simple.py     # 간단한 챗봇 버전
├── requirements.txt                 # Python 의존성
├── .env                           # 환경변수 설정 (사용자 생성)
├── .gitignore                     # Git 무시 파일
└── generated-diagrams/            # 생성된 다이어그램 저장 폴더 (Git 무시)
```

## 🔧 문제 해결

### Amazon Q CLI 오류
- Amazon Q CLI가 올바르게 설치되었는지 확인
- `AMAZON_Q_PATH` 환경변수가 올바른 경로를 가리키는지 확인
- Windows에서 WSL 사용 시 WSL이 활성화되어 있는지 확인

### Gemini API 오류
- `GOOGLE_API_KEY`가 올바르게 설정되었는지 확인
- Google AI Studio에서 API 키가 활성화되어 있는지 확인

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.