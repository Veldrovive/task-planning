print("Connecting to server")
http.websocketAsync("ws://127.0.0.1:8765")
_, url, handle = os.pullEvent("websocket_success")
print("Connected to server")

-- local data, binary = handle.receive()
-- if data then
--   print("Received: " .. data)
-- end
while true do
    local message = {
        topic = "test",
        message = "Hello from client"
    }
    handle.send(textutils.serializeJSON(message), false)
    os.sleep(1)
end