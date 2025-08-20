"""
다이어그램 파일 관리 모듈
"""
import streamlit as st
from pathlib import Path

class DiagramManager:
    """다이어그램 파일 관리"""
    
    def __init__(self):
        self.diagram_folder = Path('./generated-diagrams')
        self.diagram_folder.mkdir(parents=True, exist_ok=True)
    
    def find_diagram_file(self, filename):
        """지정된 파일명으로 다이어그램 파일 찾기"""
        if filename:
            target_file = self.diagram_folder / filename
            return target_file, target_file.exists()
        return None, False
    
    def find_latest_diagram(self):
        """최신 다이어그램 파일 찾기"""
        png_files = list(self.diagram_folder.glob('*.png'))
        if png_files:
            latest_file = max(png_files, key=lambda x: x.stat().st_mtime)
            return latest_file
        return None
    
    def get_folder_contents(self):
        """다이어그램 폴더 내용 반환"""
        if self.diagram_folder.exists():
            return [f.name for f in self.diagram_folder.glob('*')]
        return []
    
    def get_current_directory_png_files(self):
        """현재 디렉토리의 PNG 파일들 반환"""
        return [f.name for f in Path('.').glob('*.png')]
    
    def get_parent_directory_png_files(self):
        """상위 디렉토리의 PNG 파일들 반환"""
        return [f.name for f in Path('..').glob('*.png')]
    
    def display_debug_info(self, filename):
        """디버깅 정보 표시"""
        if filename:
            target_file, exists = self.find_diagram_file(filename)
            st.info(f"🔍 찾는 파일: {target_file}")
            st.info(f"🔍 파일 존재 여부: {exists}")
            st.info(f"🔍 현재 작업 디렉토리: {Path.cwd()}")
            st.info(f"🔍 다이어그램 폴더: {self.diagram_folder}")
            st.info(f"🔍 다이어그램 폴더 존재 여부: {self.diagram_folder.exists()}")
            
            if not exists:
                # 폴더 내용 확인
                folder_contents = self.get_folder_contents()
                if folder_contents:
                    st.info(f"🔍 폴더 내용: {folder_contents}")
                else:
                    st.warning("⚠️ 다이어그램 폴더가 비어있습니다.")
                
                # 현재 디렉토리에서 PNG 파일 찾기
                current_png_files = self.get_current_directory_png_files()
                if current_png_files:
                    st.info(f"🔍 현재 디렉토리 PNG 파일들: {current_png_files}")
                
                # 상위 디렉토리에서 PNG 파일 찾기
                parent_png_files = self.get_parent_directory_png_files()
                if parent_png_files:
                    st.info(f"🔍 상위 디렉토리 PNG 파일들: {parent_png_files}")
                
                # 절대 경로로도 확인
                absolute_target = Path.cwd() / 'generated-diagrams' / filename
                st.info(f"🔍 절대 경로 파일 존재 여부: {absolute_target.exists()}")
                
                # 전체 시스템에서 PNG 파일 검색 (최근 5개)
                all_png_files = list(Path.cwd().rglob('*.png'))
                if all_png_files:
                    recent_files = sorted(all_png_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                    st.info(f"🔍 최근 PNG 파일들: {[str(f) for f in recent_files]}")
