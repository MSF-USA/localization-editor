from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import copy

from clients.oai import generate_localization_object
import openai  # Make sure openai is installed

class LocalizationEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Localization Editor")
        self.geometry("800x600")

        self.config_file = 'config.json'
        self.locales_path = os.path.expanduser("~/WebstormProjects/chatbot-ui/public/locales")
        self.locales = {}
        self.all_files = set()
        self.all_keys = {}
        self.unsaved_changes = False

        self.create_widgets()
        self.load_last_folder()  # Load the last opened folder in prev session on startup

    def on_double_click(self, event):
        item = self.table.identify('item', event.x, event.y)
        if item:
            self.edit_value(item)

    def create_widgets(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Locales Folder", command=self.open_locales_folder, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Changes", command=self.save_changes, accelerator="Ctrl+S")
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

        # Bind keyboard shortcuts
        self.bind_all("<Control-o>", lambda event: self.open_locales_folder())
        self.bind_all("<Control-s>", lambda event: self.save_changes())
        self.bind_all("<Control-q>", lambda event: self.quit())

        # Frames
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Treeview for files and locales
        self.tree = ttk.Treeview(self.left_frame)
        self.tree.heading("#0", text="Files")
        self.tree.pack(fill=tk.Y, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_tree_context_menu)  # Right-click context menu

        # Buttons
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=tk.X)
        self.add_file_btn = ttk.Button(btn_frame, text="Add File", command=self.add_file)
        self.add_file_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.add_key_btn = ttk.Button(btn_frame, text="Add Key", command=self.add_key)
        self.add_key_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Table for keys and values
        self.table = ttk.Treeview(self.right_frame, columns=[], show='headings')
        self.table.pack(fill=tk.BOTH, expand=True)
        self.table.bind("<Double-1>", self.on_double_click)
        self.table.bind("<Configure>", self.on_table_configure)
        self.table.bind("<Button-3>", self.show_table_context_menu)  # Right-click context menu

        # Keyboard navigation
        self.table.bind("<Up>", self.on_key_press)
        self.table.bind("<Down>", self.on_key_press)
        self.table.bind("<Return>", lambda event: self.edit_value())

        # Buttons
        table_btn_frame = ttk.Frame(self.right_frame)
        table_btn_frame.pack(fill=tk.X)
        self.edit_value_btn = ttk.Button(table_btn_frame, text="Edit Value", command=self.edit_value)
        self.edit_value_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def load_last_folder(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                last_folder = config.get('last_folder', '')
                if last_folder and os.path.exists(last_folder):
                    self.locales_path = last_folder
                    self.scan_locales()
                    self.populate_tree()

    def save_last_folder(self):
        config = {'last_folder': self.locales_path}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def open_locales_folder(self):
        path = filedialog.askdirectory(title="Select Locales Folder")
        if path:
            self.locales_path = path
            self.save_last_folder()  # Save the selected folder
            self.scan_locales()
            self.populate_tree()

    def scan_locales(self):
        self.locales = {}
        self.all_files = set()
        self.all_keys = {}

        # List of locale directories
        for locale_dir in os.listdir(self.locales_path):
            locale_path = os.path.join(self.locales_path, locale_dir)
            if os.path.isdir(locale_path):
                self.locales[locale_dir] = {}
                # List of JSON files in locale directory
                for file_name in os.listdir(locale_path):
                    if file_name.endswith('.json'):
                        self.all_files.add(file_name)
                        file_path = os.path.join(locale_path, file_name)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.locales[locale_dir][file_name] = data
                            for key in data:
                                self.all_keys.setdefault(key, set()).add(locale_dir)

        # Identify missing files and keys
        for locale in self.locales:
            for file_name in self.all_files:
                if file_name not in self.locales[locale]:
                    self.locales[locale][file_name] = {}
        # Identify all keys across all files
        for file_name in self.all_files:
            for locale in self.locales:
                file_keys = self.locales[locale][file_name].keys()
                for key in file_keys:
                    self.all_keys.setdefault(key, set()).add(locale)
        self.unsaved_changes = False

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for file_name in sorted(self.all_files):
            file_node = self.tree.insert('', 'end', text=file_name, values=(file_name,))
            # Check for missing locales
            missing_locales = [loc for loc in self.locales if file_name not in self.locales[loc]]
            if missing_locales:
                self.tree.item(file_node, tags=('missing',))
                self.tree.tag_configure('missing', foreground='red')

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            file_name = self.tree.item(selected_item[0])['text']
            self.populate_table(file_name)

    def populate_table(self, file_name):
        total_keys = 0
        empty_keys = 0

        # Clear the table
        for col in self.table["columns"]:
            self.table.heading(col, text='')
        self.table.delete(*self.table.get_children())
        self.table["columns"] = []

        # Get list of locales
        locales = sorted(self.locales.keys())
        self.table["columns"] = ['Key'] + locales
        self.table.column('Key', width=200, anchor='w')
        self.table.heading('Key', text='Key')

        for locale in locales:
            self.table.column(locale, width=100, anchor='w')
            self.table.heading(locale, text=locale)

        # Collect all keys in this file across locales
        keys = set()
        for locale in self.locales:
            keys.update(self.locales[locale][file_name].keys())

        for key in sorted(keys):
            values = [key]
            tags = ['row']
            for locale in locales:
                value = self.locales[locale][file_name].get(key, '')
                values.append(value)
                if not value:
                    tags.append(f'empty_{locale}')
                    empty_keys += 1
                total_keys += 1
            item = self.table.insert('', 'end', values=values, tags=tags)

        # Configure tags for empty cells
        self.table.tag_configure('row', background='white')
        for locale in locales:
            self.table.tag_configure(f'empty_{locale}', background='#FFD700')  # Darker yellow

        self.update_statistics(total_keys, empty_keys)

        # Bind the draw callback
        self.table.bind('<Motion>', self.highlight_cell)

    def update_statistics(self, total_keys, empty_keys):
        if hasattr(self, 'stats_label'):
            self.stats_label.destroy()

        filled_keys = total_keys - empty_keys
        completion_percentage = (filled_keys / total_keys) * 100 if total_keys > 0 else 0

        stats_text = f"Total Keys: {total_keys}\n"
        stats_text += f"Filled Keys: {filled_keys}\n"
        stats_text += f"Empty Keys: {empty_keys}\n"
        stats_text += f"Completion: {completion_percentage:.2f}%"

        self.stats_label = ttk.Label(self.right_frame, text=stats_text, justify=tk.LEFT)
        self.stats_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=5)

    def edit_value(self, item: str | int = None):
        if item:
            selected_item = item
        else:
            selected_item = self.table.selection()
            if selected_item:
                selected_item = selected_item[0]
        if selected_item:
            item_values = self.table.item(selected_item)['values']
            key = item_values[0]
            locales = self.table["columns"][1:]

            # Create a dialog to edit values
            editor = tk.Toplevel(self)
            editor.title(f"Edit Value for Key: {key}")

            # Add non-writable field for key
            ttk.Label(editor, text="Key:").grid(row=0, column=0, sticky='w')
            key_entry = ttk.Entry(editor, width=50)
            key_entry.insert(0, key)
            key_entry.config(state='readonly')
            key_entry.grid(row=0, column=1, sticky='w')

            # Add toggle for editing key
            edit_key_var = tk.BooleanVar()
            edit_key_check = ttk.Checkbutton(editor, text="Edit Key", variable=edit_key_var,
                                             command=lambda: key_entry.config(
                                                 state='normal' if edit_key_var.get() else 'readonly'))
            edit_key_check.grid(row=0, column=2, sticky='w')

            entries = {}
            for i, locale in enumerate(locales):
                ttk.Label(editor, text=locale).grid(row=i + 1, column=0, sticky='w')
                value = item_values[i + 1]
                entry = ttk.Entry(editor, width=50)
                entry.insert(0, value)
                entry.grid(row=i + 1, column=1, sticky='w')
                entries[locale] = entry

            # AI localization generation options
            row_offset = len(locales) + 1

            # Separator
            ttk.Separator(editor).grid(row=row_offset, column=0, columnspan=3, pady=10)

            # Use custom phrase checkbox
            use_custom_phrase_var = tk.BooleanVar()
            use_custom_phrase_check = ttk.Checkbutton(editor, text="Use custom phrase for generation",
                                                      variable=use_custom_phrase_var)
            use_custom_phrase_check.grid(row=row_offset + 1, column=0, sticky='w')

            # Custom phrase entry
            ttk.Label(editor, text="Custom Phrase:").grid(row=row_offset + 2, column=0, sticky='w')
            custom_phrase_entry = ttk.Entry(editor, width=50, state='disabled')
            custom_phrase_entry.grid(row=row_offset + 2, column=1, sticky='w')

            # Enable/Disable custom phrase entry based on checkbox
            def toggle_custom_phrase(*args):
                state = 'normal' if use_custom_phrase_var.get() else 'disabled'
                custom_phrase_entry.config(state=state)

            use_custom_phrase_var.trace('w', toggle_custom_phrase)

            # Context entry
            ttk.Label(editor, text="Context (optional):").grid(row=row_offset + 3, column=0, sticky='w')
            context_entry = ttk.Entry(editor, width=50)
            context_entry.grid(row=row_offset + 3, column=1, sticky='w')

            # Generation locale
            ttk.Label(editor, text="Generation Locale:").grid(row=row_offset + 4, column=0, sticky='w')
            gen_locale_entry = ttk.Entry(editor, width=10)
            gen_locale_entry.insert(0, 'en')
            gen_locale_entry.grid(row=row_offset + 4, column=1, sticky='w')

            # Overwrite existing values checkbox
            overwrite_var = tk.BooleanVar(value=False)
            overwrite_check = ttk.Checkbutton(editor, text="Overwrite existing values", variable=overwrite_var)
            overwrite_check.grid(row=row_offset + 5, column=0, sticky='w')

            # Generate Translations button
            def generate_translations():
                phrase = custom_phrase_entry.get() if use_custom_phrase_var.get() else key_entry.get()
                context = context_entry.get()
                gen_locale = gen_locale_entry.get()

                # Ensure OpenAI API key is set
                openai.api_key = os.environ.get('OPENAI_API_KEY')
                if not openai.api_key:
                    messagebox.showerror("API Key Missing", "Please set the OPENAI_API_KEY environment variable.")
                    return

                # Call the AI localization function
                try:
                    generated_translations = generate_localization_object(
                        phrase=phrase,
                        phrase_locale=gen_locale,
                        context=context if context else None
                    )
                    # Update the entries with generated translations
                    for locale in entries:
                        if (overwrite_var.get() or not entries[locale].get()):
                            entries[locale].delete(0, tk.END)
                            entries[locale].insert(0, generated_translations.get(locale, ''))
                    messagebox.showinfo("Success", "Translations generated successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to generate translations:\n{e}")

            gen_button = ttk.Button(editor, text="Generate Translations", command=generate_translations)
            gen_button.grid(row=row_offset + 6, column=0, columnspan=3, pady=5)

            # Save function
            def save():
                new_key = key_entry.get()
                file_name = self.tree.item(self.tree.selection()[0])['text']

                for locale in entries:
                    new_value = entries[locale].get()
                    if new_key != key:
                        # If key has changed, remove old key and add new key
                        self.locales[locale][file_name][new_key] = new_value
                        del self.locales[locale][file_name][key]
                    else:
                        self.locales[locale][file_name][key] = new_value

                self.unsaved_changes = True
                editor.destroy()
                self.populate_table(file_name)

            ttk.Button(editor, text="Save", command=save).grid(row=row_offset + 7, column=0, columnspan=3, pady=10)
        else:
            messagebox.showwarning("No selection", "Please select a key to edit.")


    def add_file(self):
        new_file = tk.simpledialog.askstring("Add File", "Enter new JSON file name (with .json):")
        if new_file:
            if not new_file.endswith('.json'):
                new_file += '.json'
            if new_file in self.all_files:
                messagebox.showwarning("File exists", "This file already exists.")
                return
            # Add empty file to each locale
            for locale in self.locales:
                self.locales[locale][new_file] = {}
            self.all_files.add(new_file)
            self.unsaved_changes = True
            self.populate_tree()

    def add_key(self):
        selected_item = self.tree.selection()
        if selected_item:
            file_name = self.tree.item(selected_item[0])['text']
            new_key = tk.simpledialog.askstring("Add Key", "Enter new key:")
            if new_key:
                # Add key to all locales with empty value
                for locale in self.locales:
                    self.locales[locale][file_name][new_key] = ""
                self.unsaved_changes = True
                self.populate_table(file_name)
        else:
            messagebox.showwarning("No selection", "Please select a file to add a key to.")

    def save_changes(self):
        if not self.unsaved_changes:
            messagebox.showinfo("No changes", "There are no changes to save.")
            return
        for locale in self.locales:
            locale_dir = os.path.join(self.locales_path, locale)
            for file_name in self.locales[locale]:
                file_path = os.path.join(locale_dir, file_name)
                # Create locale directory if it doesn't exist
                if not os.path.exists(locale_dir):
                    os.makedirs(locale_dir)
                # Write JSON data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.locales[locale][file_name], f, ensure_ascii=False, indent=2)
        self.unsaved_changes = False
        messagebox.showinfo("Saved", "Changes have been saved.")

    def highlight_cell(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region == "cell":
            column = self.table.identify_column(event.x)
            row = self.table.identify_row(event.y)

            # Reset the background of all rows
            for item in self.table.get_children():
                self.table.item(item, tags=('row',))

            # Highlight the current row if the cell is empty
            col_index = int(column[1:]) - 1  # Convert column id to index
            cell_value = self.table.item(row, 'values')[col_index]
            if not cell_value:
                self.table.item(row, tags=('row', 'highlight'))

            # Configure styles
            self.table.tag_configure('row', background='white')
            self.table.tag_configure('highlight', background='#FFA500')  # Brighter yellow for hover

    def on_table_configure(self, event):
        self.table.unbind('<Motion>')
        self.table.after(100, lambda: self.table.bind('<Motion>', self.highlight_cell))

    def on_key_press(self, event):
        selected = self.table.selection()
        if not selected:
            # If no selection, select the first item
            items = self.table.get_children()
            if items:
                self.table.selection_set(items[0])
        else:
            index = self.table.index(selected[0])
            if event.keysym == 'Up':
                if index > 0:
                    self.table.selection_set(self.table.get_children()[index - 1])
            elif event.keysym == 'Down':
                if index < len(self.table.get_children()) - 1:
                    self.table.selection_set(self.table.get_children()[index + 1])
        self.table.focus(self.table.selection())

    def show_tree_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        self.tree.selection_set(selected_item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Add File", command=self.add_file)
        menu.add_command(label="Add Key to File", command=self.add_key)
        menu.post(event.x_root, event.y_root)

    def show_table_context_menu(self, event):
        selected_item = self.table.identify_row(event.y)
        self.table.selection_set(selected_item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit Value", command=self.edit_value)
        menu.post(event.x_root, event.y_root)




if __name__ == "__main__":
    app = LocalizationEditor()
    app.mainloop()