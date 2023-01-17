-- Listens for commands on the startCommand event and executes them. When the command is finished, it sends a commandFinished event with the output of the command.

local Utilities = require("utilities")

local CommandRunner = {}

function CommandRunner:initialize()
    self.commands = {}
end

function CommandRunner:runCommand(command, data)
    local commandModule = Utilities.loadModule("actuatorCommands." .. command)
    local result = commandModule:run(data)
    return result
end

function CommandRunner:listen()
    while true do
        local _, command, data, id = os.pullEvent("startCommand")
        -- local result = self:runCommand(command, data)
        local ok, result = pcall(self.runCommand, self, command, data)
        if not ok then
            print("\nCommand " .. command .. " raised an error: " .. result .. "\n")
            -- If result is a table with a failureID key, then leave it as is. If it is a string, then wrap it in a table with a failureID key.
            if type(result) == "string" then
                -- Then results will be of the form "path/to/file.lua:123: error message" so we need to split it up around the ": "
                local splitResult = Utilities.splitString(result, ":")
                result = { failureID = Utilities.trim(splitResult[3]), message = splitResult[1] .. ":" .. splitResult[2] }
            elseif result.failureID == nil then
                print("Command" .. command .. " raised an unknown error " .. textutils.serializeJSON(result))
                result.failureID = "unknownError"
            end
            os.queueEvent("commandFinished", false, result, id)
        else
            os.queueEvent("commandFinished", true, result, id)
        end
    end
end

return CommandRunner
