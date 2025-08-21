"""
Amazon Q CLI 클라이언트 모듈
"""
import streamlit as st
import subprocess
import platform
import os
import time
from config import AMAZON_Q_PATH, DIAGRAM_SETTINGS

class AmazonQClient:
    """Amazon Q CLI 클라이언트"""
    
    def __init__(self):
        self.platform = platform.system()
        self._last_execution_time = 0
        self._execution_cooldown = 2  # 2초 쿨다운
        self._cached_environment = None
        self._environment_cache_time = 0
        self._environment_cache_duration = 300  # 5분 캐시
        
    def _get_cached_environment(self):
        """캐시된 환경 설정 반환"""
        current_time = time.time()
        if (self._cached_environment is None or 
            current_time - self._environment_cache_time > self._environment_cache_duration):
            
            # 환경 설정 캐시 업데이트
            home_dir = os.path.expanduser("~")
            local_bin = os.path.join(home_dir, ".local", "bin")
            
            if self.platform == "Windows":
                # WSL 환경 설정
                wsl_check = subprocess.run(['wsl', '--version'], capture_output=True, text=True)
                if wsl_check.returncode == 0:
                    self._cached_environment = {
                        'type': 'wsl',
                        'local_bin': local_bin,
                        'wsl_available': True
                    }
                else:
                    self._cached_environment = {
                        'type': 'windows_native',
                        'local_bin': local_bin,
                        'wsl_available': False
                    }
            else:
                self._cached_environment = {
                    'type': 'unix',
                    'local_bin': local_bin,
                    'wsl_available': False
                }
            
            self._environment_cache_time = current_time
            
        return self._cached_environment
    
    def _check_execution_cooldown(self):
        """실행 쿨다운 확인"""
        current_time = time.time()
        if current_time - self._last_execution_time < self._execution_cooldown:
            remaining = self._execution_cooldown - (current_time - self._last_execution_time)
            st.warning(f"⚠️ Amazon Q CLI 실행 중입니다. {remaining:.1f}초 후 다시 시도해주세요.")
            return False
        return True
    
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
        """플랫폼별 명령어 실행 (최적화됨)"""
        try:
            # 실행 쿨다운 확인
            if not self._check_execution_cooldown():
                return None
                
            # 캐시된 환경 설정 사용
            env_config = self._get_cached_environment()
            
            if env_config['type'] == 'wsl':
                return self._execute_wsl_optimized(prompt, env_config)
            elif env_config['type'] == 'windows_native':
                return self._execute_windows_native(prompt, env_config)
            else:
                return self._execute_unix_optimized(prompt, env_config)
                
        except Exception as e:
            st.error(f"Amazon Q CLI 실행 오류: {str(e)}")
            return None
        finally:
            self._last_execution_time = time.time()
    
    def _execute_wsl_optimized(self, prompt, env_config):
        """WSL에서 최적화된 명령어 실행"""
        try:
            # Windows 경로를 WSL 경로로 변환
            current_dir = os.getcwd()
            wsl_path = current_dir.replace('C:', '/mnt/c').replace('\\', '/')
            diagram_folder = f"{wsl_path}/generated-diagrams"
            
            # 프롬프트에서 Windows 경로를 WSL 경로로 교체
            wsl_prompt = prompt.replace(current_dir.replace('\\', '/'), wsl_path)
            
            cmd = f'source ~/.bashrc && export PATH=$PATH:{env_config["local_bin"]} && printf "y\\ny\\ny\\n" | {AMAZON_Q_PATH} chat "{wsl_prompt}"'
            
            return subprocess.run([
                'wsl', '-e', 'bash', '-c', cmd
            ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
            
        except FileNotFoundError:
            # WSL 명령어를 찾을 수 없으면 Windows 네이티브로 폴백
            return self._execute_windows_native(prompt, env_config)
    
    def _execute_windows_native(self, prompt, env_config):
        """Windows 네이티브에서 명령어 실행"""
        cmd = f'{AMAZON_Q_PATH} chat "{prompt}"'
        return subprocess.run([
            'cmd', '/c', cmd
        ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
    
    def _execute_unix_optimized(self, prompt, env_config):
        """Linux/Mac에서 최적화된 명령어 실행"""
        cmd = f'source ~/.bashrc && export PATH=$PATH:{env_config["local_bin"]} && printf "y\\ny\\ny\\n" | {AMAZON_Q_PATH} chat "{prompt}"'
        
        return subprocess.run([
            'bash', '-c', cmd
        ], capture_output=True, text=True, timeout=DIAGRAM_SETTINGS['timeout'], encoding=DIAGRAM_SETTINGS['encoding'])
    
    def generate_diagram(self, requirement_text):
        """Amazon Q CLI를 통해 다이어그램 생성 요청 (최적화됨)"""
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
