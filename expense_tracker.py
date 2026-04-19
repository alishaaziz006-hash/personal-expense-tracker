import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime
from data_handler import load_from_excel, save_to_excel, calculate_monthly_totals, validate_expense

class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("800x600")
        self.expenses_df, self.budgets_dict = load_from_excel()
        self.categories = list(self.budgets_dict.keys()) or ['Food', 'Transport', 'Shopping', 'Others']
        self.undo_stack = []
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.setup_dashboard()
        self.setup_add_expense()
        self.setup_view_expenses()
        self.setup_budgets()
        self.setup_reports()
        tk.Button(self, text="Help", command=self.show_help).pack()
        tk.Button(self, text="Undo", command=self.undo_last).pack()

    def setup_dashboard(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Dashboard')
        self.summary_label = tk.Label(frame)
        self.summary_label.pack()
        self.recent_tree = ttk.Treeview(frame, columns=('Date', 'Category', 'Amount', 'Description'))
        for col in self.recent_tree['columns']: self.recent_tree.heading(col, text=col)
        self.recent_tree.pack()
        self.update_dashboard()

    def update_dashboard(self):
        monthly_totals = calculate_monthly_totals(self.expenses_df)
        total_expenses = sum(monthly_totals.values())
        remaining_budget = sum(self.budgets_dict.values()) - total_expenses
        self.summary_label.config(text=f"Expenses: ${total_expenses:.2f}\nRemaining: ${remaining_budget:.2f}")
        for cat, total in monthly_totals.items():
            if cat in self.budgets_dict:
                if total > self.budgets_dict[cat]: messagebox.showwarning("Alert", f"Over in {cat}")
                elif total > 0.8 * self.budgets_dict[cat]: messagebox.showinfo("Warning", f"Nearing in {cat}")
        recent = self.expenses_df.tail(5)
        self.recent_tree.delete(*self.recent_tree.get_children())
        for _, row in recent.iterrows():
            self.recent_tree.insert('', 'end', values=(row['Date'].date(), row['Category'], row['Amount'], row['Description']))

    def setup_add_expense(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Add Expense')
        tk.Label(frame, text="Date:").pack()
        self.date_entry = tk.Entry(frame)
        self.date_entry.pack()
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        tk.Label(frame, text="Category:").pack()
        self.category_combo = ttk.Combobox(frame, values=self.categories)
        self.category_combo.pack()
        tk.Label(frame, text="Amount:").pack()
        self.amount_entry = tk.Entry(frame)
        self.amount_entry.pack()
        tk.Label(frame, text="Desc:").pack()
        self.desc_entry = tk.Entry(frame)
        self.desc_entry.pack()
        tk.Button(frame, text="Add", command=self.add_expense).pack()
        tk.Label(frame, text="New Cat:").pack()
        self.new_cat_entry = tk.Entry(frame)
        self.new_cat_entry.pack()
        tk.Button(frame, text="Add Cat", command=self.add_category).pack()

    def add_category(self):
        new_cat = self.new_cat_entry.get().strip()
        if new_cat and new_cat not in self.categories:
            self.categories.append(new_cat)
            self.category_combo['values'] = self.categories
            self.budget_cat_combo['values'] = self.categories
            self.new_cat_entry.delete(0, 'end')
            messagebox.showinfo("OK", "Added")

    def add_expense(self):
        date_str = self.date_entry.get()
        category = self.category_combo.get()
        amount_str = self.amount_entry.get()
        desc = self.desc_entry.get()
        if not validate_expense(date_str, category, amount_str, desc):
            messagebox.showerror("Error", "Invalid")
            return
        amount = float(amount_str)
        if amount <= 0: messagebox.showerror("Error", "Positive")
        self.undo_stack.append(self.expenses_df.copy())
        new_row = pd.DataFrame({'Date': [pd.to_datetime(date_str)], 'Category': [category], 'Amount': [amount], 'Description': [desc]})
        self.expenses_df = pd.concat([self.expenses_df, new_row], ignore_index=True)
        save_to_excel(self.expenses_df, self.budgets_dict)
        self.update_dashboard()
        self.update_view()
        messagebox.showinfo("OK", "Added")
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.amount_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')

    def setup_view_expenses(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='View Expenses')
        search_frame = tk.Frame(frame)
        search_frame.pack()
        tk.Label(search_frame, text="Search:").pack(side='left')
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side='left')
        tk.Button(search_frame, text="Search", command=self.search_expenses).pack(side='left')
        self.exp_tree = ttk.Treeview(frame, columns=('Date', 'Category', 'Amount', 'Description'))
        for col in self.exp_tree['columns']: self.exp_tree.heading(col, text=col, command=lambda c=col: self.sort_tree(c))
        self.exp_tree.pack(expand=True, fill='both')
        btn_frame = tk.Frame(frame)
        btn_frame.pack()
        tk.Button(btn_frame, text="Edit", command=self.edit_expense).pack(side='left')
        tk.Button(btn_frame, text="Delete", command=self.delete_expense).pack(side='left')
        tk.Button(btn_frame, text="Export", command=self.export_data).pack(side='left')
        self.update_view()

    def update_view(self, df=None):
        if df is None: df = self.expenses_df
        self.exp_tree.delete(*self.exp_tree.get_children())
        for _, row in df.iterrows():
            self.exp_tree.insert('', 'end', values=(row['Date'].date(), row['Category'], row['Amount'], row['Description']))

    def sort_tree(self, col):
        self.expenses_df = self.expenses_df.sort_values(by=col)
        self.update_view()

    def search_expenses(self):
        query = self.search_entry.get().lower()
        if not query: return self.update_view()
        filtered = self.expenses_df[self.expenses_df['Category'].str.lower().str.contains(query) | self.expenses_df['Description'].str.lower().str.contains(query)]
        self.update_view(filtered)

    def get_selected_row(self):
        selected = self.exp_tree.selection()
        if not selected: return None
        values = self.exp_tree.item(selected[0])['values']
        date = datetime.strptime(str(values[0]), '%Y-%m-%d').date()
        return self.expenses_df[(self.expenses_df['Date'].dt.date == date) & (self.expenses_df['Category'] == values[1]) & (self.expenses_df['Amount'] == values[2]) & (self.expenses_df['Description'] == values[3])].index[0]

    def edit_expense(self):
        idx = self.get_selected_row()
        if idx is None: return messagebox.showerror("Error", "Select")
        edit_win = tk.Toplevel(self)
        row = self.expenses_df.loc[idx]
        tk.Label(edit_win, text="Date:").pack()
        date_entry = tk.Entry(edit_win)
        date_entry.pack()
        date_entry.insert(0, row['Date'].strftime('%Y-%m-%d'))
        tk.Label(edit_win, text="Category:").pack()
        cat_combo = ttk.Combobox(edit_win, values=self.categories)
        cat_combo.pack()
        cat_combo.set(row['Category'])
        tk.Label(edit_win, text="Amount:").pack()
        amount_entry = tk.Entry(edit_win)
        amount_entry.pack()
        amount_entry.insert(0, row['Amount'])
        tk.Label(edit_win, text="Desc:").pack()
        desc_entry = tk.Entry(edit_win)
        desc_entry.pack()
        desc_entry.insert(0, row['Description'])
        def save_edit():
            date_str = date_entry.get()
            category = cat_combo.get()
            amount_str = amount_entry.get()
            desc = desc_entry.get()
            if not validate_expense(date_str, category, amount_str, desc): return messagebox.showerror("Error", "Invalid")
            amount = float(amount_str)
            if amount <= 0: return messagebox.showerror("Error", "Positive")
            self.undo_stack.append(self.expenses_df.copy())
            self.expenses_df.at[idx, 'Date'] = pd.to_datetime(date_str)
            self.expenses_df.at[idx, 'Category'] = category
            self.expenses_df.at[idx, 'Amount'] = amount
            self.expenses_df.at[idx, 'Description'] = desc
            save_to_excel(self.expenses_df, self.budgets_dict)
            self.update_view()
            self.update_dashboard()
            edit_win.destroy()
            messagebox.showinfo("OK", "Updated")
        tk.Button(edit_win, text="Save", command=save_edit).pack()

    def delete_expense(self):
        idx = self.get_selected_row()
        if idx is None: return messagebox.showerror("Error", "Select")
        if messagebox.askyesno("Confirm", "Delete?"):
            self.undo_stack.append(self.expenses_df.copy())
            self.expenses_df = self.expenses_df.drop(idx)
            save_to_excel(self.expenses_df, self.budgets_dict)
            self.update_view()
            self.update_dashboard()
            messagebox.showinfo("OK", "Deleted")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if file_path:
            with pd.ExcelWriter(file_path) as writer: self.expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
            messagebox.showinfo("OK", "Exported")

    def setup_budgets(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Set Budgets')
        self.budget_tree = ttk.Treeview(frame, columns=('Category', 'Budget'))
        for col in self.budget_tree['columns']: self.budget_tree.heading(col, text=col)
        self.budget_tree.pack()
        set_frame = tk.Frame(frame)
        set_frame.pack()
        tk.Label(set_frame, text="Category:").pack(side='left')
        self.budget_cat_combo = ttk.Combobox(set_frame, values=self.categories)
        self.budget_cat_combo.pack(side='left')
        tk.Label(set_frame, text="Amount:").pack(side='left')
        self.budget_amount_entry = tk.Entry(set_frame)
        self.budget_amount_entry.pack(side='left')
        tk.Button(set_frame, text="Set", command=self.set_budget).pack(side='left')
        self.update_budgets_view()

    def update_budgets_view(self):
        self.budget_tree.delete(*self.budget_tree.get_children())
        for cat, bud in self.budgets_dict.items(): self.budget_tree.insert('', 'end', values=(cat, bud))

    def set_budget(self):
        category = self.budget_cat_combo.get()
        amount_str = self.budget_amount_entry.get()
        try:
            amount = float(amount_str)
            if amount < 0: raise ValueError
        except: return messagebox.showerror("Error", "Invalid")
        self.budgets_dict[category] = amount
        save_to_excel(self.expenses_df, self.budgets_dict)
        self.update_budgets_view()
        self.update_dashboard()
        messagebox.showinfo("OK", "Set")

    def setup_reports(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Reports')
        tk.Button(frame, text="Generate", command=self.generate_report).pack()
        self.report_text = tk.Text(frame, height=10)
        self.report_text.pack()
        self.figure = plt.Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, frame)
        self.canvas.get_tk_widget().pack()

    def generate_report(self):
        monthly_totals = calculate_monthly_totals(self.expenses_df)
        report = "Report:\n"
        total = 0
        for cat, amt in monthly_totals.items():
            bud = self.budgets_dict.get(cat, 0)
            variance = amt - bud
            report += f"{cat}: ${amt:.2f} (Bud: ${bud:.2f}, Var: ${variance:.2f})\n"
            total += amt
        report += f"Total: ${total:.2f}"
        self.report_text.delete(1.0, 'end')
        self.report_text.insert('end', report)
        if monthly_totals:
            self.ax.clear()
            self.ax.pie(monthly_totals.values(), labels=monthly_totals.keys(), autopct='%1.1f%%')
            self.ax.set_title("Spending")
            self.canvas.draw()

    def show_help(self):
        messagebox.showinfo("Help", "Track, budget, report")

    def undo_last(self):
        if self.undo_stack:
            self.expenses_df = self.undo_stack.pop()
            save_to_excel(self.expenses_df, self.budgets_dict)
            self.update_view()
            self.update_dashboard()
            self.update_budgets_view()
            messagebox.showinfo("OK", "Undone")

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()