@echo off
REM AWS Diagram Generator 실행 스크립트 (Windows)

echo 🚀 AWS Diagram Generator 시작 중...

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 📦 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 의존성 확인
echo 🔍 의존성 확인 중...
pip install -r requirements.txt

REM .env 파일 확인
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다. .env.example을 참고해서 .env 파일을 생성해주세요.
    echo 📝 Gemini API 키를 설정해야 합니다.
    pause
    exit /b 1
)

REM Amazon Q CLI 확인
q --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Amazon Q CLI가 설치되어 있지 않습니다.
    echo 📖 설치 가이드: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/cli-install.html
    echo 🔄 Amazon Q CLI 없이도 기본 다이어그램 생성은 가능합니다.
)

REM Streamlit 실행
echo 🌐 Streamlit 애플리케이션 시작 중...
echo 📱 브라우저에서 http://localhost:8501 로 접속하세요.
streamlit run main_app.py

pause
