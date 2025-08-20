#!/bin/bash

# AWS JSON Converter & Diagram Generator (Final Version) 실행 스크립트

echo "⚡ AWS JSON Converter & Diagram Generator (Final) 시작"
echo "=================================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 작업 디렉토리: $SCRIPT_DIR"

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "💡 .env.example을 참고하여 .env 파일을 생성해주세요."
    
    if [ -f ".env.example" ]; then
        echo "📋 .env.example 파일 내용:"
        cat .env.example
        echo ""
        echo "위 내용을 참고하여 .env 파일을 생성하고 GEMINI_API_KEY를 설정해주세요."
    fi
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

# 다이어그램 디렉토리 확인
if [ ! -d "generated-diagrams" ]; then
    mkdir -p generated-diagrams
    echo "📁 다이어그램 디렉토리 생성 완료"
else
    echo "📁 다이어그램 디렉토리 확인 완료"
fi

# 환경 테스트
echo "🧪 환경 테스트 중..."
if [ -f "test_improved_final.py" ]; then
    python3 test_improved_final.py
    
    if [ $? -eq 0 ]; then
        echo "✅ 환경 테스트 통과"
    else
        echo "❌ 환경 테스트 실패"
        exit 1
    fi
else
    echo "⚠️ 테스트 파일이 없어 환경 테스트를 건너뜁니다."
fi

# Amazon Q CLI 상태 확인
echo "🤖 Amazon Q CLI 상태 확인..."
if command -v q &> /dev/null; then
    Q_VERSION=$(q --version 2>/dev/null || echo "버전 확인 실패")
    echo "✅ Amazon Q CLI 사용 가능: $Q_VERSION"
else
    echo "ℹ️ Amazon Q CLI가 설치되지 않았습니다."
    echo "💡 CLI 없이도 안정화된 생성기로 다이어그램을 생성할 수 있습니다."
fi

# 로그 파일 설정
LOG_FILE="final_app.log"
echo "📝 로그 파일: $LOG_FILE"

# Streamlit 설정
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo ""
echo "🚀 Final AWS Diagram Generator 시작 중..."
echo "🌐 브라우저에서 http://localhost:8501 접속"
echo "⏹️ 종료하려면 Ctrl+C를 누르세요"
echo ""
echo "📋 주요 기능:"
echo "  - CLI 우선, 실패 시 안정화된 생성기 자동 사용"
echo "  - JSON 결과 숨김 (복사 기능만 제공)"
echo "  - 간단한 원클릭 다이어그램 생성"
echo ""

# Streamlit 앱 실행
streamlit run streamlit_chatbot_final_improved.py \
    --server.port=$STREAMLIT_SERVER_PORT \
    --server.address=$STREAMLIT_SERVER_ADDRESS \
    --browser.gatherUsageStats=false \
    --logger.level=info \
    2>&1 | tee "$LOG_FILE"

echo ""
echo "⚡ Final AWS Diagram Generator 종료"
echo "📝 로그는 $LOG_FILE에서 확인할 수 있습니다."
