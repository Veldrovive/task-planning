-- Breaks a block in front, below, or on top of the agent

local BreakBlock = {}

function BreakBlock:run(data)
    local direction = data.direction or "front"
    local requireInventorySpace = data.requireInventorySpace or false  -- Whether to ignore the requirement for there to be space for the block in the inventory
    local success, data = InteractionManager:breakBlock(direction, requireInventorySpace)
    if not success then
        error(data)
    end
    return { broke = data }
end

return BreakBlock