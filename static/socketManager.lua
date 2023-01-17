local expect = require "cc.expect"

local SocketManager = {}
SocketManager.callbacks = {}
SocketManager.verified = false

function SocketManager:startPing()
    -- Every 1 second send a ping to the server
    -- local timerId = os.startTimer(1)
    -- print("Starting ping")
    -- while true do
    --     local e = { os.pullEvent() }
    --     if e[1] == "timer" and e[2] == timerId then
    --         print("Sending ping")
    --         self.handle.send("ping")
    --         print("Sent ping")
    --         timerId = os.startTimer(1)
    --     end
    -- end
end

function SocketManager:initialize(serverUrl, connectionTimeout)
  -- Open the socket connection (and start the listener loop? Unless I want that to be separate for whatever reason)
  expect(1, serverUrl, "string")
  expect(2, connectionTimeout, "number", "nil")

  connectionTimeout = connectionTimeout or 5

  print('Connecting to ws server: ' .. serverUrl)
  local timerId = os.startTimer(connectionTimeout)
  local _, url, handle
  local e = {}
  http.websocketAsync(serverUrl)
  repeat
    e = { os.pullEvent() }
    if e[1] == "timer" and e[2] == timerId then
      error("Connection timed out")
    elseif e[1] == "websocket_success" then
      url = e[2]
      handle = e[3]
    end
  until url == serverUrl

  self.serverUrl = serverUrl
  self.handle = handle
end

function SocketManager:send(topic, message)
    -- Send a message to the server
    expect(1, topic, "string")
    expect(2, message, "string", "number", "table", "boolean", "nil")

    local response = {}
    response.topic = topic
    response.message = message

    -- print("Sending message to: " .. topic .. " with message: " .. textutils.serializeJSON(response))
    self.handle.send(textutils.serializeJSON(response), false)
end

function SocketManager:responderFactory(topic)
    -- When we send an event for a command we also send a function that can be called to respond
    expect(1, topic, "string")
    local function respond(message)
      expect(1, message, "string", "number", "table", "boolean", "nil")
  
      self:send(topic, message)
    end
    return respond
  end

function SocketManager:handleMessage(dataTable)
    if dataTable.topic == nil then
        error("Message recieved without a topic")
    end
    if dataTable.message == nil then
        error("Message recieved without a message")
    end
    local topic = dataTable.topic
    local messageTable = dataTable.message

    if messageTable.commands ~= nil then
        -- This is a commandSet. Currently the only thing we should be recieving.
        -- The only job we have is to spawn an event that the taskManager can listen for
        os.queueEvent("commandSetRecieved", topic, messageTable.commands)
        local _, topic, results, status, failure = os.pullEvent("commandSetFinished")
        if #results == 0 then
            results = textutils.empty_json_array
        end
        self:send(topic, { commands=results, setStatus=status, failure=failure })
    else
        error("Unknown messge type recieved")
    end
end

function SocketManager:receive()
  -- This method assumes it is inside a coroutine and starts a loop where it listens for messages from the websocket server
  repeat
    local data, binary = self.handle.receive()
    if data ~= nil then
      -- We have a message. It is either a ping or a command. We do not need to deserialize a ping so we can just respond
      if data == "ping" then
        self.handle.send("pong")
      else
        -- Then this is a command and needs to be deserialized
        local dataTable = textutils.unserializeJSON(data)
        self:handleMessage(dataTable)
      end
    end
  until false
end

function SocketManager:eventLoop()
  -- Could spawn its own coroutines in case there are multiple event handling loops necessary, but for now we only have one so we just call it
  self:receive()
end

return SocketManager
