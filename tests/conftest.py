import os
import sys

# Allow `import config`, `import analytics`, ... when running `pytest` from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
