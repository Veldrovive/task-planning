local WriteFile = {}

function WriteFile:run(data)
  local filepath = data.filepath
  local contents = data.contents
  local file = fs.open(filepath, "w")
  file.write(contents)
  file.close()
  return nil
end

return WriteFile
