from loan_amortization import Loan, export_to_csv, compare_scenarios


def test_basic_loan():
    """Test basic loan creation and calculations."""
    print("Test 1: Basic Loan Creation and Calculation")
    print("-" * 60)

    # Create a simple 5-year loan
    loan = Loan(
        principal=25000,
        annual_rate=5.5,
        term_years=5,
        extra_payment=0,
        scenario_name="Test Basic Loan"
    )

    print(f"Principal: ${loan.principal:,.2f}")
    print(f"Annual Rate: {loan.annual_rate}%")
    print(f"Term: {loan.term_years} years")
    print(f"Monthly Payment: ${loan.monthly_payment:,.2f}")

    # Get summary
    summary = loan.get_summary()
    print(f"\nTotal Paid: ${summary['total_paid']:,.2f}")
    print(f"Total Interest: ${summary['total_interest']:,.2f}")
    print(f"Payoff Time: {summary['actual_months']} months")

    # Verify payment count matches term
    schedule = loan.generate_amortization_schedule()
    print(f"Schedule Entries: {len(schedule)}")

    # Check last payment brings balance to zero
    last_payment = schedule[-1]
    print(f"Final Balance: ${last_payment['remaining_balance']:,.2f}")

    assert last_payment['remaining_balance'] == 0, "Final balance should be zero"
    print("✓ Test 1 PASSED\n")


def test_loan_with_extra_payment():
    """Test loan with extra monthly payments."""
    print("Test 2: Loan with Extra Payments")
    print("-" * 60)

    # Create two loans: one with and one without extra payment
    loan_standard = Loan(
        principal=25000,
        annual_rate=5.5,
        term_years=5,
        extra_payment=0,
        scenario_name="Standard"
    )

    loan_extra = Loan(
        principal=25000,
        annual_rate=5.5,
        term_years=5,
        extra_payment=100,
        scenario_name="With $100 Extra"
    )

    summary_standard = loan_standard.get_summary()
    summary_extra = loan_extra.get_summary()

    print(f"Standard Loan:")
    print(f"  Total Paid: ${summary_standard['total_paid']:,.2f}")
    print(f"  Payoff: {summary_standard['actual_months']} months")

    print(f"\nWith $100 Extra Payment:")
    print(f"  Total Paid: ${summary_extra['total_paid']:,.2f}")
    print(f"  Payoff: {summary_extra['actual_months']} months")

    print(f"\nSavings: ${summary_standard['total_paid'] - summary_extra['total_paid']:,.2f}")
    print(f"Time Saved: {summary_standard['actual_months'] - summary_extra['actual_months']} months")

    # Extra payment should reduce both time and total cost
    assert summary_extra['total_paid'] < summary_standard['total_paid'], \
        "Extra payments should reduce total cost"
    assert summary_extra['actual_months'] < summary_standard['actual_months'], \
        "Extra payments should reduce payoff time"

    print("✓ Test 2 PASSED\n")


def test_validation():
    """Test input validation."""
    print("Test 3: Input Validation")
    print("-" * 60)

    test_cases = [
        (0, 5.5, 5, "Zero principal"),
        (-1000, 5.5, 5, "Negative principal"),
        (25000, 0, 5, "Zero interest rate"),
        (25000, -1, 5, "Negative interest rate"),
        (25000, 5.5, 0, "Zero term"),
        (25000, 5.5, -5, "Negative term"),
        (25000, 5.5, 5, "Negative extra payment", -100),
    ]

    for test in test_cases:
        principal, rate, term, description = test[:4]
        extra = test[4] if len(test) > 4 else 0

        try:
            loan = Loan(principal, rate, term, extra)
            print(f"✗ {description}: Should have raised ValueError")
            assert False, f"{description} should raise ValueError"
        except ValueError as e:
            print(f"✓ {description}: Correctly rejected ({str(e)})")

    print("✓ Test 3 PASSED\n")


def test_amortization_schedule():
    """Test amortization schedule generation."""
    print("Test 4: Amortization Schedule Details")
    print("-" * 60)

    loan = Loan(
        principal=10000,
        annual_rate=6.0,
        term_years=2,
        scenario_name="Short Term Test"
    )

    schedule = loan.generate_amortization_schedule()

    print(f"Generated {len(schedule)} payment entries")
    print("\nFirst 3 payments:")
    print(f"{'Month':<6} {'Payment':<12} {'Interest':<12} {'Principal':<12} {'Balance':<12}")
    print("-" * 60)

    for i in range(min(3, len(schedule))):
        entry = schedule[i]
        print(f"{entry['payment_number']:<6} "
              f"${entry['payment_amount']:>10,.2f}  "
              f"${entry['interest_paid']:>10,.2f}  "
              f"${entry['principal_paid']:>10,.2f}  "
              f"${entry['remaining_balance']:>10,.2f}")

    # Verify schedule integrity
    total_principal = sum(entry['principal_paid'] for entry in schedule)
    print(f"\nTotal Principal Paid: ${total_principal:,.2f}")
    print(f"Original Principal: ${loan.principal:,.2f}")
    print(f"Difference: ${abs(total_principal - loan.principal):,.2f}")

    # Principal paid should equal original principal (within rounding)
    assert abs(total_principal - loan.principal) < 1.0, \
        "Total principal paid should equal original principal"

    # Balance should decrease monotonically
    for i in range(len(schedule) - 1):
        assert schedule[i]['remaining_balance'] >= schedule[i + 1]['remaining_balance'], \
            "Balance should decrease each month"

    print("✓ Test 4 PASSED\n")


def test_csv_export():
    """Test CSV export functionality."""
    print("Test 5: CSV Export")
    print("-" * 60)

    loan = Loan(
        principal=15000,
        annual_rate=4.5,
        term_years=3,
        scenario_name="CSV Export Test"
    )

    try:
        filepath = export_to_csv(loan)
        print(f"✓ CSV exported to: {filepath}")

        # Verify file exists and has content
        with open(filepath, 'r') as f:
            lines = f.readlines()
            print(f"✓ File contains {len(lines)} lines (including header)")

            # Check header
            header = lines[0].strip()
            expected_cols = ['payment_number', 'payment_amount', 'interest_paid',
                           'principal_paid', 'remaining_balance']
            for col in expected_cols:
                assert col in header, f"Header should contain {col}"

            print("✓ CSV structure is valid")

        print("✓ Test 5 PASSED\n")

    except Exception as e:
        print(f"✗ Test 5 FAILED: {e}\n")
        raise


def test_scenario_comparison():
    """Test multiple scenario comparison."""
    print("Test 6: Scenario Comparison")
    print("-" * 60)

    loans = [
        Loan(25000, 5.5, 5, 0, "Scenario A: Standard"),
        Loan(25000, 5.5, 5, 50, "Scenario B: $50 Extra"),
        Loan(25000, 5.5, 5, 100, "Scenario C: $100 Extra"),
    ]

    # This will print the comparison
    compare_scenarios(loans)

    # Verify scenarios are ordered correctly by cost
    summaries = [loan.get_summary() for loan in loans]
    for i in range(len(summaries) - 1):
        assert summaries[i]['total_paid'] >= summaries[i + 1]['total_paid'], \
            "More extra payment should cost less total"

    print("✓ Test 6 PASSED\n")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "=" * 60)
    print("RUNNING LOAN AMORTIZATION TOOL TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_basic_loan,
        test_loan_with_extra_payment,
        test_validation,
        test_amortization_schedule,
        test_csv_export,
        test_scenario_comparison,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} FAILED: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
