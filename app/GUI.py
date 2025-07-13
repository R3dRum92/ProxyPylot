import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from filter import ContentFilter


class ContentFilterGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize the content filter
        self.content_filter = ContentFilter()

        # Configure the main window
        self.title("Content Filter Manager")
        self.geometry("1000x700")
        self.resizable(True, True)

        # Current view tracking
        self.current_view = "domains"

        # Create the main interface
        self.create_widgets()

    def create_widgets(self):
        # Sidebar Frame - seamless with main window
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color="transparent"
        )
        self.sidebar.pack(side="left", fill="y")

        # Sidebar Title
        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="Content Filter",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1f6aa5",
        )
        self.title_label.pack(pady=(20, 40))

        # Sidebar Buttons
        self.domains_btn = ctk.CTkButton(
            self.sidebar,
            text="🚫  Blocked Domains",
            anchor="w",
            fg_color="transparent",
            hover_color=("#3B8ED0", "#1F6AA5"),
            command=lambda: self.switch_view("domains"),
        )
        self.domains_btn.pack(fill="x", pady=5, padx=10)

        self.keywords_btn = ctk.CTkButton(
            self.sidebar,
            text="🔒  Blocked Keywords",
            anchor="w",
            fg_color="transparent",
            hover_color=("#3B8ED0", "#1F6AA5"),
            command=lambda: self.switch_view("keywords"),
        )
        self.keywords_btn.pack(fill="x", pady=5, padx=10)

        self.test_btn = ctk.CTkButton(
            self.sidebar,
            text="🧪  Test Filter",
            anchor="w",
            fg_color="transparent",
            hover_color=("#3B8ED0", "#1F6AA5"),
            command=lambda: self.switch_view("test"),
        )
        self.test_btn.pack(fill="x", pady=5, padx=10)

        # Main content area - seamless with main window
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content.pack(expand=True, fill="both", padx=20, pady=20)

        # Initial view
        self.switch_view("domains")

    def switch_view(self, view_name):
        """Switch between different views in the main content area."""
        self.current_view = view_name

        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Update sidebar button colors
        self.update_sidebar_buttons()

        # Show the selected view
        if view_name == "domains":
            self.show_domains_view()
        elif view_name == "keywords":
            self.show_keywords_view()
        elif view_name == "test":
            self.show_test_view()

    def update_sidebar_buttons(self):
        """Update sidebar button colors based on current view."""
        buttons = {
            "domains": self.domains_btn,
            "keywords": self.keywords_btn,
            "test": self.test_btn,
        }

        for view, button in buttons.items():
            if view == self.current_view:
                button.configure(fg_color=("#3B8ED0", "#1F6AA5"))
            else:
                button.configure(fg_color="transparent")

    def show_domains_view(self):
        """Display the blocked domains view."""
        # Header
        header_label = ctk.CTkLabel(
            self.main_content,
            text="Blocked Domains Management",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header_label.pack(pady=(20, 30))

        # Add new domain section - seamless background
        add_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            add_frame, text="Add New Domain:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        entry_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(0, 10))

        self.domain_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Enter domain to block (e.g., example.com)",
            height=35,
        )
        self.domain_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        add_domain_btn = ctk.CTkButton(
            entry_frame,
            text="Add Domain",
            width=120,
            height=35,
            command=self.add_domain,
        )
        add_domain_btn.pack(side="right")

        # Domains list section
        list_label = ctk.CTkLabel(
            self.main_content,
            text="Currently Blocked Domains:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        list_label.pack(anchor="w", padx=20, pady=(20, 10))

        # Scrollable frame for domains - subtle background
        self.domains_scrollable = ctk.CTkScrollableFrame(
            self.main_content, fg_color=("gray90", "gray15"), corner_radius=8
        )
        self.domains_scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.update_domains_list()

    def show_keywords_view(self):
        """Display the blocked keywords view."""
        # Header
        header_label = ctk.CTkLabel(
            self.main_content,
            text="Blocked Keywords Management",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header_label.pack(pady=(20, 30))

        # Add new keyword section - seamless background
        add_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            add_frame, text="Add New Keyword:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        entry_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(0, 10))

        self.keyword_entry = ctk.CTkEntry(
            entry_frame, placeholder_text="Enter keyword to block", height=35
        )
        self.keyword_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        add_keyword_btn = ctk.CTkButton(
            entry_frame,
            text="Add Keyword",
            width=120,
            height=35,
            command=self.add_keyword,
        )
        add_keyword_btn.pack(side="right")

        # Keywords list section
        list_label = ctk.CTkLabel(
            self.main_content,
            text="Currently Blocked Keywords:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        list_label.pack(anchor="w", padx=20, pady=(20, 10))

        # Scrollable frame for keywords - subtle background
        self.keywords_scrollable = ctk.CTkScrollableFrame(
            self.main_content, fg_color=("gray90", "gray15"), corner_radius=8
        )
        self.keywords_scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.update_keywords_list()

    def show_test_view(self):
        """Display the test filter view."""
        # Header
        header_label = ctk.CTkLabel(
            self.main_content,
            text="Test Content Filter",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header_label.pack(pady=(20, 30))

        # Domain test section - seamless background
        domain_test_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        domain_test_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            domain_test_frame,
            text="Test Domain:",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        domain_entry_frame = ctk.CTkFrame(domain_test_frame, fg_color="transparent")
        domain_entry_frame.pack(fill="x", pady=(0, 10))

        self.test_domain_entry = ctk.CTkEntry(
            domain_entry_frame,
            placeholder_text="Enter domain to test (e.g., example.com)",
            height=35,
        )
        self.test_domain_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        test_domain_btn = ctk.CTkButton(
            domain_entry_frame,
            text="Test Domain",
            width=120,
            height=35,
            command=self.test_domain,
        )
        test_domain_btn.pack(side="right")

        # Content test section - seamless background
        content_test_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_test_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            content_test_frame,
            text="Test Content:",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.test_content_text = ctk.CTkTextbox(
            content_test_frame,
            height=120,
            corner_radius=8,
            placeholder_text="Enter content to test for blocked keywords...",
        )
        self.test_content_text.pack(fill="both", expand=True, pady=(0, 15))

        test_content_btn = ctk.CTkButton(
            content_test_frame,
            text="Test Content",
            width=120,
            height=35,
            command=self.test_content,
        )
        test_content_btn.pack()

        # Results area - seamless background
        results_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        results_frame.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(
            results_frame,
            text="Test Results:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.results_label = ctk.CTkLabel(
            results_frame,
            text="No tests performed yet...",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.results_label.pack(anchor="w")

    def update_domains_list(self):
        """Update the domains list display."""
        # Clear existing items
        for widget in self.domains_scrollable.winfo_children():
            widget.destroy()

        # Display domains
        for domain in self.content_filter.blocked_domains:
            domain_frame = ctk.CTkFrame(
                self.domains_scrollable, fg_color=("gray85", "gray20"), corner_radius=6
            )
            domain_frame.pack(fill="x", pady=3, padx=5)

            domain_label = ctk.CTkLabel(
                domain_frame,
                text=f"🚫  {domain}",
                font=ctk.CTkFont(size=14),
                anchor="w",
            )
            domain_label.pack(side="left", padx=15, pady=12)

            # Remove button
            remove_btn = ctk.CTkButton(
                domain_frame,
                text="Remove",
                width=80,
                height=30,
                command=lambda d=domain: self.remove_domain(d),
            )
            remove_btn.pack(side="right", padx=15, pady=12)

    def update_keywords_list(self):
        """Update the keywords list display."""
        # Clear existing items
        for widget in self.keywords_scrollable.winfo_children():
            widget.destroy()

        # Display keywords
        for keyword in self.content_filter.blocked_keywords:
            keyword_frame = ctk.CTkFrame(
                self.keywords_scrollable, fg_color=("gray85", "gray20"), corner_radius=6
            )
            keyword_frame.pack(fill="x", pady=3, padx=5)

            keyword_label = ctk.CTkLabel(
                keyword_frame,
                text=f"🔒  {keyword}",
                font=ctk.CTkFont(size=14),
                anchor="w",
            )
            keyword_label.pack(side="left", padx=15, pady=12)

            # Remove button
            remove_btn = ctk.CTkButton(
                keyword_frame,
                text="Remove",
                width=80,
                height=30,
                command=lambda k=keyword: self.remove_keyword(k),
            )
            remove_btn.pack(side="right", padx=15, pady=12)

    def add_domain(self):
        domain = self.domain_entry.get().strip()
        if domain and domain not in self.content_filter.blocked_domains:
            self.content_filter.blocked_domains.append(domain)
            self.domain_entry.delete(0, "end")
            self.update_domains_list()
            messagebox.showinfo("Success", f"Domain '{domain}' added to blocked list!")
        elif domain in self.content_filter.blocked_domains:
            messagebox.showwarning("Warning", "Domain already in blocked list!")
        else:
            messagebox.showwarning("Warning", "Please enter a valid domain!")

    def remove_domain(self, domain):
        if domain in self.content_filter.blocked_domains:
            self.content_filter.blocked_domains.remove(domain)
            self.update_domains_list()
            messagebox.showinfo(
                "Success", f"Domain '{domain}' removed from blocked list!"
            )

    def add_keyword(self):
        keyword = self.keyword_entry.get().strip()
        if keyword and keyword not in self.content_filter.blocked_keywords:
            self.content_filter.blocked_keywords.append(keyword)
            self.keyword_entry.delete(0, "end")
            self.update_keywords_list()
            messagebox.showinfo(
                "Success", f"Keyword '{keyword}' added to blocked list!"
            )
        elif keyword in self.content_filter.blocked_keywords:
            messagebox.showwarning("Warning", "Keyword already in blocked list!")
        else:
            messagebox.showwarning("Warning", "Please enter a valid keyword!")

    def remove_keyword(self, keyword):
        if keyword in self.content_filter.blocked_keywords:
            self.content_filter.blocked_keywords.remove(keyword)
            self.update_keywords_list()
            messagebox.showinfo(
                "Success", f"Keyword '{keyword}' removed from blocked list!"
            )

    def test_domain(self):
        domain = self.test_domain_entry.get().strip()
        if domain:
            is_blocked, reason = self.content_filter.is_domain_blocked(domain)
            if is_blocked:
                self.results_label.configure(
                    text=f"🚫 BLOCKED: {reason}", text_color="red"
                )
            else:
                self.results_label.configure(
                    text=f"✅ ALLOWED: Domain '{domain}' is not blocked",
                    text_color="green",
                )
        else:
            messagebox.showwarning("Warning", "Please enter a domain to test!")

    def test_content(self):
        content = self.test_content_text.get("1.0", "end-1c").strip()
        if content:
            is_blocked, reason = self.content_filter.is_content_blocked(content)
            if is_blocked:
                self.results_label.configure(
                    text=f"🚫 BLOCKED: {reason}", text_color="red"
                )
            else:
                self.results_label.configure(
                    text="✅ ALLOWED: Content does not contain blocked keywords",
                    text_color="green",
                )
        else:
            messagebox.showwarning("Warning", "Please enter content to test!")

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = ContentFilterGUI()
    app.run()
