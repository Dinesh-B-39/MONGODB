from flask_login import UserMixin
from app import db, bcrypt
import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    transactions = db.relationship('Transaction', backref='author', lazy=True)
    goals = db.relationship('SavingGoal', backref='author', lazy=True)
    budgets = db.relationship('Budget', backref='author', lazy=True)

    @staticmethod
    def create_user(username, email, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user.id

    @staticmethod
    def check_password(user, password):
        if isinstance(user, User):
            return bcrypt.check_password_hash(user.password_hash, password)
        return False

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    type = db.Column(db.String(20), nullable=False)
    recurring = db.Column(db.Boolean, default=False)
    recurring_interval = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def add_transaction(user_id, description, amount, category, date, transaction_type, recurring=False, recurring_interval=None):
        transaction = Transaction(
            user_id=user_id,
            description=description,
            amount=amount,
            category=category,
            date=date,
            type=transaction_type,
            recurring=recurring,
            recurring_interval=recurring_interval
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction.id

    @staticmethod
    def get_transactions(user_id, limit=None, sort_by='date', sort_order=-1):
        query = Transaction.query.filter_by(user_id=user_id)
        
        # Apply sorting
        if sort_by == 'date':
            if sort_order == -1:
                query = query.order_by(Transaction.date.desc())
            else:
                query = query.order_by(Transaction.date)
        elif sort_by == 'amount':
            if sort_order == -1:
                query = query.order_by(Transaction.amount.desc())
            else:
                query = query.order_by(Transaction.amount)
        elif sort_by == 'category':
            if sort_order == -1:
                query = query.order_by(Transaction.category.desc())
            else:
                query = query.order_by(Transaction.category)
        
        # Apply limit if specified
        if limit:
            query = query.limit(limit)
        
        return query.all()

    @staticmethod
    def delete_transaction(transaction_id, user_id):
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
            return True
        return False

class SavingGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def add_goal(user_id, name, target_amount, deadline, current_amount=0):
        goal = SavingGoal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=current_amount,
            deadline=deadline
        )
        db.session.add(goal)
        db.session.commit()
        return goal.id

    @staticmethod
    def get_goals(user_id):
        return SavingGoal.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_goal_amount(goal_id, user_id, new_amount):
        goal = SavingGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        if goal:
            goal.current_amount = new_amount
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_goal(goal_id, user_id):
        goal = SavingGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        if goal:
            db.session.delete(goal)
            db.session.commit()
            return True
        return False

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    limit_amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20), default="monthly")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def add_budget(user_id, category, limit_amount, period="monthly"):
        budget = Budget(
            user_id=user_id,
            category=category,
            limit_amount=limit_amount,
            period=period
        )
        db.session.add(budget)
        db.session.commit()
        return budget.id

    @staticmethod
    def get_budgets(user_id):
        return Budget.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_budget(budget_id, user_id, limit_amount):
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
        if budget:
            budget.limit_amount = limit_amount
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_budget(budget_id, user_id):
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
        if budget:
            db.session.delete(budget)
            db.session.commit()
            return True
        return False

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), default='dark')
    currency = db.Column(db.String(10), default='USD')
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    @staticmethod
    def get_settings(user_id):
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = UserSettings(
                user_id=user_id,
                theme='dark',
                currency='USD',
                notifications_enabled=True
            )
            db.session.add(settings)
            db.session.commit()
        return settings

    @staticmethod
    def update_settings(user_id, settings_data):
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if settings:
            for key, value in settings_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            db.session.commit()
            return True
        return False