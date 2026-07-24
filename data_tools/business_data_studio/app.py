from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from PIL import Image

from .engine import DataProcessingEngine, DataStudioError, ProcessingConfig
from .translations import (
    FILTER_MODE_LABELS,
    LANGUAGE_LABELS,
    detect_default_language,
    filter_label,
    filter_mode_from_label,
    language_label,
    translate,
)


class SoftSelect(ctk.CTkFrame):
    """Rounded selection control with a fully custom animated popup."""

    def __init__(
        self,
        parent,
        *,
        variable: tk.StringVar,
        values: list[str],
        colors: dict[str, str],
        command=None,
        state: str = "normal",
        width: int = 180,
        height: int = 38,
        font: ctk.CTkFont | None = None,
        arrow_image: ctk.CTkImage | None = None,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            corner_radius=10,
            fg_color=colors["surface_soft"],
            border_width=1,
            border_color=colors["border"],
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.variable = variable
        self.values = list(values)
        self.colors = colors
        self.command = command
        self._state = state
        self._popup: ctk.CTkToplevel | None = None
        self._popup_has_alpha = True

        self._button = ctk.CTkButton(
            self,
            text=self.variable.get(),
            command=self._toggle_popup,
            anchor="w",
            height=height - 2,
            corner_radius=9,
            border_width=0,
            fg_color=colors["surface_soft"],
            hover_color=colors["primary_soft"],
            text_color=colors["text"],
            font=font or ctk.CTkFont("Segoe UI", 12),
        )
        self._button.pack(fill="both", expand=True, padx=1, pady=1)
        self._arrow = ctk.CTkLabel(
            self,
            text="" if arrow_image is not None else "⌄",
            image=arrow_image,
            width=24,
            text_color=colors["muted"],
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            fg_color="transparent",
        )
        self._arrow.place(relx=1.0, rely=0.5, x=-9, anchor="e")
        self._arrow.bind("<Button-1>", lambda _event: self._toggle_popup())

        self._trace_id = self.variable.trace_add(
            "write",
            self._sync_from_variable,
        )
        self._apply_state()

    def _sync_from_variable(self, *_args) -> None:
        self._button.configure(text=self.variable.get())

    def _apply_state(self) -> None:
        disabled = self._state == "disabled"
        self._button.configure(
            state="disabled" if disabled else "normal",
            text_color=(
                "#AAB2C0" if disabled else self.colors["text"]
            ),
        )
        self._arrow.configure(
            text_color=(
                "#C2C8D2" if disabled else self.colors["muted"]
            )
        )

    def _toggle_popup(self) -> None:
        if self._state == "disabled":
            return
        if self._popup is not None and self._popup.winfo_exists():
            self._close_popup()
            return
        self._open_popup()

    def _open_popup(self) -> None:
        available_values = [value for value in self.values if value]
        if not available_values:
            return

        self.update_idletasks()
        popup = ctk.CTkToplevel(self)
        self._popup = popup
        popup.withdraw()
        popup.overrideredirect(True)
        try:
            popup.attributes("-topmost", True)
            popup.attributes("-alpha", 0.0)
            self._popup_has_alpha = True
        except tk.TclError:
            self._popup_has_alpha = False
        popup.configure(fg_color=self.colors["border"])

        visible_rows = min(len(available_values), 6)
        final_height = visible_rows * 38 + 12
        popup_width = max(self.winfo_width(), 170)
        if len(available_values) > 6:
            option_host = ctk.CTkScrollableFrame(
                popup,
                corner_radius=12,
                fg_color=self.colors["surface"],
                scrollbar_button_color="#D5DAE4",
                scrollbar_button_hover_color="#C4CBD8",
            )
        else:
            option_host = ctk.CTkFrame(
                popup,
                corner_radius=12,
                fg_color=self.colors["surface"],
                border_width=1,
                border_color=self.colors["border"],
            )
        option_host.pack(fill="both", expand=True)

        selected_value = self.variable.get()
        for value in available_values:
            is_selected = value == selected_value
            option = ctk.CTkButton(
                option_host,
                text=value,
                command=lambda selected=value: self._select(selected),
                anchor="w",
                height=34,
                corner_radius=8,
                border_width=0,
                fg_color=(
                    self.colors["primary_soft"]
                    if is_selected
                    else "transparent"
                ),
                hover_color=self.colors["primary_soft"],
                text_color=(
                    self.colors["primary"]
                    if is_selected
                    else self.colors["text"]
                ),
                font=ctk.CTkFont(
                    "Segoe UI",
                    12,
                    "bold" if is_selected else "normal",
                ),
            )
            option.pack(
                fill="x",
                padx=6,
                pady=(6 if value == available_values[0] else 0, 2),
            )

        x = self.winfo_rootx()
        target_y = self.winfo_rooty() + self.winfo_height() + 6
        screen_height = self.winfo_screenheight()
        if target_y + final_height > screen_height - 12:
            target_y = self.winfo_rooty() - final_height - 6
        start_y = target_y - 7
        popup.geometry(
            f"{popup_width}x{final_height}+{x}+{start_y}"
        )
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        try:
            popup.grab_set()
        except tk.TclError:
            pass
        popup.bind("<Escape>", lambda _event: self._close_popup())
        popup.bind("<Button-1>", self._close_when_clicked_outside, add="+")
        popup.bind(
            "<FocusOut>",
            lambda _event: popup.after(70, self._close_if_focus_lost),
        )
        self._animate_popup(
            0,
            x,
            start_y,
            target_y,
            popup_width,
            final_height,
        )

    def _animate_popup(
        self,
        step: int,
        x: int,
        start_y: int,
        target_y: int,
        width: int,
        height: int,
    ) -> None:
        popup = self._popup
        if popup is None or not popup.winfo_exists():
            return
        progress = min(1.0, step / 8)
        eased = 1 - (1 - progress) ** 3
        current_y = round(start_y + (target_y - start_y) * eased)
        popup.geometry(f"{width}x{height}+{x}+{current_y}")
        if self._popup_has_alpha:
            try:
                popup.attributes("-alpha", min(1.0, progress * 1.15))
            except tk.TclError:
                self._popup_has_alpha = False
        if step < 8:
            popup.after(
                14,
                lambda: self._animate_popup(
                    step + 1,
                    x,
                    start_y,
                    target_y,
                    width,
                    height,
                ),
            )

    def _close_when_clicked_outside(self, event) -> None:
        popup = self._popup
        if popup is None or not popup.winfo_exists():
            return
        left = popup.winfo_rootx()
        top = popup.winfo_rooty()
        right = left + popup.winfo_width()
        bottom = top + popup.winfo_height()
        if not (left <= event.x_root <= right and top <= event.y_root <= bottom):
            self._close_popup()

    def _close_if_focus_lost(self) -> None:
        popup = self._popup
        if popup is None or not popup.winfo_exists():
            return
        focused_widget = popup.focus_get()
        if focused_widget is None:
            self._close_popup()
            return
        try:
            if focused_widget.winfo_toplevel() != popup:
                self._close_popup()
        except tk.TclError:
            self._close_popup()

    def _select(self, value: str) -> None:
        self.variable.set(value)
        self._close_popup()
        if self.command is not None:
            self.command(value)

    def _close_popup(self) -> None:
        popup = self._popup
        self._popup = None
        if popup is None or not popup.winfo_exists():
            return
        try:
            popup.grab_release()
        except tk.TclError:
            pass
        popup.destroy()

    def configure(self, require_redraw: bool = False, **kwargs):
        if "values" in kwargs:
            self.values = list(kwargs.pop("values"))
        if "state" in kwargs:
            self._state = kwargs.pop("state")
            self._apply_state()
        if "command" in kwargs:
            self.command = kwargs.pop("command")
        if kwargs:
            return super().configure(
                require_redraw=require_redraw,
                **kwargs,
            )
        return None

    config = configure

    def destroy(self) -> None:
        self._close_popup()
        try:
            self.variable.trace_remove("write", self._trace_id)
        except (tk.TclError, AttributeError):
            pass
        super().destroy()


class BusinessDataStudioApp:
    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self._startup_alpha_supported = True
        self._startup_animation_done = False
        self._startup_target: tuple[int, int] = (0, 0)
        try:
            self.root.attributes("-alpha", 0.0)
        except tk.TclError:
            self._startup_alpha_supported = False
        self.root.geometry("1280x820")
        self.root.minsize(1040, 700)

        self.language_code = detect_default_language()
        self.language_var = tk.StringVar(
            value=language_label(self.language_code)
        )
        self.main_container: ctk.CTkFrame | None = None
        self.log_messages: list[str] = []

        self.engine = DataProcessingEngine(language=self.language_code)
        self.current_config = ProcessingConfig()
        self.column_renames: dict[str, str] = {}

        self.source_var = tk.StringVar(value=self._t("no_file"))
        self.file_info_var = tk.StringVar(value=self._t("load_prompt"))
        self.worksheet_var = tk.StringVar()
        self.status_var = tk.StringVar(value=self._t("ready"))

        self.trim_var = tk.BooleanVar(value=True)
        self.normalize_headers_var = tk.BooleanVar(value=True)
        self.remove_empty_var = tk.BooleanVar(value=True)
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        self.required_columns_var = tk.StringVar()
        self.filter_column_var = tk.StringVar()
        self.filter_mode_var = tk.StringVar(
            value=filter_label(self.language_code, "contains")
        )
        self.filter_value_var = tk.StringVar()
        self.rename_column_var = tk.StringVar()
        self.rename_to_var = tk.StringVar()
        self.rename_rules_var = tk.StringVar(
            value=self._t("no_rename_rules")
        )

        self._configure_theme()
        self._load_icons()
        self._create_interface()
        self._start_window_animation()

    def _t(self, key: str, **values) -> str:
        return translate(self.language_code, key, **values)

    def _configure_theme(self) -> None:
        self.colors = {
            "background": "#F6F7FB",
            "surface": "#FFFFFF",
            "surface_soft": "#F9FAFC",
            "border": "#E5E9F0",
            "text": "#263042",
            "muted": "#7C8798",
            "primary": "#6C7FDD",
            "primary_hover": "#5B6FCB",
            "primary_soft": "#EEF0FF",
            "success": "#4C9C83",
            "success_soft": "#EAF7F2",
            "warning": "#C58A4D",
        }
        ctk.set_appearance_mode("light")
        self.root.configure(fg_color=self.colors["background"])
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Modern.Treeview",
            background=self.colors["surface"],
            fieldbackground=self.colors["surface"],
            foreground=self.colors["text"],
            borderwidth=0,
            rowheight=34,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#F0F2F7",
            foreground=self.colors["text"],
            relief="flat",
            padding=(10, 9),
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "Modern.Treeview.Heading",
            background=[("active", "#E7EAF1")],
        )

    def _load_icons(self) -> None:
        self.icons: dict[str, ctk.CTkImage] = {}
        icon_folder = Path(__file__).parent / "assets" / "icons"
        for path in icon_folder.glob("*.png"):
            try:
                with Image.open(path) as image_file:
                    image = image_file.convert("RGBA").copy()
                self.icons[path.stem] = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(18, 18),
                )
            except OSError:
                continue

    def _icon(
        self,
        name: str,
        *,
        light: bool = False,
    ) -> ctk.CTkImage | None:
        tone = "light" if light else "dark"
        return self.icons.get(f"{name}-{tone}")

    def _start_window_animation(self) -> None:
        self.root.update_idletasks()
        width = max(self.root.winfo_width(), 1280)
        height = max(self.root.winfo_height(), 820)
        target_x = max(0, (self.root.winfo_screenwidth() - width) // 2)
        target_y = max(
            0,
            (self.root.winfo_screenheight() - height) // 2,
        )
        start_y = target_y + 22
        self._startup_target = (target_x, target_y)
        self.root.geometry(
            f"{width}x{height}+{target_x}+{start_y}"
        )
        if not self._startup_alpha_supported:
            self.root.geometry(f"+{target_x}+{target_y}")
            return
        self.root.after(
            45,
            lambda: self._begin_window_animation(
                target_x,
                start_y,
                target_y,
            ),
        )
        self.root.after(900, self._ensure_window_visible)

    def _begin_window_animation(
        self,
        target_x: int,
        start_y: int,
        target_y: int,
    ) -> None:
        try:
            self.root.deiconify()
            self.root.lift()
        except tk.TclError:
            return
        self._fade_window(
            0,
            target_x,
            start_y,
            target_y,
        )

    def _fade_window(
        self,
        step: int,
        target_x: int,
        start_y: int,
        target_y: int,
    ) -> None:
        progress = min(1.0, step / 18)
        eased = 1 - (1 - progress) ** 3
        current_y = round(start_y + (target_y - start_y) * eased)
        try:
            self.root.geometry(f"+{target_x}+{current_y}")
            self.root.attributes("-alpha", min(1.0, progress * 1.1))
        except tk.TclError:
            self._ensure_window_visible()
            return
        if step < 18:
            self.root.after(
                15,
                lambda: self._fade_window(
                    step + 1,
                    target_x,
                    start_y,
                    target_y,
                ),
            )
            return
        self._startup_animation_done = True
        self.root.geometry(f"+{target_x}+{target_y}")
        self.root.attributes("-alpha", 1.0)

    def _ensure_window_visible(self) -> None:
        if self._startup_animation_done:
            return
        target_x, target_y = self._startup_target
        try:
            self.root.attributes("-alpha", 1.0)
            self.root.geometry(f"+{target_x}+{target_y}")
            self.root.deiconify()
            self.root.lift()
            self._startup_animation_done = True
        except tk.TclError:
            pass

    def _button(
        self,
        parent,
        text: str,
        command,
        *,
        kind: str = "soft",
        icon: str | None = None,
        width: int = 0,
    ) -> ctk.CTkButton:
        if kind == "primary":
            foreground = self.colors["primary"]
            hover = self.colors["primary_hover"]
            text_color = "#FFFFFF"
            border_width = 0
            border_color = foreground
            image = self._icon(icon, light=True) if icon else None
        elif kind == "ghost":
            foreground = "transparent"
            hover = self.colors["surface_soft"]
            text_color = self.colors["text"]
            border_width = 1
            border_color = self.colors["border"]
            image = self._icon(icon) if icon else None
        else:
            foreground = self.colors["primary_soft"]
            hover = "#E3E6FB"
            text_color = self.colors["primary"]
            border_width = 0
            border_color = foreground
            image = self._icon(icon) if icon else None

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            image=image,
            compound="left",
            width=width,
            height=40,
            corner_radius=11,
            border_width=border_width,
            border_color=border_color,
            fg_color=foreground,
            hover_color=hover,
            text_color=text_color,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
        )

    def _create_card(
        self,
        parent,
        title: str,
        *,
        padding: int = 14,
    ) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            corner_radius=16,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"],
        )
        ctk.CTkLabel(
            card,
            text=title,
            text_color=self.colors["text"],
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=padding, pady=(padding, 9))
        return card

    def _create_interface(self) -> None:
        if self.main_container is not None:
            self.main_container.destroy()

        self.root.title(self._t("app_title"))
        container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["background"],
            corner_radius=0,
        )
        self.main_container = container
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(
            container,
            fg_color=self.colors["surface"],
            corner_radius=0,
            height=88,
            border_width=0,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        logo = ctk.CTkFrame(
            header,
            width=48,
            height=48,
            corner_radius=14,
            fg_color=self.colors["primary_soft"],
        )
        logo.pack(side="left", padx=(24, 13))
        logo.pack_propagate(False)
        ctk.CTkLabel(
            logo,
            text="",
            image=self._icon("table-2"),
        ).pack(expand=True)

        header_text = ctk.CTkFrame(header, fg_color="transparent")
        header_text.pack(side="left", pady=13)
        ctk.CTkLabel(
            header_text,
            text=self._t("app_title"),
            text_color=self.colors["text"],
            font=ctk.CTkFont("Segoe UI", 21, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_text,
            text=self._t("app_subtitle"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", pady=(1, 0))

        language_frame = ctk.CTkFrame(
            header,
            fg_color=self.colors["surface_soft"],
            corner_radius=12,
        )
        language_frame.pack(side="right", padx=24)
        ctk.CTkLabel(
            language_frame,
            text="",
            image=self._icon("languages"),
        ).pack(side="left", padx=(12, 3), pady=7)
        self.language_combo = SoftSelect(
            language_frame,
            values=list(LANGUAGE_LABELS),
            variable=self.language_var,
            colors=self.colors,
            command=self.change_language,
            width=105,
            height=34,
            font=ctk.CTkFont("Segoe UI", 12),
            arrow_image=self._icon("chevron-down"),
        )
        self.language_combo.pack(side="left", padx=(0, 4), pady=4)

        content = ctk.CTkFrame(
            container,
            fg_color=self.colors["background"],
            corner_radius=0,
        )
        content.pack(fill="both", expand=True, padx=22, pady=(18, 14))

        self.source_card = ctk.CTkFrame(
            content,
            corner_radius=16,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"],
        )
        self.source_card.pack(fill="x", pady=(0, 14))
        self.source_card.columnconfigure(1, weight=1)

        badge = ctk.CTkFrame(
            self.source_card,
            width=48,
            height=48,
            corner_radius=13,
            fg_color=self.colors["success_soft"],
        )
        badge.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="w",
            padx=(16, 13),
            pady=14,
        )
        badge.grid_propagate(False)
        ctk.CTkLabel(
            badge,
            text="",
            image=self._icon("folder-open"),
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.source_card,
            textvariable=self.source_var,
            text_color=self.colors["text"],
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", pady=(15, 0))
        ctk.CTkLabel(
            self.source_card,
            textvariable=self.file_info_var,
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
            anchor="w",
        ).grid(row=1, column=1, sticky="ew", pady=(0, 14))

        self.worksheet_frame = ctk.CTkFrame(
            self.source_card,
            fg_color="transparent",
        )
        self.worksheet_frame.grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
            padx=(16, 12),
        )
        ctk.CTkLabel(
            self.worksheet_frame,
            text=self._t("excel_worksheet"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 3))
        self.worksheet_combo = SoftSelect(
            self.worksheet_frame,
            variable=self.worksheet_var,
            values=[""],
            colors=self.colors,
            state="disabled",
            width=185,
            height=34,
            arrow_image=self._icon("chevron-down"),
            command=self.change_worksheet,
        )
        self.worksheet_combo.pack()
        self.worksheet_frame.grid_remove()

        self._button(
            self.source_card,
            text=self._t("select_data_file"),
            command=self.select_file,
            kind="primary",
            icon="folder-open",
            width=170,
        ).grid(
            row=0,
            column=3,
            rowspan=2,
            sticky="e",
            padx=(8, 16),
            pady=17,
        )

        self.tabview = ctk.CTkTabview(
            content,
            corner_radius=16,
            fg_color=self.colors["background"],
            segmented_button_fg_color="#ECEFF5",
            segmented_button_selected_color=self.colors["surface"],
            segmented_button_selected_hover_color=self.colors["surface"],
            segmented_button_unselected_color="#ECEFF5",
            segmented_button_unselected_hover_color="#E3E7EF",
            text_color=self.colors["text"],
            command=self._tab_changed,
        )
        self.tabview.pack(fill="both", expand=True)
        self.data_tab = self.tabview.add(self._t("data_preview"))
        self.rules_tab = self.tabview.add(self._t("workflow_rules"))
        self.output_tab = self.tabview.add(self._t("export_log"))
        for tab in (self.data_tab, self.rules_tab, self.output_tab):
            tab.configure(fg_color=self.colors["background"])

        self._create_data_tab()
        self._create_rules_tab()
        self._create_output_tab()

        status = ctk.CTkFrame(
            content,
            height=38,
            corner_radius=12,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"],
        )
        status.pack(fill="x", pady=(10, 0))
        status.pack_propagate(False)
        ctk.CTkLabel(
            status,
            text="●",
            text_color=self.colors["success"],
            font=ctk.CTkFont("Segoe UI", 10),
        ).pack(side="left", padx=(13, 7))
        ctk.CTkLabel(
            status,
            textvariable=self.status_var,
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(side="left")

        if self.engine.source_path is not None:
            self._configure_worksheet_control()
            self._update_column_controls(reset_selection=False)
            self._refresh_file_info()
            if self.engine.result is not None:
                self._show_rows(
                    self.engine.result.headers,
                    self.engine.result.rows,
                )
            else:
                self._show_rows(
                    self.engine.original_headers,
                    self.engine.original_rows,
                )
        self._update_rename_rule_text()

    def _create_data_tab(self) -> None:
        table_card = ctk.CTkFrame(
            self.data_tab,
            corner_radius=16,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"],
        )
        table_card.pack(fill="both", expand=True, pady=(6, 0))

        toolbar = ctk.CTkFrame(table_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=14, pady=(13, 10))
        ctk.CTkLabel(
            toolbar,
            text=self._t("data_preview"),
            text_color=self.colors["text"],
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
        ).pack(side="left")
        self._button(
            toolbar,
            text=self._t("show_processed"),
            command=self.show_processed_data,
            kind="soft",
            icon="list-checks",
        ).pack(side="right")
        self._button(
            toolbar,
            text=self._t("show_source"),
            command=self.show_source_data,
            kind="ghost",
            icon="eye",
        ).pack(side="right", padx=(0, 8))

        table_frame = tk.Frame(
            table_card,
            bg=self.colors["surface"],
            highlightthickness=0,
        )
        table_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.table = ttk.Treeview(
            table_frame,
            show="headings",
            style="Modern.Treeview",
        )
        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview,
        )
        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview,
        )
        self.table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def _create_rules_tab(self) -> None:
        rules_scroll = ctk.CTkScrollableFrame(
            self.rules_tab,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#D8DDE7",
            scrollbar_button_hover_color="#C7CEDA",
        )
        rules_scroll.pack(fill="both", expand=True, pady=(6, 0))
        rules_scroll.columnconfigure(0, weight=1, uniform="rules")
        rules_scroll.columnconfigure(1, weight=1, uniform="rules")

        cleaning = self._create_card(
            rules_scroll,
            self._t("cleaning_rules"),
        )
        cleaning.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
            pady=(0, 10),
        )

        ctk.CTkCheckBox(
            cleaning,
            text=self._t("trim_whitespace"),
            variable=self.trim_var,
            corner_radius=6,
            border_width=2,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=5)
        ctk.CTkCheckBox(
            cleaning,
            text=self._t("normalize_headers"),
            variable=self.normalize_headers_var,
            corner_radius=6,
            border_width=2,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=5)
        ctk.CTkCheckBox(
            cleaning,
            text=self._t("remove_empty"),
            variable=self.remove_empty_var,
            corner_radius=6,
            border_width=2,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=5)
        ctk.CTkCheckBox(
            cleaning,
            text=self._t("remove_duplicates"),
            variable=self.remove_duplicates_var,
            corner_radius=6,
            border_width=2,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=(5, 15))

        validation = self._create_card(
            rules_scroll,
            self._t("validation"),
        )
        validation.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
            pady=(0, 10),
        )
        ctk.CTkLabel(
            validation,
            text=self._t("required_columns"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", padx=14, pady=(0, 7))
        ctk.CTkEntry(
            validation,
            textvariable=self.required_columns_var,
            height=38,
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=self.colors["surface_soft"],
        ).pack(fill="x", padx=14, pady=(0, 15))

        filtering = self._create_card(
            rules_scroll,
            self._t("row_filter"),
        )
        filtering.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 10),
        )
        filter_fields = ctk.CTkFrame(filtering, fg_color="transparent")
        filter_fields.pack(fill="x", padx=14, pady=(0, 15))
        filter_fields.columnconfigure(0, weight=2)
        filter_fields.columnconfigure(1, weight=2)
        filter_fields.columnconfigure(2, weight=3)
        column_field = ctk.CTkFrame(filter_fields, fg_color="transparent")
        column_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(
            column_field,
            text=self._t("column"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", pady=(0, 4))
        self.filter_column_combo = SoftSelect(
            column_field,
            variable=self.filter_column_var,
            values=[""],
            colors=self.colors,
            state="readonly",
            height=38,
            arrow_image=self._icon("chevron-down"),
        )
        self.filter_column_combo.pack(fill="x")
        condition_field = ctk.CTkFrame(
            filter_fields,
            fg_color="transparent",
        )
        condition_field.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(
            condition_field,
            text=self._t("condition"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", pady=(0, 4))
        self.filter_mode_combo = SoftSelect(
            condition_field,
            variable=self.filter_mode_var,
            values=list(FILTER_MODE_LABELS[self.language_code].values()),
            colors=self.colors,
            state="readonly",
            height=38,
            arrow_image=self._icon("chevron-down"),
        )
        self.filter_mode_combo.pack(fill="x")
        value_field = ctk.CTkFrame(filter_fields, fg_color="transparent")
        value_field.grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(
            value_field,
            text=self._t("value"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkEntry(
            value_field,
            textvariable=self.filter_value_var,
            height=38,
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=self.colors["surface_soft"],
        ).pack(fill="x")

        renaming = self._create_card(
            rules_scroll,
            self._t("column_rename"),
        )
        renaming.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 10),
        )
        rename_fields = ctk.CTkFrame(renaming, fg_color="transparent")
        rename_fields.pack(fill="x", padx=14)
        rename_fields.columnconfigure(0, weight=2)
        rename_fields.columnconfigure(1, weight=3)
        current_field = ctk.CTkFrame(rename_fields, fg_color="transparent")
        current_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(
            current_field,
            text=self._t("current_column"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", pady=(0, 4))
        self.rename_column_combo = SoftSelect(
            current_field,
            variable=self.rename_column_var,
            values=[""],
            colors=self.colors,
            state="readonly",
            height=38,
            arrow_image=self._icon("chevron-down"),
        )
        self.rename_column_combo.pack(fill="x")
        new_name_field = ctk.CTkFrame(
            rename_fields,
            fg_color="transparent",
        )
        new_name_field.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(
            new_name_field,
            text=self._t("new_name"),
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkEntry(
            new_name_field,
            textvariable=self.rename_to_var,
            height=38,
            corner_radius=10,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=self.colors["surface_soft"],
        ).pack(fill="x")
        self._button(
            rename_fields,
            text=self._t("add_rename"),
            command=self.add_rename_rule,
            kind="soft",
        ).grid(row=0, column=2, sticky="s")

        ctk.CTkLabel(
            renaming,
            textvariable=self.rename_rules_var,
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 10),
        ).pack(anchor="w", padx=14, pady=(9, 14))

        actions = ctk.CTkFrame(rules_scroll, fg_color="transparent")
        actions.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(2, 0),
        )
        self._button(
            actions,
            text=self._t("apply_workflow"),
            command=self.apply_workflow,
            kind="primary",
            icon="play",
            width=180,
        ).pack(side="left")
        self._button(
            actions,
            text=self._t("save_profile"),
            command=self.save_profile,
            kind="ghost",
            icon="save",
        ).pack(side="left", padx=(8, 0))
        self._button(
            actions,
            text=self._t("load_profile"),
            command=self.load_profile,
            kind="ghost",
            icon="folder-open",
        ).pack(side="left", padx=(8, 0))
        self._button(
            actions,
            text=self._t("clear_rules"),
            command=self.clear_rules,
            kind="ghost",
            icon="rotate-ccw",
        ).pack(side="right")

    def _create_output_tab(self) -> None:
        export_card = self._create_card(
            self.output_tab,
            self._t("export_processed"),
        )
        export_card.pack(fill="x", pady=(6, 10))
        export_actions = ctk.CTkFrame(export_card, fg_color="transparent")
        export_actions.pack(fill="x", padx=14, pady=(0, 15))
        for index, (label, command, icon) in enumerate(
            (
                (self._t("export_csv"), self.export_csv, "file-text"),
                (
                    self._t("export_excel"),
                    self.export_excel,
                    "file-spreadsheet",
                ),
                (self._t("export_json"), self.export_json, "file-json"),
                (
                    self._t("export_validation"),
                    self.export_issues,
                    "download",
                ),
            )
        ):
            export_actions.columnconfigure(index, weight=1)
            self._button(
                export_actions,
                text=label,
                command=command,
                kind="primary" if index == 1 else "soft",
                icon=icon,
            ).grid(
                row=0,
                column=index,
                sticky="ew",
                padx=(0 if index == 0 else 5, 0 if index == 3 else 5),
            )

        log_card = self._create_card(
            self.output_tab,
            self._t("processing_log"),
        )
        log_card.pack(fill="both", expand=True)
        self.log = ctk.CTkTextbox(
            log_card,
            height=15,
            wrap="word",
            corner_radius=11,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=self.colors["surface_soft"],
            text_color=self.colors["text"],
            font=ctk.CTkFont("Consolas", 11),
        )
        self.log.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        if self.log_messages:
            self.log.insert(
                "end",
                "".join(f"• {message}\n" for message in self.log_messages),
            )
        self.log.configure(state="disabled")

    def _tab_changed(self) -> None:
        try:
            self.root.attributes("-alpha", 0.97)
            self.root.after(35, lambda: self.root.attributes("-alpha", 1.0))
        except tk.TclError:
            pass

    def change_language(self, _event=None) -> None:
        selected_code = LANGUAGE_LABELS.get(
            self.language_var.get(),
            "en",
        )
        if selected_code == self.language_code:
            return

        current_mode = filter_mode_from_label(
            self.language_code,
            self.filter_mode_var.get(),
        )
        had_result = self.engine.result is not None
        self.language_code = selected_code
        self.engine.set_language(selected_code)
        self.filter_mode_var.set(filter_label(selected_code, current_mode))

        if had_result:
            try:
                self.engine.process(self.current_config)
            except DataStudioError:
                self.engine.result = None

        if self.engine.source_path is None:
            self.source_var.set(self._t("no_file"))
            self.file_info_var.set(self._t("load_prompt"))
        self.status_var.set(self._t("language_changed"))
        self._create_interface()

    def select_file(self) -> None:
        selected = filedialog.askopenfilename(
            title=self._t("select_data_title"),
            filetypes=(
                (self._t("supported_files"), "*.csv *.txt *.xlsx"),
                (self._t("excel_workbooks"), "*.xlsx"),
                (self._t("csv_files"), "*.csv"),
                (self._t("text_files"), "*.txt"),
                (self._t("all_files"), "*.*"),
            ),
        )
        if not selected:
            return

        try:
            self.engine.load_file(selected)
        except DataStudioError as error:
            messagebox.showerror(self._t("file_error"), str(error))
            return

        self.source_var.set(Path(selected).name)
        self._configure_worksheet_control()
        self._refresh_file_info()
        self._update_column_controls()
        self.show_source_data()
        self._append_log(
            self._t("log_loaded_file", name=Path(selected).name)
        )
        if self.engine.worksheet_name:
            self._append_log(
                self._t(
                    "log_selected_sheet",
                    sheet=self.engine.worksheet_name,
                )
            )
        self.status_var.set(self._t("data_loaded_status"))
        self._flash_source_card()

    def change_worksheet(self, _event=None) -> None:
        selected_sheet = self.worksheet_var.get().strip()
        source_path = self.engine.source_path
        if not selected_sheet or source_path is None:
            return

        try:
            self.engine.load_file(source_path, worksheet=selected_sheet)
        except DataStudioError as error:
            messagebox.showerror(self._t("worksheet_error"), str(error))
            return

        self._refresh_file_info()
        self._update_column_controls()
        self.show_source_data()
        self._append_log(
            self._t("log_selected_sheet", sheet=selected_sheet)
        )
        self.status_var.set(
            self._t("worksheet_loaded_status", sheet=selected_sheet)
        )

    def _configure_worksheet_control(self) -> None:
        if self.engine.source_kind == "xlsx":
            self.worksheet_frame.grid()
            self.worksheet_combo.configure(
                state="readonly",
                values=list(self.engine.worksheet_names),
            )
            self.worksheet_var.set(self.engine.worksheet_name)
            return

        self.worksheet_frame.grid_remove()
        self.worksheet_combo.configure(state="disabled", values=[""])
        self.worksheet_var.set("")

    def _flash_source_card(self, step: int = 0) -> None:
        colors = (
            self.colors["success"],
            "#81B7A5",
            self.colors["border"],
        )
        self.source_card.configure(
            border_color=colors[min(step, len(colors) - 1)]
        )
        if step < len(colors) - 1:
            self.root.after(
                120,
                lambda: self._flash_source_card(step + 1),
            )

    def _refresh_file_info(self) -> None:
        if self.engine.source_kind == "xlsx":
            self.file_info_var.set(
                self._t(
                    "file_info_excel",
                    rows=len(self.engine.original_rows),
                    columns=len(self.engine.original_headers),
                    sheet=self.engine.worksheet_name,
                )
            )
            return

        delimiter_name = {
            ",": self._t("delimiter_comma"),
            ";": self._t("delimiter_semicolon"),
            "\t": self._t("delimiter_tab"),
            "|": self._t("delimiter_pipe"),
        }.get(self.engine.delimiter, repr(self.engine.delimiter))
        self.file_info_var.set(
            self._t(
                "file_info_text",
                rows=len(self.engine.original_rows),
                columns=len(self.engine.original_headers),
                encoding=self.engine.encoding,
                delimiter=delimiter_name,
            )
        )

    def apply_workflow(self) -> None:
        try:
            config = self._config_from_form()
            result = self.engine.process(config)
        except DataStudioError as error:
            messagebox.showerror(self._t("workflow_error"), str(error))
            return

        self.current_config = config
        self._show_rows(result.headers, result.rows)
        self._append_log(
            self._t(
                "log_workflow_completed",
                rows=result.stats["output_rows"],
                duplicates=result.stats["duplicates_removed"],
                issues=result.stats["validation_issues"],
            )
        )
        self.status_var.set(
            self._t(
                "workflow_complete_status",
                rows=result.stats["output_rows"],
            )
        )

    def show_source_data(self) -> None:
        if self.engine.source_path is None:
            return
        self._show_rows(
            self.engine.original_headers,
            self.engine.original_rows,
        )
        self.status_var.set(self._t("showing_source"))

    def show_processed_data(self) -> None:
        if self.engine.result is None:
            messagebox.showinfo(
                self._t("no_processed_title"),
                self._t("no_processed_message"),
            )
            return
        self._show_rows(self.engine.result.headers, self.engine.result.rows)
        self.status_var.set(self._t("showing_processed"))

    def add_rename_rule(self) -> None:
        current = self.rename_column_var.get().strip()
        new_name = self.rename_to_var.get().strip()
        if not current or not new_name:
            messagebox.showwarning(
                self._t("missing_rename_title"),
                self._t("missing_rename_message"),
            )
            return
        self.column_renames[current] = new_name
        self.rename_to_var.set("")
        self._update_rename_rule_text()

    def save_profile(self) -> None:
        config = self._config_from_form()
        selected = filedialog.asksaveasfilename(
            title=self._t("save_profile_title"),
            defaultextension=".json",
            filetypes=((self._t("json_profile"), "*.json"),),
        )
        if not selected:
            return
        try:
            self.engine.save_profile(selected, config)
        except OSError as error:
            messagebox.showerror(self._t("save_error"), str(error))
            return
        self._append_log(
            self._t("log_saved_profile", name=Path(selected).name)
        )
        self.status_var.set(self._t("profile_saved_status"))

    def load_profile(self) -> None:
        selected = filedialog.askopenfilename(
            title=self._t("load_profile_title"),
            filetypes=((self._t("json_profile"), "*.json"),),
        )
        if not selected:
            return
        try:
            config = self.engine.load_profile(
                selected,
                language=self.language_code,
            )
        except DataStudioError as error:
            messagebox.showerror(self._t("profile_error"), str(error))
            return
        self._apply_config_to_form(config)
        self._append_log(
            self._t("log_loaded_profile", name=Path(selected).name)
        )
        self.status_var.set(self._t("profile_loaded_status"))

    def export_csv(self) -> None:
        selected = filedialog.asksaveasfilename(
            title=self._t("export_csv_title"),
            defaultextension=".csv",
            filetypes=((self._t("csv_file"), "*.csv"),),
        )
        if not selected:
            return
        self._export(lambda: self.engine.export_csv(selected), selected)

    def export_excel(self) -> None:
        selected = filedialog.asksaveasfilename(
            title=self._t("export_excel_title"),
            defaultextension=".xlsx",
            filetypes=((self._t("excel_workbook"), "*.xlsx"),),
        )
        if not selected:
            return
        self._export(lambda: self.engine.export_excel(selected), selected)

    def export_json(self) -> None:
        selected = filedialog.asksaveasfilename(
            title=self._t("export_json_title"),
            defaultextension=".json",
            filetypes=((self._t("json_file"), "*.json"),),
        )
        if not selected:
            return
        self._export(lambda: self.engine.export_json(selected), selected)

    def export_issues(self) -> None:
        selected = filedialog.asksaveasfilename(
            title=self._t("export_issues_title"),
            defaultextension=".csv",
            filetypes=((self._t("csv_report"), "*.csv"),),
        )
        if not selected:
            return
        self._export(lambda: self.engine.export_issues(selected), selected)

    def clear_rules(self) -> None:
        self._apply_config_to_form(ProcessingConfig())
        self.status_var.set(self._t("rules_cleared"))

    def _export(self, action, path: str) -> None:
        try:
            action()
        except (DataStudioError, OSError) as error:
            messagebox.showerror(self._t("export_error"), str(error))
            return
        self._append_log(
            self._t("log_exported", name=Path(path).name)
        )
        self.status_var.set(
            self._t("export_status", name=Path(path).name)
        )
        messagebox.showinfo(
            self._t("export_completed_title"),
            self._t("export_completed_message"),
        )

    def _config_from_form(self) -> ProcessingConfig:
        required_columns = [
            value.strip()
            for value in self.required_columns_var.get().split(",")
            if value.strip()
        ]
        return ProcessingConfig(
            trim_whitespace=self.trim_var.get(),
            normalize_headers=self.normalize_headers_var.get(),
            remove_empty_rows=self.remove_empty_var.get(),
            remove_duplicates=self.remove_duplicates_var.get(),
            required_columns=required_columns,
            filter_column=self.filter_column_var.get(),
            filter_mode=filter_mode_from_label(
                self.language_code,
                self.filter_mode_var.get(),
            ),
            filter_value=self.filter_value_var.get(),
            column_renames=dict(self.column_renames),
        )

    def _apply_config_to_form(self, config: ProcessingConfig) -> None:
        self.trim_var.set(config.trim_whitespace)
        self.normalize_headers_var.set(config.normalize_headers)
        self.remove_empty_var.set(config.remove_empty_rows)
        self.remove_duplicates_var.set(config.remove_duplicates)
        self.required_columns_var.set(", ".join(config.required_columns))
        self.filter_column_var.set(config.filter_column)
        self.filter_mode_var.set(
            filter_label(self.language_code, config.filter_mode)
        )
        self.filter_value_var.set(config.filter_value)
        self.column_renames = dict(config.column_renames)
        self._update_rename_rule_text()
        self.current_config = config

    def _update_column_controls(self, *, reset_selection: bool = True) -> None:
        headers = self.engine.original_headers
        filter_values = [""] + headers
        self.filter_column_combo.configure(values=filter_values)
        self.rename_column_combo.configure(values=headers)
        if reset_selection:
            self.filter_column_var.set("")
            self.rename_column_var.set(headers[0] if headers else "")

    def _update_rename_rule_text(self) -> None:
        if not self.column_renames:
            self.rename_rules_var.set(self._t("no_rename_rules"))
            return
        summary = " · ".join(
            f"{source} → {target}"
            for source, target in self.column_renames.items()
        )
        self.rename_rules_var.set(summary)

    def _show_rows(
        self,
        headers: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        self.table.delete(*self.table.get_children())
        self.table.configure(columns=headers)
        for header in headers:
            self.table.heading(header, text=header)
            self.table.column(header, width=145, minwidth=90, stretch=True)
        for row_index, row in enumerate(rows[:1000]):
            self.table.insert(
                "",
                "end",
                values=[row.get(header, "") for header in headers],
                tags=("even" if row_index % 2 == 0 else "odd",),
            )
        self.table.tag_configure("even", background="#FFFFFF")
        self.table.tag_configure("odd", background="#F8FAFC")

    def _append_log(self, message: str) -> None:
        self.log_messages.append(message)
        self.log.configure(state="normal")
        self.log.insert("end", f"• {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def main() -> None:
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    BusinessDataStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
