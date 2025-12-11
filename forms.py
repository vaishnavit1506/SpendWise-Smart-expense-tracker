from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import datetime
from models import User, Category

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose another one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use another one or login.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=200)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=datetime.today)
    submit = SubmitField('Add Expense')
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name')]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Add Category')
    
    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('This category already exists.')

class BudgetForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    amount = FloatField('Budget Amount', validators=[DataRequired()])
    month = SelectField('Month', coerce=int, validators=[DataRequired()], 
                        choices=[(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)])
    year = SelectField('Year', coerce=int, validators=[DataRequired()],
                       choices=[(y, str(y)) for y in range(datetime.now().year - 1, datetime.now().year + 3)])
    submit = SubmitField('Set Budget')
    
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name')]
        
        # Default to current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        if not self.month.data:
            self.month.data = current_month
        if not self.year.data:
            self.year.data = current_year
