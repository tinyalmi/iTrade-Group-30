import tkinter as tk
from tkinter import messagebox, ttk
import csv


def load_stocks():
    stocks = []
    try:
        with open("stocks.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stock = {
                    "ID": row["ID"],
                    "Industry": row["Industry"],
                    "Performance": float(row["Performance"]),
                    "FoundationYear": int(row["FoundationYear"]),
                    "Environment": float(row["Environment"]),
                    "Social": float(row["Social"]),
                    "Governance": float(row["Governance"])
                }
                stocks.append(stock)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load stocks.csv\n{e}")
    return stocks


# MERGE SORT (DESCENDING PERFORMANCE)
def merge_sort(stocks):
    if len(stocks) <= 1:
        return stocks

    mid = len(stocks) // 2
    left = merge_sort(stocks[:mid])
    right = merge_sort(stocks[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i]["Performance"] >= right[j]["Performance"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


# APPLY FILTERS
def apply_filters(stocks, n, industry_filter, year_filter, year_limit, esg_filter):
    industry_data = {}

    if industry_filter == "YES":
        for stock in stocks:
            ind = stock["Industry"]
            if ind not in industry_data:
                industry_data[ind] = {"total": 0, "count": 0}
            industry_data[ind]["total"] += stock["Performance"]
            industry_data[ind]["count"] += 1

        for ind in industry_data:
            industry_data[ind]["average"] = industry_data[ind]["total"] / industry_data[ind]["count"]

    eligible = []

    for stock in stocks:
        ok = True

        if industry_filter == "YES":
            avg = industry_data[stock["Industry"]]["average"]
            if stock["Performance"] < avg:
                ok = False

        if year_filter == "YES":
            if stock["FoundationYear"] > year_limit:
                ok = False
                
        if esg_filter == "YES":
            env = stock["Environment"]
            soc = stock["Social"]
            gov = stock["Governance"]

            avg_esg = (env + soc + gov) / 3

            if avg_esg < 7 or env < 5 or soc < 5 or gov < 5:
                ok = False

        if ok:
            eligible.append(stock)

    eligible = merge_sort(eligible)

    return eligible


# GUI 
def run_recommendation():
    try:
        n = int(entry_n.get())
        if not (1 <= n <= 100):
            raise ValueError
    except:
        messagebox.showerror("Error", "Number of recommendations must be between 1 and 100.")
        return

    industry_filter = combo_industry.get()
    year_filter = combo_year.get()
    esg_filter = combo_esg.get()

    year_limit = None
    if year_filter == "YES":
        try:
            year_limit = int(entry_year.get())
            if not (1800 <= year_limit <= 2020):
                raise ValueError
        except:
            messagebox.showerror("Error", "Year must be between 1800 and 2020.")
            return

    stocks = load_stocks()
    if not stocks:
        return


    results = apply_filters(stocks, n, industry_filter, year_filter, year_limit, esg_filter)

    if len(results) == 0:
        messagebox.showinfo("Notice", "No stocks matched your filters.\nFilters were dropped.")
        results = merge_sort(stocks)[:n]

    elif len(results) < n:
        messagebox.showinfo("Notice", f"Only {len(results)} stocks matched your filters.\nShowing all of them.")

    else:
        results = results[:n]


    group30.delete("all")

    y = 10
    group30.create_text(10, y, anchor="nw", text="Your iTrade Recommendations:", font=("Arial", 14, "bold"))
    y += 30

    for i, stock in enumerate(results, start=1):
        text = f"Rank {i}: {stock['ID']}  |  Performance: {stock['Performance']}"
        group30.create_text(10, y, anchor="nw", text=text, font=("Arial", 12))
        y += 25

    group30.config(scrollregion=group30.bbox("all"))


#LABELS
root = tk.Tk()
root.title("iTrade – Stock Recommendation Tool")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="How many stocks do you want? (1–100)").grid(row=0, column=0, sticky="w")
entry_n = tk.Entry(frame)
entry_n.grid(row=0, column=1)

tk.Label(frame, text="Only above-industry-average performers?").grid(row=1, column=0, sticky="w")
combo_industry = ttk.Combobox(frame, values=["YES", "NO"], width=5)
combo_industry.grid(row=1, column=1)
combo_industry.set("NO")

tk.Label(frame, text="Filter by foundation year?").grid(row=2, column=0, sticky="w")
combo_year = ttk.Combobox(frame, values=["YES", "NO"], width=5)
combo_year.grid(row=2, column=1)
combo_year.set("NO")

tk.Label(frame, text="Enter year (1800–2020):").grid(row=3, column=0, sticky="w")
entry_year = tk.Entry(frame)
entry_year.grid(row=3, column=1)

tk.Label(frame, text="Only high ESG companies?").grid(row=4, column=0, sticky="w")
combo_esg = ttk.Combobox(frame, values=["YES", "NO"], width=5)
combo_esg.grid(row=4, column=1)
combo_esg.set("NO")

btn_run = tk.Button(frame, text="Recommend", command=run_recommendation, width=20)
btn_run.grid(row=5, column=0, columnspan=2, pady=10)


# CANVAS
result_frame = tk.Frame(root)
result_frame.pack(padx=10, pady=10)

scrollbar = tk.Scrollbar(result_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

group30 = tk.Canvas(result_frame, width=600, height=400, bg="white", yscrollcommand=scrollbar.set)
group30.pack(side="left", fill="both", expand=True)

scrollbar.config(command=group30.yview)

def _on_mousewheel(event):
    group30.yview_scroll(int(-1*(event.delta/120)), "units")

group30.bind_all("<MouseWheel>", _on_mousewheel)


root.mainloop()
