# 🚀 빠른 설정 가이드

## 1️⃣ 필수 준비사항

### Python 설치 확인
```bash
python --version  # 3.8 이상이어야 함
```

### Gemini API 키 발급
1. https://makersuite.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. API 키 복사

## 2️⃣ 프로젝트 설정

### 1. 가상환경 생성 (권장)
```bash
python -m venv venv
```

### 2. 가상환경 활성화
**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 텍스트 에디터로 열기
```

**.env 파일 내용:**
```
GEMINI_API_KEY=여기에_실제_API_키_입력
```

## 3️⃣ 실행

### 자동 실행 (권장)
**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

### 수동 실행
```bash
streamlit run main_app.py
```

## 4️⃣ 접속

브라우저에서 http://localhost:8501 접속

## 🧪 첫 번째 테스트

다음 프롬프트를 입력해보세요:
```
EC2 인스턴스 하나와 S3 버킷을 연결한 간단한 아키텍처 그려줘
```

## ❗ 문제 해결

### 1. 모듈을 찾을 수 없다는 오류
```bash
pip install -r requirements.txt
```

### 2. Gemini API 오류
- .env 파일에 올바른 API 키가 설정되어 있는지 확인
- API 키에 할당량이 남아있는지 확인

### 3. 다이어그램 생성 실패
- Graphviz 설치 필요할 수 있음:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install graphviz
  
  # macOS
  brew install graphviz
  
  # Windows
  # https://graphviz.org/download/ 에서 다운로드
  ```

## 📞 도움이 필요하면

1. README.md 파일 전체 읽기
2. 오류 메시지 확인
3. 의존성 재설치: `pip install -r requirements.txt --force-reinstall`
