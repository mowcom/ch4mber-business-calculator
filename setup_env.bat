@echo off
echo Creating conda environment 'carbon-credits'...
call conda create -n carbon-credits python=3.10 -y

echo Installing required packages...
call conda activate carbon-credits
call conda install -c conda-forge streamlit pandas plotly fpdf2 openpyxl -y

echo.
echo Environment setup complete. You can now activate the environment with:
echo conda activate carbon-credits
echo And run the app with:
echo streamlit run app.py
echo.
pause 