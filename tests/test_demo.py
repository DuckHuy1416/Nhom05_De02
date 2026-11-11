"""Kiểm tra lệnh demo độc lập, bao gồm đầu ra tiếng Việt trên Windows."""
import subprocess
import sys
from pathlib import Path


def test_demo_runs():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / "demo.py")], cwd=root,
                            capture_output=True, encoding="utf-8", check=False)
    assert result.returncode == 0, result.stderr
    assert "dự đoán GIẢ" in result.stdout
    assert "CN1: chưa cài đặt" in result.stdout
    assert "CN2: chưa cài đặt" in result.stdout
