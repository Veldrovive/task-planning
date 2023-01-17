local Scan = {}

function Scan:run(data)
    local radius = data.radius or 8
    
    local ok, blockData = ScanManager:scan(radius)
    if not ok then
        error(blockData)
    end

    return { blocks = blockData }
end

return Scan
