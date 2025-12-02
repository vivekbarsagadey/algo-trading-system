import os
import sys

# Ensure the repo root is on sys.path so `import app` works during pytest
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
