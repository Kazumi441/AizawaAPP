def calculate_amortized_payment(principal, interest_rate, loan_term):
    """
    Calculate the monthly payment for an amortizing loan (principal and interest).
    Args:
        principal (float): Loan amount (元金)
        interest_rate (float): Annual interest rate (金利, e.g., 0.6 for 0.6%)
        loan_term (int): Loan term in years (融資期間)
    Returns:
        float: Monthly payment
    """
    monthly_interest_rate = interest_rate / 100 / 12
    num_payments = loan_term * 12
    monthly_payment = (principal * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -num_payments)
    return monthly_payment