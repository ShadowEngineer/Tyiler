--# selene: allow(undefined_variable)
---@diagnostic disable: undefined-global

-- remodel script that takes the outputted init.lua file from tarmac,
-- and converts it into a .rbxm file for easy importing into studio manually
-- (if this is desired). Rojo-syncing the init.lua file is preferred.

local imageFileContents = remodel.readFile("MapTiles.lua")
local imageScript = Instance.new("ModuleScript")
imageScript.Name = "MapTiles"
remodel.setRawProperty(imageScript, "Source", "String", imageFileContents)

local resolutionFileContents = remodel.readFile("Resolutions.json")
local resolutionScript = Instance.new("ModuleScript")
resolutionScript.Name = "Resolutions"
remodel.setRawProperty(
	resolutionScript,
	"Source",
	"String",
	'return game:GetService("HttpService"):JSONDecode(\'' .. resolutionFileContents .. "')"
)

-- can't figure out how to package 2 top-level instances into the same rbxm
resolutionScript.Parent = imageScript

remodel.writeModelFile("MapTiles.rbxm", imageScript)
