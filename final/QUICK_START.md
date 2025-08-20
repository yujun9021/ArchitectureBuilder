# 🚀 AWS Diagram Generator - 빠른 시작 가이드

## 📁 포함된 파일들

```
final/
├── streamlit_chatbot_final_improved.py  # 메인 애플리케이션
├── amazon_q_cli_integration_improved.py # Amazon Q CLI 연동
├── run_final_app.sh                     # 실행 스크립트 (추천)
├── run_final_improved.sh                # 대체 실행 스크립트
├── test_improved_final.py               # 테스트 스크립트
├── requirements.txt                     # 필수 패키지 목록
├── .env                                 # 환경 변수 (API 키 포함)
├── .env.example                         # 환경 변수 예시
├── README.md                            # 상세 문서
├── QUICK_START.md                       # 이 파일
└── generated-diagrams/                  # 생성된 다이어그램 저장소
```

## ⚡ 빠른 실행 (3단계)

### 1단계: 환경 변수 설정
```bash
# .env 파일에 Gemini API 키가 설정되어 있는지 확인
cat .env

# 만약 API 키가 없다면:
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

### 2단계: 실행
```bash
# 실행 권한 확인 (필요시)
chmod +x run_final_app.sh

# 애플리케이션 실행
./run_final_app.sh
```

### 3단계: 브라우저 접속
```
http://localhost:8501
```

## 🔧 수동 설치 (필요시)

### 패키지 설치
```bash
# pip로 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install streamlit google-generativeai python-dotenv pyperclip diagrams matplotlib

# 시스템 레벨 graphviz 설치
sudo apt-get install graphviz
```

### 수동 실행
```bash
streamlit run streamlit_chatbot_final_improved.py
```

## 🧪 테스트

### 환경 테스트
```bash
python3 test_improved_final.py
```

### Amazon Q CLI 테스트 (선택적)
```bash
q --version
```

## 🎯 주요 특징

- **🤖 CLI 우선**: Amazon Q CLI로 전문적인 다이어그램 우선 시도
- **🔄 자동 대체**: CLI 실패 시 안정화된 생성기로 자동 전환
- **⚡ 원클릭**: 복잡한 설정 없이 간단한 다이어그램 생성
- **📊 투명성**: 사용된 생성 방식 명확히 표시
- **🛡️ 안정성**: 어떤 상황에서도 다이어그램 생성 보장

## 💡 사용법

1. **자연어 입력**: "EC2 인스턴스 3개를 생성해주세요"
2. **다이어그램 생성 버튼 클릭**
3. **자동 처리**: 시스템이 최적 방법으로 생성
4. **결과 확인**: 생성된 다이어그램 및 사용 방식 확인

## 🔍 문제 해결

### 일반적인 문제
- **API 키 오류**: `.env` 파일에 올바른 `GEMINI_API_KEY` 설정
- **패키지 오류**: `pip install -r requirements.txt` 재실행
- **권한 오류**: `chmod +x run_final_app.sh` 실행
- **포트 충돌**: 다른 Streamlit 앱 종료 후 재시도

### 고급 문제
- **graphviz 오류**: `sudo apt-get install graphviz` 실행
- **Python 경로**: 가상환경 활성화 확인
- **메모리 부족**: 브라우저 새로고침 후 재시도

## 📞 지원

- **테스트**: `python3 test_improved_final.py`
- **로그**: `final_app.log` 파일 확인
- **문서**: `README.md` 상세 문서 참조

---

**🚀 간단하고 안정적인 AWS 다이어그램 생성을 시작하세요!**
