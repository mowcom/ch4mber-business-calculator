import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import io
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
import base64

from utils.finance import calc_credits, economics, create_timeline, calculate_npv, create_cash_flow

# Helper functions
def format_currency(value, decimals=0):
    """Format a numeric value as currency with comma separators"""
    if decimals == 0:
        return f"${value:,.0f}"
    else:
        return f"${value:,.{decimals}f}"

def format_number(value):
    """Format a numeric value with comma separators"""
    return f"{value:,.0f}"

def format_percentage(value, decimals=1):
    """Format a decimal value as a percentage"""
    return f"{value*100:.{decimals}f}%"

def highlight_risk(row):
    """Return styling for rows based on risk flags"""
    if row["Risk Flag"] == "Non-viable":
        return ['background-color: #ffcccc'] * len(row)
    elif row["Risk Flag"] == "Low Credits":
        return ['background-color: #ffffcc'] * len(row)
    elif row["Risk Flag"] == "At Risk":
        return ['background-color: #ffddaa'] * len(row)
    return [''] * len(row)

# Page configuration
st.set_page_config(
    page_title="Well Plugging Carbon Credits Calculator",
    page_icon="💰",
    layout="wide",
)

# App title
st.title("Well Plugging Carbon Credits Calculator")
st.caption("CarbonPath v1.3, Solution 1 (Direct Measurement)")

# Initialize default scenarios 
def initialize_default_scenarios():
    """Initialize default scenarios with sample data"""
    default_wells = [
        {"Well Name/API": "Well-01", "Leak LPM": 15, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 1500, "County": "Johnson", "Baseline Date": datetime.now().date()},
        {"Well Name/API": "Well-02", "Leak LPM": 42, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 2200, "County": "Tarrant", "Baseline Date": datetime.now().date()},
        {"Well Name/API": "Well-03", "Leak LPM": 36, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 4800, "County": "Parker", "Baseline Date": datetime.now().date()},
        {"Well Name/API": "Well-04", "Leak LPM": 22, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 3500, "County": "Wise", "Baseline Date": datetime.now().date()},
        {"Well Name/API": "Well-05", "Leak LPM": 12, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 4200, "County": "Denton", "Baseline Date": datetime.now().date()},
        {"Well Name/API": "Well-06", "Leak LPM": 15, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 6000, "County": "Hood", "Baseline Date": datetime.now().date()},
        {"Well Name/API": "Well-07", "Leak LPM": 32, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 5500, "County": "Erath", "Baseline Date": datetime.now().date()},
    ]
    
    return {
        "A": {
            "wells": default_wells.copy(),
            "token_price": 20.0,
            "path_fee": 0.02,
        },
        "B": {
            "wells": default_wells.copy(),
            "token_price": 25.0,
            "path_fee": 0.02,
        }
    }

# Initial data template - default values based on provided screenshot
EMPTY_WELL = {
    "Well Name/API": "",
    "Leak LPM": 0.1,  # Set minimum to 0.1 to avoid StreamlitValueBelowMinError
    "PnA $": 30000,   # Mid value from screenshot
    "Reclam $": 5000, # Mid value from screenshot
    "Sensor $": 12000,# Combined VVB ($4k) + MRV sensor ($8k)
    "Other $": 1000,  # Developer admin costs
    "Depth (ft)": 0,  # New field for depth
    "County": "",     # New field for county
    "Baseline Date": None, # New field for baseline test date
}

# Initialize session state
if "scenarios" not in st.session_state:
    st.session_state.scenarios = initialize_default_scenarios()

if "active_scenario" not in st.session_state:
    st.session_state.active_scenario = "A"

if "show_results" not in st.session_state:
    st.session_state.show_results = True  # Show results by default since we have wells

if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False  # Default to not comparing

# Main app layout with tabs
main_tabs = st.tabs(["Inputs", "Results", "Comparison"])

with main_tabs[0]:  # Inputs tab
    # Scenario Manager
    st.header("Scenario Manager")
    
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        active_scenario = st.radio("Active Scenario", ["A", "B"], index=0 if st.session_state.active_scenario == "A" else 1)
        
        if active_scenario != st.session_state.active_scenario:
            st.session_state.active_scenario = active_scenario
    
    with col2:
        compare_mode = st.checkbox("Compare Scenarios", value=st.session_state.compare_mode)
        
        if compare_mode != st.session_state.compare_mode:
            st.session_state.compare_mode = compare_mode
    
    with col3:
        if st.button("Clone A → B", use_container_width=True) and st.session_state.active_scenario == "A":
            st.session_state.scenarios["B"] = {
                "wells": [well.copy() for well in st.session_state.scenarios["A"]["wells"]],
                "token_price": st.session_state.scenarios["A"]["token_price"],
                "path_fee": st.session_state.scenarios["A"]["path_fee"],
            }
            st.success("Scenario A cloned to Scenario B")
            st.session_state.active_scenario = "B"
            st.rerun()
        
        if st.button("Clone B → A", use_container_width=True) and st.session_state.active_scenario == "B":
            st.session_state.scenarios["A"] = {
                "wells": [well.copy() for well in st.session_state.scenarios["B"]["wells"]],
                "token_price": st.session_state.scenarios["B"]["token_price"],
                "path_fee": st.session_state.scenarios["B"]["path_fee"],
            }
            st.success("Scenario B cloned to Scenario A")
            st.session_state.active_scenario = "A"
            st.rerun()
    
    st.markdown("---")
    
    # Current scenario parameters
    current_scenario = st.session_state.scenarios[st.session_state.active_scenario]
    
    # Sidebar inputs
    st.sidebar.header(f"Configuration - Scenario {st.session_state.active_scenario}")
    
    # Global parameters
    st.sidebar.subheader("Global Parameters")
    token_price = st.sidebar.slider("Token Price ($/tCO₂e)", min_value=1.0, max_value=30.0, value=current_scenario["token_price"], step=1.0)
    path_fee = st.sidebar.slider("CarbonPath Fee (%)", min_value=1.0, max_value=3.0, value=current_scenario["path_fee"] * 100, step=0.1) / 100
    
    # Update scenario parameters if changed
    if token_price != current_scenario["token_price"] or path_fee != current_scenario["path_fee"]:
        current_scenario["token_price"] = token_price
        current_scenario["path_fee"] = path_fee
    
    # Default costs (expandable)
    with st.sidebar.expander("Default Well Costs (2025 USD)"):
        default_pna = st.number_input("Default P&A Cost ($)", min_value=25000, max_value=80000, value=30000, step=1000, 
                                    help="Plug & abandon cost (range: $25k-$80k)")
        default_reclam = st.number_input("Default Reclamation Cost ($)", min_value=3000, max_value=10000, value=5000, step=500,
                                        help="Site reclamation - pad, grading, vegetation (range: $3k-$10k)")
        default_vvb = st.number_input("Default VVB Cost ($)", min_value=3000, max_value=6000, value=4000, step=500,
                                    help="Third-party validation & verification body (range: $3k-$6k)")
        default_sensor = st.number_input("Default Sensor Cost ($)", min_value=6000, max_value=12000, value=8000, step=500,
                                        help="MRV sensor contractor - 2 trips (range: $6k-$12k)")
        default_other = st.number_input("Default Admin Cost ($)", min_value=500, max_value=3000, value=1000, step=100,
                                    help="Developer admin - title, landowner, docs (range: $0.5k-$3k)")
        
        if st.button("Apply Defaults to All Wells"):
            for well in current_scenario["wells"]:
                well["PnA $"] = default_pna
                well["Reclam $"] = default_reclam
                well["Sensor $"] = default_vvb + default_sensor  # Combine VVB and sensor costs
                well["Other $"] = default_other
            st.success("Default costs applied!")
    
    # Add file upload option
    st.sidebar.subheader("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            uploaded_data = pd.read_csv(uploaded_file)
            required_columns = ["Well Name/API", "Leak LPM", "PnA $", "Reclam $", "Sensor $", "Other $"]
            
            # Check if the required columns are present
            if all(col in uploaded_data.columns for col in required_columns):
                # Convert DataFrame to list of dictionaries
                wells_list = uploaded_data.to_dict('records')
                
                # Process dates if they exist
                if "Baseline Date" in uploaded_data.columns:
                    for well in wells_list:
                        if "Baseline Date" in well and well["Baseline Date"] and not pd.isna(well["Baseline Date"]):
                            well["Baseline Date"] = pd.to_datetime(well["Baseline Date"]).date()
                        else:
                            well["Baseline Date"] = datetime.now().date()
                
                # Update the current scenario
                current_scenario["wells"] = wells_list
                st.sidebar.success(f"Loaded {len(wells_list)} wells from CSV!")
                st.session_state.show_results = True
                st.rerun()
            else:
                missing = [col for col in required_columns if col not in uploaded_data.columns]
                st.sidebar.error(f"CSV is missing required columns: {', '.join(missing)}")
        except Exception as e:
            st.sidebar.error(f"Error loading data: {str(e)}")
    
    # Sample data download
    sample_path = "data/sample_wells.csv"
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as file:
            st.sidebar.download_button(
                label="Download Sample CSV Template",
                data=file,
                file_name="sample_wells.csv",
                mime="text/csv"
            )
    
    # Sample data buttons
    st.sidebar.subheader("Sample Data")
    if st.sidebar.button("Reset to Default 7 Wells"):
        default_scenarios = initialize_default_scenarios()
        current_scenario["wells"] = default_scenarios[st.session_state.active_scenario]["wells"].copy()
        st.session_state.show_results = True
        st.success("Default 7 wells loaded!")
        st.rerun()
    
    if st.sidebar.button("Load More Sample Wells"):
        # Load additional sample data for demonstration
        current_scenario["wells"] = [
            {"Well Name/API": "Well-A-01", "Leak LPM": 15.3, "PnA $": 30000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 1800, "County": "Johnson", "Baseline Date": datetime.now().date()},
            {"Well Name/API": "Well-A-02", "Leak LPM": 25.7, "PnA $": 32000, "Reclam $": 5000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 2500, "County": "Tarrant", "Baseline Date": datetime.now().date()},
            {"Well Name/API": "Well-B-03", "Leak LPM": 18.9, "PnA $": 28000, "Reclam $": 4500, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 4200, "County": "Parker", "Baseline Date": datetime.now().date()},
            {"Well Name/API": "Well-B-04", "Leak LPM": 31.2, "PnA $": 29500, "Reclam $": 5200, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 5800, "County": "Wise", "Baseline Date": datetime.now().date()},
            {"Well Name/API": "Well-C-05", "Leak LPM": 42.1, "PnA $": 33000, "Reclam $": 6000, "Sensor $": 12000, "Other $": 1000, "Depth (ft)": 6500, "County": "Denton", "Baseline Date": datetime.now().date()},
        ]
        st.session_state.show_results = True
        st.success("Sample data loaded!")
        st.rerun()
    
    if st.sidebar.button("Clear All Wells"):
        current_scenario["wells"] = [EMPTY_WELL.copy()]
        st.session_state.show_results = False
        st.success("All wells cleared!")
        st.rerun()
    
    # Well input section
    st.subheader(f"Well Data Entry - Scenario {st.session_state.active_scenario}")
    
    # Function to validate wells data
    def validate_wells(wells):
        for i, well in enumerate(wells):
            if not well["Well Name/API"]:
                st.error(f"Well #{i+1} is missing a name or API number")
                return False
            if not well["Leak LPM"] or well["Leak LPM"] < 0.1:
                st.error(f"Well #{i+1} ({well['Well Name/API']}) has an invalid leak rate. Must be greater than 0.1.")
                return False
        return True
    
    # Add individual wells
    well_tabs = st.tabs([f"Well #{i+1}" for i in range(len(current_scenario["wells"]))] + ["+ Add Well"])
    
    for i, tab in enumerate(well_tabs[:-1]):  # Exclude the "Add Well" tab
        with tab:
            col1, col2 = st.columns(2)
            with col1:
                current_scenario["wells"][i]["Well Name/API"] = st.text_input(
                    "Well Name/API", 
                    value=current_scenario["wells"][i]["Well Name/API"],
                    key=f"well_name_{i}_{st.session_state.active_scenario}"
                )
                current_scenario["wells"][i]["Leak LPM"] = st.number_input(
                    "Leak Rate (L/min)", 
                    min_value=0.1,  # Minimum value set to 0.1
                    value=float(max(0.1, current_scenario["wells"][i]["Leak LPM"])),  # Ensure min value is at least 0.1
                    step=0.1,
                    key=f"leak_lpm_{i}_{st.session_state.active_scenario}",
                    help="Use baseline 15-min average measurement"
                )
                current_scenario["wells"][i]["Depth (ft)"] = st.number_input(
                    "Well Depth (ft)",
                    min_value=0,
                    value=int(current_scenario["wells"][i].get("Depth (ft)", 0)),
                    step=100,
                    key=f"depth_{i}_{st.session_state.active_scenario}"
                )
                current_scenario["wells"][i]["County"] = st.text_input(
                    "County",
                    value=current_scenario["wells"][i].get("County", ""),
                    key=f"county_{i}_{st.session_state.active_scenario}"
                )
                current_scenario["wells"][i]["Baseline Date"] = st.date_input(
                    "Baseline Test Date",
                    value=current_scenario["wells"][i].get("Baseline Date", datetime.now().date()),
                    key=f"baseline_date_{i}_{st.session_state.active_scenario}"
                )
            with col2:
                current_scenario["wells"][i]["PnA $"] = st.number_input(
                    "P&A Cost ($)", 
                    value=int(current_scenario["wells"][i]["PnA $"]), 
                    step=1000,
                    key=f"pna_cost_{i}_{st.session_state.active_scenario}"
                )
                current_scenario["wells"][i]["Reclam $"] = st.number_input(
                    "Reclamation Cost ($)", 
                    value=int(current_scenario["wells"][i]["Reclam $"]), 
                    step=500,
                    key=f"reclam_cost_{i}_{st.session_state.active_scenario}"
                )
                current_scenario["wells"][i]["Sensor $"] = st.number_input(
                    "Sensor + VVB Cost ($)", 
                    value=int(current_scenario["wells"][i]["Sensor $"]), 
                    step=500,
                    key=f"sensor_cost_{i}_{st.session_state.active_scenario}"
                )
                current_scenario["wells"][i]["Other $"] = st.number_input(
                    "Other CAPEX ($)", 
                    value=int(current_scenario["wells"][i]["Other $"]), 
                    step=100,
                    key=f"other_cost_{i}_{st.session_state.active_scenario}"
                )
            
            if st.button("Remove This Well", key=f"remove_well_{i}_{st.session_state.active_scenario}"):
                current_scenario["wells"].pop(i)
                st.rerun()
    
    # Handle the "Add Well" tab
    with well_tabs[-1]:
        st.write("Click the button below to add a new well to your analysis.")
        if st.button("Add New Well", key=f"add_well_{st.session_state.active_scenario}"):
            current_scenario["wells"].append(EMPTY_WELL.copy())
            st.rerun()
    
    # Calculate button
    calc_col1, calc_col2 = st.columns([3, 1])
    with calc_col2:
        calculate_button = st.button("Calculate Results", type="primary", use_container_width=True, key=f"calculate_{st.session_state.active_scenario}")
        if calculate_button:
            if validate_wells(current_scenario["wells"]):
                st.session_state.show_results = True
            else:
                st.session_state.show_results = False

# Results section
with main_tabs[1]:  # Results tab
    if st.session_state.show_results:
        # Get active scenario data
        current_scenario = st.session_state.scenarios[st.session_state.active_scenario]
        
        if len(current_scenario["wells"]) > 0 and validate_wells(current_scenario["wells"]):
            # Convert wells list to DataFrame
            df = pd.DataFrame(current_scenario["wells"])
            
            # Run calculations
            token_price = current_scenario["token_price"]
            path_fee = current_scenario["path_fee"]
            results_df = economics(df, token_price, path_fee)
            timeline_df = create_timeline(df)
            
            # Display summary table with risk flags highlighting
            st.subheader(f"Wells Summary - Scenario {st.session_state.active_scenario}")
            
            # Apply styling to dataframe
            styled_results = results_df.copy()
            # Format numbers with appropriate decimal places and commas
            styled_results["Credits"] = styled_results["Credits"].map(format_number)
            styled_results["Gross $"] = styled_results["Gross $"].map(format_currency)
            styled_results["Path fee $"] = styled_results["Path fee $"].map(format_currency)
            styled_results["Net $"] = styled_results["Net $"].map(format_currency)
            styled_results["Total cost $"] = styled_results["Total cost $"].map(format_currency)
            styled_results["Profit $"] = styled_results["Profit $"].map(format_currency)
            styled_results["Breakeven %"] = styled_results["Breakeven %"].map(format_percentage)
            
            # Apply highlighting based on risk flags
            styled_display = styled_results.style.apply(highlight_risk, axis=1)
            st.dataframe(styled_display, hide_index=True)
            
            # Risk dashboard summary
            st.subheader("Risk Assessment")
            non_viable_count = (results_df["Risk Flag"] == "Non-viable").sum()
            low_credits_count = (results_df["Risk Flag"] == "Low Credits").sum()
            at_risk_count = (results_df["Risk Flag"] == "At Risk").sum()
            good_count = (results_df["Risk Flag"] == "").sum()
            
            risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
            with risk_col1:
                st.metric("Non-viable Wells", non_viable_count, help="Breakeven > 100%")
            with risk_col2:
                st.metric("Low Credit Wells", low_credits_count, help="Leak rate < 5 LPM")
            with risk_col3:
                st.metric("At Risk Wells", at_risk_count, help="Breakeven between 80-100%")
            with risk_col4:
                st.metric("Good Wells", good_count, help="No risk factors identified")
            
            # Display KPIs
            st.subheader("Key Performance Indicators")
            
            total_credits = results_df["Credits"].sum()
            total_gross = results_df["Gross $"].sum()
            total_profit = results_df["Profit $"].sum()
            total_cost = results_df["Total cost $"].sum()
            path_fee_total = results_df["Path fee $"].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Carbon Credits (tCO₂e)", format_number(total_credits))
            with col2:
                st.metric("Gross Revenue ($)", format_currency(total_gross))
            with col3:
                st.metric("Net Profit ($)", format_currency(total_profit))
            
            # Charts in sub-tabs
            chart_tabs = st.tabs(["Credits", "Financials", "Cash Flow", "Timeline", "Sensitivity"])
            
            with chart_tabs[0]:  # Credits tab
                # Credits per well bar chart
                fig1 = px.bar(
                    results_df, 
                    x="Well Name/API", 
                    y="Credits", 
                    title="Carbon Credits per Well",
                    labels={"Credits": "Carbon Credits (tCO₂e)", "Well Name/API": "Well"},
                    color="Risk Flag",
                    color_discrete_map={
                        "Non-viable": "#ff6666",
                        "Low Credits": "#ffcc66",
                        "At Risk": "#ffaa44",
                        "": "#66aa66"
                    }
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with chart_tabs[1]:  # Financials tab
                # Financial breakdown
                fig2 = px.bar(
                    results_df,
                    x="Well Name/API",
                    y=["Profit $", "Path fee $", "Total cost $"],
                    title="Financial Breakdown per Well",
                    labels={"value": "Amount ($)", "Well Name/API": "Well", "variable": "Category"}
                )
                
                # Breakeven analysis
                breakeven_df = results_df[["Well Name/API", "Breakeven %"]].copy()
                breakeven_df["Breakeven %"] = breakeven_df["Breakeven %"] * 100
                breakeven_df["Is Profitable"] = breakeven_df["Breakeven %"] < 100
                
                fig3 = px.bar(
                    breakeven_df,
                    x="Well Name/API",
                    y="Breakeven %",
                    color="Is Profitable",
                    title="Breakeven Analysis - % Revenue Required to Cover Costs",
                    labels={"Breakeven %": "Breakeven Share (%)", "Well Name/API": "Well"},
                    color_discrete_map={True: "green", False: "red"}
                )
                fig3.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Breakeven Line")
                
                col1, col2 = st.columns(2)
                col1.plotly_chart(fig2, use_container_width=True)
                col2.plotly_chart(fig3, use_container_width=True)
            
            with chart_tabs[2]:  # Cash Flow tab
                # Cash flow analysis
                st.subheader("Cash Flow Analysis")
                
                discount_rate = st.slider("Discount Rate (%)", min_value=0.0, max_value=20.0, value=8.0, step=0.5) / 100
                
                # Simple cash flow timeline
                cash_flows = create_cash_flow(total_cost, path_fee_total, total_gross - path_fee_total)
                npv = calculate_npv(cash_flows, discount_rate)
                
                st.metric("Net Present Value (NPV)", format_currency(npv, 2))
                
                # Cash flow chart
                months = ["Month " + str(i) for i in range(len(cash_flows))]
                cash_flow_df = pd.DataFrame({
                    "Month": months,
                    "Cash Flow": cash_flows
                })
                
                fig4 = px.bar(
                    cash_flow_df,
                    x="Month",
                    y="Cash Flow",
                    title=f"Project Cash Flow (NPV: {format_currency(npv, 2)})",
                    labels={"Cash Flow": "Cash Flow ($)", "Month": "Timeline"},
                    color="Cash Flow",
                    color_continuous_scale=["red", "gray", "green"],
                )
                st.plotly_chart(fig4, use_container_width=True)
                
                st.write("""
                **Cash Flow Explanation:**
                - **Month 0**: Initial capital outlay (P&A, reclamation, sensor costs)
                - **Month 1**: CarbonPath fee at token mint
                - **Month 2**: Revenue from token sales
                """)
            
            with chart_tabs[3]:  # Timeline tab
                # Project timeline (Gantt chart)
                timeline_df["Task_Well"] = timeline_df["Task"] + " (" + timeline_df["Well"] + ")"
                
                fig5 = px.timeline(
                    timeline_df, 
                    x_start="Start", 
                    x_end="End", 
                    y="Task_Well",
                    color="Task",
                    title="Project Timeline",
                    hover_data=["Description"]
                )
                fig5.update_yaxes(autorange="reversed")
                st.plotly_chart(fig5, use_container_width=True)
            
            with chart_tabs[4]:  # Sensitivity tab
                # Token price sensitivity analysis
                st.subheader("Sensitivity Analysis")
                
                # Create token price x path fee heatmap
                token_prices = np.linspace(1, 30, 10)
                fee_percents = np.linspace(1, 3, 5) / 100
                
                # Calculate profits for each combination
                heatmap_data = []
                for tp in token_prices:
                    for fee in fee_percents:
                        temp_results = economics(df, tp, fee)
                        profit = temp_results["Profit $"].sum()
                        heatmap_data.append({
                            "Token Price": tp,
                            "CarbonPath Fee (%)": fee * 100,
                            "Total Profit": profit,
                            "Profitable": profit > 0
                        })
                
                heatmap_df = pd.DataFrame(heatmap_data)
                
                fig6 = px.density_heatmap(
                    heatmap_df,
                    x="Token Price",
                    y="CarbonPath Fee (%)",
                    z="Total Profit",
                    title="Profit Sensitivity: Token Price vs CarbonPath Fee",
                    labels={
                        "Token Price": "Token Price ($/tCO₂e)",
                        "CarbonPath Fee (%)": "CarbonPath Fee (%)",
                        "Total Profit": "Total Profit ($)"
                    }
                )
                
                # Add current values marker
                fig6.add_scatter(
                    x=[token_price],
                    y=[path_fee * 100],
                    mode="markers",
                    marker=dict(size=10, color="white", symbol="star"),
                    name="Current Values"
                )
                
                st.plotly_chart(fig6, use_container_width=True)
                
                # Simple token price sensitivity line chart
                fig7 = px.line(
                    heatmap_df.groupby("Token Price")["Total Profit"].mean().reset_index(),
                    x="Token Price",
                    y="Total Profit",
                    title="Profit Sensitivity to Token Price",
                    labels={"Total Profit": "Total Profit ($)", "Token Price": "Token Price ($/tCO₂e)"}
                )
                
                breakeven_price = np.interp(0, 
                                          heatmap_df.groupby("Token Price")["Total Profit"].mean().values, 
                                          heatmap_df.groupby("Token Price")["Total Profit"].mean().index.values)
                
                fig7.add_vline(x=breakeven_price, line_dash="dash", line_color="red", 
                              annotation_text=f"Breakeven: {format_currency(breakeven_price, 2)}")
                
                st.plotly_chart(fig7, use_container_width=True)
            
            # Download options
            st.subheader("Download Results")
            
            # CSV download
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"carbon_credit_results_scenario_{st.session_state.active_scenario}.csv",
                mime="text/csv",
                type="primary"
            )
            
            # PDF report generation
            def create_pdf_report():
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                width, height = letter
                
                # Use built-in fonts instead of DejaVu
                # pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
                
                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(30, height - 50, "Well Plugging Carbon Credits Report")
                c.setFont("Helvetica", 10)
                c.drawString(30, height - 70, f"Scenario {st.session_state.active_scenario} - Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                # Summary KPIs
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, height - 100, "Key Performance Indicators:")
                c.setFont("Helvetica", 10)
                c.drawString(30, height - 120, f"Total Carbon Credits: {format_number(total_credits)} tCO₂e")
                c.drawString(30, height - 140, f"Gross Revenue: {format_currency(total_gross)}")
                c.drawString(30, height - 160, f"Net Profit: {format_currency(total_profit)}")
                
                # Parameters
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, height - 190, "Parameters:")
                c.setFont("Helvetica", 10)
                c.drawString(30, height - 210, f"Token Price: {format_currency(token_price)} / tCO₂e")
                c.drawString(30, height - 230, f"CarbonPath Fee: {format_percentage(path_fee)}")
                
                # Risk summary
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, height - 260, "Risk Summary:")
                c.setFont("Helvetica", 10)
                c.drawString(30, height - 280, f"Non-viable Wells: {non_viable_count}")
                c.drawString(30, height - 300, f"Low Credit Wells: {low_credits_count}")
                c.drawString(30, height - 320, f"At Risk Wells: {at_risk_count}")
                c.drawString(30, height - 340, f"Good Wells: {good_count}")
                
                # Summary table
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, height - 370, "Well Summary:")
                
                # Table header
                c.setFont("Helvetica-Bold", 8)
                col_width = 75
                c.drawString(30, height - 390, "Well Name/API")
                c.drawString(30 + col_width, height - 390, "Leak LPM")
                c.drawString(30 + 2*col_width, height - 390, "Credits (tCO₂e)")
                c.drawString(30 + 3*col_width, height - 390, "Profit ($)")
                c.drawString(30 + 4*col_width, height - 390, "Breakeven (%)")
                c.drawString(30 + 5*col_width, height - 390, "Risk Flag")
                
                c.line(30, height - 392, 30 + 6*col_width, height - 392)
                
                # Table rows
                c.setFont("Helvetica", 8)
                for i, (_, row) in enumerate(results_df.iterrows()):
                    y_pos = height - 410 - i*20
                    
                    if y_pos < 50:  # Start a new page if we're running out of space
                        c.showPage()
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(30, height - 50, "Well Summary (continued):")
                        c.line(30, height - 60, 30 + 6*col_width, height - 60)
                        c.setFont("Helvetica", 8)
                        y_pos = height - 80
                    
                    c.drawString(30, y_pos, str(row["Well Name/API"]))
                    c.drawString(30 + col_width, y_pos, f"{row['Leak LPM']:.1f}")
                    c.drawString(30 + 2*col_width, y_pos, f"{row['Credits']}")
                    c.drawString(30 + 3*col_width, y_pos, f"{row['Profit $']}")
                    c.drawString(30 + 4*col_width, y_pos, f"{row['Breakeven %']}")
                    c.drawString(30 + 5*col_width, y_pos, str(row["Risk Flag"]))
                
                # Notes
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(30, 30, "Note: This report is generated based on CarbonPath v1.3, Solution 1 (Direct Measurement) methodology.")
                
                c.save()
                buffer.seek(0)
                return buffer
            
            pdf_report = create_pdf_report()
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_report,
                file_name=f"carbon_credit_report_scenario_{st.session_state.active_scenario}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.warning("Please add valid well data in the Inputs tab before viewing results.")
    else:
        st.warning("Please add valid well data in the Inputs tab and click 'Calculate Results'.")

# Comparison tab
with main_tabs[2]:  # Comparison tab
    if st.session_state.compare_mode and st.session_state.show_results:
        st.header("Scenario Comparison: A vs B")
        
        # Get data for both scenarios
        scenario_a = st.session_state.scenarios["A"]
        scenario_b = st.session_state.scenarios["B"]
        
        # Validate both scenarios have data
        if (len(scenario_a["wells"]) > 0 and validate_wells(scenario_a["wells"]) and 
            len(scenario_b["wells"]) > 0 and validate_wells(scenario_b["wells"])):
            
            # Run calculations for both scenarios
            df_a = pd.DataFrame(scenario_a["wells"])
            token_price_a = scenario_a["token_price"]
            path_fee_a = scenario_a["path_fee"]
            results_a = economics(df_a, token_price_a, path_fee_a)
            
            df_b = pd.DataFrame(scenario_b["wells"])
            token_price_b = scenario_b["token_price"]
            path_fee_b = scenario_b["path_fee"]
            results_b = economics(df_b, token_price_b, path_fee_b)
            
            # Display global parameter differences
            st.subheader("Global Parameters")
            
            param_col1, param_col2, param_col3 = st.columns(3)
            with param_col1:
                st.metric("Token Price A", format_currency(token_price_a))
                st.metric("CarbonPath Fee A", format_percentage(path_fee_a))
            with param_col2:
                st.metric("Token Price B", format_currency(token_price_b))
                st.metric("CarbonPath Fee B", format_percentage(path_fee_b))
            with param_col3:
                token_diff = token_price_b - token_price_a
                fee_diff = (path_fee_b - path_fee_a) * 100
                st.metric("Token Price Diff", format_currency(token_diff), delta=format_currency(token_diff))
                st.metric("Fee Diff", format_percentage(fee_diff), delta=format_percentage(fee_diff))
            
            # Summary comparison
            st.subheader("KPI Comparison")
            
            # Calculate totals
            total_credits_a = results_a["Credits"].sum()
            total_profit_a = results_a["Profit $"].sum()
            total_cost_a = results_a["Total cost $"].sum()
            
            total_credits_b = results_b["Credits"].sum()
            total_profit_b = results_b["Profit $"].sum()
            total_cost_b = results_b["Total cost $"].sum()
            
            # Calculate differences
            credit_diff = total_credits_b - total_credits_a
            profit_diff = total_profit_b - total_profit_a
            cost_diff = total_cost_b - total_cost_a
            
            # Display metrics with deltas
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.metric("Carbon Credits A", format_number(total_credits_a))
                st.metric("Carbon Credits B", format_number(total_credits_b))
                st.metric("Credit Difference", format_number(credit_diff), delta=format_number(credit_diff))
            
            with kpi_col2:
                st.metric("Profit A", format_currency(total_profit_a))
                st.metric("Profit B", format_currency(total_profit_b))
                st.metric("Profit Difference", format_currency(profit_diff), delta=format_currency(profit_diff))
            
            with kpi_col3:
                st.metric("Total Cost A", format_currency(total_cost_a))
                st.metric("Total Cost B", format_currency(total_cost_b))
                st.metric("Cost Difference", format_currency(cost_diff), delta=format_currency(cost_diff))
            
            # Side-by-side comparison chart
            st.subheader("Profit Comparison")
            
            # Create a dataframe for comparison
            comparison_data = []
            
            # Get common wells first
            common_wells = set(results_a["Well Name/API"]).intersection(set(results_b["Well Name/API"]))
            
            for well in common_wells:
                well_a = results_a[results_a["Well Name/API"] == well].iloc[0]
                well_b = results_b[results_b["Well Name/API"] == well].iloc[0]
                
                comparison_data.append({
                    "Well": well,
                    "Scenario": "A",
                    "Profit": well_a["Profit $"],
                    "Credits": well_a["Credits"],
                    "Breakeven %": well_a["Breakeven %"] * 100,
                    "Risk Flag": well_a["Risk Flag"]
                })
                
                comparison_data.append({
                    "Well": well,
                    "Scenario": "B",
                    "Profit": well_b["Profit $"],
                    "Credits": well_b["Credits"],
                    "Breakeven %": well_b["Breakeven %"] * 100,
                    "Risk Flag": well_b["Risk Flag"]
                })
            
            # Add wells unique to each scenario
            for well in set(results_a["Well Name/API"]) - common_wells:
                well_a = results_a[results_a["Well Name/API"] == well].iloc[0]
                comparison_data.append({
                    "Well": well + " (A only)",
                    "Scenario": "A",
                    "Profit": well_a["Profit $"],
                    "Credits": well_a["Credits"],
                    "Breakeven %": well_a["Breakeven %"] * 100,
                    "Risk Flag": well_a["Risk Flag"]
                })
            
            for well in set(results_b["Well Name/API"]) - common_wells:
                well_b = results_b[results_b["Well Name/API"] == well].iloc[0]
                comparison_data.append({
                    "Well": well + " (B only)",
                    "Scenario": "B",
                    "Profit": well_b["Profit $"],
                    "Credits": well_b["Credits"],
                    "Breakeven %": well_b["Breakeven %"] * 100,
                    "Risk Flag": well_b["Risk Flag"]
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Profit comparison chart
            fig8 = px.bar(
                comparison_df,
                x="Well",
                y="Profit",
                color="Scenario",
                barmode="group",
                title="Well Profit Comparison by Scenario",
                labels={"Profit": "Profit ($)", "Well": "Well Name/API"},
                color_discrete_map={"A": "#5555ff", "B": "#ff5555"}
            )
            st.plotly_chart(fig8, use_container_width=True)
            
            # Credit comparison chart
            fig9 = px.bar(
                comparison_df,
                x="Well",
                y="Credits",
                color="Scenario",
                barmode="group",
                title="Well Credits Comparison by Scenario",
                labels={"Credits": "Carbon Credits (tCO₂e)", "Well": "Well Name/API"},
                color_discrete_map={"A": "#5555ff", "B": "#ff5555"}
            )
            st.plotly_chart(fig9, use_container_width=True)
            
            # Breakeven comparison chart
            fig10 = px.bar(
                comparison_df,
                x="Well",
                y="Breakeven %",
                color="Scenario",
                barmode="group",
                title="Breakeven % Comparison by Scenario",
                labels={"Breakeven %": "Breakeven %", "Well": "Well Name/API"},
                color_discrete_map={"A": "#5555ff", "B": "#ff5555"}
            )
            fig10.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Breakeven Line")
            st.plotly_chart(fig10, use_container_width=True)
            
            # Risk comparison
            st.subheader("Risk Comparison")
            
            risk_counts_a = results_a["Risk Flag"].value_counts().to_dict()
            risk_counts_b = results_b["Risk Flag"].value_counts().to_dict()
            
            risk_types = ["Non-viable", "Low Credits", "At Risk", ""]
            risk_labels = ["Non-viable", "Low Credits", "At Risk", "Good"]
            
            risk_data = []
            for i, risk in enumerate(risk_types):
                risk_data.append({
                    "Risk Category": risk_labels[i],
                    "Scenario": "A",
                    "Count": risk_counts_a.get(risk, 0)
                })
                risk_data.append({
                    "Risk Category": risk_labels[i],
                    "Scenario": "B",
                    "Count": risk_counts_b.get(risk, 0)
                })
            
            risk_df = pd.DataFrame(risk_data)
            
            fig11 = px.bar(
                risk_df,
                x="Risk Category",
                y="Count",
                color="Scenario",
                barmode="group",
                title="Risk Category Comparison",
                labels={"Count": "Number of Wells", "Risk Category": "Risk Category"},
                color_discrete_map={"A": "#5555ff", "B": "#ff5555"}
            )
            st.plotly_chart(fig11, use_container_width=True)
            
            # Download comparison report
            st.subheader("Download Comparison")
            
            # Create comparison table for download
            download_comparison = comparison_df.pivot_table(
                index="Well",
                columns="Scenario",
                values=["Profit", "Credits", "Breakeven %", "Risk Flag"],
                aggfunc="first"
            ).reset_index()
            
            # Flatten the MultiIndex columns
            download_comparison.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in download_comparison.columns]
            
            # Calculate differences
            download_comparison["Profit_Diff"] = download_comparison["Profit_B"] - download_comparison["Profit_A"]
            download_comparison["Profit_Diff_%"] = (download_comparison["Profit_Diff"] / download_comparison["Profit_A"] * 100).round(1)
            download_comparison["Credits_Diff"] = download_comparison["Credits_B"] - download_comparison["Credits_A"]
            download_comparison["Breakeven_%_Diff"] = download_comparison["Breakeven %_B"] - download_comparison["Breakeven %_A"]
            
            # CSV download
            csv = download_comparison.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Comparison as CSV",
                data=csv,
                file_name=f"carbon_credit_comparison_A_vs_B.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.warning("Please ensure both scenarios have valid well data.")
    else:
        st.info("Enable comparison mode in the Inputs tab to compare scenarios A and B.")

# Footer
st.markdown("---")
st.caption("Carbon Credits Calculator for Well Plugging Projects v2.0") 