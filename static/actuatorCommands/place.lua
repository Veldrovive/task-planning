local Place = {}

function Place:run(data, respond)
  local block = data.block
  local direction = data.direction

  local success, reason = InteractionManager:placeBlock(block, direction)
  if not success then
    return error(reason)
  end

  return nil
end

return Place
