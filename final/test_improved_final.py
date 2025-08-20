#!/usr/bin/env python3
"""
수정된 final_improved 파일 테스트
"""

import sys
import os
sys.path.append('/home/gowns1345/chatbot-project')

def test_safe_diagram_generator():
    """SafeDiagramGenerator 클래스 테스트"""
    print("🔧 SafeDiagramGenerator 테스트 시작")
    
    try:
        # 수정된 파일에서 클래스 import
        from streamlit_chatbot_final_improved import SafeDiagramGenerator
        
        # 인스턴스 생성
        generator = SafeDiagramGenerator()
        print("✅ SafeDiagramGenerator 인스턴스 생성 성공")
        
        # 테스트 데이터
        test_data = {
            "service": "EC2",
            "natural_language_input": "EC2 인스턴스 2개를 생성해주세요",
            "parameters": {"count": 2, "region": "us-east-1"}
        }
        
        print("📊 테스트 데이터:", test_data)
        
        # 다이어그램 생성 테스트
        print("🎨 다이어그램 생성 중...")
        diagram_path = generator.create_safe_diagram(test_data)
        
        if diagram_path and os.path.exists(diagram_path):
            file_size = os.path.getsize(diagram_path)
            print(f"✅ 다이어그램 생성 성공: {diagram_path}")
            print(f"📁 파일 크기: {file_size} bytes")
            return True
        else:
            print(f"❌ 다이어그램 생성 실패: {diagram_path}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """필요한 모듈들 import 테스트"""
    print("\n📦 모듈 import 테스트")
    
    try:
        import streamlit
        print("✅ streamlit")
        
        import matplotlib.pyplot
        print("✅ matplotlib")
        
        from diagrams import Diagram
        print("✅ diagrams")
        
        import subprocess
        print("✅ subprocess")
        
        return True
        
    except Exception as e:
        print(f"❌ import 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 수정된 final_improved 파일 테스트")
    print("=" * 50)
    
    # 모듈 테스트
    import_success = test_imports()
    
    # 다이어그램 생성기 테스트
    generator_success = test_safe_diagram_generator()
    
    print("\n🏁 테스트 결과")
    print(f"📦 모듈 import: {'✅ 성공' if import_success else '❌ 실패'}")
    print(f"🔧 다이어그램 생성기: {'✅ 성공' if generator_success else '❌ 실패'}")
    
    if import_success and generator_success:
        print("🎉 모든 테스트 통과! 수정된 파일이 정상 작동합니다.")
        sys.exit(0)
    else:
        print("⚠️ 일부 테스트 실패")
        sys.exit(1)
