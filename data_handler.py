import pandas as pd
from datetime import datetime

EXCEL_FILE = 'data/expenses.xlsx'

def load_from_excel():
    try:
        expenses_df = pd.read_excel(EXCEL_FILE, sheet_name='Expenses', engine='openpyxl')
        if not all(col in expenses_df.columns for col in ['Date', 'Category', 'Amount', 'Description']):
            raise ValueError
        expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
        budgets_df = pd.read_excel(EXCEL_FILE, sheet_name='Budgets', engine='openpyxl')
        if not all(col in budgets_df.columns for col in ['Category', 'Budget']):
            raise ValueError
        budgets_dict = dict(zip(budgets_df['Category'], budgets_df['Budget']))
        return expenses_df, budgets_dict
    except (FileNotFoundError, ValueError):
        expenses_df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        budgets_dict = {}
        save_to_excel(expenses_df, budgets_dict)
        return expenses_df, budgets_dict

def save_to_excel(expenses_df, budgets_dict):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
        budgets_df = pd.DataFrame(list(budgets_dict.items()), columns=['Category', 'Budget'])
        budgets_df.to_excel(writer, sheet_name='Budgets', index=False)

def calculate_monthly_totals(expenses_df, month=None):
    if month is None:
        month = datetime.now().strftime('%Y-%m')
    monthly_expenses = expenses_df[expenses_df['Date'].dt.strftime('%Y-%m') == month]
    return monthly_expenses.groupby('Category')['Amount'].sum().to_dict()

def validate_expense(date_str, category, amount, description):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        float(amount)
        return True
    except:
        return False