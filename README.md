# personal-expense-tracker
This is an open-source Python desktop application built with Tkinter for tracking personal expenses, setting budgets, and generating reports. It helps users manage their finances by categorizing expenses, monitoring budgets with alerts, and visualizing spending patterns through charts.  It's designed for 3 team members
The app stores data in a simple Excel file (`data/expenses.xlsx`) for persistence, making it easy to use without a database. It's designed for 3 team members, focusing on GUI development, backend logic, and features/polish.

## Features
- **Dashboard**: Overview of monthly expenses, remaining budget, and recent entries.
- **Add/Edit/Delete Expenses**: Form to input expenses with date, category, amount, and description. Validation included.
- **Budget Management**: Set monthly budgets per category and get alerts for overspending.
- **View & Search**: Scrollable table of all expenses with search, filter, sort, and export options.
- **Reports & Visualizations**: Generate monthly reports and pie charts for category-wise spending.
- **Data Persistence**: Saves/loads data from Excel using pandas and openpyxl.
- **Additional**: Undo last action, help/about section.

## Technologies Used
- Python 3.x
- Tkinter (for GUI)
- Pandas & Openpyxl (for Excel handling)
- Matplotlib (for charts)
- Datetime (for date management)

## How to Run
1. Install dependencies:  

