"""
다이어그램 파일 관리 모듈
"""
import streamlit as st
from pathlib import Path
import time
from typing import Optional, Tuple, List

class DiagramManager:
    """다이어그램 파일 관리"""
    
    def __init__(self):
        self.diagram_folder = Path('./generated-diagrams')
        self.diagram_folder.mkdir(parents=True, exist_ok=True)
        
        # 캐싱을 위한 변수들
        self._file_cache = {}
        self._latest_file_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 5  # 5초 캐시 유지
        
    def _is_cache_valid(self) -> bool:
        """캐시가 유효한지 확인"""
        return time.time() - self._cache_timestamp < self._cache_duration
    
    def _update_cache(self):
        """캐시 업데이트"""
        self._file_cache.clear()
        self._latest_file_cache = None
        self._cache_timestamp = time.time()
        
        # 폴더 내 모든 PNG 파일을 캐시에 저장
        if self.diagram_folder.exists():
            for png_file in self.diagram_folder.glob('*.png'):
                self._file_cache[png_file.name] = png_file
                if (self._latest_file_cache is None or 
                    png_file.stat().st_mtime > self._latest_file_cache.stat().st_mtime):
                    self._latest_file_cache = png_file
    
    def find_diagram_file(self, filename: str) -> Tuple[Optional[Path], bool]:
        """지정된 파일명으로 다이어그램 파일 찾기 (캐시 활용)"""
        if not filename:
            return None, False
            
        # 캐시가 유효하지 않으면 업데이트
        if not self._is_cache_valid():
            self._update_cache()
        
        # 캐시에서 파일 찾기
        if filename in self._file_cache:
            return self._file_cache[filename], True
            
        # 캐시에 없으면 직접 확인 (새로 생성된 파일일 수 있음)
        target_file = self.diagram_folder / filename
        exists = target_file.exists()
        
        # 존재하면 캐시에 추가
        if exists:
            self._file_cache[filename] = target_file
            
        return target_file, exists
    
    def find_latest_diagram(self) -> Optional[Path]:
        """최신 다이어그램 파일 찾기 (캐시 활용)"""
        # 캐시가 유효하지 않으면 업데이트
        if not self._is_cache_valid():
            self._update_cache()
            
        return self._latest_file_cache
    
    def find_diagram_by_pattern(self, pattern: str) -> Optional[Path]:
        """패턴으로 다이어그램 파일 찾기"""
        if not self._is_cache_valid():
            self._update_cache()
            
        # 캐시된 파일들 중에서 패턴 매칭
        for filename, file_path in self._file_cache.items():
            if pattern.lower() in filename.lower():
                return file_path
        return None
    
    def get_all_diagrams(self) -> List[Path]:
        """모든 다이어그램 파일 반환 (캐시 활용)"""
        if not self._is_cache_valid():
            self._update_cache()
            
        return list(self._file_cache.values())
    
    def get_folder_contents(self) -> List[str]:
        """다이어그램 폴더 내용 반환 (캐시 활용)"""
        if not self._is_cache_valid():
            self._update_cache()
            
        return list(self._file_cache.keys())
    
    def force_refresh_cache(self):
        """캐시 강제 새로고침"""
        self._update_cache()
    
    def get_current_directory_png_files(self):
        """현재 디렉토리의 PNG 파일들 반환"""
        return [f.name for f in Path('.').glob('*.png')]
    
    def get_parent_directory_png_files(self):
        """상위 디렉토리의 PNG 파일들 반환"""
        return [f.name for f in Path('..').glob('*.png')]
    
    def display_debug_info(self, filename):
        """디버깅 정보 표시 (최적화됨)"""
        if filename:
            target_file, exists = self.find_diagram_file(filename)
            st.info(f"🔍 찾는 파일: {target_file}")
            st.info(f"🔍 파일 존재 여부: {exists}")
            st.info(f"🔍 현재 작업 디렉토리: {Path.cwd()}")
            st.info(f"🔍 다이어그램 폴더: {self.diagram_folder}")
            st.info(f"🔍 다이어그램 폴더 존재 여부: {self.diagram_folder.exists()}")
            
            if not exists:
                # 캐시된 폴더 내용 사용
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
