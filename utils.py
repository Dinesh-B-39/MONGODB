import datetime
from collections import defaultdict

def format_currency(amount, currency_code='USD'):
    """Format amount according to currency code"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'CA$',
        'AUD': 'A$'
    }
    
    symbol = currency_symbols.get(currency_code, '$')
    
    if currency_code == 'JPY':
        return f"{symbol}{int(amount):,}"
    else:
        return f"{symbol}{amount:,.2f}"

def calculate_category_expenses(transactions):
    """Calculate expenses by category for pie chart"""
    if not transactions:
        return {'labels': [], 'data': []}
        
    category_expenses = defaultdict(float)
    
    for transaction in transactions:
        if not hasattr(transaction, 'type') or not hasattr(transaction, 'category') or not hasattr(transaction, 'amount'):
            continue
            
        if transaction.type == 'expense':
            try:
                category = str(transaction.category) if transaction.category else 'Uncategorized'
                amount = float(transaction.amount)
                if amount < 0:
                    continue
                category_expenses[category] += amount
            except (ValueError, TypeError) as e:
                print(f"Error processing transaction: {e}")
                continue
    
    # Convert to format for Chart.js with fallback for empty data
    if not category_expenses:
        return {'labels': ['No expenses'], 'data': [1]}
        
    return {
        'labels': list(category_expenses.keys()),
        'data': list(category_expenses.values())
    }

def calculate_monthly_expenses(transactions):
    """Calculate monthly expenses for the past 6 months"""
    if not transactions:
        return {'labels': [], 'data': []}
        
    today = datetime.datetime.today()
    
    # Initialize data for the past 6 months
    months = []
    monthly_data = []
    
    for i in range(5, -1, -1):
        # Calculate month date
        month_date = today.replace(day=1) - datetime.timedelta(days=i*30)
        month_name = month_date.strftime('%b %Y')
        months.append(month_name)
        monthly_data.append(0.0)  # Initialize as float
    
    # Fill in the data with validation
    for transaction in transactions:
        if not hasattr(transaction, 'type') or transaction.type != 'expense':
            continue
            
        try:
            if not hasattr(transaction, 'date'):
                continue
                
            transaction_date = transaction.date
            if isinstance(transaction_date, str):
                try:
                    transaction_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d')
                except ValueError as e:
                    print(f"Error parsing transaction date: {e}")
                    continue
                    
            if not hasattr(transaction, 'amount'):
                continue
                
            try:
                amount = float(transaction.amount)
                if amount <= 0:
                    continue
            except (ValueError, TypeError) as e:
                print(f"Error processing transaction amount: {e}")
                continue
        except Exception as e:
            print(f"Unexpected error processing transaction: {e}")
            continue
            
        # Convert date to datetime for comparison if it's just a date
        if isinstance(transaction_date, datetime.date) and not isinstance(transaction_date, datetime.datetime):
            transaction_date = datetime.datetime.combine(transaction_date, datetime.datetime.min.time())
        
        # Check if transaction is within the past 6 months
        if (today - transaction_date).days <= 180:
            # Find the right month index
            for i in range(6):
                month_date = today.replace(day=1) - datetime.timedelta(days=i*30)
                if (transaction_date.year == month_date.year and 
                    transaction_date.month == month_date.month):
                    monthly_data[5-i] += transaction.amount
                    break
    
    return {
        'labels': months,
        'data': monthly_data
    }

def calculate_budget_status(budgets, transactions):
    """Calculate current spending against budget limits"""
    today = datetime.datetime.today()
    start_of_month = today.replace(day=1)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    start_of_year = today.replace(month=1, day=1)
    
    budget_status = []
    
    for budget in budgets:
        category = budget.category
        limit = budget.limit_amount
        period = budget.period
        
        # Determine period start date
        if period == 'weekly':
            period_start = start_of_week
        elif period == 'monthly':
            period_start = start_of_month
        elif period == 'yearly':
            period_start = start_of_year
        else:
            period_start = start_of_month  # Default to monthly
        
        # Convert to datetime.date for comparison
        if isinstance(period_start, datetime.datetime):
            period_start_date = period_start.date()
        else:
            period_start_date = period_start
        
        # Calculate total spending in this category for the period
        spent = 0
        for transaction in transactions:
            if (transaction.type == 'expense' and 
                transaction.category == category and
                transaction.date >= period_start_date):
                spent += transaction.amount
        
        # Calculate percentage
        percentage = (spent / limit * 100) if limit > 0 else 0
        percentage = min(percentage, 100)  # Cap at 100%
        
        remaining = max(limit - spent, 0)
        
        status = {
            'category': category,
            'limit': limit,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'period': period,
            'status': 'danger' if percentage >= 100 else 'warning' if percentage >= 80 else 'success'
        }
        
        budget_status.append(status)
    
    return budget_status

def generate_insights(transactions, budgets):
    """Generate smart insights based on user data"""
    insights = []
    
    # Only analyze if we have enough transactions
    if len(transactions) < 3:
        insights.append({
            'type': 'info',
            'title': 'Not enough data',
            'message': 'Add more transactions to see personalized insights.',
            'icon': 'info-circle'
        })
        return insights
    
    # Get today's date
    today = datetime.datetime.today()
    start_of_current_month = today.replace(day=1)
    start_of_previous_month = (start_of_current_month - datetime.timedelta(days=1)).replace(day=1)
    
    # Convert to date objects for comparison
    start_of_current_month_date = start_of_current_month.date()
    start_of_previous_month_date = start_of_previous_month.date()
    
    # Calculate monthly spending trends
    current_month_expenses = defaultdict(float)
    previous_month_expenses = defaultdict(float)
    
    for transaction in transactions:
        if transaction.type == 'expense':
            category = transaction.category
            amount = transaction.amount
            transaction_date = transaction.date
            
            if isinstance(transaction_date, str):
                try:
                    transaction_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d').date()
                except ValueError:
                    continue
            
            if transaction_date >= start_of_current_month_date:
                current_month_expenses[category] += amount
            elif transaction_date >= start_of_previous_month_date and transaction_date < start_of_current_month_date:
                previous_month_expenses[category] += amount
    
    # Generate spending trend insights
    for category, current_amount in current_month_expenses.items():
        if category in previous_month_expenses and previous_month_expenses[category] > 0:
            previous_amount = previous_month_expenses[category]
            percent_change = ((current_amount - previous_amount) / previous_amount) * 100
            
            if percent_change >= 20:
                insights.append({
                    'type': 'warning',
                    'title': f'{category.capitalize()} spending increased',
                    'message': f'Your {category} spending has increased by {percent_change:.0f}% compared to last month.',
                    'icon': 'arrow-up'
                })
            elif percent_change <= -20:
                insights.append({
                    'type': 'success',
                    'title': f'{category.capitalize()} spending decreased',
                    'message': f'Your {category} spending has decreased by {abs(percent_change):.0f}% compared to last month.',
                    'icon': 'arrow-down'
                })
    
    # Budget warnings
    for budget in budgets:
        category = budget.category
        limit = budget.limit_amount
        
        spent = sum(t.amount for t in transactions 
                  if t.type == 'expense' 
                  and t.category == category 
                  and t.date >= start_of_current_month_date)
        
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        if percentage >= 90:
            insights.append({
                'type': 'danger',
                'title': f'{category.capitalize()} budget at risk',
                'message': f'You have used {percentage:.0f}% of your {category} budget this month.',
                'icon': 'exclamation-triangle'
            })
        elif percentage >= 80:
            insights.append({
                'type': 'warning',
                'title': f'{category.capitalize()} budget approaching limit',
                'message': f'You have used {percentage:.0f}% of your {category} budget this month.',
                'icon': 'exclamation-circle'
            })
    
    # Upcoming goal deadlines
    for transaction in transactions:
        if (transaction.type == 'expense' and 
            transaction.recurring and 
            hasattr(transaction, 'date')):
            
            insights.append({
                'type': 'info',
                'title': 'Recurring expense reminder',
                'message': f"Don't forget about your recurring {transaction.description} payment.",
                'icon': 'sync'
            })
            break  # Just show one reminder
    
    return insights