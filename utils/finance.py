import pandas as pd
import numpy as np
import numpy_financial as npf
import math
from datetime import datetime, timedelta

# Constants
GWP_CO2E = 28
DENSITY_KG_PER_L = 0.000714
MINUTES_PER_YEAR = 525_600
YEARS = 50

# Depth-based cost presets
DEPTH_COST_PRESETS = {
    2000: 30000,    # < 2,000 ft
    5000: 55000,    # 2,000 - 5,000 ft
    math.inf: 80000  # > 5,000 ft
}

def get_depth_bucket(depth):
    """
    Get the appropriate depth bucket for cost presets
    """
    for bucket in sorted(DEPTH_COST_PRESETS.keys()):
        if depth <= bucket:
            return bucket
    return max(DEPTH_COST_PRESETS.keys())

def get_pna_cost_from_depth(depth):
    """
    Get the P&A cost based on well depth
    """
    if depth is None or pd.isna(depth):
        return None
    bucket = get_depth_bucket(depth)
    return DEPTH_COST_PRESETS[bucket]

def calc_credits(lpm: float) -> float:
    """
    Calculate carbon credits from methane leak rate in L/min
    """
    if pd.isna(lpm) or lpm <= 0:
        return 0
    ch4_t_per_year = lpm * DENSITY_KG_PER_L * MINUTES_PER_YEAR / 1_000
    return ch4_t_per_year * YEARS * GWP_CO2E

def economics(df, token_price, path_fee):
    """
    Calculate economics of well plugging projects
    
    Args:
        df: DataFrame with well data
        token_price: Price of carbon credit token ($/tCO2e)
        path_fee: CarbonPath fee as decimal (e.g., 0.02 for 2%)
        
    Returns:
        DataFrame with economics calculations
    """
    df = df.copy()
    
    # Auto-fill P&A costs from depth if available and P&A is empty
    if "Depth (ft)" in df.columns:
        for idx, row in df.iterrows():
            if pd.isna(row["PnA $"]) or row["PnA $"] == 0:
                df.at[idx, "PnA $"] = get_pna_cost_from_depth(row["Depth (ft)"])
    
    df["Credits"] = df["Leak LPM"].apply(calc_credits)
    df["Gross $"] = df["Credits"] * token_price
    df["Path fee $"] = df["Gross $"] * path_fee
    df["Net $"] = df["Gross $"] - df["Path fee $"]
    df["Total cost $"] = df[["PnA $", "Reclam $", "Sensor $", "Other $"]].sum(axis=1)
    df["Profit $"] = df["Net $"] - df["Total cost $"]
    df["Breakeven %"] = df["Total cost $"] / df["Net $"]
    
    # Add risk flags
    conditions = [
        (df["Breakeven %"] > 1.0),
        (df["Leak LPM"] < 5.0),
        (df["Breakeven %"] > 0.8) & (df["Breakeven %"] <= 1.0)
    ]
    choices = ["Non-viable", "Low Credits", "At Risk"]
    df["Risk Flag"] = np.select(conditions, choices, default="")
    
    return df

def calculate_npv(cash_flows, discount_rate=0.08):
    """
    Calculate Net Present Value of cash flows
    
    Args:
        cash_flows: List of cash flows
        discount_rate: Discount rate (default 8%)
        
    Returns:
        NPV value
    """
    return npf.npv(discount_rate, cash_flows)

def create_cash_flow(total_cost, path_fee, net_revenue, timeline=None):
    """
    Create cash flow timeline for NPV calculation
    
    Args:
        total_cost: Total project costs
        path_fee: CarbonPath fee amount
        net_revenue: Net revenue after fees
        timeline: Optional custom timeline in months for each cash flow
        
    Returns:
        List of cash flows
    """
    if timeline is None:
        # Default timeline: costs at t0, registry fee at month 1, revenue at month 2
        timeline = [0, 1, 2]
    
    # Initialize cash flow array with zeros
    max_month = max(timeline)
    cash_flows = [0] * (max_month + 1)
    
    # Populate cash flows at specified months
    cash_flows[timeline[0]] = -total_cost
    cash_flows[timeline[1]] = -path_fee
    cash_flows[timeline[2]] = net_revenue
    
    return cash_flows

def create_timeline(df, reference_date=None):
    """
    Create timeline dataframes for Gantt chart
    
    Args:
        df: DataFrame with well data
        reference_date: Optional reference date (defaults to today)
        
    Returns:
        DataFrame formatted for Gantt chart
    """
    if reference_date is None:
        # Get baseline test date if available, otherwise use today
        if "Baseline Date" in df.columns and not df["Baseline Date"].isna().all():
            # Use the earliest baseline date as reference
            reference_date = df["Baseline Date"].min()
        else:
            reference_date = datetime.now().date()
    
    timeline_data = []
    
    for _, row in df.iterrows():
        well_name = row["Well Name/API"]
        
        # Baseline test (day 0)
        baseline_date = reference_date
        if "Baseline Date" in row and not pd.isna(row["Baseline Date"]):
            baseline_date = row["Baseline Date"]
        
        # P&A date (default +30 days)
        pna_date = baseline_date + timedelta(days=30)
        
        # Token mint (+31 days after P&A)
        mint_date = pna_date + timedelta(days=31)
        
        # Second test (+365 days after P&A)
        retest_date = pna_date + timedelta(days=365)
        
        timeline_data.extend([
            {
                "Well": well_name,
                "Task": "Baseline CH₄ Test",
                "Start": baseline_date,
                "End": baseline_date + timedelta(days=1),
                "Description": "Initial methane measurement"
            },
            {
                "Well": well_name,
                "Task": "Plug & Abandon",
                "Start": pna_date,
                "End": pna_date + timedelta(days=1),
                "Description": "Well plugging operation"
            },
            {
                "Well": well_name,
                "Task": "Token Mint",
                "Start": mint_date,
                "End": mint_date + timedelta(days=1),
                "Description": "100% provisional credits minted"
            },
            {
                "Well": well_name,
                "Task": "Second Test",
                "Start": retest_date,
                "End": retest_date + timedelta(days=1),
                "Description": "Verification measurement"
            }
        ])
    
    return pd.DataFrame(timeline_data) 