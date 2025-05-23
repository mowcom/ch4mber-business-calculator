#!/usr/bin/env python3
"""
Test script to verify all required imports work correctly
"""

print("Testing imports...")

try:
    print("Testing streamlit...")
    import streamlit as st
    print(f"✓ streamlit {st.__version__}")
except ImportError as e:
    print(f"✗ streamlit failed: {e}")

try:
    print("Testing pandas...")
    import pandas as pd
    print(f"✓ pandas {pd.__version__}")
except ImportError as e:
    print(f"✗ pandas failed: {e}")

try:
    print("Testing plotly...")
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go
    print(f"✓ plotly {plotly.__version__}")
except ImportError as e:
    print(f"✗ plotly failed: {e}")

try:
    print("Testing numpy...")
    import numpy as np
    print(f"✓ numpy {np.__version__}")
except ImportError as e:
    print(f"✗ numpy failed: {e}")

try:
    print("Testing numpy_financial...")
    import numpy_financial as npf
    print(f"✓ numpy_financial {npf.__version__}")
except ImportError as e:
    print(f"✗ numpy_financial failed: {e}")

try:
    print("Testing reportlab...")
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    print("✓ reportlab")
except ImportError as e:
    print(f"✗ reportlab failed: {e}")

try:
    print("Testing utils modules...")
    from utils.finance import calc_credits, economics, create_timeline, calculate_npv, create_cash_flow
    from utils.credit_calc import compute_credits
    print("✓ utils modules")
except ImportError as e:
    print(f"✗ utils modules failed: {e}")

print("\nAll tests completed!") 