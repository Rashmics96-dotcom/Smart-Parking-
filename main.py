import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import re

# Database setup
conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS parking (
    slot_id INTEGER PRIMARY KEY,
    vehicle_number TEXT,
    entry_time TEXT,
    exit_time TEXT,
    fee INTEGER,
    status TEXT
)
""")
conn.commit()

MAX_SLOTS = 5

# Check slot
def is_slot_available(slot):
    cursor.execute("SELECT status FROM parking WHERE slot_id=?", (slot,))
    result = cursor.fetchone()
    return result is None or result[0] == "Free"

# Park vehicle
def park_vehicle():
    try:
        slot = int(slot_entry.get())
    except:
        messagebox.showerror("Error", "Enter valid slot number")
        return
    vehicle = vehicle_entry.get()
    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$"

    if not re.match(pattern, vehicle):
        messagebox.showerror(
            "Error",
            "Enter valid vehicle number\nExample: KA01AB1234"
        )
        return


    cursor.execute("SELECT COUNT(*) FROM parking WHERE status='Occupied'")
    count = cursor.fetchone()[0]

    if count >= MAX_SLOTS:
        messagebox.showerror("Error", "Parking Full")
        return

    if not is_slot_available(slot):
        messagebox.showerror("Error", "Slot Occupied")
        return

    entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("REPLACE INTO parking VALUES (?, ?, ?, ?, ?, ?)",
                   (slot, vehicle, entry_time, None, 0, "Occupied"))
    conn.commit()
    cursor.execute("SELECT * FROM parking")
    rows = cursor.fetchall()

    print("\nParking Records:")
    for row in rows:
        print(row)

    messagebox.showinfo("Success", "Vehicle Parked")

# Exit vehicle
def exit_vehicle():
    slot = int(slot_entry.get())

    cursor.execute("SELECT entry_time FROM parking WHERE slot_id=?", (slot,))
    result = cursor.fetchone()

    if result is None:
        messagebox.showerror("Error", "Slot not found")
        return

    entry_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
    exit_time = datetime.now()

    duration = (exit_time - entry_time).seconds /60
    fee = int(duration * 50)

    cursor.execute("""
    UPDATE parking
    SET exit_time=?, fee=?, status='Free'
    WHERE slot_id=?
    """, (exit_time.strftime("%Y-%m-%d %H:%M:%S"), fee, slot))

    conn.commit()
    cursor.execute("SELECT * FROM parking")
    rows = cursor.fetchall()

    print("\nUpdated Parking Records:")
    for row in rows:
        print(row)

    messagebox.showinfo("Exit", f"Fee: ₹{fee}")

# View data
def view_parking():
    cursor.execute("SELECT * FROM parking")
    rows = cursor.fetchall()

    data = ""
    for row in rows:
        data += str(row) + "\n"

    messagebox.showinfo("Parking Data", data)

# Report
def view_report():
    cursor.execute("SELECT COUNT(*) FROM parking")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(fee) FROM parking")
    revenue = cursor.fetchone()[0]

    if revenue is None:
        revenue = 0

    messagebox.showinfo("Report",
                        f"Total Vehicles: {total}\nRevenue: ₹{revenue}")

# Login system
def login():
    if user_entry.get() == "admin" and pass_entry.get() == "1234":
        login_window.destroy()
        main_app()
    else:
        messagebox.showerror("Error", "Invalid Login")

# Main GUI
def main_app():
    global slot_entry, vehicle_entry

    root = tk.Tk()
    root.title("Smart Parking System")
    root.geometry("400x350")

    tk.Label(root, text="SMART PARKING", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="Slot Number").pack()
    slot_entry = tk.Entry(root)
    slot_entry.pack()

    tk.Label(root, text="Vehicle Number").pack()
    vehicle_entry = tk.Entry(root)
    vehicle_entry.pack()

    tk.Button(root, text="Park Vehicle", command=park_vehicle).pack(pady=5)
    tk.Button(root, text="Exit Vehicle", command=exit_vehicle).pack(pady=5)
    tk.Button(root, text="View Parking", command=view_parking).pack(pady=5)
    tk.Button(root, text="View Report", command=view_report).pack(pady=5)

    root.mainloop()

# Login window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")

tk.Label(login_window, text="Username").pack()
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password").pack()
pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()

tk.Button(login_window, text="Login", command=login).pack(pady=10)

login_window.mainloop()
cursor.execute("SELECT * FROM parking")
rows = cursor.fetchall()

for row in rows:
    print(row)c
