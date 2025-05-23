# Streamlit Deployment Troubleshooting Guide

## Recent Fixes Applied (January 2025)

### Problem: "No module named 'plotly'" on Streamlit Cloud
Multiple deployment attempts failed with missing plotly dependency.

### Root Causes Identified:
1. **Conflicting dependency management**: Both `environment.yml` (conda) and `requirements.txt` (pip) were present
2. **Streamlit Cloud prioritized conda over pip**: This caused version conflicts
3. **Python version mismatch**: Local vs. deployment environment differences

### Solutions Applied:

#### 1. Standardized on pip dependency management
- ✅ **Removed** `environment.yml` to eliminate conda conflicts
- ✅ **Updated** `requirements.txt` with specific version ranges:
  ```
  streamlit>=1.28.0
  pandas>=2.0.0
  plotly>=5.17.0
  numpy>=1.24.0,<2.0.0
  numpy-financial==1.0.0
  reportlab>=4.0.0
  ```

#### 2. Aligned Python versions
- ✅ **Changed** `runtime.txt` from `python-3.10` to `python-3.9`
- ✅ **Added** system dependencies in `packages.txt`:
  ```
  python3-dev
  build-essential
  ```

#### 3. Optimized Streamlit configuration
- ✅ **Updated** `.streamlit/config.toml` with deployment-friendly settings
- ✅ **Disabled** problematic features like `enableStaticServing`

### Key Insights from Streamlit Documentation:

According to [Streamlit's dependency docs](https://docs.streamlit.io/deploy/concepts/dependencies):

> "Since dependencies may rely on a specific version of Python, always be aware of the Python version used in your development environment, and select the same version for your deployment environment."

> "If you have a script that uses pandas and numpy, you would only need to install Streamlit. No extra dependencies would be needed since pandas and numpy are installed as direct dependencies of streamlit."

However, for complex apps with plotting libraries, **explicit version specification is critical**.

### Testing Strategy:

1. **Local verification**: Run `python test_imports.py` to verify all dependencies
2. **Streamlit Cloud logs**: Monitor for warning messages about multiple requirements files
3. **Version alignment**: Ensure `runtime.txt`, `requirements.txt`, and local environment match

### Future Deployment Best Practices:

1. ✅ **Use only pip** (`requirements.txt`) for Streamlit Cloud
2. ✅ **Specify version ranges** not exact pins (allows flexibility)
3. ✅ **Test locally** with matching Python version
4. ✅ **Monitor deployment logs** for warnings about dependency management
5. ✅ **Keep dependencies minimal** but explicit

### Emergency Debugging Commands:

If deployment fails again:

```bash
# Local test
python test_imports.py

# Check for conflicting files
ls -la *.txt *.yml

# Verify requirements format
cat requirements.txt

# Check Python version alignment
cat runtime.txt
```

This guide helped resolve 5+ consecutive deployment failures with "No module named 'plotly'" errors. 