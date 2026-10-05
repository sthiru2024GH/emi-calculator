# utils/emi.py

CURRENCIES = {
    'INR': {'symbol': '₹', 'locale': 'en-IN'},
    'USD': {'symbol': '$', 'locale': 'en-US'},
    'EUR': {'symbol': '€', 'locale': 'de-DE'},
    'GBP': {'symbol': '£', 'locale': 'en-GB'},
    'AED': {'symbol': 'د.إ', 'locale': 'ar-AE'}
}

def calculate_base_emi(principal, annual_rate, tenure_months):
    """Calculates standard monthly EMI."""
    if annual_rate == 0:
        return principal / tenure_months
    monthly_rate = (annual_rate / 12) / 100
    emi = (principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)

def generate_amortization_schedule(principal, annual_rate, tenure_months, scenario_config=None):
    """
    Generates amortization schedule and calculates overall gain/loss.
    
    scenario_config keys:
      - scenario_type: 'one_time_lump_sum' | 'increased_emi' | 'annual_extra'
      - prepayment_mode: 'reduce_tenure' | 'reduce_emi'
      - lump_sum_amount, lump_sum_month
      - new_emi_amount, increased_emi_start_month
      - annual_extra_amount
    """
    monthly_rate = (annual_rate / 12) / 100 if annual_rate > 0 else 0
    base_emi = calculate_base_emi(principal, annual_rate, tenure_months)
    
    # 1. Base Schedule (No Prepayments)
    base_balance = principal
    base_total_interest = 0
    for m in range(1, tenure_months + 1):
        interest = base_balance * monthly_rate
        principal_paid = min(base_emi - interest, base_balance)
        base_total_interest += interest
        base_balance -= principal_paid
        if base_balance <= 0:
            break
            
    # 2. Scenario Schedule Simulation
    scenario_schedule = []
    current_balance = principal
    current_emi = base_emi
    scenario_total_interest = 0
    scenario_type = scenario_config.get('scenario_type') if scenario_config else 'none'
    prepayment_mode = scenario_config.get('prepayment_mode', 'reduce_tenure') if scenario_config else 'reduce_tenure'

    month = 1
    max_months = tenure_months * 2  # Safety guard
    
    while current_balance > 0.01 and month <= max_months:
        beginning_balance = current_balance  # <--- Capture starting balance
        interest = current_balance * monthly_rate
        extra_payment = 0

        # Apply Increased Regular EMI if applicable
        if scenario_type == 'increased_emi':
            start_m = int(scenario_config.get('increased_emi_start_month', 1))
            if month >= start_m:
                new_emi = float(scenario_config.get('new_emi_amount', base_emi))
                current_emi = max(new_emi, base_emi)

        # Apply One-time Lump Sum
        if scenario_type == 'one_time_lump_sum':
            lump_m = int(scenario_config.get('lump_sum_month', 1))
            if month == lump_m:
                extra_payment += float(scenario_config.get('lump_sum_amount', 0))

        # Apply Annual Extra Payment
        if scenario_type == 'annual_extra':
            if month % 12 == 0:
                extra_payment += float(scenario_config.get('annual_extra_amount', 0))

        # Calculate principal paid this month
        principal_paid = min((current_emi - interest) + extra_payment, current_balance)
        if principal_paid < 0:
            principal_paid = 0

        current_balance -= principal_paid
        scenario_total_interest += interest

        scenario_schedule.append({
            'month': month,
            'emi': round(current_emi, 2),
            'beginning_balance': round(beginning_balance, 2),  # <--- Add this key
            'interest_paid': round(interest, 2),
            'extra_payment': round(extra_payment, 2),
            'principal_paid': round(principal_paid, 2),
            'ending_balance': round(max(current_balance, 0), 2) # <--- Rename to ending_balance
            
        })

        # Recalculate EMI if user chooses 'Reduce EMI' mode after a lump sum payment
        if current_balance > 0 and extra_payment > 0 and prepayment_mode == 'reduce_emi':
            remaining_months = tenure_months - month
            if remaining_months > 0:
                current_emi = calculate_base_emi(current_balance, annual_rate, remaining_months)

        month += 1

    actual_tenure = len(scenario_schedule)
    interest_saved = base_total_interest - scenario_total_interest
    tenure_reduced_months = tenure_months - actual_tenure

    return {
        'base_summary': {
            'base_emi': round(base_emi, 2),
            'total_interest': round(base_total_interest, 2),
            'total_payment': round(principal + base_total_interest, 2),
            'tenure_months': tenure_months
        },
        'scenario_summary': {
            'total_interest': round(scenario_total_interest, 2),
            'total_payment': round(principal + scenario_total_interest, 2),
            'actual_tenure_months': actual_tenure,
            'interest_saved': round(interest_saved, 2),
            'tenure_reduced_months': max(tenure_reduced_months, 0)
        },
        'schedule': scenario_schedule
    }