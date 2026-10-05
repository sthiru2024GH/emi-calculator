// Toggle input visibility based on scenario choice
document.getElementById('scenario_type').addEventListener('change', (e) => {
    const val = e.target.value;
    document.getElementById('lump_sum_fields').style.display = val === 'one_time_lump_sum' ? 'block' : 'none';
    document.getElementById('increased_emi_fields').style.display = val === 'increased_emi' ? 'block' : 'none';
    document.getElementById('annual_extra_fields').style.display = val === 'annual_extra' ? 'block' : 'none';
    document.getElementById('prepayment_mode_field').style.display = val === 'one_time_lump_sum' ? 'block' : 'none';
});

// Calculate and render gain/loss summary
async function calculateEMI() {
    const formData = new FormData(document.getElementById('emiForm'));
    const payload = Object.fromEntries(formData.entries());

    const response = await fetch('/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    const symbol = data.currency.symbol;

    // Display Gains Summary
    const saved = data.scenario_summary.interest_saved;
    document.getElementById('gainLossCard').innerHTML = `
        <h3>Scenario Results</h3>
        <p><strong>Total Interest Saved:</strong> ${symbol}${saved.toLocaleString()}</p>
        <p><strong>Tenure Reduced By:</strong> ${data.scenario_summary.tenure_reduced_months} Months</p>
        <p><strong>New Loan Duration:</strong> ${data.scenario_summary.actual_tenure_months} Months</p>
    `;
}
function generateRepaymentSchedule(loanAmount, annualRate, tenureMonths) {
  const monthlyRate = annualRate / 12 / 100;
  const emi = (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, tenureMonths)) / 
              (Math.pow(1 + monthlyRate, tenureMonths) - 1);

  let balance = loanAmount;
  const tbody = document.getElementById('scheduleTableBody');
  tbody.innerHTML = ''; // Clear previous results

  for (let month = 1; month <= tenureMonths; month++) {
    const interest = balance * monthlyRate;
    const principal = emi - interest;
    const endingBalance = Math.max(0, balance - principal);

    const row = `
      <tr>
        <td>${month}</td>
        <td>${balance.toFixed(2)}</td>
        <td>${emi.toFixed(2)}</td>
        <td>${principal.toFixed(2)}</td>
        <td>${interest.toFixed(2)}</td>
        <td>${endingBalance.toFixed(2)}</td>
      </tr>
    `;

    tbody.innerHTML += row;
    balance = endingBalance;
  }
  return render_template(
        "index.html",
        result=result

}