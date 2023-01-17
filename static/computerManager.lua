-- This module is responsible for managing commands have have to do with internal computer systems and not any interaction with the world

local Utilities = require("utilities")

local ComputerManager = {}

function ComputerManager:initialize(CommandManager)
    CommandManager:registerCallback("initialize", Utilities.bind(self, self.initializeCallback))
    CommandManager:registerCallback("setLabel", Utilities.bind(self, self.setLabelCallback))
    CommandManager:registerCallback("getSettings", Utilities.bind(self, self.getSettingsCallback))
    CommandManager:registerCallback("setSetting", Utilities.bind(self, self.setSettingCallback))
    CommandManager:registerCallback("getIdentity", Utilities.bind(self, self.getIdentityCallback))
    CommandManager:registerCallback("getLocation", Utilities.bind(self, self.getLocationCallback))
end

function ComputerManager:getField(fieldId)
    if fieldId == "id" then
        return os.getComputerID()
    elseif fieldId == "label" then
        return os.getComputerLabel()
    else
        -- Otherwise we should take user input to get the field
        print("Please enter the value for " .. fieldId)
        return read()
    end
end

function ComputerManager:initializeCallback(data)
    local requiredFields = data.requiredFields
    local fieldResponses = {}
    for i, field in ipairs(requiredFields) do
        local fieldId = field.fieldId
        fieldResponses[i] = { fieldId = fieldId, value = self:getField(fieldId) }
    end

--   respond(fieldResponses)
    return { initializedFields = fieldResponses }
end

function ComputerManager:getIdentityCallback(data)
    local identity = {}
    identity.id = os.getComputerID()
    identity.label = os.getComputerLabel()
--   respond(identity)
    return identity
end

function ComputerManager:setLabelCallback(data, respond)
    local label = data.label
    os.setComputerLabel(label)
    -- respond(true)
    return true
end

function ComputerManager:getSettingsCallback(data, respond)
    local settingNames = settings.getNames()
    local settingDetails = {}
    for i, settingName in ipairs(settingNames) do
        settingDetails[i] = { name = settingName, value = settings.getDetails(settingName) }
    end
    -- respond(settingDetails)
    return settingDetails
end

function ComputerManager:setSettingCallback(data, respond)
    local name = data.name
    local value = data.value
    settings.set(name, value)
    settings.save()
    -- respond(settings.getDetails(name))
    return settings.getDetails(name)
end

function ComputerManager:getLocationCallback(data, respond)
    local location = {}
    local relativePosition = MovementManager:getCurrentRelativePosition()
    location.relative = {}
    location.relative.x = relativePosition.forward
    location.relative.y = relativePosition.up
    location.relative.z = relativePosition.side
    local truePosition = MovementManager:getTruePosition()
    location.global = {}
    location.global.x = truePosition.x
    location.global.y = truePosition.y
    location.global.z = truePosition.z
    -- respond(location)
    return location
end

return ComputerManager
