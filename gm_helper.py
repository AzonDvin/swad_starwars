#!/usr/bin/env python3
"""
Star Wars Savage Worlds GM Helper
Python 3.12 - Enemy selection and combat management for Savage Worlds Explorer Edition
"""

import json
import random
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Font: Segoe UI 12pt; reference window uses 11pt
FONT = ("Segoe UI", 12)
REFERENCE_FONT = ("Segoe UI", 11)

# Savage Worlds standard deck for initiative
CARD_VALUES = {
    "A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8,
    "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2
}
SUITS = ["♠", "♥", "♦", "♣"]


def load_enemies() -> list[dict]:
    """Load enemies from JSON file."""
    json_path = Path(__file__).parent / "starwars_enemies.json"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    return data["enemies"]


def build_deck() -> list[tuple[str, str]]:
    """Build standard 54-card Savage Worlds deck (52 + 2 jokers)."""
    deck = []
    for suit in SUITS:
        for rank in CARD_VALUES:
            deck.append((rank, suit))
    deck.append(("Joker", ""))
    deck.append(("Joker", ""))
    return deck


def wound_penalty(wounds: int) -> int:
    """Each wound gives -1 to Pace and trait rolls, max -3."""
    return min(wounds, 3)


def draw_initiative(combatants: list) -> list[tuple]:
    """Assign initiative cards. Wild Cards draw two and keep the best (core SWADE rule)."""
    deck = build_deck()
    random.shuffle(deck)
    results = []
    card_index = 0

    def draw_one():
        nonlocal deck, card_index
        if card_index >= len(deck):
            deck = build_deck()
            random.shuffle(deck)
            card_index = 0
        rank, suit = deck[card_index]
        card_index += 1
        if rank == "Joker":
            return 100, "JOKER!"
        return CARD_VALUES[rank], f"{rank}{suit}"

    for c in combatants:
        card_val, card_str = draw_one()
        if c.get("wild_card", False):
            card_val2, card_str2 = draw_one()
            if card_val2 > card_val:
                card_val, card_str = card_val2, card_str2
        results.append((c, card_val, card_str))
    results.sort(key=lambda x: (-x[1], x[0]["display_name"]))
    return results


class EnemySelector(tk.Frame):
    """Frame for browsing and selecting enemies."""

    def __init__(self, parent, enemies: list, on_select, **kwargs):
        super().__init__(parent, **kwargs)
        self.enemies = enemies
        self.on_select = on_select
        self.selected: dict[str, int] = {}  # name -> quantity

        # ── Filter bar ──────────────────────────────────────────────────────────
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        ttk.Entry(filter_frame, textvariable=self.search_var, width=28).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        ttk.Label(filter_frame, text="Faction:").pack(side=tk.LEFT, padx=(0, 4))
        self.faction_var = tk.StringVar(value="All Factions")
        _raw = set(e.get("faction", "other") for e in self.enemies)
        _order = [
            "imperial_forces", "rebel_forces", "separatist", "criminals", "bounty_hunters",
            "creatures", "force_users_sith", "force_users_jedi", "republic_era", "yuuzhan_vong",
            "broodika",
        ]
        _sorted = [f for f in _order if f in _raw] + sorted(_raw - set(_order))
        _labels = {
            "imperial_forces": "Imperial Forces",
            "rebel_forces": "Rebel Forces",
            "separatist": "Separatist",
            "criminals": "Criminals",
            "bounty_hunters": "Bounty Hunters",
            "creatures": "Creatures",
            "force_users_sith": "Force Users (Sith)",
            "force_users_jedi": "Force Users (Jedi)",
            "republic_era": "Republic Era",
            "yuuzhan_vong": "Yuuzhan Vong",
            "broodika": "Broodika",
        }
        self._faction_labels = _labels
        self._faction_label_to_raw = {v: k for k, v in _labels.items()}
        factions = ["All Factions"] + [_labels.get(f, f.replace("_", " ").title()) for f in _sorted]
        ttk.Combobox(filter_frame, textvariable=self.faction_var, values=factions, state="readonly", width=22).pack(side=tk.LEFT)
        self.faction_var.trace_add("write", lambda *a: self._refresh_list())

        # ── Action bar (qty + buttons) ───────────────────────────────────────────
        action_bar = ttk.Frame(self)
        action_bar.pack(fill=tk.X, padx=8, pady=(0, 4))
        ttk.Label(action_bar, text="Qty:").pack(side=tk.LEFT, padx=(0, 4))
        self.qty_var = tk.StringVar(value="1")
        ttk.Spinbox(action_bar, from_=1, to=20, textvariable=self.qty_var, width=4).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_bar, text="Add to Combat ↓", command=self._add_selected).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(action_bar, text="Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(action_bar, text="Clear All", command=self.clear_selection).pack(side=tk.LEFT)

        # ── Horizontal split: list (left) | details + selected (right) ──────────
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Left: enemy listbox
        left = ttk.Frame(paned)
        paned.add(left, weight=2)
        self.listbox = tk.Listbox(left, font=FONT, selectmode=tk.EXTENDED)
        sb_left = ttk.Scrollbar(left, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sb_left.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_left.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind("<<ListboxSelect>>", self._on_list_select)
        self.listbox.bind("<Double-1>", self._on_double_click)

        # Right: details (top, expands) + selected (bottom, fixed)
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        detail_frame = ttk.LabelFrame(right, text="Enemy Details")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        self.detail_text = scrolledtext.ScrolledText(detail_frame, font=FONT, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        sel_frame = ttk.LabelFrame(right, text="Selected for Combat")
        sel_frame.pack(fill=tk.X)
        self.selected_text = scrolledtext.ScrolledText(sel_frame, height=5, font=FONT, state=tk.DISABLED)
        self.selected_text.pack(fill=tk.X, padx=6, pady=(4, 6))

        self._filtered_enemies: list[dict] = []
        self._refresh_list()

    def _refresh_list(self):
        query = self.search_var.get().strip().lower()
        faction_sel = self.faction_var.get()
        faction_raw = self._faction_label_to_raw.get(faction_sel, faction_sel) if faction_sel != "All Factions" else None
        self._filtered_enemies = [
            e for e in self.enemies
            if (query in e["name"].lower() or (e.get("description", "") and query in e["description"].lower()))
            and (faction_raw is None or e.get("faction", "other") == faction_raw)
        ]
        self._filtered_enemies.sort(key=lambda e: e["name"].lower())
        self.listbox.delete(0, tk.END)
        _labels = getattr(self, "_faction_labels", {})
        for e in self._filtered_enemies:
            fac_raw = e.get("faction", "other")
            fac = _labels.get(fac_raw, fac_raw.replace("_", " ").title())
            wc = " ★" if e.get("wild_card", False) else ""
            self.listbox.insert(tk.END, f"{e['name']} [{fac}]{wc} (P:{e['parry']} T:{e['toughness']})")

    def _on_search(self, *args):
        self._refresh_list()

    def _on_list_select(self, event):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            if idx < len(self._filtered_enemies):
                self._show_detail(self._filtered_enemies[idx])

    def _on_double_click(self, event):
        self._add_selected()

    def _show_detail(self, enemy: dict):
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        attrs = enemy.get("attributes", {})
        skills = enemy.get("skills", {})
        attrs_str = " ".join(f"{k}:{v}" for k, v in attrs.items())
        skills_str = " ".join(f"{k}:{v}" for k, v in skills.items())
        faction = enemy.get("faction", "")
        lines = [
            f"{enemy['name']}",
            *([f"Faction: {faction}"] if faction else []),
            f"Parry: {enemy['parry']}  Toughness: {enemy['toughness']} ({enemy.get('armor', 0)} armor)  Pace: {enemy['pace']}",
            f"Attributes: {attrs_str}",
            f"Skills: {skills_str}",
            f"Gear: {', '.join(enemy.get('gear', []))}",
            f"Edges: {', '.join(enemy.get('edges', [])) or 'None'}",
            f"Special: {', '.join(enemy.get('special_abilities', [])) or 'None'}",
            f"--- {enemy.get('description', '')}",
        ]
        self.detail_text.insert(tk.END, "\n".join(lines))
        self.detail_text.config(state=tk.DISABLED)

    def _add_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Select one or more enemies from the list.")
            return
        try:
            qty = max(1, int(self.qty_var.get()))
        except ValueError:
            qty = 1
        for idx in sel:
            if idx < len(self._filtered_enemies):
                e = self._filtered_enemies[idx]
                name = e["name"]
                self.selected[name] = self.selected.get(name, 0) + qty
        self._update_selected_display()

    def _remove_selected(self):
        """Remove selected enemy types from combat roster."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Select one or more enemies from the list to remove.")
            return
        for idx in sel:
            if idx < len(self._filtered_enemies):
                name = self._filtered_enemies[idx]["name"]
                if name in self.selected:
                    del self.selected[name]
        self._update_selected_display()

    def _update_selected_display(self):
        self.selected_text.config(state=tk.NORMAL)
        self.selected_text.delete(1.0, tk.END)
        if not self.selected:
            self.selected_text.insert(tk.END, "(none)")
        else:
            lines = []
            for name, qty in sorted(self.selected.items()):
                lines.append(f"  {qty}x {name}")
            self.selected_text.insert(tk.END, "\n".join(lines))
        self.selected_text.config(state=tk.DISABLED)

    def get_combatants(self) -> list[dict]:
        """Return flat list of combatants (each with display_name for duplicates)."""
        result = []
        for name, qty in self.selected.items():
            enemy = next(e for e in self.enemies if e["name"] == name)
            for i in range(qty):
                copy = enemy.copy()
                copy["display_name"] = f"{name}" if qty == 1 else f"{name} #{i+1}"
                result.append(copy)
        return result

    def clear_selection(self):
        self.selected.clear()
        self._update_selected_display()


class CombatManager(tk.Frame):
    """Frame for managing combat: initiative, wounds, status."""

    def __init__(self, parent, combatants: list, reference_window=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.combatants = combatants
        self.reference_window = reference_window
        # Style for Wild Card / Ace entries (gold color)
        self._wild_card_style = None
        try:
            style = ttk.Style()
            style.configure("WildCard.TLabel", foreground="#B8860B")  # darkgoldenrod
            self._wild_card_style = "WildCard.TLabel"
            style.configure("Out.TLabel", foreground="#808080")
            style.configure("Out.TButton", foreground="#808080")
            style.configure("Out.TCheckbutton", foreground="#808080")
        except tk.TclError:
            pass
        self.initiative_order: list[tuple] = []
        self.wounds: dict[str, int] = {}
        self.shaken: dict[str, bool] = {}
        self.eliminated: set[str] = set()
        self.bennies: dict[str, int] = {}
        self.round_num: int = 0

        # Combat header: draw button + round counter on one row
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))
        ttk.Button(header, text="Draw Initiative Cards", command=self._draw_initiative).pack(side=tk.LEFT, padx=(0, 16))
        self.round_label = ttk.Label(header, text="Round: —", font=("Segoe UI", 13, "bold"))
        self.round_label.pack(side=tk.LEFT)

        # Combatant cards (initiative + stats + tracking combined)
        self.card_frames: dict[str, ttk.Frame] = {}
        self.scroll_frame = None
        self._build_combatant_cards()

    def _draw_initiative(self):
        self.round_num += 1
        self.round_label.config(text=f"Round: {self.round_num}")
        self.initiative_order = draw_initiative(self.combatants)
        self._refresh_combatant_cards()

    def _build_combatant_cards(self):
        cards_container = ttk.LabelFrame(self, text="Initiative & Combat Tracking")
        cards_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        canvas = tk.Canvas(cards_container)
        scrollbar = ttk.Scrollbar(cards_container)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=canvas.yview)
        self.scroll_frame = scroll_frame

        # Order: initiative order if drawn, else combatants order
        ordered = []
        if self.initiative_order:
            ordered = [(c, val, card_str) for c, val, card_str in self.initiative_order]
        else:
            ordered = [(c, None, None) for c in self.combatants]

        for i, item in enumerate(ordered, 1):
            c = item[0]
            val, card_str = item[1], item[2]
            name = c["display_name"]
            self.wounds[name] = self.wounds.get(name, 0)
            self.shaken[name] = self.shaken.get(name, False)
            if name not in self.bennies:
                self.bennies[name] = 3 if c.get("wild_card", False) else 0
            f = ttk.Frame(scroll_frame)
            f.pack(fill=tk.X, padx=5, pady=3)
            self.card_frames[name] = f
            init_info = (i, card_str, val == 100) if val is not None else None
            self._build_one_card(f, c, init_info)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    @staticmethod
    def _wound_penalty(wounds: int) -> int:
        """Each wound = -1 to Pace and trait rolls, max -3."""
        return min(wounds, 3)

    def _build_one_card(self, parent: ttk.Frame, c: dict, init_info=None):
        """init_info: (position, card_str, is_joker) or None."""
        name = c["display_name"]
        for w in parent.winfo_children():
            w.destroy()
        row = ttk.Frame(parent)
        row.pack(fill=tk.X)
        row.columnconfigure(1, weight=1)
        # Initiative column (left)
        init_str = "—"
        if init_info:
            pos, card_str, is_joker = init_info
            joker_note = " (+2!)" if is_joker else ""
            init_str = f"{pos}. {card_str}{joker_note}"
        init_lbl = ttk.Label(row, text=init_str, width=18, anchor=tk.W)
        init_lbl.grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        parent._init_lbl = init_lbl
        # Name and stats - gold color for wild cards; Pace shows effective when wounded
        penalty = self._wound_penalty(self.wounds.get(name, 0))
        base_pace = c["pace"]
        eff_pace = max(0, base_pace - penalty)
        if penalty > 0:
            pace_str = f"Pace:{base_pace}→{eff_pace}"
        else:
            pace_str = f"Pace:{base_pace}"
        stat_str = f"P:{c['parry']} T:{c['toughness']} {pace_str}"
        status = ""
        if name in self.eliminated:
            status = " [OUT]"
        elif self.shaken.get(name):
            status = " [SHAKEN]"
        if penalty > 0:
            status += f" [-{penalty}]"
        name_style = "WildCard.TLabel" if c.get("wild_card", False) else "TLabel"
        name_lbl = ttk.Label(row, text=f"{name} ({stat_str}){status}", style=name_style)
        name_lbl.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        # Tracking section - right-aligned for consistent alignment across all cards
        track_frame = ttk.Frame(row)
        track_frame.grid(row=0, column=2, sticky=tk.E, padx=(0, 5))
        track_frame.columnconfigure(0, minsize=52)   # "Wounds:"
        track_frame.columnconfigure(1, minsize=24)  # Wound value
        track_frame.columnconfigure(2, minsize=28)
        track_frame.columnconfigure(3, minsize=28)
        wounds_header = ttk.Label(track_frame, text="Wounds:")
        wounds_header.grid(row=0, column=0, sticky=tk.W, padx=(0, 4))
        wound_lbl = ttk.Label(track_frame, text="0", width=3, anchor=tk.CENTER)
        wound_lbl.grid(row=0, column=1, padx=2, sticky=tk.EW)
        minus_btn = ttk.Button(track_frame, text="-", width=2, command=lambda: self._wound_change(name, wound_lbl, -1))
        minus_btn.grid(row=0, column=2, padx=1)
        plus_btn = ttk.Button(track_frame, text="+", width=2, command=lambda: self._wound_change(name, wound_lbl, 1))
        plus_btn.grid(row=0, column=3, padx=1)
        shaken_var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(track_frame, text="Shaken", variable=shaken_var,
                             command=lambda: self._set_shaken(name, shaken_var.get()))
        cb.grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        out_btn = ttk.Button(track_frame, text="Out", command=lambda: self._eliminate(name))
        out_btn.grid(row=0, column=5, padx=(0, 0))
        # Benny tracking — Wild Cards only
        benny_lbl = None
        if c.get("wild_card", False):
            track_frame.columnconfigure(6, minsize=10)   # spacer
            track_frame.columnconfigure(7, minsize=52)   # "Bennies:"
            track_frame.columnconfigure(8, minsize=24)   # benny value
            track_frame.columnconfigure(9, minsize=28)
            track_frame.columnconfigure(10, minsize=28)
            ttk.Label(track_frame, text="Bennies:", foreground="#B8860B").grid(row=0, column=7, sticky=tk.W, padx=(10, 4))
            benny_lbl = ttk.Label(track_frame, text=str(self.bennies.get(name, 3)), width=3, anchor=tk.CENTER)
            benny_lbl.grid(row=0, column=8, padx=2, sticky=tk.EW)
            ttk.Button(track_frame, text="-", width=2, command=lambda: self._benny_change(name, -1)).grid(row=0, column=9, padx=1)
            ttk.Button(track_frame, text="+", width=2, command=lambda: self._benny_change(name, 1)).grid(row=0, column=10, padx=1)
        # Store refs for updates
        parent._wound_lbl = wound_lbl
        parent._benny_lbl = benny_lbl
        parent._shaken_var = shaken_var
        parent._name_lbl = name_lbl
        parent._combatant = c
        parent._out_widgets = [init_lbl, name_lbl, wounds_header, wound_lbl, minus_btn, plus_btn, cb, out_btn]

    def _benny_change(self, name: str, delta: int):
        self.bennies[name] = max(0, self.bennies.get(name, 0) + delta)
        self._refresh_combatant_cards()

    def _wound_change(self, name: str, wound_lbl: ttk.Label, delta: int):
        self.wounds[name] = max(0, min(4, self.wounds.get(name, 0) + delta))
        self._refresh_combatant_cards()

    def _set_wounds(self, name: str, val: str):
        try:
            self.wounds[name] = max(0, min(4, int(val)))
        except ValueError:
            pass
        self._refresh_combatant_cards()

    def _set_shaken(self, name: str, val: bool):
        self.shaken[name] = val
        self._refresh_combatant_cards()

    def _eliminate(self, name: str):
        self.eliminated.add(name)
        self.wounds[name] = 4  # Max wounds
        self._refresh_combatant_cards()

    def _refresh_combatant_cards(self):
        if not self.scroll_frame:
            return
        # Reorder: pack_forget all, then pack in initiative order
        order = [(c, val, card_str) for c, val, card_str in self.initiative_order] if self.initiative_order else [(c, None, None) for c in self.combatants]
        for f in self.card_frames.values():
            if f.winfo_exists():
                f.pack_forget()
        for i, item in enumerate(order, 1):
            c, val, card_str = item[0], item[1], item[2]
            name = c["display_name"]
            f = self.card_frames.get(name)
            if f and f.winfo_exists():
                f.pack(fill=tk.X, padx=5, pady=3)
                # Update initiative label
                if hasattr(f, "_init_lbl"):
                    init_str = f"{i}. {card_str}{' (+2!)' if val == 100 else ''}" if val is not None else "—"
                    f._init_lbl.config(text=init_str)
        # Update wound, shaken, name/status for all cards
        for c in self.combatants:
            name = c["display_name"]
            f = self.card_frames.get(name)
            if f and f.winfo_exists():
                w = self.wounds.get(name, 0)
                penalty = self._wound_penalty(w)
                if hasattr(f, "_wound_lbl"):
                    f._wound_lbl.config(text=str(w))
                if hasattr(f, "_benny_lbl") and f._benny_lbl is not None:
                    f._benny_lbl.config(text=str(self.bennies.get(name, 0)))
                if hasattr(f, "_shaken_var"):
                    f._shaken_var.set(self.shaken.get(name, False))
                if hasattr(f, "_name_lbl") and hasattr(f, "_combatant"):
                    base_pace = f._combatant["pace"]
                    eff_pace = max(0, base_pace - penalty)
                    pace_str = f"Pace:{base_pace}→{eff_pace}" if penalty > 0 else f"Pace:{base_pace}"
                    stat_str = f"P:{f._combatant['parry']} T:{f._combatant['toughness']} {pace_str}"
                    status = ""
                    if name in self.eliminated:
                        status = " [OUT]"
                    elif self.shaken.get(name):
                        status = " [SHAKEN]"
                    if penalty > 0:
                        status += f" [-{penalty}]"
                    f._name_lbl.config(text=f"{name} ({stat_str}){status}")
                # Grey out entire row when Out
                if hasattr(f, "_out_widgets"):
                    if name in self.eliminated:
                        for w in f._out_widgets:
                            try:
                                if isinstance(w, ttk.Label):
                                    w.config(style="Out.TLabel")
                                elif isinstance(w, ttk.Button):
                                    w.config(style="Out.TButton")
                                elif isinstance(w, ttk.Checkbutton):
                                    w.config(style="Out.TCheckbutton")
                            except tk.TclError:
                                pass
                    else:
                        for w in f._out_widgets:
                            try:
                                if isinstance(w, ttk.Label):
                                    style = "WildCard.TLabel" if w is f._name_lbl and f._combatant.get("wild_card") else "TLabel"
                                    w.config(style=style)
                                elif isinstance(w, ttk.Button):
                                    w.config(style="TButton")
                                elif isinstance(w, ttk.Checkbutton):
                                    w.config(style="TCheckbutton")
                            except tk.TclError:
                                pass
        if self.reference_window and self.reference_window.winfo_exists():
            self.reference_window.update_wounds(self.wounds)
            self.reference_window.update_eliminated(self.eliminated)


def format_combatant_stat_block(c: dict, wounds: dict | None = None) -> str:
    """Format a combatant's full stat block for display. If wounds dict provided, apply penalty to each trait/skill."""
    attrs = c.get("attributes", {})
    skills = c.get("skills", {})
    w = wounds.get(c["display_name"], 0) if wounds else 0
    penalty = wound_penalty(w)
    suffix = f" -{penalty}" if penalty > 0 else ""
    base_pace = c["pace"]
    eff_pace = max(0, base_pace - penalty)
    pace_str = f"{base_pace}→{eff_pace}" if penalty > 0 else str(base_pace)

    lines = [
        f"Parry: {c['parry']}   Toughness: {c['toughness']} ({c.get('armor', 0)} armor)   Pace: {pace_str}",
        "Attributes: " + ", ".join(f"{k[:3]}: {v}{suffix}" for k, v in attrs.items()),
        "Skills:",
    ]
    skill_items = [f"{k}: {v}{suffix}" for k, v in skills.items()]
    for i in range(0, len(skill_items), 3):
        lines.append("  " + ", ".join(skill_items[i:i + 3]))
    gear = c.get("gear", [])
    if gear:
        lines.extend(["Gear:", *[f"  • {g}" for g in gear]])
    edges = c.get("edges", [])
    if edges:
        lines.extend(["Edges:", *[f"  • {e}" for e in edges]])
    hindrances = c.get("hindrances", [])
    if hindrances:
        lines.extend(["Hindrances:", *[f"  • {h}" for h in hindrances]])
    special = c.get("special_abilities", [])
    if special:
        lines.extend(["Special:", *[f"  • {s}" for s in special]])
    if c.get("description"):
        lines.append("— " + c["description"])
    return "\n".join(lines)


class StatBlockPanel(ttk.Frame):
    """Embedded panel showing each combatant's full stat block, scrollable."""

    def __init__(self, parent, combatants: list, **kwargs):
        super().__init__(parent, **kwargs)

        ttk.Label(self, text="Stat Blocks", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, padx=8, pady=(6, 2))
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=(0, 4))

        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.combatants = combatants
        self.combatant_texts: dict[str, tuple[ttk.LabelFrame, scrolledtext.ScrolledText, dict]] = {}
        for c in combatants:
            name = c["display_name"]
            wc_marker = " ★" if c.get("wild_card") else ""
            block = format_combatant_stat_block(c)
            line_count = len(block.splitlines())
            text_height = max(6, min(40, line_count + 1))
            frame = ttk.LabelFrame(scroll_frame, text=f"{name}{wc_marker}")
            frame.pack(fill=tk.X, padx=8, pady=4)
            text = scrolledtext.ScrolledText(frame, height=text_height, font=REFERENCE_FONT, wrap=tk.WORD, state=tk.DISABLED)
            text.config(spacing1=0, spacing2=0, spacing3=0)
            text.tag_configure("block", lmargin1=12, lmargin2=12, rmargin=12)
            text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
            text.config(state=tk.NORMAL)
            text.insert(tk.END, block)
            text.tag_add("block", "1.0", tk.END)
            text.config(state=tk.DISABLED)
            self.combatant_texts[name] = (frame, text, c)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mousewheel scrolls this canvas when hovering over it
        def _on_enter(e):
            canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units"))
        def _on_leave(e):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        scroll_frame.bind("<Enter>", _on_enter)
        scroll_frame.bind("<Leave>", _on_leave)

    def update_wounds(self, wounds: dict):
        """Refresh stat blocks with current wound/penalty info."""
        if not self.winfo_exists():
            return
        for name, (frame, text_widget, c) in self.combatant_texts.items():
            block = format_combatant_stat_block(c, wounds)
            line_count = len(block.splitlines())
            text_height = max(6, min(40, line_count + 1))
            text_widget.config(height=text_height, state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, block)
            text_widget.tag_add("block", "1.0", tk.END)
            text_widget.config(state=tk.DISABLED)

    def update_eliminated(self, eliminated: set):
        """Dim stat blocks for eliminated combatants."""
        if not self.winfo_exists():
            return
        for name, (frame, text_widget, c) in self.combatant_texts.items():
            wc_marker = " ★" if c.get("wild_card") else ""
            if name in eliminated:
                frame.config(text=f"{name}{wc_marker}  —  OUT")
                text_widget.config(fg="#aaaaaa", bg="#f0f0f0")
            else:
                frame.config(text=f"{name}{wc_marker}")
                text_widget.config(fg="black", bg="white")


class GMHelperApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Star Wars Savage Worlds GM Helper")
        self.minsize(1100, 650)
        self.geometry("1400x850")

        # Load data
        try:
            self.enemies = load_enemies()
        except FileNotFoundError:
            messagebox.showerror("Error", "starwars_enemies.json not found. Place it next to gm_helper.py.")
            self.destroy()
            return
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON in starwars_enemies.json: {e}")
            self.destroy()
            return

        # ── Main horizontal split: left = tabs, right = stat blocks ─────────────
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left pane: notebook with Select + Combat tabs
        left = ttk.Frame(paned)
        paned.add(left, weight=3)

        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.selector = EnemySelector(self.notebook, self.enemies, self._on_combat_ready)
        self.notebook.add(self.selector, text="1. Select Enemies")

        self.combat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.combat_frame, text="2. Combat")
        self._show_combat_placeholder()

        self.combat_manager: StatBlockPanel | None = None

        # Right pane: stat block panel
        self.right_pane = ttk.Frame(paned)
        paned.add(self.right_pane, weight=2)
        self.stat_panel: StatBlockPanel | None = None
        self._show_stat_placeholder()

    def _show_combat_placeholder(self):
        ttk.Label(
            self.combat_frame,
            text="Select enemies in Tab 1, then click Start Combat.",
            wraplength=300,
        ).pack(pady=30, padx=20)
        ttk.Button(self.combat_frame, text="Start Combat", command=self._start_combat).pack(pady=8)

    def _show_stat_placeholder(self):
        for w in self.right_pane.winfo_children():
            w.destroy()
        ttk.Label(
            self.right_pane,
            text="Enemy stat blocks will appear here once combat starts.",
            wraplength=200,
            justify=tk.CENTER,
        ).pack(expand=True)

    def _on_combat_ready(self):
        pass

    def _start_combat(self):
        combatants = self.selector.get_combatants()
        if not combatants:
            messagebox.showinfo("No Combatants", "Select at least one enemy in the 'Select Enemies' tab first.")
            return

        # Populate right pane with stat blocks
        for w in self.right_pane.winfo_children():
            w.destroy()
        self.stat_panel = StatBlockPanel(self.right_pane, combatants)
        self.stat_panel.pack(fill=tk.BOTH, expand=True)

        # Build combat manager in Tab 2
        for w in self.combat_frame.winfo_children():
            w.destroy()
        self.combat_manager = CombatManager(self.combat_frame, combatants, self.stat_panel)
        self.combat_manager.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self.combat_frame, text="New Combat (Clear & Reselect)", command=self._new_combat).pack(pady=5)
        self.notebook.select(1)

    def _new_combat(self):
        self.selector.clear_selection()
        for w in self.combat_frame.winfo_children():
            w.destroy()
        self._show_combat_placeholder()
        self._show_stat_placeholder()
        self.stat_panel = None
        self.combat_manager = None
        self.notebook.select(0)


def main():
    app = GMHelperApp()
    if app.winfo_exists():
        app.mainloop()


if __name__ == "__main__":
    main()
