from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt
from forms import RegistrationForm, LoginForm, TransactionForm, GoalForm, UpdateGoalForm, BudgetForm, SettingsForm
from models import User, Transaction, SavingGoal, Budget, UserSettings
from utils import calculate_budget_status, generate_insights, format_currency, calculate_monthly_expenses, calculate_category_expenses
import datetime
import json
import decimal

# Helper function to handle datetime serialization for JSON
def json_serialize_date(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', title='Personal Finance Tracker')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and User.check_password(user, form.password.data):
            login_user(user)
            
            # Initialize user settings if not exists
            UserSettings.get_settings(user.id)
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's transactions
    recent_transactions = Transaction.get_transactions(current_user.id, limit=5)
    
    # Calculate financial summary
    all_transactions = Transaction.get_transactions(current_user.id)
    total_income = sum(t.amount for t in all_transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in all_transactions if t.type == 'expense')
    current_balance = total_income - total_expenses
    
    # Get category expense data for charts
    category_expenses = calculate_category_expenses(all_transactions)
    
    # Get monthly expense data for charts
    monthly_expenses = calculate_monthly_expenses(all_transactions)
    
    # Get user's saving goals
    goals = SavingGoal.get_goals(current_user.id)
    
    # Get budget status
    budgets = Budget.get_budgets(current_user.id)
    budget_status = calculate_budget_status(budgets, all_transactions)
    
    # Get user settings for currency formatting
    settings = UserSettings.get_settings(current_user.id)
    
    # Generate insights
    insights = generate_insights(all_transactions, budgets)
    
    return render_template(
        'dashboard.html',
        title='Dashboard',
        recent_transactions=recent_transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        current_balance=current_balance,
        category_expenses=json.dumps(category_expenses, default=json_serialize_date),
        monthly_expenses=json.dumps(monthly_expenses, default=json_serialize_date),
        goals=goals,
        budget_status=budget_status,
        insights=insights,
        format_currency=lambda amount: format_currency(amount, settings.currency if settings else 'USD'),
        settings=settings
    )

@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    form = TransactionForm()
    
    if form.validate_on_submit():
        Transaction.add_transaction(
            user_id=current_user.id,
            description=form.description.data,
            amount=form.amount.data,
            category=form.category.data,
            date=form.date.data,
            transaction_type=form.transaction_type.data,
            recurring=form.recurring.data,
            recurring_interval=form.recurring_interval.data if form.recurring.data else None
        )
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))
    
    # Get all transactions
    user_transactions = Transaction.get_transactions(current_user.id)
    
    # Get user settings for currency formatting
    settings = UserSettings.get_settings(current_user.id)
    
    return render_template(
        'transactions.html',
        title='Transactions',
        form=form,
        transactions=user_transactions,
        format_currency=lambda amount: format_currency(amount, settings.currency if settings else 'USD'),
        settings=settings
    )

@app.route('/delete_transaction/<transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    if Transaction.delete_transaction(transaction_id, current_user.id):
        flash('Transaction deleted successfully!', 'success')
    else:
        flash('Failed to delete transaction.', 'danger')
    return redirect(url_for('transactions'))

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    form = GoalForm()
    update_form = UpdateGoalForm()
    
    if form.validate_on_submit():
        SavingGoal.add_goal(
            user_id=current_user.id,
            name=form.name.data,
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data,
            deadline=form.deadline.data
        )
        flash('Saving goal added successfully!', 'success')
        return redirect(url_for('goals'))
    
    # Get all goals
    user_goals = SavingGoal.get_goals(current_user.id)
    
    # Get user settings for currency formatting
    settings = UserSettings.get_settings(current_user.id)
    
    return render_template(
        'goals.html',
        title='Saving Goals',
        form=form,
        update_form=update_form,
        goals=user_goals,
        format_currency=lambda amount: format_currency(amount, settings.currency if settings else 'USD'),
        settings=settings
    )

@app.route('/update_goal', methods=['POST'])
@login_required
def update_goal():
    form = UpdateGoalForm()
    if form.validate_on_submit():
        if SavingGoal.update_goal_amount(
            goal_id=form.goal_id.data,
            user_id=current_user.id,
            new_amount=form.current_amount.data
        ):
            flash('Goal progress updated successfully!', 'success')
        else:
            flash('Failed to update goal progress.', 'danger')
    return redirect(url_for('goals'))

@app.route('/delete_goal/<goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    if SavingGoal.delete_goal(goal_id, current_user.id):
        flash('Goal deleted successfully!', 'success')
    else:
        flash('Failed to delete goal.', 'danger')
    return redirect(url_for('goals'))

@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    form = BudgetForm()
    
    if form.validate_on_submit():
        # Check if budget for category already exists
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category=form.category.data,
            period=form.period.data
        ).first()
        
        if existing_budget:
            Budget.update_budget(
                budget_id=existing_budget.id,
                user_id=current_user.id,
                limit_amount=form.limit_amount.data
            )
            flash('Budget updated successfully!', 'success')
        else:
            Budget.add_budget(
                user_id=current_user.id,
                category=form.category.data,
                limit_amount=form.limit_amount.data,
                period=form.period.data
            )
            flash('Budget added successfully!', 'success')
        
        return redirect(url_for('budget'))
    
    # Get all budgets and calculate status
    user_budgets = Budget.get_budgets(current_user.id)
    all_transactions = Transaction.get_transactions(current_user.id)
    budget_status = calculate_budget_status(user_budgets, all_transactions)
    
    # Get user settings for currency formatting
    settings = UserSettings.get_settings(current_user.id)
    
    return render_template(
        'budget.html',
        title='Budget Planning',
        form=form,
        budgets=user_budgets,
        budget_status=budget_status,
        format_currency=lambda amount: format_currency(amount, settings.currency if settings else 'USD'),
        settings=settings
    )

@app.route('/delete_budget/<budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    if Budget.delete_budget(budget_id, current_user.id):
        flash('Budget deleted successfully!', 'success')
    else:
        flash('Failed to delete budget.', 'danger')
    return redirect(url_for('budget'))

@app.route('/insights')
@login_required
def insights():
    # Get all transactions
    all_transactions = Transaction.get_transactions(current_user.id)
    
    # Get all budgets
    budgets = Budget.get_budgets(current_user.id)
    
    # Generate insights
    insights_data = generate_insights(all_transactions, budgets)
    
    # Get user settings for currency formatting
    settings = UserSettings.get_settings(current_user.id)
    
    # Get category expense data and monthly expense data for the charts
    category_expenses = calculate_category_expenses(all_transactions)
    monthly_expenses = calculate_monthly_expenses(all_transactions)
    
    return render_template(
        'insights.html',
        title='Smart Insights',
        insights=insights_data,
        category_expenses=json.dumps(category_expenses, default=json_serialize_date),
        monthly_expenses=json.dumps(monthly_expenses, default=json_serialize_date),
        transactions=json.dumps([{
            'id': t.id,
            'description': t.description,
            'amount': t.amount,
            'category': t.category,
            'date': t.date.isoformat() if hasattr(t.date, 'isoformat') else t.date,
            'type': t.type,
            'recurring': t.recurring
        } for t in all_transactions], default=json_serialize_date),
        format_currency=lambda amount: format_currency(amount, settings.currency if settings else 'USD'),
        settings=settings
    )

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Get current settings
    user_settings = UserSettings.get_settings(current_user.id)
    
    form = SettingsForm(obj=user_settings)
    
    if form.validate_on_submit():
        settings_data = {
            'theme': form.theme.data,
            'currency': form.currency.data,
            'notifications_enabled': form.notifications_enabled.data
        }
        
        if UserSettings.update_settings(current_user.id, settings_data):
            # Update session data
            session['theme'] = form.theme.data
            flash('Settings updated successfully!', 'success')
        else:
            flash('Failed to update settings.', 'danger')
        
        return redirect(url_for('settings'))
    
    # Pre-fill form with current settings
    if user_settings:
        form.theme.data = user_settings.theme
        form.currency.data = user_settings.currency
        form.notifications_enabled.data = user_settings.notifications_enabled
    
    return render_template(
        'settings.html',
        title='Settings',
        form=form,
        settings=user_settings
    )

@app.route('/export_data')
@login_required
def export_data():
    # Get all user data
    transactions = Transaction.get_transactions(current_user.id)
    goals = SavingGoal.get_goals(current_user.id)
    budgets = Budget.get_budgets(current_user.id)
    
    # Create export data object with serializable data
    export_data = {
        'transactions': [{
            'id': t.id,
            'description': t.description,
            'amount': t.amount,
            'category': t.category,
            'date': t.date.isoformat() if hasattr(t.date, 'isoformat') else str(t.date),
            'type': t.type,
            'recurring': t.recurring,
            'recurring_interval': t.recurring_interval
        } for t in transactions],
        'goals': [{
            'id': g.id,
            'name': g.name,
            'target_amount': g.target_amount,
            'current_amount': g.current_amount,
            'deadline': g.deadline.isoformat() if hasattr(g.deadline, 'isoformat') else str(g.deadline)
        } for g in goals],
        'budgets': [{
            'id': b.id,
            'category': b.category,
            'limit_amount': b.limit_amount,
            'period': b.period
        } for b in budgets],
        'exported_at': datetime.datetime.utcnow().isoformat()
    }
    
    # Convert dates to string for JSON serialization
    json_data = json.dumps(export_data, default=json_serialize_date)
    
    # Return as JSON download
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Disposition"] = "attachment; filename=finance_data.json"
    
    return response

@app.route('/export_csv')
@login_required
def export_csv():
    import csv
    from io import StringIO
    
    # Get all transactions
    transactions = Transaction.get_transactions(current_user.id)
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Description', 'Category', 'Type', 'Amount', 'Recurring'])
    
    # Write transactions
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d') if hasattr(transaction.date, 'strftime') else str(transaction.date),
            transaction.description,
            transaction.category,
            transaction.type,
            transaction.amount,
            'Yes' if transaction.recurring else 'No'
        ])
    
    # Return as CSV download
    response = app.response_class(
        response=output.getvalue(),
        status=200,
        mimetype='text/csv'
    )
    response.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    
    return response

# Set theme preference in session for all routes
@app.before_request
def before_request():
    if current_user.is_authenticated:
        settings = UserSettings.get_settings(current_user.id)
        if settings:
            session['theme'] = settings.theme