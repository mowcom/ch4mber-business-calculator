# Well Plugging Carbon Credits Calculator

A Streamlit application to calculate carbon credits and financial metrics for well plugging projects based on the CarbonPath v1.3 methodology (Solution 1: Direct Measurement).

## Features

- **Scenario Management**: Create A/B scenarios for side-by-side comparison of different assumptions
- **Depth-Based Cost Presets**: Automatically calculate P&A costs based on well depth
- **Risk Assessment Dashboard**: Flag non-viable wells and those with low credit potential
- **Cash Flow Analysis**: Visualize NPV and cash flow timeline for project planning
- **Token Price Sensitivity**: Interactive heatmap to understand profit under different price points
- **Improved Data Entry**: Enhanced input forms with validation and tooltips
- **Advanced Exports**: Download CSV and PDF reports with scenario comparison

## Demo

You can try the application at: [Streamlit Cloud App](https://carbon-credit-calculator.streamlit.app)

## Local Development

### Running Locally

1. Clone this repository
2. Create and activate a conda environment:
   ```
   conda create -n carbon-credits python=3.10
   conda activate carbon-credits
   ```
3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Deployment

### Deploying to Streamlit Community Cloud

1. Push your code to GitHub (this repository)
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Sign in with GitHub
4. Click "New app"
5. Select this repository, branch, and `app.py` as the main file
6. Click "Deploy"

That's it! Your app will be deployed and accessible via a public URL.

## Structure

- `app.py`: Main application code
- `utils/finance.py`: Financial calculations and utilities
- `data/`: Sample data files
- `docs/`: Documentation and screenshots

## License

This project is for internal use only. 