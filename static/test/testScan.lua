s = peripheral.find("geoScanner")

data = s.scan(8)

dataFile = fs.open("data.txt", "w")

allLocations = {}

for _, v in pairs(data) do
    table.insert(allLocations, tostring(v.x) .. "," .. tostring(v.y) .. "," .. tostring(v.z))
end

dataFile.write(textutils.serialize(allLocations))