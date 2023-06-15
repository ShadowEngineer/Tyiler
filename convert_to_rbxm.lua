--# selene: allow(undefined_variable)
---@diagnostic disable: undefined-global

-- remodel script that takes the outputted init.lua file from tarmac,
-- and converts it into a .rbxm file for easy importing into studio manually
-- (if this is desired). Rojo-syncing the init.lua file is preferred.

local imageFileContents = remodel.readFile("init.lua")
local imageScript = Instance.new("ModuleScript")
imageScript.Name = "MapTiles"
remodel.setRawProperty(imageScript, "Source", "String", imageFileContents)
remodel.writeModelFile("MapTiles.rbxm", imageScript)
