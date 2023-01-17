-- Manages equipment for turtle agents

local PeripheralManager = {}
PeripheralManager.left = nil
PeripheralManager.right = nil
PeripheralManager.leftType = nil
PeripheralManager.rightType = nil

PeripheralManager.typeItemMap = {
    -- Maps from the peripheralType to the name of the item that has to be equip to enable the operations
    -- Listed in the perferred order if there are multiple that can server the same purpose
    ["modem"] = { "computercraft:wireless_modem_advanced", "computercraft:wireless_modem" },
    ["geoScanner"] = { "advancedperipherals:geo_scanner" }
}

function PeripheralManager:initialize()
    self:getCurrent()
end

function PeripheralManager:getCurrent()
    self.left = peripheral.wrap("left")
    if self.left ~= nil then
        self.leftType = peripheral.getType(self.left)
    end
    self.right = peripheral.wrap("right")
    if self.right ~= nil then
        self.rightType = peripheral.getType(self.right)
    end
end

function PeripheralManager:checkTypeEquip(peripheralType)
    if self.leftType == peripheralType then
        return self.left
    elseif self.rightType == peripheralType then
        return self.right
    end
    return nil
end

function PeripheralManager:equipToSide(peripheralType, side)
    -- Equip the peripheral to the given side. Returns success, original peripheral/reason
    -- Check if we already have it equipped
    if self:checkTypeEquip(peripheralType) ~= nil then
        return true, nil
    end

    -- Check if we have the item in our inventory
    for _, item in ipairs(self.typeItemMap[peripheralType]) do
        local slot = InventoryManager:getItemSlot(item)
        local current = nil
        if slot ~= nil then
            -- We have the item, so equip it
            turtle.select(slot)
            if side == "left" then
                current = self.leftType
                turtle.equipLeft()
            elseif side == "right" then
                current = self.rightType
                turtle.equipRight()
            else
                return false, "Invalid side"
            end
            return true, current
        end
    end
    return false, "Item not found"
end

function PeripheralManager:switchTo(peripheralType)
    -- Equip the peripheral. Returns success, original peripheral
    -- Check if we already have it equipped
    if self:checkTypeEquip(peripheralType) ~= nil then
        return true, nil
    end

    -- We perfer to equip to a side that is not currently occupied
    if self.left == nil then
        return self:equipToSide(peripheralType, "left")
    else
        -- We just equip to the right side
        return self:equipToSide(peripheralType, "right")
    end

end

return PeripheralManager