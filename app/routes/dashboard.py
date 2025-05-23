from flask import Blueprint, render_template, request, redirect, url_for,flash
from flask_login import login_required, current_user
from app.models import Expense, db
from datetime import datetime
from sqlalchemy import extract, func
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

dashboard=Blueprint('dashboard',__name__)

@dashboard.route('/dashboard')
@login_required
def dashboard_home():
    expenses=Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    current_month=datetime.now().month
    current_year=datetime.now().year

    monthly_expenses=db.session.query(func.sum(Expense.amount).filter(
        extract('month',Expense.date)==current_month,
        extract('year',Expense.date)==current_year,
        Expense.user_id==current_user.id
    )).scalar()or 0

    yearly_expenses=db.session.query(func.sum(Expense.amount).filter(
        extract('year',Expense.date)==current_year,
        Expense.user_id==current_user.id
    )).scalar()or 0

    return render_template('dashboard.html',expenses=expenses,monthly_expenses=monthly_expenses,yearly_expenses=yearly_expenses)

@dashboard.route('/create',methods=['GET','POST'])
@login_required
def create_expense():
    if request.method=='POST':
        date_str=request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        amount=float(request.form['amount'])
        category=request.form['category']
        description=request.form['description']

        new_expense=Expense(date=date,amount=amount,category=category,
        description=description,user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('dashboard.dashboard_home',))
    return render_template('create_expense.html')

@dashboard.route('/delete/<int:id_expense>')
@login_required
def delete(id_expense):
    expense=Expense.query.get_or_404(id_expense)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('dashboard.dashboard_home'))

@dashboard.route('/edit/<int:id_expense>', methods=['GET', 'POST'])
def edit(id_expense):
    expense = Expense.query.get_or_404(id_expense)

    if request.method == 'POST':
        expense.date = request.form['date']
        expense.date = datetime.strptime(expense.date, '%Y-%m-%d').date()
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        expense.description = request.form['description']

        
        db.session.commit()
           
        return redirect(url_for('dashboard.dashboard_home'))
       

    return render_template('edit_expense.html', expense=expense)

@dashboard.route('/expense_analysis')
@login_required
def monthly_expenses_chart():
    current_month=datetime.now().month
    current_year=datetime.now().year

    data=(
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter(
            Expense.user_id == current_user.id,
            extract('month', Expense.date) == current_month,
            extract('year', Expense.date) == current_year
        )
        .group_by(Expense.category)
        .all()
    )
    categories = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]
    
    # Generate bar chart using matplotlib
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'width': 0.4},  # This creates the donut effect
        textprops={'color': 'black'}
    )
    

    # Save plot to a PNG in memory
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Pass image to HTML template
    return render_template('monthly_expense_chart.html', chart_data=img_base64)

@dashboard.route('/expense_analysis')
@login_required
def yearly_expenses_chart():
    current_year = datetime.now().year

    data = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == current_year
        )
        .group_by(Expense.category)
        .all()
    )
    
    categories = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]

    # Generate donut chart using matplotlib
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'width': 0.4},  # Donut effect
        textprops={'color': 'black'}
    )
    
    title("Yearly Expenses")
    # Save plot to a PNG in memory
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('monthly_expense_chart.html', chart_data=img_base64)
