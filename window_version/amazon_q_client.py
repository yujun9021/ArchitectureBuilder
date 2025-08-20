"""
Amazon Q CLI 클라이언트 모듈
"""
import streamlit as st
import subprocess
import platform
import os
from config import AMAZON_Q_PATH, DIAGRAM_SETTINGS

class AmazonQClient:
    """Amazon Q CLI 클라이언트"""
    
    def __init__(self):
        self.platform = platform.system()
    
    def generate_diagram_prompt(self, requirement_text):
        """다이어그램 생성 프롬프트 생성"""
        # 현재 작업 디렉토리의 절대 경로 계산
        current_dir = os.getcwd()
        diagram_folder = os.path.join(current_dir, 'generated-diagrams')
        
        return f"""
다음 클라우드 아키텍처 요구사항에 대한 다이어그램을 생성해주세요:

요구사항: {requirement_text}

작업 내용:
1. Python diagrams 라이브러리를 사용하여 다이어그램 코드 생성
2. 실제 다이어그램 이미지 파일(.png)을 '{diagram_folder}' 폴더에 저장
3. AWS 서비스 아이콘과 연결 관계를 포함한 시각적 아키텍처 다이어그램 생성

응답 형식:
다이어그램 코드:
```python
[생성된 Python 코드]
```

파일 정보:
- 파일명: [생성된_파일명.png]
- 저장 경로: {diagram_folder}/[생성된_파일명.png]
- 상태: 완료

아키텍처 설명:
[생성된 아키텍처에 대한 간단한 설명]
"""
    
    def execute_command(self, prompt):
        """플랫폼별 명령어 실행"""
        try:
            if self.platform == "Windows":
                return self._execute_windows(prompt)
            else:
                return self._execute_unix(prompt)
        except Exception as e:
            st.error(f"Amazon Q CLI 실행 오류: {str(e)}")
            return None
    
    def _execute_windows(self, prompt):
        """Windows에서 명령어 실행"""
        try:
            # WSL이 설치되어 있는지 확인
            wsl_check = subprocess.run(['wsl', '--version'], capture_output=True, text=True)
            if wsl_check.returncode == 0:
                # WSL 사용 - Windows 경로를 WSL 경로로 변환
                current_dir = os.getcwd()
                wsl_path = current_dir.replace('C:', '/mnt/c').replace('\\', '/')
                diagram_folder = f"{wsl_path}/generated-diagrams"
                
                # 프롬프트에서 Windows 경로를 WSL 경로로 교체
                wsl_prompt = prompt.replace(current_dir.replace('\\', '/'), wsl_path)
                
                home_dir = os.path.expanduser("~")
                local_bin = os.path.join(home_dir, ".local", "bin")
                cmd = f'source ~/.bashrc && export PATH=$PATH:{local_bin} && printf "y\\ny\\ny\\n" | {AMAZON_Q_PATH} chat "{wsl_prompt}"'
                
                return subprocess.run([
                    'wsl', '-e', 'bash', '-c', cmd
                ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
            else:
                # WSL이 없으면 직접 실행 시도
                cmd = f'{AMAZON_Q_PATH} chat "{prompt}"'
                return subprocess.run([
                    'cmd', '/c', cmd
                ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
                
        except FileNotFoundError:
            # WSL 명령어를 찾을 수 없으면 직접 실행
            cmd = f'{AMAZON_Q_PATH} chat "{prompt}"'
            return subprocess.run([
                'cmd', '/c', cmd
            ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
    
    def _execute_unix(self, prompt):
        """Linux/Mac에서 명령어 실행"""
        home_dir = os.path.expanduser("~")
        local_bin = os.path.join(home_dir, ".local", "bin")
        cmd = f'source ~/.bashrc && export PATH=$PATH:{local_bin} && printf "y\\ny\\ny\\n" | {AMAZON_Q_PATH} chat "{prompt}"'
        
        return subprocess.run([
            'bash', '-c', cmd
        ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
    
    def generate_diagram(self, requirement_text):
        """Amazon Q CLI를 통해 다이어그램 생성 요청"""
        try:
            prompt = self.generate_diagram_prompt(requirement_text)
            result = self.execute_command(prompt)
            
            if result and result.returncode == 0:
                return result.stdout or ""
            else:
                if result:
                    st.error(f"Amazon Q CLI 오류: {result.stderr}")
                return None
                
        except Exception as e:
            st.error(f"Amazon Q CLI 실행 오류: {str(e)}")
            return None
