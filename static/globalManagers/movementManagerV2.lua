-- Movement manager keeps track of the location of the agent and makes it easier to move to specific positions
-- This manager assumes that we have a gps available or that we are in a known location and orientation

local MovementManager = {}

MovementManager.location = vector.new(0, 0, 0)
MovementManager.orientation = vector.new(1, 0, 0)

function MovementManager:initialize(position)
    local initialized = false
    if position then
        self.location = position.location
        self.orientation = position.orientation
        initialized = true
    else
        initialized = self:gpsLocateRoutine()
    end
    return initialized
end

function MovementManager:gpsLocateRoutine()
    local hasGps = PeripheralManager:enableGps()
    if not hasGps then
        return false
    end

    local location1 = gps.locate()
    if not location1 then
        return false
    end

    function ForwardAndMeasure()
        turtle.forward()
        local location2 = gps.locate()
        turtle.back()
        return location2
    end

    -- We also need a second measurement to know the orientation. To do this, we will try to move forward, then turn and try again until we have done this 4 times
    -- If we fail to move 4 times, we will stop and return false
    local count = 0
    while count < 4 do
        local location2 = ForwardAndMeasure()
        if location2 then
            -- We have a second measurement, so we can calculate the orientation
            self.orientation = vector.new(location2[1] - location1[1], location2[2] - location1[2], location2[3] - location1[3])
            self.location = vector.new(location1[1], location1[2], location1[3])
            return true
        end
        turtle.turnRight()
        count = count + 1
    end

    return false
end

return MovementManager