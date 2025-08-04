import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil
from PIL import Image, ImageTk

if not os.path.exists("profile_pics"):
    os.makedirs("profile_pics")

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute('''
    create table if not exists users (
        id int primary key autoincrement,
        role text,
        fname text,
        lname text,
        profile_pic text,
        username text unique,
        email text,
        password text,
        address text
    )
''')
conn.commit()

# SignUp window
def signup_window(selected_role):
    def browse_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            profile_pic_path.set(file_path)

    def submit_signup():
        if password.get() != confirm_password.get():
            messagebox.showerror("Input Error", "Passwords do not match!")
            return
        try:
            dest_path = os.path.join("profile_pics", os.path.basename(profile_pic_path.get()))
            shutil.copy(profile_pic_path.get(), dest_path)

            address = f"{line1.get()}, {city.get()}, {state.get()}, {pincode.get()}"
            cursor.execute('''
                INSERT INTO users (role, fname, lname, profile_pic, username, email, password, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (selected_role, fname.get(), lname.get(), dest_path, username.get(), email.get(), password.get(), address))
            conn.commit()
            messagebox.showinfo("Success", "Signup successful!")
            signup.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        except Exception as e:
            messagebox.showerror("Error Msg", str(e))

    signup = tk.Toplevel(root)
    signup.title("Signup")
    signup.geometry("800x600")
    signup.configure(bg="lavender blush")

    def on_close():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit this page?"):
            signup.destroy()

    signup.protocol("WM_DELETE_WINDOW", on_close)

    fname, lname, username, email = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
    password, confirm_password = tk.StringVar(), tk.StringVar()
    profile_pic_path = tk.StringVar()
    line1, city, state, pincode = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()

    tk.Label(signup, text="SIGNUP FORM", font=("Arial", 16), bg="lavender blush").pack(pady=10)

    for label, var, is_pass in [
        ("First Name", fname, False),
        ("Last Name", lname, False),
        ("Profile Picture", profile_pic_path, False),
        ("Username", username, False),
        ("Email", email, False),
        ("Password", password, True),
        ("Confirm Password", confirm_password, True),
        ("Address Line 1", line1, False),
        ("City", city, False),
        ("State", state, False),
        ("Pincode", pincode, False)
    ]:
        tk.Label(signup, text=label, bg="lavender blush").pack()
        if label == "Profile Picture":
            tk.Entry(signup, textvariable=var, state='readonly').pack()
            tk.Button(signup, text="Browse", command=browse_file).pack()
        else:
            tk.Entry(signup, textvariable=var, show="*" if is_pass else None).pack()

    tk.Button(signup, text="Submit", width=15, height=2, command=submit_signup).pack(pady=10)


# Login Page
def login_window(selected_role):
    def submit_login():
        cursor.execute("select * from users where username=? and password=? and role=?",
                       (username.get(), password.get(), selected_role))
        user = cursor.fetchone()
        if user:
            login.destroy()
            show_dashboard(user)
        else:
            messagebox.showerror("Error", f"Invalid credentials for {selected_role}!")

    login = tk.Toplevel(root)
    login.title("Login")
    login.geometry("500x300")
    login.configure(bg="misty rose")

    def on_close():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit this page?"):
            login.destroy()

    login.protocol("WM_DELETE_WINDOW", on_close)

    username, password = tk.StringVar(), tk.StringVar()
    tk.Label(login, text=f"{selected_role} Login", font=("Arial", 16), bg="misty rose").pack(pady=10)

    tk.Label(login, text="Username", bg="misty rose").pack(pady=5)
    tk.Entry(login, textvariable=username).pack()
    tk.Label(login, text="Password", bg="misty rose").pack(pady=5)
    tk.Entry(login, textvariable=password, show="*").pack()
    tk.Button(login, text="Login", width=10, height=2, command=submit_login).pack(pady=10)


#Dashboard page
def show_dashboard(user):
    dashboard = tk.Toplevel(root)
    dashboard.title(f"{user[1]} Dashboard")
    dashboard.geometry("500x400")
    dashboard.configure(bg="honeydew")

    def on_close():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit this page?"):
            dashboard.destroy()

    dashboard.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(dashboard, text=f"{user[1]} Dashboard", font=("Arial", 16), bg="honeydew").pack(pady=10)
    tk.Label(dashboard, text=f"Name: {user[2]} {user[3]}", bg="honeydew").pack()
    tk.Label(dashboard, text=f"Username: {user[5]}", bg="honeydew").pack()
    tk.Label(dashboard, text=f"Email: {user[6]}", bg="honeydew").pack()
    tk.Label(dashboard, text=f"Address: {user[8]}", bg="honeydew").pack()

    if os.path.exists(user[4]):
        img = Image.open(user[4])
        img = img.resize((100, 100))
        img = ImageTk.PhotoImage(img)
        panel = tk.Label(dashboard, image=img, bg="honeydew")
        panel.image = img
        panel.pack(pady=10)


#Role selection page
def open_role_selection(action_type):
    def proceed(role_selected):
        role_win.destroy()
        if action_type == "Signup":
            signup_window(role_selected)
        else:
            login_window(role_selected)

    role_win = tk.Toplevel(root)
    role_win.title("Select Role")
    role_win.geometry("500x300")
    role_win.configure(bg="light cyan")

    def on_close():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit this page?"):
            role_win.destroy()

    role_win.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(role_win, text="Continue as:", font=("Arial", 18), bg="light cyan").pack(pady=15)
    tk.Button(role_win, text="Patient", width=25, height=2, command=lambda: proceed("Patient")).pack(pady=10)
    tk.Button(role_win, text="Doctor", width=25, height=2, command=lambda: proceed("Doctor")).pack(pady=10)


#Main Page
root = tk.Tk()
root.title("User Login App")
root.geometry("500x300")
root.configure(bg="MediumPurple1")

def on_close():
    if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit the application?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(root, text="Welcome", font=("Arial", 25), bg="MediumPurple1").pack(pady=30)
tk.Button(root, text="Signup", font=("Arial", 14), width=20, height=2, command=lambda: open_role_selection("Signup")).pack(pady=10)
tk.Button(root, text="Login", font=("Arial", 14), width=20, height=2, command=lambda: open_role_selection("Login")).pack(pady=10)

root.mainloop()
