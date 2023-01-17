-- Chop vertical tree only works on one wide trunks with no branching. Other types of tree will not work with this system.
-- Optionally replace the tree with a sapling if there is one in the inventory
-- If there is no tree present at the location or the sapling has not grown yet, we do nothing and simply notify the server

local ChopVerticalTree = {}

local maxTreeHeight = 10

local function getSaplingTypeFromLog(logData)
  -- error("Not implemented yet")
  return "minecraft:oak_sapling"
end

function ChopVerticalTree:run(data)
  local replaceSapling = data.replaceSapling
  -- First, we check if there is a tree at the location
  local hasLog = InteractionManager:checkForBlock('log', 'front')
  if not hasLog then
    -- No tree, let's check what block is actually in front and then tell the server and move on
    return error("Already complete")
  end
  -- Otherwise we can chop the tree
  -- First, let's verify we have space in our inventory for this tree
  local spaceForLogs = InventoryManager:getSpaceFor(InteractionManager:getBlockData('front'))
  if spaceForLogs < maxTreeHeight then
    error({ failureID = 'Not enough inventory space', required_space = maxTreeHeight })
  end

  -- If we are replacing the tree with a sapling, we need to make sure we have one
  local saplingType
  if replaceSapling then
    local logData = InteractionManager:getBlockData('front')
    saplingType = getSaplingTypeFromLog(logData)
    local numSaplingAvailable = InventoryManager:getItemCount(saplingType)
    if numSaplingAvailable == 0 then
        error({ failureID = 'No block available', block = saplingType })
    end
    -- Now we are sure we have a sapling so we can proceed with chopping the tree
  end

  -- Now we are sure that we have enough space. Let's chop the tree
  local startPosition = MovementManager:getCurrentRelativePosition()
  print("Starting from position " .. startPosition.forward .. ", " .. startPosition.side .. ", " .. startPosition.up)
  local success, reason
  repeat
    -- Break log, move up one, check for log
    success, reason = InteractionManager:breakBlock('front')
    if not success then
      error(reason)
    end
    -- There may be a leaf above us now so we need to break that
    InteractionManager:breakBlock('up')
    success, reason = MovementManager:up()
    if not success then
      error(reason)
    end
    hasLog = InteractionManager:checkForBlock('log', 'front')
  until not hasLog
  -- Now we just move down to where we were
  print("Moving back down")
  local newPosition = MovementManager:getCurrentRelativePosition()
  print("New position " .. newPosition.forward .. ", " .. newPosition.side .. ", " .. newPosition.up)
  MovementManager:moveTo(startPosition)

  -- And finally we need to place the sapling if we are replacing the tree
  if replaceSapling then
    print("Placing sapling")
    InteractionManager:placeBlock(saplingType, 'front')
  end

  print("Done chopping tree")
  return nil
end

return ChopVerticalTree
