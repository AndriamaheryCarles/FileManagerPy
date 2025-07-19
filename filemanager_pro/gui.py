import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from file_operations import *
from utils import list_drives

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("🗂 Explorateur de fichiers")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f0f0")

        # Style ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=('Segoe UI', 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.configure("TButton", padding=6, relief="flat", background="#ddd")
        style.configure("TCombobox", padding=4)

        self.clipboard = None
        self.current_path = None

        top_frame = tk.Frame(root, bg="#f0f0f0")
        top_frame.pack(fill="x", padx=10, pady=10)

        self.drive_combo = ttk.Combobox(top_frame, values=list_drives(), state="readonly", width=15)
        self.drive_combo.pack(side="left", padx=(0, 10))
        self.drive_combo.bind("<<ComboboxSelected>>", self.on_drive_change)

        self.path_label = tk.Label(top_frame, text="", anchor='w', bg="white", relief="sunken", height=2)
        self.path_label.pack(fill="x", expand=True)

        # Buttons
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        buttons = [
            ("⬅️ Retour", self.go_back),
            ("📋 Copier", self.copy_selected),
            ("📥 Coller", self.paste_file),
            ("🗑 Supprimer", self.delete_selected),
            ("✏️ Renommer", self.rename_selected),
            ("📁 Nouveau dossier", self.create_new_folder),
        ]

        for (text, command) in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side="left", padx=5)

        # Treeview
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(tree_frame, columns=("fullpath", "type"), displaycolumns=(), selectmode='browse')
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Charger le disque par défaut
        default_drive = self.drive_combo['values'][0] if self.drive_combo['values'] else "/"
        self.load_directory(default_drive)

    def load_directory(self, path):
        try:
            self.tree.delete(*self.tree.get_children())
            self.current_path = path
            self.path_label.config(text=path)

            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                item_type = "dossier" if os.path.isdir(full_path) else "fichier"
                self.tree.insert("", "end", text=item, values=(full_path, item_type))
        except PermissionError:
            messagebox.showwarning("Accès refusé", f"Vous n'avez pas la permission d'accéder à :\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def on_drive_change(self, event):
        selected = self.drive_combo.get()
        self.load_directory(selected)

    def on_double_click(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            full_path, item_type = self.tree.item(selected_item, "values")
            if item_type == "dossier":
                self.load_directory(full_path)

    def go_back(self):
        if not self.current_path:
            return
        parent = os.path.dirname(self.current_path.rstrip("\\/"))
        if parent and parent != self.current_path:
            self.load_directory(parent)

    def get_selected_path(self):
        selected = self.tree.focus()
        if not selected:
            return None, None
        return self.tree.item(selected, "values")

    def copy_selected(self):
        path, _ = self.get_selected_path()
        if path:
            self.clipboard = path
            messagebox.showinfo("Copié", f"{os.path.basename(path)} copié.")

    def paste_file(self):
        if not self.clipboard:
            return
        try:
            filename = os.path.basename(self.clipboard)
            dst = os.path.join(self.current_path, filename)
            if os.path.isdir(self.clipboard):
                shutil.copytree(self.clipboard, dst)
            else:
                copy_file(self.clipboard, dst)
            self.load_directory(self.current_path)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete_selected(self):
        path, _ = self.get_selected_path()
        if path:
            if messagebox.askyesno("Confirmer", f"Supprimer {os.path.basename(path)} ?"):
                delete_path(path)
                self.load_directory(self.current_path)

    def rename_selected(self):
        path, _ = self.get_selected_path()
        if path:
            new_name = simpledialog.askstring("Renommer", "Nouveau nom :")
            if new_name:
                new_path = os.path.join(os.path.dirname(path), new_name)
                rename_path(path, new_path)
                self.load_directory(self.current_path)

    def create_new_folder(self):
        name = simpledialog.askstring("Nouveau dossier", "Nom du dossier :")
        if name:
            path = os.path.join(self.current_path, name)
            create_folder(path)
            self.load_directory(self.current_path)
