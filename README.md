# CH4mber Business Calculator

A comprehensive Streamlit application for calculating carbon credits and financial metrics for methane abatement projects, specifically well plugging operations based on the CarbonPath v1.3 methodology (Solution 1: Direct Measurement).

## 🚀 Live App

**[Deploy on Streamlit Cloud →](https://ch4mber-business-calculator-hgsakhjsfoc7aquagvcvge.streamlit.app/)**

## ✨ Features

### Business Analysis
- **A/B Scenario Management**: Create and compare multiple scenarios side-by-side
- **Depth-Based Cost Presets**: Automatic P&A cost calculation based on well depth buckets
- **Risk Assessment Dashboard**: Color-coded flags for non-viable wells and low credit potential
- **NPV & Cash Flow Analysis**: Interactive timeline with adjustable discount rates
- **Token Price Sensitivity**: Heatmap analysis for profit optimization under varying market conditions

### User Experience
- **Tabbed Interface**: Organized workflow (Inputs → Results → Comparison → Credit Calculator)
- **Mathematical Credit Calculation**: Step-by-step LaTeX formula display with detailed breakdowns
- **Advanced Data Export**: CSV downloads and professional PDF reports with ReportLab
- **File Upload Support**: Import well data from CSV files
- **Enhanced Data Validation**: Real-time input validation with helpful tooltips

### Technical Features
- **Professional PDF Generation**: Using ReportLab (replaced FPDF for Unicode support)
- **Interactive Visualizations**: Plotly charts for cash flow, sensitivity analysis, and risk assessment
- **Responsive Design**: Modern UI with dark theme and professional styling
- **Error Handling**: Comprehensive validation and user-friendly error messages

## 🛠 Local Development

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mowcom/ch4mber-business-calculator.git
   cd ch4mber-business-calculator
   ```

2. **Set up the environment** (choose one):

   **Option A: Using our setup script**:
   ```bash
   # On macOS/Linux
   ./setup_env.sh
   
   # On Windows
   setup_env.bat
   ```

   **Option B: Manual setup**:
   ```bash
   conda create -n carbon-credits python=3.9
   conda activate carbon-credits
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

### Testing Dependencies

We include a dependency test script to verify your environment:

```bash
python test_imports.py
```

This will verify all required packages are properly installed.

## 🚀 Deployment

### Streamlit Community Cloud

**This repository is optimized for one-click deployment to Streamlit Cloud.**

1. **Fork or clone** this repository to your GitHub account
2. **Visit** [Streamlit Community Cloud](https://streamlit.io/cloud)
3. **Create new app** pointing to:
   - **Repository**: `your-username/ch4mber-business-calculator`
   - **Branch**: `main`
   - **Main file**: `app.py`
4. **Deploy** - it should work immediately!

### Deployment Configuration

The repository includes optimized deployment files:
- `requirements.txt`: Python dependencies with tested version ranges
- `runtime.txt`: Python 3.9 (aligned with Streamlit Cloud)
- `packages.txt`: System dependencies (python3-dev, build-essential)
- `.streamlit/config.toml`: Optimized Streamlit configuration

### Troubleshooting

If you encounter deployment issues, see our comprehensive [Deployment Troubleshooting Guide](DEPLOYMENT_TROUBLESHOOTING.md).

## 📁 Project Structure

```
business-scenarios/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies  
├── runtime.txt                     # Python version for deployment
├── packages.txt                    # System dependencies
├── test_imports.py                 # Dependency verification script
├── utils/
│   ├── finance.py                  # Financial calculations & NPV analysis
│   └── credit_calc.py              # Carbon credit mathematical calculations
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── data/                           # Sample CSV files
├── docs/                           # Documentation assets
├── setup_env.sh                    # Environment setup (Unix)
├── setup_env.bat                   # Environment setup (Windows)
├── DEPLOYMENT_TROUBLESHOOTING.md   # Comprehensive deployment guide
└── README.md                       # This file
```

## 🧮 Credit Calculation Methodology

The application implements the **CarbonPath v1.3 methodology** for calculating carbon credits from methane abatement:

1. **Leak Rate Measurement**: Direct measurement in kg/min
2. **Annual Emissions**: Convert to tonnes CO₂e using GWP factors
3. **Total Project Emissions**: Multiply by crediting period (years)
4. **Credit Generation**: Apply methodology-specific factors

The Credit Calculator tab provides step-by-step mathematical breakdowns with LaTeX formula rendering.

## 🔧 Development Notes

### Recent Improvements (Sprint 2)
- Replaced FPDF with ReportLab for better PDF generation
- Added numpy-financial for accurate NPV calculations  
- Implemented comprehensive A/B scenario management
- Created interactive sensitivity analysis tools
- Enhanced UI with tabbed interface and risk dashboards

### Dependencies Resolved
- Fixed plotly import issues on Streamlit Cloud
- Eliminated conda/pip conflicts by standardizing on pip
- Aligned Python versions between local and deployment environments

## 📊 Key Business Metrics

The calculator provides analysis across multiple dimensions:
- **Financial**: NPV, IRR, payback period, cash flow projections
- **Technical**: P&A costs by depth, equipment requirements, timeline
- **Market**: Token price sensitivity, profit optimization scenarios
- **Risk**: Well viability flags, credit generation potential

## 🤝 Contributing

This is an internal project for Chamber technologies. For questions or enhancement requests, please contact the development team.

## 📄 License

Internal use only - Chamber Technologies © 2025 