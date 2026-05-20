import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def load_data(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.csv':
            return pd.read_csv(path, encoding='latin1', dtype=str)
        else:
            return pd.read_excel(path, dtype=str)
    except Exception as e:
        raise ValueError(f"Could not read {os.path.basename(path)}: {e}")

def browse_file(entry_field):
    filename = filedialog.askopenfilename()
    entry_field.delete(0, tk.END)
    entry_field.insert(0, filename)

def run_update():
    path_web = entry_web.get()
    path_ev = entry_ev.get()

    if not path_web or not path_ev:
        messagebox.showerror("Error", "Please select both files.")
        return

    try:
        df_web = load_data(path_web)
        df_ev = load_data(path_ev)

        # Identify Code column (case-insensitive)
        web_code_col = next((c for c in df_web.columns if c.lower() == 'code'), None)
        ev_code_col = next((c for c in df_ev.columns if c.lower() == 'code'), None)

        if not web_code_col or not ev_code_col:
            messagebox.showerror("Error", "Could not find 'Code' column in one of the files.")
            return

        # Columns to import
        ev_cols_wanted = {'picture': 'PICTURE', 'new picture': 'NEW PICTURE', 'description': 'Description', 'price': 'Price'}
        ev_found = {}
        for lower_name, desired_name in ev_cols_wanted.items():
            col = next((c for c in df_ev.columns if c.lower() == lower_name), None)
            if col: ev_found[desired_name] = col

        if not ev_found:
            messagebox.showerror("Error", "No matching columns found in Everest file.")
            return

        df_ev_prepared = df_ev[[ev_code_col] + list(ev_found.values())].copy()
        df_ev_prepared.columns = ['code_join'] + list(ev_found.keys())
        
        df_web['code_join'] = df_web[web_code_col].astype(str).str.strip().str.upper()
        df_ev_prepared['code_join'] = df_ev_prepared['code_join'].astype(str).str.strip().str.upper()
        df_ev_prepared = df_ev_prepared.drop_duplicates(subset=['code_join'])

        merged = pd.merge(df_web, df_ev_prepared, on='code_join', how='left', suffixes=('', '_ev'))

        for desired_name in ev_found.keys():
            ev_col = desired_name + '_ev'
            if desired_name in merged.columns:
                merged[desired_name] = merged[ev_col].combine_first(merged[desired_name])
            else:
                merged[desired_name] = merged[ev_col]

        cols_to_drop = [c for c in merged.columns if c.endswith('_ev')] + ['code_join']
        merged.drop(columns=[c for c in cols_to_drop if c in merged.columns], inplace=True)

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if save_path:
            if save_path.endswith('.xlsx'):
                merged.to_excel(save_path, index=False)
            else:
                merged.to_csv(save_path, index=False)
            messagebox.showinfo("Success", "Process Complete!")

    except Exception as e:
        messagebox.showerror("Error", f"Details: {str(e)}")

# --- GUI SETUP ---
root = tk.Tk()
root.title("Data Merger Tool")
root.geometry("500x200")

# Website File Row
tk.Label(root, text="Website File:").grid(row=0, column=0, padx=10, pady=10)
entry_web = tk.Entry(root, width=40)
entry_web.grid(row=0, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file(entry_web)).grid(row=0, column=2)

# Everest File Row
tk.Label(root, text="Everest File:").grid(row=1, column=0, padx=10, pady=10)
entry_ev = tk.Entry(root, width=40)
entry_ev.grid(row=1, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file(entry_ev)).grid(row=1, column=2)

# Run Button
tk.Button(root, text="Run Update", command=run_update, bg="green", fg="white", height=2, width=20).grid(row=2, column=1, pady=20)

root.mainloop()
