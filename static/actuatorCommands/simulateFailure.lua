local SimulateFailure = {}

function SimulateFailure:run(data)
  local failureType = data.failureType or "commandFailed"
  if failureType == "crash" then
    error("Simulated crash")
  elseif failureType == "hang" then
    while true do
      os.sleep(1)
    end
  elseif failureType == "reboot" then
    os.reboot()
  elseif failureType == "commandFailed" then
    -- return false, { failureReason = "Simulated failure" }
    error("Simulated failure")
  end
  return nil
end

return SimulateFailure
