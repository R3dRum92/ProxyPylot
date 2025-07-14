import asyncio
import tkinter as tk
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from app.filter import ContentFilter


class ContentFilterGUI(ctk.CTk):
    def __init__(self, filter: Optional[ContentFilter] = None):
        super().__init__()

        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        # ctk.set_default_color_theme("blue")

        # Initialize the content filter
        if filter is None:
            self.content_filter = ContentFilter()
        else:
            self.content_filter = filter

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
        title_frame = ctk.CTkFrame(
            self.sidebar_inner, fg_color="#2a2a2a", corner_radius=15
        )
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

    def update_sidebar_buttons(self):
        """Update sidebar button colors based on current view."""
        buttons = {
            "domains": self.domains_btn,
        }

        for view, button in buttons.items():
            if view == self.current_view:
                button.configure(
                    fg_color="#142760", border_width=0, text_color="#faf9f6"
                )
            else:
                button.configure(
                    fg_color="transparent", border_width=2, border_color="#374151"
                )

    def show_domains_view(self):
        """Display the blocked domains view."""
        content_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=30)

        header_label = ctk.CTkLabel(
            content_container,
            text="Blocked Domains",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#faf9f6",
        )
        header_label.pack(anchor="w", pady=(0, 30))

        add_card = ctk.CTkFrame(content_container, fg_color="#1a1a1a", corner_radius=15)
        add_card.pack(fill="x", pady=(0, 25))

        add_content = ctk.CTkFrame(add_card, fg_color="transparent")
        add_content.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            add_content,
            text="Add New Domain",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6",
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
            border_color="#374151",
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

        list_card = ctk.CTkFrame(
            content_container, fg_color="#1a1a1a", corner_radius=15
        )
        list_card.pack(fill="both", expand=True)

        list_content = ctk.CTkFrame(list_card, fg_color="transparent")
        list_content.pack(fill="both", expand=True, padx=25, pady=25)

        list_header = ctk.CTkFrame(list_content, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 15))

        list_title = ctk.CTkLabel(
            list_header,
            text="Currently Blocked Domains",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6",
        )
        list_title.pack(side="left")

        # Instead of fixed count, use placeholder
        self.count_badge = ctk.CTkLabel(
            list_header,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color="#faf9f6",
            fg_color="#374151",
            corner_radius=15,
            width=100,
            height=30,
        )
        self.count_badge.pack(side="right")

        self.domains_scrollable = ctk.CTkScrollableFrame(
            list_content,
            fg_color="#0f0f0f",
            corner_radius=12,
            scrollbar_button_color="#68696C",
        )
        self.domains_scrollable.pack(fill="both", expand=True)

        # Load from DB immediately
        asyncio.run(self.load_domains_from_db())

    def update_domains_list(self):
        asyncio.run(self.load_domains_from_db())

    async def load_domains_from_db(self):
        """Update the domains list display."""
        # Clear existing items
        for widget in self.domains_scrollable.winfo_children():
            widget.destroy()

        rules = await self.content_filter.list_block_rules()

        count = len(rules)
        for child in self.main_content.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for sub in child.winfo_children():
                    for badge in sub.winfo_children():
                        if (
                            isinstance(badge, ctk.CTkLabel)
                            and "domains" in badge.cget("text").lower()
                        ):
                            badge.configure(text=f"{count} domains")

        # Display
        for rule in rules:
            domain = rule.pattern

            domain_frame = ctk.CTkFrame(
                self.domains_scrollable,
                fg_color="#2a2a2a",
                corner_radius=10,
                border_width=1,
                border_color="#374151",
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

            remove_btn = ctk.CTkButton(
                domain_content,
                text="Remove",
                width=80,
                height=30,
                corner_radius=8,
                font=ctk.CTkFont(size=12),
                fg_color="#921d1d",
                hover_color="#ee4444",
                command=lambda rid=rule.id: self.remove_domain(rid),
            )
            remove_btn.pack(side="right")

        self.count_badge.configure(text=f"{len(rules)} domains")

    def add_domain(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Warning", "Please enter a valid domain!")
            return

        try:
            asyncio.run(self._add_domain_async(domain))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add domain: {e}")

    async def _add_domain_async(self, domain):
        await self.content_filter.add_block_rule(
            pattern=domain, scope="global", reason="Added via GUI"
        )
        self.domain_entry.delete(0, "end")
        messagebox.showinfo("Success", f"Domain '{domain}' added to blocked list!")
        await self.load_domains_from_db()

    def remove_domain(self, rule_id):
        try:
            asyncio.run(self._remove_domain_async(rule_id))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove domain: {e}")

    async def _remove_domain_async(self, rule_id):
        await self.content_filter.delete_block_rule(rule_id)
        messagebox.showinfo("Success", "Domain removed from blocked list!")
        await self.load_domains_from_db()

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = ContentFilterGUI()
    app.run()
