@echo off
echo Creating conda environment 'carbon-credits'...
call conda create -n carbon-credits python=3.10 -y

echo Installing required packages...
call conda activate carbon-credits
call conda install -c conda-forge streamlit pandas plotly reportlab numpy -y
call pip install numpy-financial==1.0.0

echo.
echo Environment setup complete. You can now activate the environment with:
echo conda activate carbon-credits
echo And run the app with:
echo streamlit run app.py
echo.
pause 