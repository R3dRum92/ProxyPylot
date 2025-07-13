import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from filter import ContentFilter


class ContentFilterGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        #ctk.set_default_color_theme("blue")

        # Initialize the content filter
        self.content_filter = ContentFilter()

        # Configure the main window
        self.title("Content Filter Manager")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Current view tracking
        self.current_view = "domains"

        # Create the main interface
        self.create_widgets()

    def create_widgets(self):
        # Sidebar Frame with modern styling
        self.sidebar = ctk.CTkFrame(
            self, width=280, corner_radius=0, fg_color="#1a1a1a"
        )
        self.sidebar.pack(side="left", fill="y")

        # Sidebar content
        self.sidebar_inner = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_inner.pack(pady=30, padx=20, fill="both", expand=True)

        # Modern title section
        title_frame = ctk.CTkFrame(self.sidebar_inner, fg_color="#2a2a2a", corner_radius=15)
        title_frame.pack(fill="x", pady=(0, 30))

        self.title_label = ctk.CTkLabel(
            title_frame,
            text="🛡️ Content Filter",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#faf9f6",
        )
        self.title_label.pack(pady=20)

        # Navigation buttons with modern styling
        self.domains_btn = ctk.CTkButton(
            self.sidebar_inner,
            text="🚫  Blocked Domains",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color="#374151",
            border_width=2,
            border_color="#374151",
            text_color="#FAF9F6",
            height=50,
            corner_radius=12,
            command=lambda: self.switch_view("domains"),
        )
        self.domains_btn.pack(fill="x", pady=(0, 15))

        self.keywords_btn = ctk.CTkButton(
            self.sidebar_inner,
            text="🔒  Blocked Keywords",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color="#374151",
            border_width=2,
            border_color="#374151",
            text_color="#FAF9F6",
            height=50,
            corner_radius=12,
            command=lambda: self.switch_view("keywords"),
        )
        self.keywords_btn.pack(fill="x", pady=(0, 15))

        self.test_btn = ctk.CTkButton(
            self.sidebar_inner,
            text="🧪  Test Filter",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color="#374151",
            border_width=2,
            border_color="#374151",
            text_color="#FAF9F6",
            height=50,
            corner_radius=12,
            command=lambda: self.switch_view("test"),
        )
        self.test_btn.pack(fill="x", pady=(0, 15))

        # Main content area
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f0f0f")
        self.main_content.pack(expand=True, fill="both")

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
                button.configure(fg_color="#142760", border_width=0, text_color = "#faf9f6")
            else:
                button.configure(fg_color="transparent", border_width=2, border_color="#374151")

    def show_domains_view(self):
        """Display the blocked domains view."""
        # Content container
        content_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header_label = ctk.CTkLabel(
            content_container,
            text="Blocked Domains",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#faf9f6"
        )
        header_label.pack(anchor="w", pady=(0, 30))

        # Add new domain card
        add_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        add_card.pack(fill="x", pady=(0, 25))

        add_content = ctk.CTkFrame(add_card, fg_color="transparent")
        add_content.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            add_content, 
            text="Add New Domain", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6"
        ).pack(anchor="w", pady=(0, 15))

        entry_frame = ctk.CTkFrame(add_content, fg_color="transparent")
        entry_frame.pack(fill="x")

        self.domain_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Enter domain to block (e.g., example.com)",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151"
        )
        self.domain_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        add_domain_btn = ctk.CTkButton(
            entry_frame,
            text="Add Domain",
            width=130,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#057669",
            hover_color="#02b981",
            command=self.add_domain,
        )
        add_domain_btn.pack(side="right")

        # Domains list card
        list_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        list_card.pack(fill="both", expand=True)

        list_content = ctk.CTkFrame(list_card, fg_color="transparent")
        list_content.pack(fill="both", expand=True, padx=25, pady=25)

        # List header
        list_header = ctk.CTkFrame(list_content, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 15))

        list_title = ctk.CTkLabel(
            list_header,
            text="Currently Blocked Domains",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6"
        )
        list_title.pack(side="left")

        count_badge = ctk.CTkLabel(
            list_header,
            text=f"{len(self.content_filter.blocked_domains)} domains",
            font=ctk.CTkFont(size=12),
            text_color="#faf9f6",
            fg_color="#374151",
            corner_radius=15,
            width=100,
            height=30
        )
        count_badge.pack(side="right")

        # Scrollable frame for domains
        self.domains_scrollable = ctk.CTkScrollableFrame(
            list_content, 
            fg_color="#0f0f0f", 
            corner_radius=12,
            scrollbar_button_color="#2563eb",
            scrollbar_button_hover_color="#1d4ed8"
        )
        self.domains_scrollable.pack(fill="both", expand=True)

        self.update_domains_list()

    def show_keywords_view(self):
        """Display the blocked keywords view."""
        # Content container
        content_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header_label = ctk.CTkLabel(
            content_container,
            text="Blocked Keywords",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#faf9f6"
        )
        header_label.pack(anchor="w", pady=(0, 30))

        # Add new keyword card
        add_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        add_card.pack(fill="x", pady=(0, 25))

        add_content = ctk.CTkFrame(add_card, fg_color="transparent")
        add_content.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            add_content, 
            text="Add New Keyword", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6"
        ).pack(anchor="w", pady=(0, 15))

        entry_frame = ctk.CTkFrame(add_content, fg_color="transparent")
        entry_frame.pack(fill="x")

        self.keyword_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Enter keyword to block",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151"
        )
        self.keyword_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        add_keyword_btn = ctk.CTkButton(
            entry_frame,
            text="Add Keyword",
            width=130,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.add_keyword,
        )
        add_keyword_btn.pack(side="right")

        # Keywords list card
        list_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        list_card.pack(fill="both", expand=True)

        list_content = ctk.CTkFrame(list_card, fg_color="transparent")
        list_content.pack(fill="both", expand=True, padx=25, pady=25)

        # List header
        list_header = ctk.CTkFrame(list_content, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 15))

        list_title = ctk.CTkLabel(
            list_header,
            text="Currently Blocked Keywords",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6"
        )
        list_title.pack(side="left")

        count_badge = ctk.CTkLabel(
            list_header,
            text=f"{len(self.content_filter.blocked_keywords)} keywords",
            font=ctk.CTkFont(size=12),
            text_color="#faf9f6",
            fg_color="#374151",
            corner_radius=15,
            width=100,
            height=30
        )
        count_badge.pack(side="right")

        # Scrollable frame for keywords
        self.keywords_scrollable = ctk.CTkScrollableFrame(
            list_content, 
            fg_color="#0f0f0f", 
            corner_radius=12,
            scrollbar_button_color="#2563eb",
            scrollbar_button_hover_color="#1d4ed8"
        )
        self.keywords_scrollable.pack(fill="both", expand=True)

        self.update_keywords_list()

    def show_test_view(self):
        """Display the test filter view."""
        # Content container
        content_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header_label = ctk.CTkLabel(
            content_container,
            text="Test Filter",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#faf9f6"
        )
        header_label.pack(anchor="w", pady=(0, 30))

        # Domain test card
        domain_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        domain_card.pack(fill="x", pady=(0, 25))

        domain_content = ctk.CTkFrame(domain_card, fg_color="transparent")
        domain_content.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            domain_content,
            text="Test Domain",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6"
        ).pack(anchor="w", pady=(0, 15))

        domain_entry_frame = ctk.CTkFrame(domain_content, fg_color="transparent")
        domain_entry_frame.pack(fill="x", pady=(0, 15))

        self.test_domain_entry = ctk.CTkEntry(
            domain_entry_frame,
            placeholder_text="Enter domain to test (e.g., example.com)",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151"
        )
        self.test_domain_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        test_domain_btn = ctk.CTkButton(
            domain_entry_frame,
            text="Test Domain",
            width=130,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.test_domain,
        )
        test_domain_btn.pack(side="right")

        # Results area
        self.results_label = ctk.CTkLabel(
            domain_content,
            text="No tests performed yet...",
            font=ctk.CTkFont(size=12),
            text_color="#9ca3af",
            anchor="w"
        )
        self.results_label.pack(anchor="w")

        # Content test card
        content_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        content_card.pack(fill="both", expand=True)

        content_content = ctk.CTkFrame(content_card, fg_color="transparent")
        content_content.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            content_content,
            text="Test Content",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6"
        ).pack(anchor="w", pady=(0, 15))

        self.test_content_text = ctk.CTkTextbox(
            content_content,
            height=120,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151"
        )
        self.test_content_text.pack(fill="both", expand=True, pady=(0, 15))

        test_content_btn = ctk.CTkButton(
            content_content,
            text="Test Content",
            width=130,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.test_content,
        )
        test_content_btn.pack(anchor="e")

    def update_domains_list(self):
        """Update the domains list display."""
        # Clear existing items
        for widget in self.domains_scrollable.winfo_children():
            widget.destroy()

        # Display domains
        for domain in self.content_filter.blocked_domains:
            domain_frame = ctk.CTkFrame(
                self.domains_scrollable, 
                fg_color="#2a2a2a", 
                corner_radius=10,
                border_width=1,
                border_color="#374151"
            )
            domain_frame.pack(fill="x", pady=5, padx=10)

            domain_content = ctk.CTkFrame(domain_frame, fg_color="transparent")
            domain_content.pack(fill="x", padx=20, pady=15)

            domain_label = ctk.CTkLabel(
                domain_content,
                text=f"🚫  {domain}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#faf9f6",
                anchor="w",
            )
            domain_label.pack(side="left", fill="x", expand=True)

            # Remove button
            remove_btn = ctk.CTkButton(
                domain_content,
                text="Remove",
                width=80,
                height=30,
                corner_radius=8,
                font=ctk.CTkFont(size=12),
                fg_color="#921d1d",
                hover_color="#ee4444",
                command=lambda d=domain: self.remove_domain(d),
            )
            remove_btn.pack(side="right")

    def update_keywords_list(self):
        """Update the keywords list display."""
        # Clear existing items
        for widget in self.keywords_scrollable.winfo_children():
            widget.destroy()

        # Display keywords
        for keyword in self.content_filter.blocked_keywords:
            keyword_frame = ctk.CTkFrame(
                self.keywords_scrollable, 
                fg_color="#2a2a2a", 
                corner_radius=10,
                border_width=1,
                border_color="#374151"
            )
            keyword_frame.pack(fill="x", pady=5, padx=10)

            keyword_content = ctk.CTkFrame(keyword_frame, fg_color="transparent")
            keyword_content.pack(fill="x", padx=20, pady=15)

            keyword_label = ctk.CTkLabel(
                keyword_content,
                text=f"🔒  {keyword}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#faf9f6",
                anchor="w",
            )
            keyword_label.pack(side="left", fill="x", expand=True)

            # Remove button
            remove_btn = ctk.CTkButton(
                keyword_content,
                text="Remove",
                width=80,
                height=30,
                corner_radius=8,
                font=ctk.CTkFont(size=12),
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda k=keyword: self.remove_keyword(k),
            )
            remove_btn.pack(side="right")

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
                    text=f"🚫 BLOCKED: {reason}", text_color="#ef4444"
                )
            else:
                self.results_label.configure(
                    text=f"✅ ALLOWED: Domain '{domain}' is not blocked",
                    text_color="#10b981",
                )
        else:
            messagebox.showwarning("Warning", "Please enter a domain to test!")

    def test_content(self):
        content = self.test_content_text.get("1.0", "end-1c").strip()
        if content:
            is_blocked, reason = self.content_filter.is_content_blocked(content)
            if is_blocked:
                self.results_label.configure(
                    text=f"🚫 BLOCKED: {reason}", text_color="#ef4444"
                )
            else:
                self.results_label.configure(
                    text="✅ ALLOWED: Content does not contain blocked keywords",
                    text_color="#10b981",
                )
        else:
            messagebox.showwarning("Warning", "Please enter content to test!")

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = ContentFilterGUI()
    app.run()