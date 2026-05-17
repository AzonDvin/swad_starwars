#!/usr/bin/env python3
"""
Star Wars Enemy Editor - View and modify entries in starwars_enemies.json
"""

import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

FONT = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)

JSON_PATH = Path(__file__).parent / "starwars_enemies.json"
FACTIONS = [
    "imperial_forces", "rebel_forces", "separatist", "criminals",
    "bounty_hunters", "creatures", "force_users_sith", "force_users_jedi",
    "republic_era", "yuuzhan_vong", "xenvari",
]


def load_data():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def parse_dict_text(text: str) -> dict:
    """Parse 'key: value' lines into dict."""
    result = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def parse_list_text(text: str) -> list:
    """Parse lines or comma-separated into list."""
    if not text.strip():
        return []
    items = []
    for line in text.strip().splitlines():
        for part in line.split(","):
            p = part.strip()
            if p:
                items.append(p)
    return items


def dict_to_text(d: dict) -> str:
    return "\n".join(f"{k}: {v}" for k, v in sorted(d.items()))


def list_to_text(lst: list) -> str:
    return "\n".join(lst) if lst else ""


class EnemyEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Star Wars Enemy Editor")
        self.minsize(900, 600)
        self.geometry("1100x700")

        self.data = load_data()
        self.enemies = self.data["enemies"]
        self.current_index = -1

        # Paned window
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: list + search
        left = ttk.Frame(paned)
        ttk.Label(left, text="Enemies", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_list())
        ttk.Entry(left, textvariable=self.search_var, width=25).pack(fill=tk.X, pady=(0, 5))
        self.listbox = tk.Listbox(left, font=FONT, height=30, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        scroll = ttk.Scrollbar(left)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.listbox.yview)
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add New", command=self._add_new).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Delete", command=self._delete).pack(side=tk.LEFT)
        paned.add(left, weight=1)

        # Right: edit form (scrollable)
        right = ttk.Frame(paned)
        canvas = tk.Canvas(right)
        scrollbar = ttk.Scrollbar(right)
        form_frame = ttk.Frame(canvas)
        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        form_frame.bind("<Configure>", _on_frame_configure)
        canvas_window = canvas.create_window((0, 0), window=form_frame, anchor=tk.NW)
        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(form_frame, text="Edit Entry", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10)
        )
        row = 1

        # name
        ttk.Label(form_frame, text="Name:").grid(row=row, column=0, sticky=tk.W, padx=(0, 8))
        self.var_name = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_name, width=40).grid(
            row=row, column=1, sticky=tk.EW, pady=2
        )
        row += 1

        # id (read-only or editable)
        ttk.Label(form_frame, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=(0, 8))
        self.var_id = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_id, width=10, state=tk.DISABLED).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1

        # faction
        ttk.Label(form_frame, text="Faction:").grid(row=row, column=0, sticky=tk.W, padx=(0, 8))
        self.var_faction = tk.StringVar()
        ttk.Combobox(
            form_frame, textvariable=self.var_faction, values=FACTIONS, width=22, state="readonly"
        ).grid(row=row, column=1, sticky=tk.W, pady=2)
        row += 1

        # pace, parry, toughness, armor
        ttk.Label(form_frame, text="Pace / Parry / Toughness / Armor:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 8)
        )
        sub = ttk.Frame(form_frame)
        sub.grid(row=row, column=1, sticky=tk.W, pady=2)
        self.var_pace = tk.StringVar()
        self.var_parry = tk.StringVar()
        self.var_toughness = tk.StringVar()
        self.var_armor = tk.StringVar()
        for i, (lbl, var) in enumerate([
            ("Pace", self.var_pace), ("Parry", self.var_parry),
            ("Toughness", self.var_toughness), ("Armor", self.var_armor)
        ]):
            ttk.Label(sub, text=lbl + ":").grid(row=0, column=i * 2, padx=(10 if i else 0, 2))
            ttk.Spinbox(sub, textvariable=var, from_=0, to=99, width=5).grid(
                row=0, column=i * 2 + 1, padx=(0, 8)
            )
        row += 1

        # wild_card
        ttk.Label(form_frame, text="Wild Card:").grid(row=row, column=0, sticky=tk.W, padx=(0, 8))
        self.var_wild_card = tk.BooleanVar()
        ttk.Checkbutton(form_frame, variable=self.var_wild_card).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1

        # description
        ttk.Label(form_frame, text="Description:").grid(row=row, column=0, sticky=tk.NW, padx=(0, 8))
        self.var_description = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_description, width=50).grid(
            row=row, column=1, sticky=tk.EW, pady=2
        )
        row += 1

        # attributes (dict)
        ttk.Label(form_frame, text="Attributes\n(key: value):").grid(
            row=row, column=0, sticky=tk.NW, padx=(0, 8)
        )
        self.text_attributes = tk.Text(form_frame, height=6, width=45, font=FONT_SMALL)
        self.text_attributes.grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1

        # skills (dict)
        ttk.Label(form_frame, text="Skills\n(key: value):").grid(
            row=row, column=0, sticky=tk.NW, padx=(0, 8)
        )
        self.text_skills = tk.Text(form_frame, height=8, width=45, font=FONT_SMALL)
        self.text_skills.grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1

        # hindrances (list)
        ttk.Label(form_frame, text="Hindrances\n(one per line):").grid(
            row=row, column=0, sticky=tk.NW, padx=(0, 8)
        )
        self.text_hindrances = tk.Text(form_frame, height=3, width=45, font=FONT_SMALL)
        self.text_hindrances.grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1

        # edges (list)
        ttk.Label(form_frame, text="Edges\n(one per line):").grid(
            row=row, column=0, sticky=tk.NW, padx=(0, 8)
        )
        self.text_edges = tk.Text(form_frame, height=3, width=45, font=FONT_SMALL)
        self.text_edges.grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1

        # gear (list)
        ttk.Label(form_frame, text="Gear\n(one per line):").grid(
            row=row, column=0, sticky=tk.NW, padx=(0, 8)
        )
        self.text_gear = tk.Text(form_frame, height=4, width=45, font=FONT_SMALL)
        self.text_gear.grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1

        # special_abilities (list)
        ttk.Label(form_frame, text="Special Abilities\n(one per line):").grid(
            row=row, column=0, sticky=tk.NW, padx=(0, 8)
        )
        self.text_special = tk.Text(form_frame, height=3, width=45, font=FONT_SMALL)
        self.text_special.grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1

        form_frame.columnconfigure(1, weight=1)

        # Save button
        ttk.Button(form_frame, text="Save Changes", command=self._save).grid(
            row=row, column=1, sticky=tk.W, pady=10
        )

        paned.add(right, weight=2)

        self._filtered = []
        self._refresh_list()

    def _refresh_list(self):
        q = self.search_var.get().strip().lower()
        self._filtered = [
            e for e in self.enemies
            if q in e.get("name", "").lower()
            or q in e.get("description", "").lower()
            or q in e.get("faction", "").lower()
        ]
        self._filtered.sort(key=lambda e: e["name"].lower())
        self.listbox.delete(0, tk.END)
        for e in self._filtered:
            wc = " ★" if e.get("wild_card") else ""
            self.listbox.insert(tk.END, f"{e['name']} [{e.get('faction','')}]{wc}")

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = self.listbox.index(sel[0])
        if idx < len(self._filtered):
            self._load_entry(self._filtered[idx])

    def _find_index_in_enemies(self, e: dict) -> int:
        for i, x in enumerate(self.enemies):
            if x.get("id") == e.get("id") and x.get("name") == e.get("name"):
                return i
        return -1

    def _load_entry(self, e: dict):
        self.current_index = self._find_index_in_enemies(e)
        if self.current_index < 0:
            return
        self.var_id.set(str(e.get("id", "")))
        self.var_name.set(e.get("name", ""))
        self.var_faction.set(e.get("faction", ""))
        self.var_pace.set(str(e.get("pace", 6)))
        self.var_parry.set(str(e.get("parry", 4)))
        self.var_toughness.set(str(e.get("toughness", 6)))
        self.var_armor.set(str(e.get("armor", 0)))
        self.var_wild_card.set(bool(e.get("wild_card", False)))
        self.var_description.set(e.get("description", ""))
        self.text_attributes.delete(1.0, tk.END)
        self.text_attributes.insert(tk.END, dict_to_text(e.get("attributes", {})))
        self.text_skills.delete(1.0, tk.END)
        self.text_skills.insert(tk.END, dict_to_text(e.get("skills", {})))
        self.text_hindrances.delete(1.0, tk.END)
        self.text_hindrances.insert(tk.END, list_to_text(e.get("hindrances", [])))
        self.text_edges.delete(1.0, tk.END)
        self.text_edges.insert(tk.END, list_to_text(e.get("edges", [])))
        self.text_gear.delete(1.0, tk.END)
        self.text_gear.insert(tk.END, list_to_text(e.get("gear", [])))
        self.text_special.delete(1.0, tk.END)
        self.text_special.insert(tk.END, list_to_text(e.get("special_abilities", [])))

    def _collect_form(self) -> dict | None:
        try:
            pace = int(self.var_pace.get())
            parry = int(self.var_parry.get())
            toughness = int(self.var_toughness.get())
            armor = int(self.var_armor.get())
        except ValueError:
            messagebox.showerror("Error", "Pace, Parry, Toughness, and Armor must be numbers.")
            return None
        attrs = parse_dict_text(self.text_attributes.get(1.0, tk.END))
        skills = parse_dict_text(self.text_skills.get(1.0, tk.END))
        hindrances = parse_list_text(self.text_hindrances.get(1.0, tk.END))
        edges = parse_list_text(self.text_edges.get(1.0, tk.END))
        gear = parse_list_text(self.text_gear.get(1.0, tk.END))
        special = parse_list_text(self.text_special.get(1.0, tk.END))
        return {
            "id": int(self.var_id.get()) if self.var_id.get().isdigit() else 0,
            "name": self.var_name.get().strip(),
            "attributes": attrs,
            "skills": skills,
            "pace": pace,
            "parry": parry,
            "toughness": toughness,
            "armor": armor,
            "hindrances": hindrances,
            "edges": edges,
            "gear": gear,
            "special_abilities": special,
            "description": self.var_description.get().strip(),
            "faction": self.var_faction.get(),
            "wild_card": self.var_wild_card.get(),
        }

    def _save(self):
        if self.current_index < 0:
            messagebox.showwarning("No Selection", "Select an entry to save.")
            return
        data = self._collect_form()
        if not data:
            return
        if not data["name"]:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        self.enemies[self.current_index] = data
        save_data(self.data)
        messagebox.showinfo("Saved", f"Saved '{data['name']}'.")
        self._refresh_list()

    def _add_new(self):
        max_id = max((e.get("id", 0) for e in self.enemies), default=0)
        new_id = max_id + 1
        new_entry = {
            "id": new_id,
            "name": f"New Enemy {new_id}",
            "attributes": {"Agility": "d6", "Smarts": "d6", "Spirit": "d6", "Strength": "d6", "Vigor": "d6"},
            "skills": {"Fighting": "d6", "Shooting": "d6", "Notice": "d6"},
            "pace": 6,
            "parry": 5,
            "toughness": 6,
            "armor": 0,
            "hindrances": [],
            "edges": [],
            "gear": [],
            "special_abilities": [],
            "description": "",
            "faction": "imperial_forces",
            "wild_card": False,
        }
        self.enemies.append(new_entry)
        save_data(self.data)
        self._refresh_list()
        self.current_index = len(self.enemies) - 1
        self._load_entry(new_entry)
        messagebox.showinfo("Added", f"Created new entry. Edit and save to confirm.")

    def _delete(self):
        if self.current_index < 0:
            messagebox.showwarning("No Selection", "Select an entry to delete.")
            return
        name = self.enemies[self.current_index].get("name", "?")
        if not messagebox.askyesno("Delete", f"Delete '{name}'?"):
            return
        del self.enemies[self.current_index]
        self.current_index = -1
        # Reassign IDs
        for i, e in enumerate(self.enemies):
            e["id"] = i + 1
        save_data(self.data)
        self._refresh_list()
        # Clear form
        self.var_name.set("")
        self.var_id.set("")
        self.var_faction.set("")
        self.var_pace.set("6")
        self.var_parry.set("5")
        self.var_toughness.set("6")
        self.var_armor.set("0")
        self.var_wild_card.set(False)
        self.var_description.set("")
        self.text_attributes.delete(1.0, tk.END)
        self.text_skills.delete(1.0, tk.END)
        self.text_hindrances.delete(1.0, tk.END)
        self.text_edges.delete(1.0, tk.END)
        self.text_gear.delete(1.0, tk.END)
        self.text_special.delete(1.0, tk.END)
        messagebox.showinfo("Deleted", f"Removed '{name}'.")


def main():
    app = EnemyEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
