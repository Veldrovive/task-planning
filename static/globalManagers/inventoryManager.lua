local pretty_print = require("cc.pretty").pretty_print

local InventoryManager = {}

InventoryManager.inventory = {}  -- An array of item names in the inventory
InventoryManager.blockCounts = {}  -- A map from block name to the number of that block in the inventory
InventoryManager.blockOpenCounts = {}  -- A map from block name to the number of blocks that can be placed in slots that currently have that block in it
InventoryManager.blockSlotMap = {}  -- A map from block name to a list of slots that contain that block in ascending order
InventoryManager.totallyOpenSlots = -1  -- The number of slots that are totally empty

local function blockDataToName(blockData)
  if type(blockData) == "string" then
    return blockData
  else
    return blockData.name
  end
end

function InventoryManager:getStackSize(blockData)
  local blockName = blockDataToName(blockData)
  local stackSize = 64
  return stackSize  -- TODO: Actually make this get the real stack size for non-stackable items
end

function InventoryManager:updateInventory()
  -- For when we don't know enough to pinpoint exactly what changed so we just refresh the whole inventoryManager
  local inventory, blockCounts, blockOpenCounts, blockSlotMap, totallyOpenSlots = {}, {}, {}, {}, 0
  local ok, itemDetail, itemCount, openCount
  local slot = 1
  repeat
    ok, itemDetail = pcall(turtle.getItemDetail, slot)
    if not ok then
      break
    end
    if itemDetail == nil then
      totallyOpenSlots = totallyOpenSlots + 1
      inventory[slot] = nil
    else
      local blockName = blockDataToName(itemDetail)
      itemCount = turtle.getItemCount(slot)
      openCount = turtle.getItemSpace(slot)
      local totalItemCount = (blockCounts[blockName] or 0) + itemCount
      local totalOpenCount = (blockOpenCounts[blockName] or 0) + openCount
      blockCounts[blockName] = totalItemCount
      blockOpenCounts[blockName] = totalOpenCount
      inventory[slot] = blockName

      if blockSlotMap[blockName] == nil then
        blockSlotMap[blockName] = {}
      end
      table.insert(blockSlotMap[blockName], slot)
    end

    slot = slot + 1
  until false

  self.inventory = inventory
  self.blockCounts = blockCounts
  self.blockOpenCounts = blockOpenCounts
  self.blockSlotMap = blockSlotMap
  self.totallyOpenSlots = totallyOpenSlots
end

function InventoryManager:getInventory()
    local inventory = {
        blockNames = self.inventory,
        blockCounts = self.blockCounts,
        blockOpenCounts = self.blockOpenCounts,
        blockSlotMap = self.blockSlotMap,
        totallyOpenSlots = self.totallyOpenSlots,
    }
    return inventory
end

function InventoryManager:startWatchingInventory()
  while true do
    os.pullEvent("turtle_inventory")
    -- We could also set a "dirty" flag and only update the inventory when we need to, but this is easier and probably not too inefficient
    self:updateInventory()
  end
end

function InventoryManager:rearrangeInventory()
  -- Shifts blocks around in the inventory so that blocks are stacked up as much as possible and compressed toward the front of the inventory
  error("Not implemented")
end

function InventoryManager:getItemSlot(blockData)
  local blockName = blockDataToName(blockData)
  local blockSlots = self.blockSlotMap[blockName]
  if blockSlots == nil then
    return nil
  end

  return blockSlots[#blockSlots]
end

function InventoryManager:getSpaceFor(blockData)
  local blockName = blockDataToName(blockData)
  -- Space for a block is the number of open slots * num blocks per slot + the number of open blocks for that block type
  local stackSize = self:getStackSize(blockData)
  local space = self.totallyOpenSlots * stackSize + (self.blockOpenCounts[blockName] or 0)
  return space
end

function InventoryManager:getItemCount(blockData)
  local blockName = blockDataToName(blockData)
  print("Getting item count for " .. blockName)
  pretty_print(self.blockCounts)
  return self.blockCounts[blockName] or 0
end

function InventoryManager:selectBlock(blockData)
  local blockName = blockDataToName(blockData)
  local blockSlots = self.blockSlotMap[blockName]
  if blockSlots == nil then
    return false
  end

  local slot = blockSlots[#blockSlots]
  turtle.select(slot)
  return true
end

local dropMethod = {
  ["up"] = turtle.dropUp,
  ["down"] = turtle.dropDown,
  ["forward"] = turtle.drop,
}
function InventoryManager:drop(direction, blockName, quantity)
  -- Returns the quantity of blocks that were actually dropped
  -- If quantity is nil, drop all of the blocks
  local drop = dropMethod[direction]
  if drop == nil then
    print("Invalid direction: " .. direction)
  end
  local blockSlots = self.blockSlotMap[blockName]

  if blockSlots == nil then
    return 0
  end

  local dropped = 0
  local slotIndex = 1
  while quantity == nil or dropped < quantity do
    local slot = blockSlots[slotIndex]
    if slot == nil then
      break
    end

    turtle.select(slot)
    local count = turtle.getItemCount(slot)
    local toDrop = quantity == nil and count or math.min(count, quantity - dropped)
    -- local ok, droppedCount = pcall(drop, toDrop)
    -- if not ok then
    --   error(droppedCount)
    -- end
    drop(toDrop)
    dropped = dropped + toDrop
    slotIndex = slotIndex + 1
  end

  return dropped
end

function InventoryManager:takeFromInventory(direction, blockName, quantity)
  error("Not implemented yet")
end

return InventoryManager
