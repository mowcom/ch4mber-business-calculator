#!/usr/bin/env python3
"""
Test script to verify all dependencies can be imported.
Run this locally and on deployment to debug import issues.
"""

import sys
print(f"Python version: {sys.version}")

try:
    import streamlit as st
    print("✅ streamlit imported successfully")
    print(f"   Streamlit version: {st.__version__}")
except ImportError as e:
    print(f"❌ streamlit import failed: {e}")

try:
    import pandas as pd
    print("✅ pandas imported successfully")
    print(f"   Pandas version: {pd.__version__}")
except ImportError as e:
    print(f"❌ pandas import failed: {e}")

try:
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go
    print("✅ plotly imported successfully")
    print(f"   Plotly version: {plotly.__version__}")
except ImportError as e:
    print(f"❌ plotly import failed: {e}")

try:
    import numpy as np
    print("✅ numpy imported successfully") 
    print(f"   Numpy version: {np.__version__}")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

try:
    import numpy_financial as npf
    print("✅ numpy-financial imported successfully")
except ImportError as e:
    print(f"❌ numpy-financial import failed: {e}")

try:
    import reportlab
    print("✅ reportlab imported successfully")
    print(f"   ReportLab version: {reportlab.Version}")
except ImportError as e:
    print(f"❌ reportlab import failed: {e}")

print("\n🎯 All dependency tests completed!") 