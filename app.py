from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

def format_currency(amount):
    return f"${amount:.2f}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    transactions = json.loads(request.cookies.get('transactions', '[]'))
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expenses = -sum(t['amount'] for t in transactions if t['type'] == 'expense')
    current_balance = total_income + total_expenses
    category_expenses = {'labels': ['Food', 'Housing'], 'data': [100, 200]}
    monthly_expenses = {'labels': ['Jan', 'Feb'], 'data': [300, 400]}
    return render_template('dashboard.html', total_income=total_income, total_expenses=total_expenses,
                          current_balance=current_balance, category_expenses=category_expenses,
                          monthly_expenses=monthly_expenses)

@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/budget')
def budget():
    return render_template('budget.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

if __name__ == '__main__':
    app.run(debug=True)