-- Run from the addon root:  lua tests/register.test.lua
--
-- This addon does exactly one thing: hand its tables to the panel. That makes
-- it easy to break quietly -- adding data files to the toc but not passing them
-- on leaves an addon that loads, weighs ten megabytes and does nothing. The
-- test loads the real data the way the game does, from the toc, so it cannot
-- drift from what actually ships.

local captured

CreateFrame = function()
  local f = {}
  f.RegisterEvent = function() end
  f.SetScript = function(_, _, fn) f.fn = fn end
  return f
end

-- Every Lua file a toc loads, in the order the game loads them. There is one
-- toc per game and they list different data, so both are checked: a manifest
-- pointing at a file that is not there fails only on the game that reads it.
local function data_files(toc)
  local files = {}
  for line in io.lines(toc) do
    line = line:gsub("%s+$", "")
    if line:match("^Data/.+%.lua$") then files[#files + 1] = line end
  end
  assert(#files > 0, toc .. " lists no data files")
  return files
end

local function count(t)
  local n = 0
  for _ in pairs(t or {}) do n = n + 1 end
  return n
end

local function load_toc(toc)
  WordHunterWoW_ENNames_Item = nil
  WordHunterWoW_ENDesc_Item = nil
  local files = data_files(toc)
  for _, f in ipairs(files) do
    assert(io.open(f), toc .. " lists " .. f .. ", which is not in the package")
    dofile(f)
  end
  print("loaded " .. #files .. " data files from " .. toc)
  return files
end

load_toc("WordHunterWoW-ENPanel-Items_Vanilla.toc")
local classicNames = count(WordHunterWoW_ENNames_Item)
local classicDescs = count(WordHunterWoW_ENDesc_Item)
assert(classicNames > 15000 and classicNames < 40000,
       "Classic item names should be the Classic set, got " .. classicNames)
assert(classicDescs > 5000 and classicDescs < 20000,
       "Classic item descriptions should be the Classic set, got " .. classicDescs)
print(string.format("  Classic payload: %d names, %d descriptions", classicNames, classicDescs))

load_toc("WordHunterWoW-ENPanel-Items_Mainline.toc")

-- Missing panel: the addon must not error. It is a hard dependency, so this
-- should not happen, but failing loudly here would break the player's tooltips
-- rather than merely doing nothing.
WordHunterWoW_ENPanelNames = nil
assert(pcall(assert(loadfile("Bootstrap.lua")), "WordHunterWoW-ENPanel-Items"),
       "the addon raised when the panel was absent")
print("survives the panel being absent")

WordHunterWoW_ENPanelNames = {
  Register = function(kind, entries, texts)
    captured = { kind = kind, entries = entries, texts = texts }
    return true
  end,
}
assert(loadfile("Bootstrap.lua"))("WordHunterWoW-ENPanel-Items")

assert(captured, "the addon never registered anything with the panel")
assert(captured.kind == "item", "registered as " .. tostring(captured.kind))

local names = count(captured.entries)
assert(names > 160000, "expected the full item name set, got " .. names)
print(string.format("  %d item names registered", names))

-- The descriptions are the point of this version; before it they were built but
-- never passed on.
assert(captured.texts, "descriptions were loaded but never handed to the panel")
local descs = count(captured.texts)
assert(descs > 30000, "expected the full description set, got " .. descs)
print(string.format("  %d item descriptions registered", descs))

-- Every description must belong to an item that is actually named, or the
-- tooltip has text with nothing to attach it to.
local orphans = 0
for id in pairs(captured.texts) do
  if not captured.entries[id] then orphans = orphans + 1 end
end
assert(orphans == 0, orphans .. " descriptions have no matching item name")
print("  every description belongs to a named item")

for id, text in pairs(captured.texts) do
  assert(type(text) == "string" and text ~= "", "empty description for item " .. id)
end
print("  no blank descriptions")

print("items: all assertions passed")
