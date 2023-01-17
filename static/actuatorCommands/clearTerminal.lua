local ClearTerminal = {}

function ClearTerminal:run(data)
  term.clear()
  term.setCursorPos(1, 1)
  return nil
end

return ClearTerminal
