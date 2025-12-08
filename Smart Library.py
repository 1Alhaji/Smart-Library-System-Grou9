import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, timedelta


class SmartLibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartLibrary Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f2f5')

        self.conn = None
        self.current_user = None
        self.current_role = None

        self.setup_styles()
        self.show_login()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f2f5')
        style.configure('TLabel', background='#f0f2f5', font=('Arial', 10))
        style.configure('Treeview', font=('Arial', 9), rowheight=30)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                dbname="smartlibrary",
                user="postgres",
                password="Alhaji2007",  # Change this
                host="localhost",
                port="5432"
            )
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Connection failed:\n{str(e)}")
            return False

    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(self.root, bg='#ffffff', padx=50, pady=50)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(login_frame, text="SmartLibrary", font=('Arial', 28, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=(0, 10))
        tk.Label(login_frame, text="Library Management System",
                 font=('Arial', 12), bg='#ffffff', fg='#7f8c8d').pack(pady=(0, 40))

        tk.Label(login_frame, text="Username:", bg='#ffffff',
                 font=('Arial', 11)).pack(anchor='w', pady=(10, 5))
        username_entry = ttk.Entry(login_frame, width=35, font=('Arial', 11))
        username_entry.pack(pady=(0, 15))

        tk.Label(login_frame, text="Password:", bg='#ffffff',
                 font=('Arial', 11)).pack(anchor='w', pady=(0, 5))
        password_entry = ttk.Entry(login_frame, width=35, show='●', font=('Arial', 11))
        password_entry.pack(pady=(0, 30))

        def attempt_login():
            if self.login(username_entry.get(), password_entry.get()):
                self.show_main_interface()
            else:
                messagebox.showerror("Error", "Invalid credentials")

        login_btn = tk.Button(login_frame, text="Login", command=attempt_login,
                              bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                              padx=60, pady=12, cursor='hand2', bd=0)
        login_btn.pack()

        password_entry.bind('<Return>', lambda e: attempt_login())

        tk.Label(login_frame, text="Demo: admin / password123",
                 font=('Arial', 9), bg='#ffffff', fg='#95a5a6').pack(pady=(25, 0))

    def login(self, username, password):
        if not username or not password:
            return False

        if not self.connect_db():
            return False

        try:
            cursor = self.conn.cursor()
            # Simplified query without crypt
            cursor.execute("""
                SELECT u.id, u.name, r.name 
                FROM users u JOIN roles r ON u.role_id = r.id 
                WHERE u.username = %s
            """, (username,))

            result = cursor.fetchone()
            if result:
                user_id, name, role = result
                # For testing: store passwords as plain text
                # This is NOT secure - only for testing!
                self.current_user = {'id': user_id, 'name': name, 'username': username}
                self.current_role = role
                cursor.close()
                return True

            cursor.close()
            return False
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def show_main_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_container = tk.Frame(self.root, bg='#f0f2f5')
        main_container.pack(fill='both', expand=True)

        self.create_sidebar(main_container)

        self.content_frame = tk.Frame(main_container, bg='#ffffff')
        self.content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        self.show_dashboard()

    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg='#2c3e50', width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        user_frame = tk.Frame(sidebar, bg='#34495e', pady=20)
        user_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(user_frame, text=self.current_user['name'], bg='#34495e',
                 fg='white', font=('Arial', 13, 'bold')).pack()
        tk.Label(user_frame, text=self.current_role, bg='#34495e',
                 fg='#bdc3c7', font=('Arial', 10)).pack()

        nav_items = [
            ('Dashboard', self.show_dashboard),
            ('Books', self.show_books),
            ('Members', self.show_members),
            ('Loans', self.show_loans),
            ('Authors', self.show_authors),
            ('Book Clubs', self.show_book_clubs),
        ]

        for text, command in nav_items:
            btn = tk.Button(sidebar, text=text, command=command, bg='#2c3e50',
                            fg='white', font=('Arial', 11), bd=0, pady=15,
                            cursor='hand2', anchor='w', padx=25)
            btn.pack(fill='x')
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#1a252f'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#2c3e50'))

        tk.Button(sidebar, text="Logout", command=self.logout, bg='#e74c3c',
                  fg='white', font=('Arial', 11, 'bold'), bd=0, pady=15,
                  cursor='hand2').pack(side='bottom', fill='x', padx=10, pady=10)

    def show_dashboard(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Dashboard", font=('Arial', 26, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=20, anchor='w', padx=20)

        stats_frame = tk.Frame(self.content_frame, bg='#ffffff')
        stats_frame.pack(fill='x', padx=20, pady=10)

        try:
            cursor = self.conn.cursor()
            stats_queries = [
                ("Total Books", "SELECT COUNT(*) FROM books", "#27ae60"),
                ("Available", "SELECT COUNT(*) FROM books WHERE available = TRUE", "#3498db"),
                ("Members", "SELECT COUNT(*) FROM members", "#f39c12"),
                ("Active Loans", "SELECT COUNT(*) FROM loans WHERE status = 'Active'", "#9b59b6"),
                ("Overdue", "SELECT COUNT(*) FROM loans WHERE status = 'Overdue'", "#e74c3c"),
            ]

            for i, (label, query, color) in enumerate(stats_queries):
                cursor.execute(query)
                value = cursor.fetchone()[0]

                card = tk.Frame(stats_frame, bg=color, padx=25, pady=18)
                card.grid(row=0, column=i, padx=8, sticky='ew')
                stats_frame.columnconfigure(i, weight=1)

                tk.Label(card, text=str(value), font=('Arial', 32, 'bold'),
                         bg=color, fg='white').pack()
                tk.Label(card, text=label, font=('Arial', 10),
                         bg=color, fg='white').pack()

            cursor.close()

            # Recent loans
            recent_frame = tk.LabelFrame(self.content_frame, text="Recent Loans",
                                         font=('Arial', 14, 'bold'), bg='#ffffff',
                                         padx=20, pady=15)
            recent_frame.pack(fill='both', expand=True, padx=20, pady=20)

            columns = ('ID', 'Book', 'Member', 'Due Date', 'Status')
            tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=12)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)

            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT l.id, b.title, u.name, l.due_date, l.status
                FROM loans l
                JOIN books b ON l.book_id = b.id
                JOIN members m ON l.member_id = m.id
                JOIN users u ON m.user_id = u.id
                WHERE l.status IN ('Active', 'Overdue')
                ORDER BY l.due_date
                LIMIT 15
            """)

            for loan in cursor.fetchall():
                tag = 'overdue' if loan[4] == 'Overdue' else 'active'
                tree.insert('', 'end', values=loan, tags=(tag,))

            cursor.close()

            tree.tag_configure('overdue', background='#fadbd8')
            tree.tag_configure('active', background='#d5f4e6')

            scrollbar = ttk.Scrollbar(recent_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_books(self):
        self.clear_content()

        header_frame = tk.Frame(self.content_frame, bg='#ffffff')
        header_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(header_frame, text="Books Management", font=('Arial', 26, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(side='left')

        if self.current_role == 'Librarian':
            tk.Button(header_frame, text="+ Add Book", command=self.add_book_dialog,
                      bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                      padx=20, pady=8, cursor='hand2', bd=0).pack(side='right', padx=5)

        tk.Button(header_frame, text="↻ Refresh", command=self.show_books,
                  bg='#3498db', fg='white', font=('Arial', 10),
                  padx=20, pady=8, cursor='hand2', bd=0).pack(side='right')

        # Search
        search_frame = tk.Frame(self.content_frame, bg='#ffffff')
        search_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(search_frame, text="Search:", bg='#ffffff',
                 font=('Arial', 10)).pack(side='left', padx=(0, 10))

        search_entry = ttk.Entry(search_frame, font=('Arial', 10), width=40)
        search_entry.pack(side='left')

        tk.Button(search_frame, text="Search",
                  command=lambda: self.load_books(search_entry.get()),
                  bg='#3498db', fg='white', font=('Arial', 10),
                  padx=15, pady=5, cursor='hand2', bd=0).pack(side='left', padx=10)

        # Table
        table_frame = tk.Frame(self.content_frame, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Title', 'ISBN', 'Author', 'Genre', 'Available')
        self.books_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        self.books_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        if self.current_role == 'Librarian':
            action_frame = tk.Frame(self.content_frame, bg='#ffffff')
            action_frame.pack(fill='x', padx=20, pady=10)

            tk.Button(action_frame, text="Delete Selected", command=self.delete_book,
                      bg='#e74c3c', fg='white', font=('Arial', 10),
                      padx=20, pady=8, cursor='hand2', bd=0).pack(side='left', padx=5)

        self.load_books()

    def load_books(self, search=''):
        try:
            cursor = self.conn.cursor()
            if search:
                cursor.execute("""
                    SELECT b.id, b.title, b.isbn, a.name, b.genre, b.available
                    FROM books b LEFT JOIN authors a ON b.author_id = a.id
                    WHERE b.title ILIKE %s OR b.isbn ILIKE %s OR a.name ILIKE %s
                    ORDER BY b.title
                """, (f'%{search}%', f'%{search}%', f'%{search}%'))
            else:
                cursor.execute("""
                    SELECT b.id, b.title, b.isbn, a.name, b.genre, b.available
                    FROM books b LEFT JOIN authors a ON b.author_id = a.id
                    ORDER BY b.title
                """)

            for item in self.books_tree.get_children():
                self.books_tree.delete(item)

            for book in cursor.fetchall():
                data = list(book)
                data[5] = 'Yes' if book[5] else 'No'
                tag = 'available' if book[5] else 'borrowed'
                self.books_tree.insert('', 'end', values=data, tags=(tag,))

            self.books_tree.tag_configure('available', background='#d5f4e6')
            self.books_tree.tag_configure('borrowed', background='#fadbd8')

            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("500x500")
        dialog.configure(bg='#ffffff')
        dialog.transient(self.root)
        dialog.grab_set()

        frame = tk.Frame(dialog, bg='#ffffff', padx=30, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Add New Book", font=('Arial', 20, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=(0, 25))

        tk.Label(frame, text="Title:", bg='#ffffff').pack(anchor='w', pady=(10, 5))
        title_entry = ttk.Entry(frame, font=('Arial', 10), width=45)
        title_entry.pack(fill='x')

        tk.Label(frame, text="ISBN:", bg='#ffffff').pack(anchor='w', pady=(10, 5))
        isbn_entry = ttk.Entry(frame, font=('Arial', 10), width=45)
        isbn_entry.pack(fill='x')

        tk.Label(frame, text="Genre:", bg='#ffffff').pack(anchor='w', pady=(10, 5))
        genre_entry = ttk.Entry(frame, font=('Arial', 10), width=45)
        genre_entry.pack(fill='x')

        tk.Label(frame, text="Author:", bg='#ffffff').pack(anchor='w', pady=(10, 5))

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name FROM authors ORDER BY name")
            authors = cursor.fetchall()
            cursor.close()

            author_var = tk.StringVar()
            author_combo = ttk.Combobox(frame, textvariable=author_var,
                                        font=('Arial', 10), width=43)
            author_combo['values'] = [f"{a[0]} - {a[1]}" for a in authors]
            author_combo.pack(fill='x')
        except:
            dialog.destroy()
            return

        def save():
            if not all([title_entry.get(), isbn_entry.get(), author_var.get()]):
                messagebox.showwarning("Error", "Fill all fields")
                return

            try:
                author_id = int(author_var.get().split(' - ')[0])
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO books (title, isbn, genre, author_id, available)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (title_entry.get(), isbn_entry.get(), genre_entry.get(), author_id))
                self.conn.commit()
                cursor.close()
                messagebox.showinfo("Success", "Book added!")
                dialog.destroy()
                self.show_books()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", str(e))

        btn_frame = tk.Frame(frame, bg='#ffffff')
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Save", command=save, bg='#27ae60',
                  fg='white', font=('Arial', 11, 'bold'),
                  padx=30, pady=10, cursor='hand2', bd=0).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                  bg='#95a5a6', fg='white', font=('Arial', 11),
                  padx=30, pady=10, cursor='hand2', bd=0).pack(side='left', padx=5)

    def delete_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a book")
            return

        book_id = self.books_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Confirm", "Delete this book?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                self.conn.commit()
                cursor.close()
                messagebox.showinfo("Success", "Book deleted!")
                self.show_books()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", str(e))

    def show_members(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Members", font=('Arial', 26, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=20, anchor='w', padx=20)

        table_frame = tk.Frame(self.content_frame, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Student ID', 'Name', 'Email', 'Contact', 'Active Loans')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT m.id, m.student_id, u.name, u.email, m.contact,
                       (SELECT COUNT(*) FROM loans WHERE member_id = m.id AND status = 'Active')
                FROM members m JOIN users u ON m.user_id = u.id
                ORDER BY m.student_id
            """)
            for member in cursor.fetchall():
                tree.insert('', 'end', values=member)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_loans(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Loans", font=('Arial', 26, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=20, anchor='w', padx=20)

        table_frame = tk.Frame(self.content_frame, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Book', 'Member', 'Borrow', 'Due', 'Return', 'Status')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT l.id, b.title, u.name, l.borrow_date, l.due_date, l.return_date, l.status
                FROM loans l
                JOIN books b ON l.book_id = b.id
                JOIN members m ON l.member_id = m.id
                JOIN users u ON m.user_id = u.id
                ORDER BY l.borrow_date DESC
            """)
            for loan in cursor.fetchall():
                tree.insert('', 'end', values=loan)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_authors(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Authors", font=('Arial', 26, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=20, anchor='w', padx=20)

        table_frame = tk.Frame(self.content_frame, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Name', 'Bio')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, bio FROM authors ORDER BY name")
            for author in cursor.fetchall():
                tree.insert('', 'end', values=author)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_book_clubs(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Book Clubs", font=('Arial', 26, 'bold'),
                 bg='#ffffff', fg='#2c3e50').pack(pady=20, anchor='w', padx=20)

        table_frame = tk.Frame(self.content_frame, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Name', 'Description', 'Members')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT bc.id, bc.name, bc.description,
                       (SELECT COUNT(*) FROM book_club_members WHERE club_id = bc.id)
                FROM book_clubs bc
                ORDER BY bc.name
            """)
            for club in cursor.fetchall():
                tree.insert('', 'end', values=club)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def logout(self):
        if self.conn:
            self.conn.close()
        self.current_user = None
        self.current_role = None
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartLibraryGUI(root)
    root.mainloop()