-- Returns the position and orientation of the turtle in the agent state format
-- { location = { forward, side, up }, orientation = { forward, side, up } }

local GetState = {}

function GetState:run(data)
    return { location = MovementManager.relativePosition, orientation = MovementManager.facing }
end

return GetState