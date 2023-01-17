local MoveAndDig = {}

function MoveAndDig:run(data, request)
  -- If there is a block in front of the turtle, dig in front of the turtle
  -- Then move forward
  local numBlocks = data.numBlocks
  local breakAbove = data.breakAbove
  local placeTorchesEvery = data.placeTorchesEvery

  for i = 1, numBlocks do
    while turtle.detect() do
      local broken, reason = turtle.dig()
      if not broken then
        -- return false, reason
        error(reason)
      end
    end
    if breakAbove then
      local blocked = turtle.detectUp()
      if blocked then
        local broken, reason = turtle.digUp()
        if not broken then
        --   return false, reason
            error(reason)
        end
      end
    end
    if placeTorchesEvery ~= nil and i % placeTorchesEvery == 1 then
      MovementManager:turnLeft()
      local success, reason = InteractionManager:placeBlock('minecraft:torch', 'up')
      if not success then
        print("Failed to place torch: " .. reason)
      end
      MovementManager:turnRight()
    end

    -- local success, reason = turtle.forward()
    local success, reason = MovementManager:forward()
    if not success then
    --   return false, reason
        error(reason)
    end
  end

  return nil
end

return MoveAndDig
