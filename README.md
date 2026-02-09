# Personal Loan Amortization Tool

A simple, Python tool for calculating loan amortization schedules, comparing multiple loan scenarios, and exporting results to CSV files.

## Features

- Calculate fixed monthly payments for personal loans
- Generate detailed amortization schedules showing:
  - Payment number
  - Monthly payment amount
  - Interest portion
  - Principal portion
  - Remaining balance
- Support for extra monthly payments
- Compare multiple loan scenarios side-by-side
- Export amortization schedules to CSV files
- Clean, readable Python code with comprehensive docstrings

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Usage

### Running the Application

Simply run the Python script from your terminal:

```bash
python loan_amortization.py
```

### Interactive Prompts

The tool will guide you through entering loan details:

1. **Scenario name**: A descriptive name for this loan (e.g., "5-Year Loan", "With Extra Payments")
2. **Loan principal**: The amount you're borrowing (e.g., 25000)
3. **Annual interest rate**: The yearly interest rate as a percentage (e.g., 5.5)
4. **Loan term**: The duration in years (e.g., 5)
5. **Extra monthly payment**: Optional additional payment each month (press Enter for 0)

### Example Session

```
PERSONAL LOAN AMORTIZATION TOOL
======================================================================

Welcome! This tool helps you:
  - Calculate loan payments and amortization schedules
  - Compare multiple loan scenarios
  - Export detailed schedules to CSV files

----------------------------------------------------------------------
Enter Loan Details:
----------------------------------------------------------------------
Scenario name: Standard 5-Year Loan
Loan principal ($): 25000
Annual interest rate (%): 5.5
Loan term (years): 5
Extra monthly payment ($ or press Enter for 0):

======================================================================
LOAN SUMMARY: Standard 5-Year Loan
======================================================================
Principal:           $25,000.00
Interest Rate:       5.5% annually
Loan Term:           5 years
Monthly Payment:     $477.42

Total Amount Paid:   $28,645.00
Total Interest:      $3,645.00
Actual Payoff Time:  60 months (5.0 years)
======================================================================

Export this schedule to CSV? (y/n): y
✓ Schedule exported to: Standard_5-Year_Loan_amortization.csv

Add another loan scenario? (y/n): y
```

### Comparing Multiple Scenarios

If you create multiple loan scenarios in one session, the tool will automatically show a comparison summary at the end, highlighting:

- The scenario with the lowest total cost
- The scenario with the fastest payoff time

## Input Validation

The tool validates all inputs:

- Principal must be positive
- Interest rate must be greater than zero
- Loan term must be greater than zero
- Extra payment cannot be negative
- Invalid numbers are rejected with clear error messages

## CSV Export Format

Exported CSV files contain these columns:

- `payment_number`: The month number (1, 2, 3, ...)
- `payment_amount`: Total amount paid that month
- `interest_paid`: Portion going to interest
- `principal_paid`: Portion reducing the principal
- `remaining_balance`: Balance after the payment

Files are named based on the scenario name (e.g., `Standard_5-Year_Loan_amortization.csv`).

## Example Scenarios to Try

### Scenario 1: Basic 5-Year Loan
- Principal: $25,000
- Rate: 5.5%
- Term: 5 years
- Extra payment: $0

### Scenario 2: With Extra Payments
- Principal: $25,000
- Rate: 5.5%
- Term: 5 years
- Extra payment: $100

Compare these to see how extra payments reduce total interest and payoff time!

## Technical Notes

### Monthly Payment Formula

The tool uses the standard amortization formula:

```
M = P * [r(1+r)^n] / [(1+r)^n - 1]

Where:
  M = Monthly payment
  P = Principal
  r = Monthly interest rate (annual rate / 12 / 100)
  n = Total number of months
```

### Extra Payments

Extra payments are applied entirely to the principal after interest is calculated each month. This accelerates payoff and reduces total interest.

### Early Payoff

The schedule automatically stops when the loan is paid off, which may be earlier than the original term if extra payments are made.


## Test Cases

To run the test suite, simply run `python test_loan.py` from the project root directory.
