-- This could be part of the interaction manager, but it is complex enough to warrent being separated out

local ScanManager = {}
ScanManager.scanners = {}
ScanManager.numScanners = 0

function ScanManager:initialize()
    -- Check if we have a scanner peripheral
    self.scanners = { peripheral.find("geoScanner") }
    self.numScanners = #self.scanners
end

function ScanManager:scan(radius, scannerIndex, waitForScan)
    if waitForScan == nil then
        waitForScan = true
    end
    if self.numScanners == 0 then
        return false, "Peripheral not found"
    end
    radius = radius or 8
    scannerIndex = scannerIndex or 1
    local scanner = self.scanners[scannerIndex]

    local scanned = false
    local data, reason
    while not scanned do
        data, reason = scanner.scan(radius)
        if not data then
            if reason ~= "scanBlocks is on cooldown" or not waitForScan then
                return false, reason
            end
        else
            scanned = true
            os.sleep(0.01)  -- Yield to other threads
        end
    end

    -- Air blocks are not returned by the scanner, but we want to know they were scanned so we insert them manually
    -- To do this, first we need to be able to look up if we scanned the block at a given location efficiently
    local scannedLocations = {}
    for _, v in pairs(data) do
        scannedLocations[tostring(v.x) .. "," .. tostring(v.y) .. "," .. tostring(v.z)] = true
    end
    for x = -radius, radius do
        for y = -radius, radius do
            for z = -radius, radius do
                if not scannedLocations[tostring(x) .. "," .. tostring(y) .. "," .. tostring(z)] then
                    table.insert(data, { x = x, y = y, z = z, name = "minecraft:air", tags = {} })
                end
            end
        end
    end

    -- Now, we need to convert the positions relative to the turtle into movement aligned positions
    -- We also want to convert into a map from position to the blockdata to prepare for sending it to the server
    local blocks = {}
    local side, up, forward, value
    for _, v in pairs(data) do
        side, up, forward = MovementManager:fromLocal(v.x, -v.z, v.y, false)  -- TODO: The xyz here is given in global coordinates so this only works if the turtle starts in the +x direction. Follow this here https://github.com/SirEndii/AdvancedPeripherals/issues/392
        if v.x == 0 and v.y == 0 and v.z == 0 then
            -- This is the turtle, so we don't want to send it to the server
            value = { forward, side, up, "minecraft:air" }
        else
            value = { forward, side, up, v.name }
        end
        table.insert(blocks, value)
    end

    print("Scanned " .. #blocks .. " blocks")

    return true, blocks
end

function ScanManager:analyzeChunk(scannerIndex)
    if self.numScanners == 0 then
        return false, "Peripheral not found"
    end
    scannerIndex = scannerIndex or 1
    local scanner = self.scanners[scannerIndex]
    local data, reason = scanner.chunkAnalyze()
    if not data then
        return false, reason
    end
    return true, data
end

function ScanManager:scanCost(radius)
    if self.numScanners == 0 then
        return false, "Peripheral not found"
    end
    local scanner = self.scanners[1]
    return true, scanner.cost(radius)
end

return ScanManager