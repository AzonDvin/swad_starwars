# Star Wars Enemies - Savage Worlds Explorer Edition

A JSON repository of **100 Star Wars enemies** for use with the Savage Worlds Explorer Edition ruleset. Each enemy includes full stat blocks compatible with SWEE character/NPC format.

## Contents

- **starwars_enemies.json** - Complete enemy database with Savage Worlds stats
- **gm_helper.py** - GM Helper app for enemy selection and combat tracking

## GM Helper

Run `python gm_helper.py` to launch the GM Helper for selecting enemies and tracking combat.

## Stat Block Format

Each enemy includes:
- **faction** - Group (imperial, criminals, creatures, etc.) for filtering
- **wild_card** - true for boss/elite Savage Worlds Wild Cards (Aces)
- **attributes** - Agility, Smarts, Spirit, Strength, Vigor (d4-d12)
- **skills** - Fighting, Shooting, and other relevant skills
- **pace** - Movement per round
- **parry** - Defensive value (2 + half Fighting)
- **toughness** - Hit points (2 + half Vigor)
- **armor** - Armor value (included in toughness)
- **hindrances** - Character flaws
- **edges** - Special advantages
- **gear** - Weapons and equipment with damage/range
- **special_abilities** - Unique traits
- **description** - Brief lore/flavor text

## Enemy Categories

| Category | Examples |
|----------|----------|
| Imperial Forces | Stormtrooper, Death Trooper, TIE Pilot, Inquisitor |
| Separatist Droids | B1, B2, Droideka, Magnaguard |
| Criminals & Bounty Hunters | Bounty Hunter, Black Sun, Hutt Cartel, IG-88 |
| Creatures | Rancor, Wampa, Krayt Dragon, Acklay, Sarlacc |
| Force Users | Sith Acolyte, Imperial Inquisitor, Nightsister |
| Republic Era | Clone Trooper, ARC Trooper, Gungan Warrior |
| First Order | First Order Stormtrooper, Praetorian Guard, Knights of Ren |
| Aliens & Beasts | Tusken Raider, Trandoshan, Wookiee, various fauna |

## Ruleset

Designed for **Savage Worlds Explorer Edition** (SWEE). Damage notation: 2d8 = two d8 dice, 24/48/96 = range in inches (Short/Medium/Long).
