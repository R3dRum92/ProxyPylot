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
        self.title("ProxyPylot")
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

        self.traffics_btn = ctk.CTkButton(
            self.sidebar_inner,
            text="📊  Traffic Logs",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color="#374151",
            border_width=2,
            border_color="#374151",
            text_color="#FAF9F6",
            height=50,
            corner_radius=12,
            command=lambda: self.switch_view("traffics"),
        )
        self.traffics_btn.pack(fill="x", pady=(0, 15))

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
        elif view_name == "traffics":
            self.show_traffics_view()

    def update_sidebar_buttons(self):
        """Update sidebar button colors based on current view."""
        buttons = {
            "domains": self.domains_btn,
            "traffics": self.traffics_btn,
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

        self.stop_traffic_auto_refresh()
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
            text="Add New Domain Block",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6",
        ).pack(anchor="w", pady=(0, 20))

        # Create form fields
        form_frame = ctk.CTkFrame(add_content, fg_color="transparent")
        form_frame.pack(fill="x")

        # Domain field
        domain_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        domain_row.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            domain_row,
            text="Domain:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            width=100,
        ).pack(side="left", padx=(0, 10))

        self.domain_entry = ctk.CTkEntry(
            domain_row,
            placeholder_text="Enter domain to block (e.g., example.com)",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151",
        )
        self.domain_entry.pack(side="left", fill="x", expand=True)

        # Scope field
        scope_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        scope_row.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            scope_row,
            text="Scope:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            width=100,
        ).pack(side="left", padx=(0, 10))

        self.scope_var = ctk.StringVar(value="global")
        self.scope_dropdown = ctk.CTkComboBox(
            scope_row,
            values=["global", "subnet"],
            variable=self.scope_var,
            state="readonly",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151",
            dropdown_fg_color="#2a2a2a",
            dropdown_hover_color="#374151",
            command=self.on_scope_change,
        )
        self.scope_dropdown.pack(side="left", fill="x", expand=True)

        # Subnet field (initially hidden)
        self.subnet_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.subnet_row.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            self.subnet_row,
            text="Subnet:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            width=100,
        ).pack(side="left", padx=(0, 10))

        self.subnet_entry = ctk.CTkEntry(
            self.subnet_row,
            placeholder_text="Enter subnet (e.g., 192.168.1.0/24)",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151",
        )
        self.subnet_entry.pack(side="left", fill="x", expand=True)

        # Duration field
        duration_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        duration_row.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            duration_row,
            text="Duration:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            width=100,
        ).pack(side="left", padx=(0, 10))

        duration_inner = ctk.CTkFrame(duration_row, fg_color="transparent")
        duration_inner.pack(side="left", fill="x", expand=True)

        self.duration_entry = ctk.CTkEntry(
            duration_inner,
            placeholder_text="Enter duration (e.g., 24)",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151",
            width=200,
        )
        self.duration_entry.pack(side="left", padx=(0, 10))

        self.duration_unit = ctk.CTkComboBox(
            duration_inner,
            values=["hours", "days", "weeks", "permanent"],
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151",
            dropdown_fg_color="#2a2a2a",
            dropdown_hover_color="#374151",
            state="readonly",
            width=120,
        )
        self.duration_unit.pack(side="left")
        self.duration_unit.set("hours")

        # Button row
        button_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=(10, 0))

        add_domain_btn = ctk.CTkButton(
            button_row,
            text="Add Domain Block",
            width=150,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#057669",
            hover_color="#02b981",
            command=self.add_domain,
        )
        add_domain_btn.pack(side="left")

        clear_btn = ctk.CTkButton(
            button_row,
            text="Clear Form",
            width=120,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.clear_form,
        )
        clear_btn.pack(side="left", padx=(10, 0))

        # Initially hide subnet field
        self.subnet_row.pack_forget()

        # --- IMPROVED BLENDED TABLE DESIGN ---
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

        # Count badge
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

        # Create a single container for the entire table (header + rows)
        self.table_container = ctk.CTkFrame(
            list_content,
            fg_color="#2a2a2a",  # Single background color for entire table
            corner_radius=12,
            border_width=0,
        )
        self.table_container.pack(fill="both", expand=True)

        # Table header (now part of the same container)
        table_header_frame = ctk.CTkFrame(
            self.table_container,
            fg_color="transparent",  # Transparent so it blends with container
            corner_radius=0,
        )
        table_header_frame.pack(fill="x", padx=20, pady=(20, 0))

        # Configure grid weights for columns
        table_header_frame.grid_columnconfigure(0, weight=3)  # Domain
        table_header_frame.grid_columnconfigure(1, weight=1)  # Scope
        table_header_frame.grid_columnconfigure(2, weight=2)  # Duration
        table_header_frame.grid_columnconfigure(3, weight=1)  # Actions

        ctk.CTkLabel(
            table_header_frame,
            text="Domain",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            table_header_frame,
            text="Scope",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            table_header_frame,
            text="Duration",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            table_header_frame,
            text="Actions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="e",
        ).grid(row=0, column=3, sticky="e")

        # Add a subtle separator line
        separator = ctk.CTkFrame(
            self.table_container,
            height=1,
            fg_color="#374151",
            corner_radius=0,
        )
        separator.pack(fill="x", padx=20, pady=(15, 0))

        # Scrollable area for rows (also part of the same container)
        self.domains_scrollable = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",  # Transparent so it blends
            corner_radius=0,
            scrollbar_button_color="#68696C",
            scrollbar_button_hover_color="#A0A0A0",
        )
        self.domains_scrollable.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Load from DB immediately
        asyncio.run(self.load_domains_from_db())

    def on_scope_change(self, selected_scope):
        """Show/hide subnet field based on scope selection."""
        if selected_scope == "subnet":
            self.subnet_row.pack(
                fill="x",
                pady=(0, 15),
                before=self.subnet_row.master.winfo_children()[-2],
            )
        else:
            self.subnet_row.pack_forget()

    def clear_form(self):
        """Clear all form fields."""
        self.domain_entry.delete(0, "end")
        self.scope_var.set("global")
        self.subnet_entry.delete(0, "end")
        self.duration_entry.delete(0, "end")
        self.duration_unit.set("hours")
        self.subnet_row.pack_forget()

    def show_traffics_view(self):
        """Display the traffics log view."""
        content_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header_label = ctk.CTkLabel(
            content_container,
            text="Traffic Logs",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#faf9f6",
        )
        header_label.pack(anchor="w", pady=(0, 30))

        # Search card
        search_card = ctk.CTkFrame(
            content_container, fg_color="#1a1a1a", corner_radius=15
        )
        search_card.pack(fill="x", pady=(0, 25))

        search_content = ctk.CTkFrame(search_card, fg_color="transparent")
        search_content.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            search_content,
            text="Search Traffic",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6",
        ).pack(anchor="w", pady=(0, 15))

        search_frame = ctk.CTkFrame(search_content, fg_color="transparent")
        search_frame.pack(fill="x")

        self.traffic_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by IP address or site name...",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#374151",
        )
        self.traffic_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=130,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#057669",
            hover_color="#02b981",
            command=self.search_traffic,
        )
        search_btn.pack(side="right", padx=(0, 15))

        clear_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            width=100,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.clear_traffic_search,
        )
        clear_btn.pack(side="right")

        # Traffic table card
        table_card = ctk.CTkFrame(
            content_container, fg_color="#1a1a1a", corner_radius=15
        )
        table_card.pack(fill="both", expand=True)

        table_content = ctk.CTkFrame(table_card, fg_color="transparent")
        table_content.pack(fill="both", expand=True, padx=25, pady=25)

        table_header = ctk.CTkFrame(table_content, fg_color="transparent")
        table_header.pack(fill="x", pady=(0, 15))

        table_title = ctk.CTkLabel(
            table_header,
            text="Network Traffic",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#faf9f6",
        )
        table_title.pack(side="left")

        # Traffic count badge
        self.traffic_count_badge = ctk.CTkLabel(
            table_header,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color="#faf9f6",
            fg_color="#374151",
            corner_radius=15,
            width=120,
            height=30,
        )
        self.traffic_count_badge.pack(side="right")

        # Table header
        table_header_frame = ctk.CTkFrame(
            table_content,
            fg_color="#2a2a2a",
            corner_radius=10,
            border_width=1,
            border_color="#374151",
        )
        table_header_frame.pack(fill="x", pady=(0, 10))

        header_content = ctk.CTkFrame(table_header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)

        # Configure grid weights for columns
        header_content.grid_columnconfigure(0, weight=2)  # Site name
        header_content.grid_columnconfigure(1, weight=1)  # IP address
        header_content.grid_columnconfigure(2, weight=1)  # Time

        ctk.CTkLabel(
            header_content,
            text="Site Name",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            header_content,
            text="IP Address",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            header_content,
            text="Time",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=2, sticky="w")

        # Scrollable traffic list
        self.traffic_scrollable = ctk.CTkScrollableFrame(
            table_content,
            fg_color="#0f0f0f",
            corner_radius=12,
            scrollbar_button_color="#68696C",
        )
        self.traffic_scrollable.pack(fill="both", expand=True)

        # Load traffic data (you'll need to implement this)
        self.load_traffic_data()

        self.start_traffic_auto_refresh(interval_ms=5000)

    def start_traffic_auto_refresh(self, interval_ms=500):
        """Start periodically refreshing traffic data"""
        self._traffic_auto_refresh_interval = interval_ms
        self._traffic_auto_refresh_running = True
        self._traffic_auto_refresh()

    def stop_traffic_auto_refresh(self):
        """Stop the auto refresh loop."""
        self._traffic_auto_refresh_running = False

    def _traffic_auto_refresh(self):
        if not self._traffic_auto_refresh_running:
            return
        self.load_traffic_data()
        self.after(self._traffic_auto_refresh_interval, self._traffic_auto_refresh)

    def load_traffic_data(self, search_term=None):
        """Load traffic data from DB and display it"""
        asyncio.run(self._load_traffic_data_async(search_term))

    async def _load_traffic_data_async(self, search_term=None):
        from app.db.crud import get_all_traffic_logs

        for child in self.traffic_scrollable.winfo_children():
            child.destroy()

        logs = await get_all_traffic_logs()

        if search_term:
            search_term = search_term.lower()
            logs = [
                log
                for log in logs
                if search_term in log.url.lower()
                or search_term in log.client_ip.lower()
            ]

        self.traffic_count_badge.configure(text=f"{len(logs)} records")

        for log in logs:
            self._add_traffic_row(log)

    def _add_traffic_row(self, log):
        row_frame = ctk.CTkFrame(
            self.traffic_scrollable, fg_color="#1a1a1a", corner_radius=8
        )

        row_frame.pack(fill="x", pady=4)

        row_content = ctk.CTkFrame(row_frame, fg_color="transparent")
        row_content.pack(fill="x", padx=15, pady=10)

        row_content.grid_columnconfigure(0, weight=2)
        row_content.grid_columnconfigure(1, weight=1)
        row_content.grid_columnconfigure(2, weight=1)

        # Site Name
        ctk.CTkLabel(
            row_content,
            text=log.url,
            font=ctk.CTkFont(size=13),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # IP Address
        ctk.CTkLabel(
            row_content,
            text=log.client_ip,
            font=ctk.CTkFont(size=13),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        # Time
        ctk.CTkLabel(
            row_content,
            text=log.time.strftime("%Y-%m-%d %H:%M:%S"),
            font=ctk.CTkFont(size=13),
            text_color="#faf9f6",
            anchor="w",
        ).grid(row=0, column=2, sticky="w")

    def search_traffic(self):
        """Search traffic logs based on the search entry."""
        search_term = self.traffic_search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term!")
            return

        from app.db.crud import get_all_traffic_logs

        logs = get_all_traffic_logs(limit=500)

        filtered = [
            log
            for log in logs
            if search_term.lower() in log.url.lower() or search_term in log.client_ip
        ]

        for child in self.traffic_scrollable.winfo_children():
            child.destroy()

        if not filtered:
            self.traffic_count_badge.configure(text="0 results")
            label = ctk.CTkLabel(
                self.traffic_scrollable,
                text="No matching records.",
                font=ctk.CTkFont(size=14),
                text_color="#faf9f6",
            )
            label.pack(padx=10, pady=10)
            return

        self.traffic_count_badge.configure(text=f"{len(filtered)} results")

        for log in filtered:
            row_frame = ctk.CTkFrame(
                self.traffic_scrollable, fg_color="#1a1a1a", corner_radius=8
            )
            row_frame.pack(fill="x", pady=4)

            row_content = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_content.pack(fill="x", padx=15, pady=10)

            row_content.grid_columnconfigure(0, weight=2)
            row_content.grid_columnconfigure(1, weight=1)
            row_content.grid_columnconfigure(2, weight=1)

            ctk.CTkLabel(
                row_content,
                text=log.url,
                font=ctk.CTkFont(size=13),
                text_color="#faf9f6",
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                row_content,
                text=log.client_ip,
                font=ctk.CTkFont(size=13),
                text_color="#faf9f6",
                anchor="w",
            ).grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(
                row_content,
                text=log.time.strftime("%Y-%m-%d %H:%M:%S"),
                font=ctk.CTkFont(size=13),
                text_color="#faf9f6",
                anchor="w",
            ).grid(row=0, column=2, sticky="w")

    def clear_traffic_search(self):
        """Clear the traffic search entry and reload all traffic."""
        self.traffic_search_entry.delete(0, "end")
        self.load_traffic_data()

    def update_domains_list(self):
        asyncio.run(self.load_domains_from_db())

    async def load_domains_from_db(self):
        """Update the domains list display with blended rows."""
        # Clear existing items
        for widget in self.domains_scrollable.winfo_children():
            widget.destroy()

        rules = await self.content_filter.list_block_rules()

        count = len(rules)
        # Update count badge
        self.count_badge.configure(text=f"{count} domains")

        # Display rules with blended appearance
        for i, rule in enumerate(rules):
            domain = rule.pattern
            scope_display = rule.scope
            duration_display = "Permanent"
            if rule.duration_hours is not None:
                duration_display = f"{rule.duration_hours} hours"

            # Create row frame with transparent background for blending
            domain_frame = ctk.CTkFrame(
                self.domains_scrollable,
                fg_color="transparent",  # Transparent for seamless blending
                corner_radius=0,
            )
            domain_frame.pack(fill="x", pady=2, padx=0)

            # Add subtle hover effect with a frame that can change color
            hover_frame = ctk.CTkFrame(
                domain_frame,
                fg_color="transparent",
                corner_radius=8,
            )
            hover_frame.pack(fill="x", padx=10, pady=5)

            # Bind hover effects
            def on_enter(event, frame=hover_frame):
                frame.configure(fg_color="#374151")

            def on_leave(event, frame=hover_frame):
                frame.configure(fg_color="transparent")

            hover_frame.bind("<Enter>", on_enter)
            hover_frame.bind("<Leave>", on_leave)

            domain_content = ctk.CTkFrame(hover_frame, fg_color="transparent")
            domain_content.pack(fill="x", padx=15, pady=12)

            # Configure grid weights for columns within each rule row
            domain_content.grid_columnconfigure(0, weight=3)  # Domain
            domain_content.grid_columnconfigure(1, weight=1)  # Scope
            domain_content.grid_columnconfigure(2, weight=2)  # Duration
            domain_content.grid_columnconfigure(3, weight=1)  # Actions

            # Domain Label
            ctk.CTkLabel(
                domain_content,
                text=f"🚫  {domain}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#faf9f6",
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=(0, 10))

            # Scope Label
            ctk.CTkLabel(
                domain_content,
                text=scope_display,
                font=ctk.CTkFont(size=14),
                text_color="#B0B0B0",
                anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=(0, 10))

            # Duration Label
            ctk.CTkLabel(
                domain_content,
                text=duration_display,
                font=ctk.CTkFont(size=14),
                text_color="#B0B0B0",
                anchor="w",
            ).grid(row=0, column=2, sticky="w", padx=(0, 10))

            # Remove Button
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
            remove_btn.grid(row=0, column=3, sticky="e")

            # Propagate hover events to child widgets
            for widget in [domain_content, hover_frame]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

    def add_domain(self):
        domain = self.domain_entry.get().strip()
        scope = self.scope_var.get()
        duration_value = self.duration_entry.get().strip()
        duration_unit = self.duration_unit.get()

        # Validation
        if not domain:
            messagebox.showwarning("Warning", "Please enter a valid domain!")
            return

        if scope == "subnet":
            subnet = self.subnet_entry.get().strip()
            if not subnet:
                messagebox.showwarning(
                    "Warning", "Please enter a subnet when scope is set to 'subnet'!"
                )
                return

        if duration_unit != "permanent" and not duration_value:
            messagebox.showwarning("Warning", "Please enter a duration value!")
            return

        # Calculate duration in hours for database storage
        duration_hours = None
        if duration_unit != "permanent":
            try:
                duration_val = int(duration_value)
                if duration_unit == "hours":
                    duration_hours = duration_val
                elif duration_unit == "days":
                    duration_hours = duration_val * 24
                elif duration_unit == "weeks":
                    duration_hours = duration_val * 24 * 7
            except ValueError:
                messagebox.showwarning("Warning", "Duration must be a number!")
                return

        try:
            asyncio.run(self._add_domain_async(domain, scope, subnet, duration_hours))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add domain: {e}")

    async def _add_domain_async(self, domain, scope, subnet, duration_hours):
        await self.content_filter.add_block_rule(
            pattern=domain,
            scope=scope,
            subnet=subnet,
            reason="Added via GUI",
            duration_hours=duration_hours,
        )
        self.clear_form()

        duration_text = (
            "permanent" if duration_hours is None else f"{duration_hours} hours"
        )
        messagebox.showinfo(
            "Success",
            f"Domain '{domain}' added to blocked list!\nScope: {scope}\nDuration: {duration_text}",
        )
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
    app.run()
    app.run()
    app.run()
    app.run()
    app.run()
