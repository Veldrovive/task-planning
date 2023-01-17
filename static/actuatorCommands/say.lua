-- Say is a basic task that prints something to the screen and then waits for some time before returning

local Say = {}

function Say:run(data, requestInfo)
  local message
  if data.dynamic then
    message = requestInfo("sayWhat")
  else
    message = data.message
  end
  print(message)
  os.sleep(data.wait)
  return { said = message }
end

return Say
