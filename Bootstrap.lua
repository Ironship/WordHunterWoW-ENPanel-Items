-- Item names are 168,000 entries and around ten megabytes, which is most of
-- what the English name data weighs. Spell and creature names are small enough
-- to ship with the panel itself; these are not, so they are opt-in and hand
-- themselves over when installed.

local function register()
  local names = WordHunterWoW_ENPanelNames
  if not names or not names.Register or type(WordHunterWoW_ENNames_Item) ~= "table" then return end
  names.Register("item", WordHunterWoW_ENNames_Item)
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
