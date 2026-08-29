# QuestWordHunter — English Item Names

You are playing WoW in German, someone links an item in chat, and you have no idea what the guides call it. This adds the English name to the item tooltip, underneath the one the game already shows you.

168,833 items, straight from Blizzard's Game Data API.

It is a separate addon for one reason: size. Item names are around ten megabytes, roughly ninety percent of everything the English name data weighs. Spell and creature names are small enough that the [English Quest Panel](https://github.com/Ironship/WordHunterWoW-ENPanel) just ships them; these are not, so you decide whether you want them.

## What you need

- Retail 12.1 (`Interface 120100`)
- [QuestWordHunter - English Quest Panel](https://github.com/Ironship/WordHunterWoW-ENPanel) — this pack does nothing without it
- A client set to something other than English. On an English client the addon stays quiet, since there would be nothing to add.

## What it does not cover

Blizzard's API publishes 168,833 items, which is most but not all of what exists in the game files. An item it does not publish simply gets no extra line — the tooltip is left exactly as it was.

## Rebuild (maintainers)

From the English Quest Panel's `Tools`:

```
python Tools/fetch_names.py --kind item
python Tools/build_names_lua.py --kind item --out ../WordHunterWoW-ENPanel-Items/Data --chunk 40000
```

Commit the generated `Data/NamesItem_*.lua`.

All rights reserved.
