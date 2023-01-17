local pretty = require "cc.pretty"
term.clear()
term.setCursorPos(1, 1)

StaticRoot = "http://127.0.0.1:8766"
WebsocketRoot = "ws://127.0.0.1:8765"

local handle = http.get(StaticRoot .. "/utilities.lua")
local file = fs.open("utilities.lua", "w")
file.write(handle.readAll())
file.close()
Utilities = require("utilities")

-- Create the global managers
IsTurtle = turtle ~= nil
if not IsTurtle then
  print("Not a turtle, creating a fake turtle api")
  turtle = {}
end

MovementManager = Utilities.loadModule("globalManagers.movementManager")
InventoryManager = Utilities.loadModule("globalManagers.inventoryManager")
InteractionManager = Utilities.loadModule("globalManagers.interactionManager")
ScanManager = Utilities.loadModule("globalManagers.scanManager")

if IsTurtle then
  InventoryManager:updateInventory()
end

SocketManager = Utilities.loadModule("socketManager")
CommandManager = Utilities.loadModule("commandManager")
CommandRunner = Utilities.loadModule("commandRunner")
ComputerManager = Utilities.loadModule("computerManager")


-- Initialize the components
SocketManager:initialize(WebsocketRoot)
ComputerManager:initialize(CommandManager)
CommandManager:initialize()
CommandRunner:initialize()
ScanManager:initialize()


-- Set up some convenience functions
local function printCommands()
  -- Test for the event listener version. Should also be a coroutine
  local e = {}
  repeat
    e = { os.pullEvent() }
    if e[1]:match("s_") then
      print("Received command: " .. e[1])
    end
  until false
end


-- And now we start the event loop
parallel.waitForAll(
    Utilities.bind(SocketManager, SocketManager.eventLoop),
    Utilities.bind(CommandManager, CommandManager.listen),
    Utilities.bind(CommandRunner, CommandRunner.listen),
    Utilities.bind(InventoryManager, InventoryManager.startWatchingInventory),
    Utilities.bind(SocketManager, SocketManager.startPing)
)
