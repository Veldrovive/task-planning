local pretty_print = require("cc.pretty").pretty_print

local MovementManager = {}

MovementManager.relativePosition = { forward = 0, side = 0, up = 0 }
MovementManager.facing = { forward = 1, side = 0, up = 0 }
MovementManager.originalPosition = nil  -- { x: XPOS, y: YPOS, z: ZPOS }
MovementManager.originalOrientation = nil  -- { x: +-1, y: 0, z: +-1 } Only one of x, y, z can be non-zero

-- For movement, we will think about a graph where the +z direction lies on the forward and back axis, the +x direction lies on the left and right axis, and z is up and down
-- This is a right hand dextral frame of reference and corresponds to the in game yaw=0 axis

-- Similarly, when in relative coordinates, forward is on the forward and back axis, side is on the left and right axis, and up is up and down
-- This also being right hand dextral will help us out a bit. I doubt I'll use any rotation matrices though cause I don't want to write a linear algebra library and I'm not supposed to use that sort of thing off the internet as a self imposed rule

local function validateOrientation(orientation)
  local xOrient, yOrient, zOrient = orientation.x, orientation.y, orientation.z
  xOrient = xOrient or 0
  yOrient = yOrient or 0
  zOrient = zOrient or 0

  -- A turtle cannot face two ways at once
  if xOrient ~= 0 and zOrient ~= 0 then
    return false
  end
  -- It also cannot face up or down
  if yOrient ~= 0 then
    return false
  end
  -- And it cannot face in a direction with magnitude greater than 1
  if math.abs(xOrient) > 1 or math.abs(zOrient) > 1 then
    return false
  end
  -- But it must be facing in a direction
  if xOrient == 0 and zOrient == 0 then
    return false
  end
  return true
end

local function validateFacing(facing)
  local forwardFacing, sideFacing, upFacing = facing.forward, facing.side, facing.up
  forwardFacing = forwardFacing or 0
  sideFacing = sideFacing or 0
  upFacing = upFacing or 0

  -- A turtle cannot face two ways at once
  if forwardFacing ~= 0 and sideFacing ~= 0 then
    return false
  end
  -- It also cannot face up or down
  if upFacing ~= 0 then
    return false
  end
  -- And it cannot face in a direction with magnitude greater than 1
  if math.abs(forwardFacing) > 1 or math.abs(sideFacing) > 1 then
    return false
  end
  -- But it must be facing in a direction
  if forwardFacing == 0 and sideFacing == 0 then
    return false
  end
  return true
end

local stringToOrientation = {
  ["+x"] = { x = 1, y = 0, z = 0 },
  ["-x"] = { x = -1, y = 0, z = 0 },
  ["+z"] = { x = 0, y = 0, z = 1 },
  ["-z"] = { x = 0, y = 0, z = -1 },
}

local stringToFacing = {
  ["+f"] = { forward = 1, side = 0, up = 0 },
  ["-f"] = { forward = -1, side = 0, up = 0 },
  ["+s"] = { forward = 0, side = 1, up = 0 },
  ["-s"] = { forward = 0, side = -1, up = 0 },
}

function MovementManager:getCurrentRelativePosition()
  return self.relativePosition
end

function MovementManager:setTruePosition(position, orientation)
  if type(orientation) == "string" then
    orientation = stringToOrientation[orientation]
  end
  -- Verify that the position and orientation are valid
  local x, y, z = position.x, position.y, position.z
  local xOrient, yOrient, zOrient = orientation.x, orientation.y, orientation.z
  xOrient = xOrient or 0
  yOrient = yOrient or 0
  zOrient = zOrient or 0

  if not validateOrientation(orientation) then
    error("Invalid orientation: " .. orientation.x .. ", " .. orientation.y .. ", " .. orientation.z)
  end

  -- Now we can set the position and orientation
  self.originalPosition = { x = x, y = y, z = z }
  self.originalOrientation = { x = xOrient, y = yOrient, z = zOrient }
end

function MovementManager:trueOrientationToFacing(orientation)
  if type(orientation) == "string" then
    orientation = stringToOrientation[orientation]
  end
  if not validateOrientation(orientation) then
    error("Invalid orientation: " .. orientation.x .. ", " .. orientation.y .. ", " .. orientation.z)
  end
  -- In order to move in a specific direction we need to be able to transform from a true orientation to a facing direction
  error("Not implemented")
end

function MovementManager:getTruePosition()
  -- If an originalPosition and originalOrientation have not been set, then we are not in a valid state
  if not self.originalPosition or not self.originalOrientation then
    return nil
  end

  -- Otherwise we can calculate the true position with the relative position and orientation
  -- First we will calculate the relative offset
  local xOrient, yOrient, zOrient = self.originalOrientation.x, self.originalOrientation.y, self.originalOrientation.z
  local xOffset, yOffset, zOffset = 0, self.relativePosition.up, 0
  if zOrient == 1 then
    -- The our forward direction coincides with the +z direction and our side direction coincides with the +x direction
    -- See I told you being right hand dextral would help us out
    xOffset = self.relativePosition.side
    zOffset = self.relativePosition.forward
  elseif zOrient == -1 then
    -- The our forward direction coincides with the -z direction and our side direction coincides with the -x direction
    xOffset = -self.relativePosition.side
    zOffset = -self.relativePosition.forward
  elseif xOrient == 1 then
    -- The our forward direction coincides with the +x direction and our side direction coincides with the -z direction
    xOffset = -self.relativePosition.forward
    zOffset = self.relativePosition.side
  elseif xOrient == -1 then
    -- The our forward direction coincides with the -x direction and our side direction coincides with the +z direction
    xOffset = self.relativePosition.forward
    zOffset = -self.relativePosition.side
  end
  -- Would be neater to use a rotation matrix, but, again, way too lazy

  -- Now we can calculate the true position
  local x, y, z = self.originalPosition.x, self.originalPosition.y, self.originalPosition.z
  x = x + xOffset
  y = y + yOffset
  z = z + zOffset

  return { x = x, y = y, z = z }
end

function MovementManager:fromLocal(f, s, u, respectOrientation)
    -- Translate from the reference frame at the turtle facing in the direction of the turtle to the relativePosition frame
    -- First, we need to rotate the vector from the current facing to facing forward=1, side=0, up=0
    if respectOrientation == nil then
        respectOrientation = true
    end
    local x, y, z = s, u, f
    if respectOrientation then
        if self.facing.forward == 1 then
            x = s
            z = f
        elseif self.facing.forward == -1 then
            x = -s
            z = -f
        elseif self.facing.side == 1 then
            x = -f
            z = s
        elseif self.facing.side == -1 then
            x = f
            z = -s
        end
    end
    -- Now we can translate from the turtle facing frame to the relativePosition frame
    x = x + self.relativePosition.side
    y = y + self.relativePosition.up
    z = z + self.relativePosition.forward
    return x, y, z
end

-- Our movement manager handles actually calling the movement functions so that the relative position and orientation can be updated
function MovementManager:printState(prefix, logFile)
  local state = prefix .. ": "
  state = state .. "Facing: " .. self.facing.forward .. ", " .. self.facing.side .. ", " .. self.facing.up .. "; "
  state = state .. "Relative Position: " .. self.relativePosition.forward .. ", " .. self.relativePosition.side .. ", " .. self.relativePosition.up .. "; "
  print(state)
  if logFile ~= nil then
    file = fs.open(logFile, "a")
    file.writeLine(state)
    file.close()
  end
end

function MovementManager:turnLeft()
  local success, reason = turtle.turnLeft()
  if success then
    -- then we need to update our facing
    local newFacing = {}
    newFacing.forward = -self.facing.side
    newFacing.side = self.facing.forward
    newFacing.up = self.facing.up
    self.facing = newFacing
    -- self:printState("Turned left", "movelog.txt")
  end
  return success, reason
end

function MovementManager:turnRight()
  local success, reason = turtle.turnRight()
  if success then
    -- then we need to update our facing
    local newFacing = {}
    newFacing.forward = self.facing.side
    newFacing.side = -self.facing.forward
    newFacing.up = self.facing.up
    self.facing = newFacing
    -- self:printState("Turned right", "movelog.txt")
  end
  return success, reason
end

function MovementManager:forward()
  local success, reason = turtle.forward()
  if success then
    -- then we need to update our position
    local newPosition = {}
    newPosition.forward = self.relativePosition.forward + self.facing.forward
    newPosition.side = self.relativePosition.side + self.facing.side
    newPosition.up = self.relativePosition.up + self.facing.up
    self.relativePosition = newPosition
    -- self:printState("Moved forward", "movelog.txt")
  end
  return success, reason
end

function MovementManager:back()
  local success, reason = turtle.back()
  if success then
    -- then we need to update our position
    local newPosition = {}
    newPosition.forward = self.relativePosition.forward - self.facing.forward
    newPosition.side = self.relativePosition.side - self.facing.side
    newPosition.up = self.relativePosition.up - self.facing.up
    -- self:printState("Moved back", "movelog.txt")
  end
  return success, reason
end

function MovementManager:up()
  local success, reason = turtle.up()
  if success then
    -- then we need to update our position
    local newPosition = {}
    newPosition.forward = self.relativePosition.forward
    newPosition.side = self.relativePosition.side
    newPosition.up = self.relativePosition.up + 1
    self.relativePosition = newPosition
    -- self:printState("Moved up", "movelog.txt")
  end
  return success, reason
end

function MovementManager:down()
  local success, reason = turtle.down()
  if success then
    -- then we need to update our position
    local newPosition = {}
    newPosition.forward = self.relativePosition.forward
    newPosition.side = self.relativePosition.side
    newPosition.up = self.relativePosition.up - 1
    self.relativePosition = newPosition
    -- self:printState("Moved down", "movelog.txt")
  end
  return success, reason
end

-- Now that we have the atomic building blocks, we can build some higher level functions
function MovementManager:turn(amount)
  -- +1 is turn left one. -1 is turn right one.
  local success, reason
  local turnFunction = amount > 0 and self.turnLeft or self.turnRight
  for i = 1, math.abs(amount) do
    success, reason = turnFunction(self)
    if not success then
      return success, reason
    end
  end
  return true, nil
end

function MovementManager:moveHorizontal(numBlocks)
  local success, reason
  local moveFunction = numBlocks > 0 and self.forward or self.back
  for i = 1, math.abs(numBlocks) do
    success, reason = moveFunction(self)
    if not success then
      return success, reason
    end
  end
  return true, nil
end

function MovementManager:moveVertical(numBlocks)
  local success, reason
  local moveFunction = numBlocks > 0 and self.up or self.down
  for i = 1, math.abs(numBlocks) do
    success, reason = moveFunction(self)
    if not success then
      return success, reason
    end
  end
  return true, nil
end

-- It will also be helpful to be able to turn to face a specific direction
function MovementManager:faceTo(facing)
  if type(facing) == "string" then
    facing = stringToFacing[facing]
  end
  facing.forward = facing.forward or 0
  facing.side = facing.side or 0
  facing.up = facing.up or 0
  if not validateFacing(facing) then
    error("Invalid facing: " .. facing.forward .. ", " .. facing.side .. ", " .. facing.up)
  end
  -- Now we need to figure out which way we need to turn and how many times
  -- Luckily we can just use the cross product... I totally thought of that immediately and didn't have to reinvent the wheel to figure it out
  -- I'm so smart
  -- We only need to compute the up component since that's the one that should be non-zero
  local upTurn = self.facing.forward * facing.side - self.facing.side * facing.forward
  local dotProduct = self.facing.forward * facing.forward + self.facing.side * facing.side
  if upTurn == 0 and dotProduct == 1 then
    -- then we are already facing the right way
    return true, nil
  elseif upTurn == 0 and dotProduct == -1 then
    -- Then we are facing 180 degrees off
    return self:turn(2)
  else
    -- Then we are facing 90 degrees off
    return self:turn(upTurn)  -- Since we are orthonormal, this will always be 1 or -1
  end
end

-- And we also want to be able to do that in the world frame
function MovementManager:orientTo(orientation)
  local relativeFacing = self:trueOrientationToFacing(orientation)
  return self:faceTo(relativeFacing)
end

function MovementManager:moveBy(relativePosition)
  local dForward = relativePosition.forward or 0
  local dSide = relativePosition.side or 0
  local dUp = relativePosition.up or 0

  if dForward ~= 0 then
    -- We need to turn to face either forward or backward and then move
    local toFace = dForward > 0 and "+f" or "-f"
    local success, reason = self:faceTo(toFace)
    if not success then
      return success, reason
    end
    success, reason = self:moveHorizontal(math.abs(dForward))
    if not success then
      return success, reason
    end
  end

  if dSide ~= 0 then
    -- We need to turn to face either left or right and then move
    local toFace = dSide > 0 and "+s" or "-s"
    local success, reason = self:faceTo(toFace)
    if not success then
      return success, reason
    end
    success, reason = self:moveHorizontal(math.abs(dSide))
    if not success then
      return success, reason
    end
  end

  if dUp ~= 0 then
    -- We need to move up or down
    local success, reason = self:moveVertical(dUp)
    if not success then
      return success, reason
    end
  end

  return true, nil
end

function MovementManager:moveTo(relativePosition)
  local dForward = (relativePosition.forward or 0) - self.relativePosition.forward
  local dSide = (relativePosition.side or 0) - self.relativePosition.side
  local dUp = (relativePosition.up or 0) - self.relativePosition.up

  print("Moving from " .. self.relativePosition.forward .. ", " .. self.relativePosition.side .. ", " .. self.relativePosition.up .. " to " .. (relativePosition.forward or 0) .. ", " .. (relativePosition.side or 0) .. ", " .. (relativePosition.up or 0) .. " by " .. dForward .. ", " .. dSide .. ", " .. dUp)


  return self:moveBy({forward = dForward, side = dSide, up = dUp})
end



return MovementManager
