-- Item names are 168,000 entries and around ten megabytes, which is most of
-- what the English name data weighs. Spell and creature names are small enough
-- to ship with the panel itself; these are not, so they are opt-in and hand
-- themselves over when installed.

-- What the item does, in English, under its English name. A name alone tells
-- you what to search for; this tells you what you are holding. Only a fifth of
-- items have any -- the rest are ore, cloth and vendor trash the game says
-- nothing about either.
local function register()
  local names = WordHunterWoW_ENPanelNames
  if not names or not names.Register or type(WordHunterWoW_ENNames_Item) ~= "table" then return end
  local descriptions = WordHunterWoW_ENDesc_Item
  if type(descriptions) ~= "table" then descriptions = nil end
  names.Register("item", WordHunterWoW_ENNames_Item, descriptions)
end

local addonName = ...
local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:SetScript("OnEvent", function(_, _, loaded)
  if loaded == addonName then register() end
end)

-- The panel is a required dependency, so its registry already exists. Register
-- immediately as well as on ADDON_LOADED to survive load-order edge cases.
register()
