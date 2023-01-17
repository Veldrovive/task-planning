-- Returns the current turtle inventory

local GetInventory = {}

function GetInventory:run(data)
    local inventory = InventoryManager:getInventory()
    if #inventory.blockNames == 0 then
        inventory.blockNames = textutils.empty_json_array
    end
    return { inventory = inventory }
end

return GetInventory