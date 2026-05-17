# Star Wars Enemies - Savage Worlds Explorer Edition

A JSON repository of **163+ Star Wars enemies** for use with the Savage Worlds Explorer Edition ruleset. Includes a **GM Helper** desktop app for enemy selection, initiative, and combat tracking.

## Contents

- **starwars_enemies.json** - Complete enemy database with Savage Worlds stats
- **gm_helper.py** - GM Helper app for enemy selection and combat tracking
- **enemy_editor.py** - Editor to view and modify enemy entries in the JSON

## Quick Start

```bash
python gm_helper.py
```

To edit enemies:
```bash
python enemy_editor.py
```

**Requirements:** Python 3.12+ (uses only standard library; no pip install needed)

---

## GM Helper - How to Use

### Tab 1: Select Enemies

1. **Search** - Type in the search box to filter by enemy name or description
2. **Faction filter** - Use the dropdown to show only Imperial Forces, Rebel Forces, Separatist, Criminals, Bounty Hunters, Creatures, etc.
3. **Select enemies** - Click to select one or more from the list (alphabetically sorted)
4. **Set quantity** - Enter how many of each enemy (1–20)
5. **Add to Combat** - Click the button or double-click an enemy to add to your combat roster
6. **Remove/Clear** - Use "Remove Selected" or "Clear All" to adjust your roster

**Wild cards** (bosses/elites) are marked with ★ and shown in gold during combat.

### Tab 2: Combat

1. **Start Combat** - Click after adding enemies in Tab 1
2. **Draw Initiative Cards** - Assigns Savage Worlds initiative (standard deck with jokers)
3. **Track combat** - For each combatant:
   - **Wounds** - Use +/- buttons (each wound = -1 to Pace and trait rolls, max -3)
   - **Shaken** - Check the box when shaken
   - **Out** - Mark eliminated
4. **Reference window** - Opens automatically with full stat blocks for all combatants; updates when wounds change
5. **New Combat** - Clear and reselect enemies for a fresh encounter

---

## GM Helper - Capabilities

| Feature | Description |
|---------|-------------|
| **Enemy browser** | Search and filter 163+ Star Wars enemies by name, description, or faction |
| **Combat roster** | Add multiple of any enemy; duplicates get numbered (e.g., Stormtrooper #1, #2) |
| **Savage Worlds initiative** | Card-based initiative with jokers (+2 to rolls) |
| **Wound tracking** | Track 0–4 wounds; applies -1 penalty per wound to Pace and trait rolls (max -3) |
| **Shaken status** | Mark combatants as shaken; shown in initiative order |
| **Wild card highlight** | Boss/elite NPCs (Wild Cards) shown in gold |
| **Combat Reference window** | Separate window with full stat blocks; attributes, skills, gear, edges, hindrances, special abilities |
| **Live stat updates** | Reference window updates wound penalties in real time |
| **Dynamic layout** | Reference text boxes size to content |

---

## Stat Block Format

Each enemy includes:
- **faction** - Group for filtering (Imperial Forces, Rebel Forces, Separatist, Criminals, Bounty Hunters, Creatures, Force Users Sith/Jedi, Republic Era, Yuuzhan Vong, Xenvari)
- **wild_card** - true for Savage Worlds Wild Cards (Aces)
- **attributes** - Agility, Smarts, Spirit, Strength, Vigor (d4–d12)
- **skills** - Fighting, Shooting, and other relevant skills
- **pace**, **parry**, **toughness**, **armor**
- **hindrances**, **edges**, **gear**, **special_abilities**
- **description** - Brief lore/flavor text

## Enemy Categories

| Category | Examples |
|----------|----------|
| Imperial Forces | Stormtrooper, Navy Trooper, TIE Pilot, Death Star Gunner, Royal Guard, AT-AT Driver |
| Rebel Forces | Rebel Soldier, Rebel Pilot, Rebel Commando, Ewok Warrior |
| Separatist | B1/B2 Droids, Droideka, Magnaguard, Geonosian, Neimoidian |
| Criminals | Black Sun, Hutt Cartel, Pyke, Smuggler, Pirate |
| Bounty Hunters | Bounty Hunter, Trandoshan Hunter |
| Creatures | Rancor, Wampa, Krayt Dragon, Acklay, Tusken, Jawas, fauna |
| Force Users (Sith) | Sith Acolyte, Inquisitor, Nightsister, Knights of Ren |
| Force Users (Jedi) | Jedi Padawan |
| Republic Era | Clone Trooper, ARC Trooper, Wookiee, Gungan, Mon Calamari |
| Yuuzhan Vong | Yuuzhan Vong Warrior, Shaper |
| Xenvari | Patriarch, Purestrain, Carnifex, Hive Tyrant, Lictor |

## Ruleset

Designed for **Savage Worlds Explorer Edition** (SWEE). Damage notation: 2d8 = two d8 dice; 24/48/96 = range in inches (Short/Medium/Long).
