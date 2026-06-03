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

def run_update():
    path_web = entry_web.get()
    path_ev = entry_ev.get()

    if not path_web or not path_ev:
        messagebox.showerror("Error", "Please select both files.")
        return

    try:
        df1 = load_data(path_web)
        df2 = load_data(path_ev)

        # Forcefully clean up column names (removes hidden spaces and Excel BOM artifacts)
        df1.columns = df1.columns.str.strip().str.replace(r'^\ufeff', '', regex=True)
        df2.columns = df2.columns.str.strip().str.replace(r'^\ufeff', '', regex=True)

        # 1. Identify Website columns (Fuzzy match looking for 'code' and 'location')
        web_code = next((c for c in df1.columns if 'code' in c.lower()), None)
        web_loc_col = next((c for c in df1.columns if 'location' in c.lower()), 'Location')

        # 2. Identify Everest columns
        ev_code = next((c for c in df2.columns if 'code' in c.lower()), None)
        ev_loc = next((c for c in df2.columns if 'location' in c.lower()), None)

        # Validation with fallback to show what python actually sees
        if not web_code:
            messagebox.showerror("Error", f"Could not find 'Code' column in Website file.\n\nAvailable columns:\n{list(df1.columns)}")
            return
        if not ev_code or not ev_loc:
            messagebox.showerror("Error", f"Everest file needs both 'Code' and 'Location' columns.\n\nAvailable columns:\n{list(df2.columns)}")
            return

        # 3. Prepare Everest Data (Code, Location)
        df2_prepared = df2[[ev_code, ev_loc]].copy()
        df2_prepared.columns = ['code_join', 'location_new']
        
        # Clean data inside rows for matching
        df1['code_join'] = df1[web_code].astype(str).str.strip().str.upper()
        df2_prepared['code_join'] = df2_prepared['code_join'].astype(str).str.strip().str.upper()
        df2_prepared = df2_prepared.drop_duplicates(subset=['code_join'])

        # 4. Merge Data on Code
        updated_df = pd.merge(df1, df2_prepared, on='code_join', how='left')

        # 5. Handle Location Update
        if web_loc_col in df1.columns:
            updated_df[web_loc_col] = updated_df['location_new'].combine_first(updated_df[web_loc_col])
        else:
            updated_df[web_loc_col] = updated_df['location_new']

        # Cleanup internal join columns
        cols_to_drop = ['code_join', 'location_new']
        updated_df.drop(columns=[c for c in cols_to_drop if c in updated_df.columns], inplace=True)

        # 6. Save result
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("Excel file", "*.xlsx")],
            initialfile="Updated_Locations.csv"
        )
        
        if save_path:
            if save_path.endswith('.xlsx'):
                updated_df.to_excel(save_path, index=False)
            else:
                updated_df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", "Locations linked successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# --- GUI ---
root = tk.Tk()
root.title("Inventory Sync: Location")
root.geometry("500x320")

def browse(entry_box):
    fn = filedialog.askopenfilename(filetypes=[("Sheets", "*.csv *.xlsx *.xls")])
    if fn:
        entry_box.delete(0, tk.END)
        entry_box.insert(0, fn)

tk.Label(root, text="Website File (To be updated)", font=('Arial', 10, 'bold')).pack(pady=(20,0))
entry_web = tk.Entry(root, width=55); entry_web.pack(pady=5)
tk.Button(root, text="Browse Website", command=lambda: browse(entry_web)).pack()

tk.Label(root, text="Everest File (Source of Locations)", font=('Arial', 10, 'bold')).pack(pady=(20,0))
entry_ev = tk.Entry(root, width=55); entry_ev.pack(pady=5)
tk.Button(root, text="Browse Everest", command=lambda: browse(entry_ev)).pack()

tk.Button(root, text="SYNC LOCATIONS", command=run_update, 
          bg="#2ecc71", fg="white", font=('Arial', 12, 'bold'), height=2).pack(pady=30)

root.mainloop()
