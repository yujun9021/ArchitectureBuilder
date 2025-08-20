#!/bin/bash

# 수정된 final_improved 파일 실행 스크립트

echo "⚡ AWS JSON Converter & Diagram Generator (안정화) 시작"
echo "=================================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 작업 디렉토리: $SCRIPT_DIR"

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "💡 .env.example을 참고하여 .env 파일을 생성해주세요."
    exit 1
fi

# Gemini API 키 확인
if ! grep -q "GEMINI_API_KEY" .env; then
    echo "❌ GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다."
    echo "💡 .env 파일에 GEMINI_API_KEY=your_api_key를 추가해주세요."
    exit 1
fi

echo "✅ 환경 설정 확인 완료"

# 필수 패키지 확인
echo "📦 필수 패키지 확인 중..."

REQUIRED_PACKAGES=(
    "streamlit"
    "google-generativeai"
    "python-dotenv"
    "pyperclip"
    "diagrams"
    "matplotlib"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import ${package//-/_}" 2>/dev/null; then
        echo "✅ $package 사용 가능"
    else
        echo "📦 $package 설치 중..."
        pip install "$package" --user
    fi
done

# 시스템 레벨 graphviz 확인
if command -v dot &> /dev/null; then
    echo "✅ graphviz 사용 가능"
else
    echo "📦 graphviz 설치 중..."
    sudo apt-get update && sudo apt-get install -y graphviz
fi

echo "✅ 모든 패키지 확인 완료"

# 다이어그램 디렉토리 생성
mkdir -p generated-diagrams
echo "📁 다이어그램 디렉토리 준비 완료"

# 환경 테스트
echo "🧪 환경 테스트 중..."
python3 test_improved_final.py

if [ $? -eq 0 ]; then
    echo "✅ 환경 테스트 통과"
else
    echo "❌ 환경 테스트 실패"
    exit 1
fi

# 로그 파일 설정
LOG_FILE="final_improved_chatbot.log"
echo "📝 로그 파일: $LOG_FILE"

# Streamlit 설정
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo ""
echo "🚀 안정화된 다이어그램 생성기 시작 중..."
echo "🌐 브라우저에서 http://localhost:8501 접속"
echo "⏹️ 종료하려면 Ctrl+C를 누르세요"
echo ""

# Streamlit 앱 실행
streamlit run streamlit_chatbot_final_improved.py \
    --server.port=$STREAMLIT_SERVER_PORT \
    --server.address=$STREAMLIT_SERVER_ADDRESS \
    --browser.gatherUsageStats=false \
    --logger.level=info \
    2>&1 | tee "$LOG_FILE"

echo ""
echo "⚡ AWS JSON Converter & Diagram Generator (안정화) 종료"
echo "📝 로그는 $LOG_FILE에서 확인할 수 있습니다."
