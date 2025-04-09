from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app import db
from models import User
import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('housing', 'Housing'),
        ('transportation', 'Transportation'),
        ('food', 'Food'),
        ('utilities', 'Utilities'),
        ('healthcare', 'Healthcare'),
        ('entertainment', 'Entertainment'),
        ('personal', 'Personal'),
        ('education', 'Education'),
        ('investments', 'Investments'),
        ('income', 'Income'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    date = DateField('Date', default=datetime.date.today, validators=[DataRequired()])
    transaction_type = SelectField('Type', choices=[('expense', 'Expense'), ('income', 'Income')], validators=[DataRequired()])
    recurring = BooleanField('Recurring Transaction')
    recurring_interval = SelectField('Interval', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ])
    submit = SubmitField('Add Transaction')

class GoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired()])
    target_amount = FloatField('Target Amount', validators=[DataRequired()])
    current_amount = FloatField('Current Amount Saved', default=0.0)
    deadline = DateField('Goal Deadline', validators=[DataRequired()])
    submit = SubmitField('Add Goal')

class UpdateGoalForm(FlaskForm):
    goal_id = HiddenField('Goal ID')
    current_amount = FloatField('Current Amount Saved', validators=[DataRequired()])
    submit = SubmitField('Update Progress')

class BudgetForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('housing', 'Housing'),
        ('transportation', 'Transportation'),
        ('food', 'Food'),
        ('utilities', 'Utilities'),
        ('healthcare', 'Healthcare'),
        ('entertainment', 'Entertainment'),
        ('personal', 'Personal'),
        ('education', 'Education'),
        ('investments', 'Investments'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    limit_amount = FloatField('Budget Limit', validators=[DataRequired()])
    period = SelectField('Budget Period', choices=[
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], default='monthly')
    submit = SubmitField('Add Budget')

class SettingsForm(FlaskForm):
    theme = SelectField('Theme', choices=[('light', 'Light'), ('dark', 'Dark')], default='dark')
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CAD', 'Canadian Dollar (CA$)'),
        ('AUD', 'Australian Dollar (A$)')
    ], default='USD')
    notifications_enabled = BooleanField('Enable Notifications', default=True)
    submit = SubmitField('Save Settings')