import tkinter as tk
from tkinter import messagebox, ttk

import bcrypt
import sqlite3

# Connect to the database
conn = sqlite3.connect('passwords.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS passwords
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              service TEXT,
              username TEXT,
              password TEXT)''')


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


window = tk.Tk()
window.title("Quản lý mật khẩu")

# Labels
password_label = tk.Label(window, text="Mật khẩu:")
service_label = tk.Label(window, text="Dịch vụ:")
username_label = tk.Label(window, text="Tên đăng nhập:")

# Entries
password_entry = tk.Entry(window, show="*")  # Hide password characters
service_entry = tk.Entry(window)
username_entry = tk.Entry(window)

tree = ttk.Treeview(window, columns=("service", "username", "password", "action"), style="Treeview")  # Định nghĩa các cột
tree.heading("service", text="Dịch vụ")
tree.heading("username", text="Tên đăng nhập")
tree.heading("password", text="Mật khẩu")
tree.heading("action", text = "Xóa")
tree.column("action", width = 100)  # Điều chỉnh độ rộng cột "Xóa"
tree.column("#0", width = 0, stretch = "no")


def show_passwords():
    # Clear existing items in the Treeview before adding new data
    tree.delete(*tree.get_children())

    c.execute("SELECT service, username, password FROM passwords")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", tk.END, values = row)


def add_password():
    hashed_password = hash_password(password_entry.get())

    # Validate entries before saving
    if not service_entry.get() or not username_entry.get() or not password_entry.get():
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        return

    # Insert data into database
    c.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
              (service_entry.get(), username_entry.get(), hashed_password))
    conn.commit()
    messagebox.showinfo("Thông báo", "Mật khẩu đã được thêm!")

    show_passwords()

    # Clear entries after saving
    service_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)


# Hàm xóa mật khẩu
def delete_password(event):
    tree_selection = tree.selection()
    if len(tree_selection) == 0:
        return
    selected_item = tree_selection[0]
    service = tree.item(selected_item)['values'][0]

    # Xác nhận xóa
    result = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa mật khẩu này?")
    if result:
        c.execute("DELETE FROM passwords WHERE service = ?", (service,))
        conn.commit()
        # Xóa item khỏi Treeview
        tree.delete(selected_item)


# Liên kết sự kiện click vào nút xóa
def on_tree_click(event):
    column = tree.identify_column(event.x)
    if column == "#4":  # Nếu click vào cột "delete"
        delete_password(event)

# Button
save_btn = tk.Button(window, text="Lưu", command=add_password)
tree.bind("<Button-1>", on_tree_click)

# Grid layout with improved formatting
service_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
service_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W + tk.E)
username_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
username_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W + tk.E)
password_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
password_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W + tk.E)
save_btn.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W + tk.E)
tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W + tk.E)

show_passwords()

# Close connection at the end of the program
window.mainloop()
conn.close()
