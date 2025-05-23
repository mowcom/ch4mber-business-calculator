#!/bin/bash

# Create and set up conda environment for the carbon credits calculator
echo "Creating conda environment 'carbon-credits'..."
conda create -n carbon-credits python=3.10 -y

# Activate the environment
eval "$(conda shell.bash hook)"
conda activate carbon-credits

# Install required packages
echo "Installing required packages..."
conda install -c conda-forge streamlit pandas plotly reportlab numpy -y
pip install numpy-financial==1.0.0

echo ""
echo "Environment setup complete. You can now activate the environment with:"
echo "conda activate carbon-credits"
echo "And run the app with:"
echo "streamlit run app.py" 