local pretty_print = require("cc.pretty").pretty_print

local Utilities = {}

function createControlModuleFolder()
  local controlModuleFolder = "/controlModules"
  if not fs.isDir(controlModuleFolder) then
    fs.makeDir(controlModuleFolder)
  end
  return controlModuleFolder
end

function Utilities.loadModule(moduleName, backupUrl, redownload)
  local forceRedownload = settings.get("control.force_module_redownload")
  if forceRedownload == nil then
    settings.set("control.force_module_redownload", true)
    settings.save()
    forceRedownload = true
  end
  if backupUrl == nil then
    backupUrl = StaticRoot .. "/" .. moduleName:gsub("%.", "%/") .. ".lua"
  end
  redownload = redownload or forceRedownload
  local moduleFolder = createControlModuleFolder()
  local moduleRequirePath = moduleFolder .. "/" .. moduleName:gsub("%.", "%/")
  -- print("Loading module " .. moduleName .. " from " .. moduleRequirePath)
  local hasModule, Module, ok
  if not redownload then
    hasModule, Module = pcall(require, moduleRequirePath)
  end
  if not hasModule or redownload then
    -- Then we need to download the controller
    local modulePath = moduleFolder .. "/" .. moduleName:gsub("%.", "%/") .. ".lua"
    local handle = http.get(backupUrl)
    -- And save it to the modules directory at /rom/modules/controller.lua
    local file = fs.open(modulePath, "w")
    file.write(handle.readAll())
    file.close()
    -- And then require it
    ok, Module = pcall(require, moduleRequirePath)
    if not ok then
      print("Failed to load module " .. moduleName .. " from " .. moduleRequirePath)
      print("Error: " .. Module)
      error("Failed to load module " .. moduleName .. " from " .. moduleRequirePath)
    end
  end
  return Module
end

function Utilities.bind(self, func)
  return function(...)
    return func(self, ...)
  end
end


Stack = {}
Stack.entries = {}

function Stack:new(o)
  o = o or {}
  setmetatable(o, self)
  self.__index = self
  o.entries = {}
  return o
end

function Stack:push(item)
  table.insert(self.entries, item)
end

function Stack:pop()
  return table.remove(self.entries)
end

Utilities.Stack = Stack



-- TODO: Improve this implementation in case tasks get very large
Queue = {}
Queue.entries = {}

function Queue:new(o, elements)
  o = o or {}
  setmetatable(o, self)
  self.__index = self
  o.entries = {}
  if elements ~= nil then
    o.addListToQueue(o, elements)
  end
  return o
end

function Queue:addListToQueue(elements)
  for _, element in ipairs(elements) do
    self:enqueue(element)
  end
end

function Queue:enqueue(item)
  table.insert(self.entries, item)
end

function Queue:dequeue()
  return table.remove(self.entries, 1)
end

function Queue:isEmpty()
  return #self.entries == 0
end

Utilities.Queue = Queue


function Utilities.splitString(inputstr, sep)
  if sep == nil then
    sep = "%s"
  end
  local t = {}
  for str in string.gmatch(inputstr, "([^" .. sep .. "]+)") do
    table.insert(t, str)
  end
  return t
end

function Utilities.trim(s)
    return (s:gsub("^%s*(.-)%s*$", "%1"))
 end

function Utilities.findInString(inputstr, findstr)
  local t = {}
  for str in string.gmatch(inputstr, findstr) do
    table.insert(t, str)
  end
  return t
end

return Utilities
