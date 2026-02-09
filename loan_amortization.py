import csv
import os
from typing import List, Dict, Tuple


class Loan:
    """
    Represents a personal loan with amortization calculation capabilities.

    Attributes:
        principal: The initial loan amount (must be positive)
        annual_rate: Annual interest rate as a percentage (e.g., 5.5 for 5.5%)
        term_years: Loan term in years (must be positive)
        extra_payment: Optional extra monthly payment amount (default 0)
        scenario_name: A descriptive name for this loan scenario
    """

    def __init__(self, principal: float, annual_rate: float, term_years: int,
                 extra_payment: float = 0.0, scenario_name: str = "Default"):
        """
        Initialize a Loan object with validation.

        Parameters:
            principal: Loan amount in currency units (must be > 0)
            annual_rate: Annual interest rate as percentage (must be > 0)
            term_years: Loan duration in years (must be > 0)
            extra_payment: Additional monthly payment (must be >= 0)
            scenario_name: Name to identify this scenario

        Raises:
            ValueError: If any validation rules are violated
        """
        # Validate inputs
        if principal <= 0:
            raise ValueError("Principal must be a positive number")
        if annual_rate <= 0:
            raise ValueError("Interest rate must be greater than zero")
        if term_years <= 0:
            raise ValueError("Loan term must be greater than zero")
        if extra_payment < 0:
            raise ValueError("Extra payment cannot be negative")

        self.principal = round(principal, 2)
        self.annual_rate = annual_rate
        self.term_years = term_years
        self.extra_payment = round(extra_payment, 2)
        self.scenario_name = scenario_name

        # Calculate monthly rate and total months
        self.monthly_rate = annual_rate / 100 / 12
        self.total_months = term_years * 12

        # Calculate fixed monthly payment (without extra payment)
        self.monthly_payment = self._calculate_monthly_payment()

    def _calculate_monthly_payment(self) -> float:
        """
        Calculate the fixed monthly payment using the standard amortization formula.

        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
            M = Monthly payment
            P = Principal
            r = Monthly interest rate
            n = Total number of months

        Returns:
            The calculated monthly payment amount, rounded to 2 decimal places
        """
        if self.monthly_rate == 0:
            # If no interest, simply divide principal by months
            return round(self.principal / self.total_months, 2)

        # Standard loan payment formula
        numerator = self.monthly_rate * (1 + self.monthly_rate) ** self.total_months
        denominator = (1 + self.monthly_rate) ** self.total_months - 1
        monthly_payment = self.principal * (numerator / denominator)

        return round(monthly_payment, 2)

    def generate_amortization_schedule(self) -> List[Dict[str, float]]:
        """
        Generate a complete amortization schedule for the loan.

        Returns:
            A list of dictionaries, each representing one month's payment details:
            - payment_number: The payment number (1, 2, 3, ...)
            - payment_amount: Total amount paid this month
            - interest_paid: Portion going to interest
            - principal_paid: Portion going to principal
            - remaining_balance: Balance after this payment
        """
        schedule = []
        remaining_balance = self.principal
        payment_number = 0

        while remaining_balance > 0.01:  # Continue until balance is essentially zero
            payment_number += 1

            # Calculate interest for this month
            interest_paid = round(remaining_balance * self.monthly_rate, 2)

            # Calculate principal payment
            # Start with the regular monthly payment plus any extra payment
            total_payment = self.monthly_payment + self.extra_payment
            principal_paid = total_payment - interest_paid

            # Don't overpay - cap at remaining balance
            if principal_paid > remaining_balance:
                principal_paid = remaining_balance
                total_payment = interest_paid + principal_paid

            # Update remaining balance
            remaining_balance = round(remaining_balance - principal_paid, 2)

            # Ensure balance doesn't go negative
            if remaining_balance < 0:
                remaining_balance = 0

            # Add this month's entry to the schedule
            schedule.append({
                'payment_number': payment_number,
                'payment_amount': round(total_payment, 2),
                'interest_paid': interest_paid,
                'principal_paid': round(principal_paid, 2),
                'remaining_balance': remaining_balance
            })

            # Safety check: don't run forever
            if payment_number > self.total_months * 2:
                break

        return schedule

    def get_summary(self) -> Dict[str, any]:
        """
        Calculate summary statistics for this loan.

        Returns:
            A dictionary containing:
            - total_paid: Total amount paid over life of loan
            - total_interest: Total interest paid
            - actual_months: Actual number of months to pay off
            - actual_years: Actual years to pay off (rounded to 2 decimals)
        """
        schedule = self.generate_amortization_schedule()

        total_paid = sum(entry['payment_amount'] for entry in schedule)
        total_interest = sum(entry['interest_paid'] for entry in schedule)
        actual_months = len(schedule)
        actual_years = round(actual_months / 12, 2)

        return {
            'scenario_name': self.scenario_name,
            'total_paid': round(total_paid, 2),
            'total_interest': round(total_interest, 2),
            'actual_months': actual_months,
            'actual_years': actual_years
        }


def export_to_csv(loan: Loan, directory: str = ".") -> str:
    """
    Export a loan's amortization schedule to a CSV file.

    Parameters:
        loan: The Loan object to export
        directory: Directory to save the CSV file (default: current directory)

    Returns:
        The filepath of the created CSV file
    """
    # Create a safe filename from the scenario name
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_'
                       for c in loan.scenario_name)
    safe_name = safe_name.strip().replace(' ', '_')
    filename = f"{safe_name}_amortization.csv"
    filepath = os.path.join(directory, filename)

    # Generate the schedule
    schedule = loan.generate_amortization_schedule()

    # Write to CSV
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['payment_number', 'payment_amount', 'interest_paid',
                     'principal_paid', 'remaining_balance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(schedule)

    return filepath


def compare_scenarios(loans: List[Loan]) -> None:
    """
    Compare multiple loan scenarios and display a summary.

    Parameters:
        loans: A list of Loan objects to compare
    """
    if not loans:
        print("No scenarios to compare.")
        return

    print("\n" + "="*70)
    print("LOAN SCENARIO COMPARISON")
    print("="*70)

    summaries = [loan.get_summary() for loan in loans]

    # Display each scenario
    for i, summary in enumerate(summaries, 1):
        print(f"\nScenario {i}: {summary['scenario_name']}")
        print(f"  Total Amount Paid:  ${summary['total_paid']:,.2f}")
        print(f"  Total Interest:     ${summary['total_interest']:,.2f}")
        print(f"  Payoff Time:        {summary['actual_months']} months ({summary['actual_years']} years)")

    # Find best scenarios
    print("\n" + "-"*70)
    print("COMPARISON SUMMARY:")
    print("-"*70)

    min_cost = min(summaries, key=lambda x: x['total_paid'])
    min_time = min(summaries, key=lambda x: x['actual_months'])

    print(f"\nLowest Total Cost: {min_cost['scenario_name']}")
    print(f"  Total Paid: ${min_cost['total_paid']:,.2f}")

    print(f"\nFastest Payoff: {min_time['scenario_name']}")
    print(f"  Payoff Time: {min_time['actual_months']} months ({min_time['actual_years']} years)")

    print("="*70 + "\n")


def get_float_input(prompt: str, allow_zero: bool = False) -> float:
    """
    Get a valid float input from the user with error handling.

    Parameters:
        prompt: The prompt message to display
        allow_zero: Whether to allow zero as a valid input

    Returns:
        A valid float value
    """
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Error: Value cannot be negative. Please try again.")
                continue
            if not allow_zero and value == 0:
                print("Error: Value must be greater than zero. Please try again.")
                continue
            return value
        except ValueError:
            print("Error: Please enter a valid number.")


def get_int_input(prompt: str) -> int:
    """
    Get a valid integer input from the user with error handling.

    Parameters:
        prompt: The prompt message to display

    Returns:
        A valid positive integer
    """
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Error: Value must be greater than zero. Please try again.")
                continue
            return value
        except ValueError:
            print("Error: Please enter a valid whole number.")


def create_loan_interactive() -> Loan:
    """
    Interactively create a Loan object by prompting the user for input.

    Returns:
        A new Loan object with user-provided values
    """
    print("\n" + "-"*70)
    print("Enter Loan Details:")
    print("-"*70)

    scenario_name = input("Scenario name: ").strip()
    if not scenario_name:
        scenario_name = "Unnamed Scenario"

    principal = get_float_input("Loan principal ($): ")
    annual_rate = get_float_input("Annual interest rate (%): ")
    term_years = get_int_input("Loan term (years): ")

    extra_input = input("Extra monthly payment ($ or press Enter for 0): ").strip()
    extra_payment = float(extra_input) if extra_input else 0.0

    try:
        loan = Loan(principal, annual_rate, term_years, extra_payment, scenario_name)
        return loan
    except ValueError as e:
        print(f"\nError creating loan: {e}")
        print("Please try again.\n")
        return create_loan_interactive()


def display_loan_summary(loan: Loan) -> None:
    """
    Display a formatted summary of a loan's key details and calculations.

    Parameters:
        loan: The Loan object to display
    """
    summary = loan.get_summary()

    print("\n" + "="*70)
    print(f"LOAN SUMMARY: {loan.scenario_name}")
    print("="*70)
    print(f"Principal:           ${loan.principal:,.2f}")
    print(f"Interest Rate:       {loan.annual_rate}% annually")
    print(f"Loan Term:           {loan.term_years} years")
    print(f"Monthly Payment:     ${loan.monthly_payment:,.2f}")
    if loan.extra_payment > 0:
        print(f"Extra Payment:       ${loan.extra_payment:,.2f}")
        print(f"Total Monthly:       ${loan.monthly_payment + loan.extra_payment:,.2f}")
    print(f"\nTotal Amount Paid:   ${summary['total_paid']:,.2f}")
    print(f"Total Interest:      ${summary['total_interest']:,.2f}")
    print(f"Actual Payoff Time:  {summary['actual_months']} months ({summary['actual_years']} years)")
    print("="*70 + "\n")


def main():
    """
    Main application loop - handles user interaction and orchestrates the tool.
    """
    print("\n" + "="*70)
    print("PERSONAL LOAN AMORTIZATION TOOL")
    print("="*70)
    print("\nWelcome! This tool helps you:")
    print("  - Calculate loan payments and amortization schedules")
    print("  - Compare multiple loan scenarios")
    print("  - Export detailed schedules to CSV files")
    print()

    loans = []

    while True:
        # Create a loan scenario
        loan = create_loan_interactive()
        loans.append(loan)

        # Display summary
        display_loan_summary(loan)

        # Ask about CSV export
        export = input("Export this schedule to CSV? (y/n): ").strip().lower()
        if export == 'y':
            try:
                filepath = export_to_csv(loan)
                print(f"✓ Schedule exported to: {filepath}")
            except Exception as e:
                print(f"Error exporting to CSV: {e}")

        # Ask about adding another scenario
        another = input("\nAdd another loan scenario? (y/n): ").strip().lower()
        if another != 'y':
            break

    # If multiple scenarios, show comparison
    if len(loans) > 1:
        compare_scenarios(loans)

    print("Thank you for using the Loan Amortization Tool!")
    print()


if __name__ == "__main__":
    main()
