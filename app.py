from flask import Flask, render_template, request, jsonify
from utils.emi import generate_amortization_schedule, CURRENCIES

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Pass currencies to template so the dropdown loads initially
    return render_template('index.html', currencies=CURRENCIES)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json() or request.form
    
    principal = float(data.get('principal', 1000000))
    annual_rate = float(data.get('annual_rate', 8.5))
    tenure_months = int(data.get('tenure_months', 120))
    currency_code = data.get('currency', 'INR')

    scenario_config = {
        'scenario_type': data.get('scenario_type', 'none'),
        'prepayment_mode': data.get('prepayment_mode', 'reduce_tenure'),
        'lump_sum_amount': float(data.get('lump_sum_amount', 0)),
        'lump_sum_month': int(data.get('lump_sum_month', 12)),
        'new_emi_amount': float(data.get('new_emi_amount', 0)),
        'increased_emi_start_month': int(data.get('increased_emi_start_month', 1)),
        'annual_extra_amount': float(data.get('annual_extra_amount', 0))
    }

    results = generate_amortization_schedule(principal, annual_rate, tenure_months, scenario_config)
    results['currency'] = CURRENCIES.get(currency_code, CURRENCIES['INR'])

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)