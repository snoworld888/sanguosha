"""
GEO 智能优化平台 - 测试配置
"""
import sys
from pathlib import Path

# 添加src到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))
