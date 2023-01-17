local InventoryInsert = {}

function InventoryInsert:run(data, respond)
  local allOf = data.allOf
  local allBut = data.allBut
  local blocks = data.blocks
  local direction = data.direction

  if allBut ~= nil then
    -- We need to get all keys in InventoryManager.blockCounts that are not in allBut
    local allButKeys = {}
    for _, block in ipairs(allBut) do
      allButKeys[block] = true
    end
    local to_drop = {}
    for block, _ in pairs(InventoryManager.blockCounts) do
      if not allButKeys[block] then
        table.insert(to_drop, block)
      end
    end

    -- call InventoryManager.drop(down, BLOCK_NAME) for each block in blocks
    for _, block in ipairs(to_drop) do
      local success, reason = InventoryManager:drop(direction, block)
      if not success then
        return error(reason)
      end
    end
  end

  if allOf ~= nil then
    for _, block in ipairs(allOf) do
      local success, reason = InventoryManager:drop(direction, block)
      if not success then
        return error(reason)
      end
    end
  end

  if blocks ~= nil then
    -- Blocks contains tables of "block" and "amount"
    for _, block in ipairs(blocks) do
      local success, reason = InventoryManager:drop(direction, block.block, block.amount)
      if not success then
        return error(reason)
      end
    end
  end

  return nil
end

return InventoryInsert
