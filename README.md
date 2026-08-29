# QuestWordHunter — English Item Names

Someone links an item in chat, you are playing in German, and you have no idea what the guides call it.

This adds the English name to the item tooltip, underneath the one the game already shows you. **168,833 items.**

## Install

Unzip into `_retail_\Interface\AddOns\` and restart the game.

You need [QuestWordHunter - English Quest Panel](https://github.com/Ironship/WordHunterWoW-ENPanel) as well — this pack does nothing on its own.

Playing in English already? The addon stays quiet.

## Why is this a separate download

Item names are big — about ten megabytes, more than everything else in the panel put together. Spell and creature names come with the panel itself; these you take only if you want them.

A handful of items are not covered. Their tooltip is simply left alone.

Retail 12.1. All rights reserved.

## Rebuild (maintainers)

From the English Quest Panel's `Tools`:

```
python Tools/fetch_names.py --kind item
python Tools/build_names_lua.py --kind item --out ../WordHunterWoW-ENPanel-Items/Data --chunk 40000
```

Commit the generated `Data/NamesItem_*.lua`.
