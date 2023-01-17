-- Chops a 2x2 spruce tree


local ChopFourTree = {}

local maxHeight = 30

local function getSaplingTypeFromLog(logData)
  -- error("Not implemented yet")
  return "minecraft:spruce_sapling"
end

function ChopFourTree:run(data)
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
  if spaceForLogs < maxHeight*4 then
    return error({ failureID = 'Not enough inventory space', required_space = maxHeight*4 })
  end

  -- If we are replacing the tree with a sapling, we need to make sure we have one
  local saplingType
  if replaceSapling then
    local logData = InteractionManager:getBlockData('front')
    saplingType = getSaplingTypeFromLog(logData)
    local numSaplingAvailable = InventoryManager:getItemCount(saplingType)
    if numSaplingAvailable < 4 then
      return error({ failureID = 'No block available', block = saplingType })
    end
    -- Now we are sure we have a sapling so we can proceed with chopping the tree
  end

  local startPosition = MovementManager:getCurrentRelativePosition()
  print("Starting from position " .. startPosition.forward .. ", " .. startPosition.side .. ", " .. startPosition.up)
  -- Our general strategy is to move into the tree and then break forward and up until we reach the top, then move in the opposite direction and break forward and down until we reach the bottom
  success, reason = InteractionManager:breakBlock('front')
  if not success then
    return error(reason)
  end
  success, reason = MovementManager:forward()
  if not success then
    return error(reason)
  end
  -- Now we need to check to which side there are logs
  local logDirection = 0
  MovementManager:turnLeft()
  if InteractionManager:checkForBlock('log', 'front') then
    logDirection = 1
    MovementManager:turnRight()
  else
    MovementManager:turnRight()
    MovementManager:turnRight()
    if InteractionManager:checkForBlock('log', 'front') then
      logDirection = -1
    end
    MovementManager:turnLeft()
  end
  -- If there were not logs to either side, this is a not a 2x2 tree
  if logDirection == 0 then
    error({ failureID="Command requirements not met", reason="Not a 2x2 tree" })
  end
  -- Now we can move forward and break the log
  repeat
    success, reason = InteractionManager:breakBlock('front')
    success, reason = InteractionManager:breakBlock('up')
    success, reason = MovementManager:up()
    if not success then
      return error(reason)
    end
    hasLog = InteractionManager:checkForBlock('log', 'front')
  until not hasLog
  -- Now we are above the top of the tree, let's get into the new position
  MovementManager:turn(logDirection)
  success, reason = InteractionManager:breakBlock('front')
  success, reason = MovementManager:forward()
  if not success then
    return error(reason)
  end
  MovementManager:turn(-1*logDirection)
  -- Now we can move down and break the logs
  repeat
    -- Break down, move down, break forward, check for log
    success, reason = InteractionManager:breakBlock('down')
    success, reason = MovementManager:down()
    if not success then
      return error(reason)
    end
    success, reason = InteractionManager:breakBlock('front')
    hasLog = InteractionManager:checkForBlock('log', 'down')
  until not hasLog

  -- Now we are at the bottom of the tree, if we are replacing the tree with a sapling, we need to place them
  if replaceSapling then
    -- Move forward, turn logDirection, place sapling, turn -1*logDirection, move back, place sapling, turn logDirection, place sapling, turn -1*logDirection, move back, place sapling
    success, reason = MovementManager:forward()
    if not success then
      return error(reason)
    end
    MovementManager:turn(-1*logDirection)
    success, reason = InteractionManager:placeBlock(saplingType, 'front')
    if not success then
      return error(reason)
    end
    MovementManager:turn(logDirection)
    success, reason = MovementManager:back()
    if not success then
      return error(reason)
    end
    success, reason = InteractionManager:placeBlock(saplingType, 'front')
    if not success then
      return error(reason)
    end
    MovementManager:turn(-1*logDirection)
    success, reason = InteractionManager:placeBlock(saplingType, 'front')
    if not success then
      return error(reason)
    end
    MovementManager:turn(logDirection)
    success, reason = MovementManager:back()
    if not success then
      return error(reason)
    end
    success, reason = InteractionManager:placeBlock(saplingType, 'front')
    if not success then
      return error(reason)
    end
  end

  -- We are done, let's move back to the starting position
  local endPosition = MovementManager:getCurrentRelativePosition()
  print("Ending at position " .. endPosition.forward .. ", " .. endPosition.side .. ", " .. endPosition.up)
  MovementManager:moveTo(startPosition)

  return nil
end

return ChopFourTree
