"""
backend/__init__.py

Centralizes sys.path management so all backend sub-modules
(tools, mcp, etc.) can import from the backend root without
needing to hack sys.path inside each file.
"""
import sys
import os

# Ensure the backend/ directory is always on the Python path
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
