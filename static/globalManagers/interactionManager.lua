local pretty_print = require("cc.pretty").pretty_print

local Utilities = require("utilities")

local InteractionManager = {}

local inspectMap = {
  ['up'] = turtle.inspectUp,
  ['down'] = turtle.inspectDown,
  ['front'] = turtle.inspect
}
function InteractionManager:getBlockData(direction)
  -- Gets the blockData for the block the turtle is facing. Returns nil if there is no block.
  local inspectFunc = inspectMap[direction]
  if not inspectFunc then
    error("Invalid direction: " .. direction)
  end
  local hasBlock, blockData = inspectFunc()
  if not hasBlock then
    return nil
  end

  return blockData
end

function InteractionManager:getBlockName(direction)
  -- Gets the name of the block the turtle is facing. Returns nil if there is no block.
  local blockData = InteractionManager:getBlockData(direction)
  if not blockData then
    return nil
  end

  -- local blockNameData = Utilities.split(blockData.name, ":")
  -- local blockName = blockNameData[2]
  -- return blockName
  return blockData.name
end

function InteractionManager:checkForBlock(blockSubname, direction)
  -- Checks to see if the block the turtle is facing has blockSubname in its name
  local blockName = InteractionManager:getBlockName(direction)
  if not blockName then
    return false
  end

  local subNameInString = #Utilities.findInString(blockName, blockSubname) > 0
  return subNameInString
end

local breakMap = {
  ['up'] = turtle.digUp,
  ['down'] = turtle.digDown,
  ['front'] = turtle.dig
}
function InteractionManager:breakBlock(direction, requireInventorySpace)
  local blockData = InteractionManager:getBlockData(direction)
  if requireInventorySpace then
    if not blockData then
      return false, "No block to break"
    end
    local spaceForBlock = InventoryManager:getSpaceFor(blockData)
    if spaceForBlock == 0 then
      return false, "Not enough space in inventory"
    end
  end

  local breakFunc = breakMap[direction]
  if not breakFunc then
    return false, "Invalid direction: " .. direction
  end

  local success, reason = breakFunc()
  if not success then
    return false, reason
  end

  -- We successfully broke the block. Now we need to tell the inventory manager to update its inventory
  -- InventoryManager:atomicUpdateAdd(blockName, 1)  -- TODO: Implement the efficient add function
  InventoryManager:updateInventory()
  return true, blockData
end

local placeMap = {
  ['up'] = turtle.placeUp,
  ['down'] = turtle.placeDown,
  ['front'] = turtle.place
}
function InteractionManager:placeBlock(blockName, direction)
  local hasBlock = InventoryManager:selectBlock(blockName)
  if not hasBlock then
    return false, "No block to place: " .. blockName .. " to  " .. direction
  end

  local placeFunc = placeMap[direction]
  if not placeFunc then
    return false, "Invalid direction: " .. direction
  end

  local success, reason = placeFunc()
  if not success then
    return false, reason
  end

  return true, nil
end

return InteractionManager
