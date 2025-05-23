def compute_credits(leak_lpm, gwp=28, period_yr=50):
    """
    Calculate carbon credits from methane leak rate
    
    Args:
        leak_lpm: Leak rate in liters per minute
        gwp: Global Warming Potential (default: 28)
        period_yr: Crediting period in years (default: 50)
        
    Returns:
        Dictionary with calculation steps and final credit amount
    """
    # 1. kg/min
    kg_per_min = leak_lpm * 0.000714
    # 2. t/yr
    t_per_yr = kg_per_min * 525_600 / 1_000
    # 3. t over period
    t_total = t_per_yr * period_yr
    # 4. t CO2e
    credits = t_total * gwp
    return {
        "kg_per_min": kg_per_min,
        "t_per_yr": t_per_yr,
        "t_total": t_total,
        "credits": credits
    } 