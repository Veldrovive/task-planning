-- The commandManager listens for the commandSetRecieved event and and executes the commands in the set.
-- Once all commands in the set have executed, the commandManager sends a message back to the server with the output.
-- Callbacks can be registered with the commandManager to handle specific commands. Otherwise it is assumed the commands are actuator
--   commands and the correct coroutine will be downloaded and executed

local expect = require("cc.expect").expect

local CommandManager = {}
CommandManager.callbacks = {}
CommandManager.count = 0

function CommandManager:initialize()
    
end

function CommandManager:registerCallback(commandName, callback)
    expect(1, commandName, "string")
    expect(2, callback, "function")
    self.callbacks[commandName] = callback
end

function CommandManager:runCallback(command, commandData)
    local ok, result = pcall(self.callbacks[command], commandData)
    return ok, result
end

function CommandManager:listen()
    while true do
        local _, topic, commands = os.pullEvent("commandSetRecieved")
        -- print("Command set recieved: " .. #commands .. " commands")
        -- For each command in the command set, if the command name is in the callbacks table, call the callback and take the output as the result
        -- If the command is not in the callbacks table, spawn a startCommand event and wait for the commandFinished event. Take the output of the commandFinished event as the result
        local results = {}
        local failure = nil
        for i, commandTable in ipairs(commands) do
            local command = commandTable.command
            local commandData = commandTable.data
            local _, result, success, eventTaskId
            local startTime = os.epoch("utc")
            self.count = self.count + 1
            if self.callbacks[command] ~= nil then
                success, result = self:runCallback(command, commandData)
            else
                local taskId = self.count
                os.queueEvent("startCommand", command, commandData, taskId)
                repeat
                    _, success, result, eventTaskId = os.pullEvent("commandFinished")
                until eventTaskId == taskId
            end
            local endTime = os.epoch("utc")
            if success then
                results[i] = { command = command, data = result, startTime = startTime, endTime = endTime, totalTime = endTime - startTime }
            else
                failure = result
                break
            end
        end
        local status = (failure == nil) and "completed" or "failed"
        -- respond({ commands = results, setStatus = status, failure = failure })
        os.queueEvent("commandSetFinished", topic, results, status, failure)
    end
end

return CommandManager