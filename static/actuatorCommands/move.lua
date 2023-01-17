-- Relies on the global MovementManager being initialized
local pretty_print = require("cc.pretty").pretty_print
local Move = {}

function Move:run(data)
  local moveTo = data.moveTo
  local moveBy = data.moveBy
  local faceTo = data.faceTo
  if moveTo ~= nil and moveBy ~= nil then
    return false, "Cannot move to and move by"
  end

  if moveTo ~= nil then
    local success, reason = MovementManager:moveTo(moveTo)
    if not success then
    --   return false, reason
    error(reason)
    end
  elseif moveBy ~= nil then
    local success, reason = MovementManager:moveBy(moveBy)
    if not success then
    --   return false, reason
        error(reason)
    end
  end

  if faceTo ~= nil then
    local success, reason = MovementManager:faceTo(faceTo)
    if not success then
    --   return false, reason
        error(reason)
    end
  end

  return nil
end

return Move
