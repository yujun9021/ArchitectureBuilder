import streamlit as st
import subprocess
import re
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="클라우드 아키텍처 다이어그램 생성기",
    page_icon="☁️",
    layout="wide"
)

# 세션 상태 초기화
if 'diagram_code' not in st.session_state:
    st.session_state.diagram_code = ""
if 'diagram_image' not in st.session_state:
    st.session_state.diagram_image = None

def call_amazon_q_cli(requirement_text):
    """Amazon Q CLI를 통해 다이어그램 생성 요청"""
    try:
        # 구조화된 다이어그램 생성 프롬프트
        diagram_prompt = f"""
다음 클라우드 아키텍처 요구사항에 대한 다이어그램을 생성해주세요:

요구사항: {requirement_text}

작업 내용:
1. Python diagrams 라이브러리를 사용하여 다이어그램 코드 생성
2. 실제 다이어그램 이미지 파일(.png)을 './generated-diagrams' 폴더에 저장
3. AWS 서비스 아이콘과 연결 관계를 포함한 시각적 아키텍처 다이어그램 생성

응답 형식:
다이어그램 코드:
```python
[생성된 Python 코드]
```

파일 정보:
- 파일명: [생성된_파일명.png]
- 저장 경로: ./generated-diagrams/[생성된_파일명.png]
- 상태: 완료

아키텍처 설명:
[생성된 아키텍처에 대한 간단한 설명]
"""
        
        # Amazon Q CLI 실행 (현재 디렉토리에서 실행)
        cmd = f'source ~/.bashrc && export PATH=$PATH:/home/yujun/.local/bin && cd /mnt/c/study/AB/ArchitectureBuilder && printf "y\\ny\\ny\\n" | q chat "{diagram_prompt}"'
        
        result = subprocess.run([
            'wsl', '-e', 'bash', '-c', cmd
        ], capture_output=True, text=True, timeout=120, encoding='utf-8')
        
        # 디버깅 정보
        st.info(f"🔍 Return Code: {result.returncode}")
        st.info(f"🔍 STDOUT 길이: {len(result.stdout) if result.stdout else 0}")
        st.info(f"🔍 STDERR 길이: {len(result.stderr) if result.stderr else 0}")
        
        if result.returncode == 0:
            return result.stdout or ""
        else:
            st.error(f"Amazon Q CLI 오류: {result.stderr}")
            return None
                
    except Exception as e:
        st.error(f"Amazon Q CLI 실행 오류: {str(e)}")
        return None

def parse_amazon_q_response(response):
    """Amazon Q 응답을 구조화된 형식으로 파싱"""
    result = {
        'filename': None,
        'code': None,
        'description': None,
        'status': 'unknown'
    }
    
    # MCP generate_diagram 호출 패턴 찾기 (우선순위 1)
    mcp_match = re.search(r'"filename":\s*"([^"]+)"', response)
    if mcp_match:
        result['filename'] = f"{mcp_match.group(1)}.png"
        result['status'] = 'mcp_detected'
    
    # 구조화된 형식에서 파일명 추출 (우선순위 2)
    file_match = re.search(r'파일명:\s*([^\s\n]+\.png)', response)
    if file_match:
        result['filename'] = file_match.group(1)
        result['status'] = 'structured'
    
    # Python 코드 추출
    if "```python" in response:
        code_start = response.find("```python") + 9
        code_end = response.find("```", code_start)
        if code_end != -1:
            result['code'] = response[code_start:code_end].strip()
    
    # 아키텍처 설명 추출
    desc_match = re.search(r'아키텍처 설명:\s*(.+?)(?=\n\n|\n파일 정보:|$)', response, re.DOTALL)
    if desc_match:
        result['description'] = desc_match.group(1).strip()
    
    return result

def main():
    st.title("☁️ 클라우드 아키텍처 다이어그램 생성기")
    st.markdown("Amazon Q와 DiagramMCP를 사용하여 클라우드 아키텍처 다이어그램을 생성합니다.")
    
    # 메인 컨텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 요구사항 입력")
        
        requirement = st.text_area(
            "클라우드 아키텍처 요구사항을 자세히 설명해주세요:",
            height=200,
            placeholder="예시: 웹 애플리케이션을 위한 고가용성 아키텍처가 필요합니다..."
        )
        
        if st.button("🚀 아키텍처 다이어그램 생성", type="primary"):
            if requirement:
                with st.spinner("Amazon Q CLI를 통해 다이어그램을 생성하고 있습니다..."):
                    q_response = call_amazon_q_cli(requirement)
                    
                    if q_response:
                        # Amazon Q 응답 파싱
                        parsed_response = parse_amazon_q_response(q_response)
                        
                        # 파싱 결과 표시
                        st.info(f"📄 응답 상태: {parsed_response['status']}")
                        if parsed_response['filename']:
                            st.info(f"📄 추출된 파일명: {parsed_response['filename']}")
                        if parsed_response['description']:
                            st.info(f"📝 아키텍처 설명: {parsed_response['description']}")
                        
                        # 다이어그램 폴더 확인 (상대 경로 사용)
                        diagram_folder = Path('./generated-diagrams')
                        diagram_folder.mkdir(parents=True, exist_ok=True)
                        
                        if parsed_response['filename']:
                            target_file = diagram_folder / parsed_response['filename']
                            
                            # 디버깅 정보 추가
                            st.info(f"🔍 찾는 파일: {target_file}")
                            st.info(f"🔍 파일 존재 여부: {target_file.exists()}")
                            st.info(f"🔍 현재 작업 디렉토리: {Path.cwd()}")
                            
                            if target_file.exists():
                                st.success("✅ 다이어그램 생성 완료")
                                st.session_state.diagram_image = str(target_file)
                            else:
                                st.warning(f"⚠️ 파일을 찾을 수 없습니다: {parsed_response['filename']}")
                                
                                # 폴더 내용 확인
                                if diagram_folder.exists():
                                    all_files = list(diagram_folder.glob('*'))
                                    st.info(f"🔍 폴더 내용: {[f.name for f in all_files]}")
                                
                                # 현재 디렉토리에서 PNG 파일 찾기
                                current_png_files = list(Path('.').glob('*.png'))
                                if current_png_files:
                                    st.info(f"🔍 현재 디렉토리 PNG 파일들: {[f.name for f in current_png_files]}")
                                
                                # 상위 디렉토리에서 PNG 파일 찾기
                                parent_png_files = list(Path('..').glob('*.png'))
                                if parent_png_files:
                                    st.info(f"🔍 상위 디렉토리 PNG 파일들: {[f.name for f in parent_png_files]}")
                        else:
                            # 폴더 내 최신 PNG 파일 찾기
                            png_files = list(diagram_folder.glob('*.png'))
                            if png_files:
                                latest_file = max(png_files, key=lambda x: x.stat().st_mtime)
                                st.success("✅ 다이어그램 생성 완료")
                                st.session_state.diagram_image = str(latest_file)
                            else:
                                st.error("❌ 다이어그램 파일을 찾을 수 없습니다.")
                        
                        # Python 코드 저장
                        if parsed_response['code']:
                            st.session_state.diagram_code = parsed_response['code']
                        else:
                            st.session_state.diagram_code = q_response
                    else:
                        st.error("❌ 다이어그램 생성 실패")
            else:
                st.warning("⚠️ 요구사항을 입력해주세요.")
    
    with col2:
        st.header("📊 생성된 다이어그램")
        
        if st.session_state.diagram_image:
            st.image(st.session_state.diagram_image, use_column_width=True)
            
            with open(st.session_state.diagram_image, "rb") as file:
                st.download_button(
                    label="📥 다이어그램 다운로드",
                    data=file.read(),
                    file_name="cloud_architecture.png",
                    mime="image/png"
                )
        else:
            st.info("👈 왼쪽에서 요구사항을 입력하고 다이어그램을 생성해보세요.")
    
    # 생성된 코드 표시
    if st.session_state.diagram_code:
        st.header("💻 생성된 Python 코드")
        st.code(st.session_state.diagram_code, language="python")
        
        st.download_button(
            label="📥 Python 코드 다운로드",
            data=st.session_state.diagram_code,
            file_name="cloud_architecture.py",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
