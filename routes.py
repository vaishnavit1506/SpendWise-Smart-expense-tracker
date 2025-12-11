import calendar
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from models import User, Category, Expense, Budget
from forms import RegistrationForm, LoginForm, ExpenseForm, CategoryForm, BudgetForm
import json

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html', title='SpendWise - Track Your Expenses')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
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
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get total expenses this month
    start_date = datetime(current_year, current_month, 1).date()
    end_date = datetime(current_year, current_month, calendar.monthrange(current_year, current_month)[1]).date()
    
    monthly_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()
    
    total_spent = sum(expense.amount for expense in monthly_expenses)
    
    # Get expenses by category
    expenses_by_category = {}
    for expense in monthly_expenses:
        category_name = expense.category.name
        if category_name in expenses_by_category:
            expenses_by_category[category_name] += expense.amount
        else:
            expenses_by_category[category_name] = expense.amount
    
    # Get budgets and calculate remaining amounts
    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month,
        year=current_year
    ).all()
    
    budget_data = []
    for budget in budgets:
        category_name = budget.category.name
        spent = expenses_by_category.get(category_name, 0)
        remaining = budget.amount - spent
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        
        budget_data.append({
            'category': category_name,
            'budget': budget.amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage
        })
    
    # Recent 5 expenses
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    
    # Chart data
    category_names = [item['category'] for item in budget_data]
    category_spent = [item['spent'] for item in budget_data]
    category_budgets = [item['budget'] for item in budget_data]
    
    return render_template(
        'dashboard.html',
        title='Dashboard',
        total_spent=total_spent,
        budget_data=budget_data,
        recent_expenses=recent_expenses,
        month_name=datetime(current_year, current_month, 1).strftime('%B'),
        year=current_year,
        chart_categories=json.dumps(category_names),
        chart_spent=json.dumps(category_spent),
        chart_budgets=json.dumps(category_budgets),
        min=min
    )

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
            user_id=current_user.id,
            category_id=form.category_id.data
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    # Get all expenses for the current user
    expenses_list = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    return render_template('expenses.html', title='Manage Expenses', form=form, expenses=expenses_list)

@app.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Check if the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You are not authorized to delete this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
        return redirect(url_for('categories'))
    
    categories_list = Category.query.order_by(Category.name).all()
    
    return render_template('categories.html', title='Manage Categories', form=form, categories=categories_list)

@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    form = BudgetForm()
    
    if form.validate_on_submit():
        # Check if budget already exists for this category, month, and year
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=form.category_id.data,
            month=form.month.data,
            year=form.year.data
        ).first()
        
        if existing_budget:
            # Update existing budget
            existing_budget.amount = form.amount.data
            flash('Budget updated successfully!', 'success')
        else:
            # Create new budget
            budget = Budget(
                amount=form.amount.data,
                month=form.month.data,
                year=form.year.data,
                user_id=current_user.id,
                category_id=form.category_id.data
            )
            db.session.add(budget)
            flash('Budget added successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('budgets'))
    
    # Get current month and year for filtering budgets
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # If month and year are specified in the query parameters, use those
    month = request.args.get('month', current_month, type=int)
    year = request.args.get('year', current_year, type=int)
    
    # Set the form's month and year to match the filter
    form.month.data = month
    form.year.data = year
    
    # Get budgets for the selected month and year
    budgets_list = Budget.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year
    ).all()
    
    # Get all categories and mark which ones have budgets
    all_categories = Category.query.order_by(Category.name).all()
    categories_with_budget = {budget.category_id for budget in budgets_list}
    
    budget_data = []
    for category in all_categories:
        budget = next((b for b in budgets_list if b.category_id == category.id), None)
        
        # Get actual spending for this category in the selected month
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()
        
        expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.category_id == category.id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
        
        spent = sum(expense.amount for expense in expenses)
        
        budget_data.append({
            'category': category,
            'budget': budget.amount if budget else 0,
            'budget_id': budget.id if budget else None,
            'spent': spent,
            'has_budget': category.id in categories_with_budget
        })
    
    return render_template(
        'budgets.html',
        title='Manage Budgets',
        form=form,
        budget_data=budget_data,
        current_month=month,
        current_year=year,
        month_name=datetime(year, month, 1).strftime('%B'),
        datetime=datetime,
        min=min
    )

@app.route('/analytics')
@login_required
def analytics():
    # Get date range (default to current year)
    current_year = datetime.now().year
    year = request.args.get('year', current_year, type=int)
    
    # Get yearly data by month
    monthly_data = []
    for month in range(1, 13):
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()
        
        expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
        
        total = sum(expense.amount for expense in expenses)
        monthly_data.append({
            'month': datetime(year, month, 1).strftime('%B'),
            'total': total
        })
    
    # Get yearly data by category
    category_data = {}
    for expense in Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= datetime(year, 1, 1).date(),
        Expense.date <= datetime(year, 12, 31).date()
    ).all():
        category_name = expense.category.name
        if category_name in category_data:
            category_data[category_name] += expense.amount
        else:
            category_data[category_name] = expense.amount
    
    # Sort categories by amount spent
    sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare data for charts
    months = [item['month'] for item in monthly_data]
    monthly_totals = [item['total'] for item in monthly_data]
    
    category_names = [item[0] for item in sorted_categories]
    category_totals = [item[1] for item in sorted_categories]
    
    return render_template(
        'analytics.html',
        title='Analytics',
        year=year,
        monthly_data=monthly_data,
        category_data=sorted_categories,
        months=json.dumps(months),
        monthly_totals=json.dumps(monthly_totals),
        category_names=json.dumps(category_names),
        category_totals=json.dumps(category_totals),
        datetime=datetime,
        min=min
    )
