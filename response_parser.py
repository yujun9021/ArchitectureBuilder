"""
Amazon Q 응답 파싱 모듈
"""
import re

class ResponseParser:
    """Amazon Q 응답을 구조화된 형식으로 파싱"""
    
    @staticmethod
    def parse_response(response):
        """응답을 구조화된 형식으로 파싱"""
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
