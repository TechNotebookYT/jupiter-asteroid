name = input("name: ")
data = input("data: ")

# Url json
if input("type (x or u): ") == 'u':
#   Printing URL JSON
    print(f'"{name}": "{data}",')
    print(f"url_data['{name}']")
# Xpath Json
else:
    jsonstr = ''
    for char in data:
        if char == '"':
            jsonstr += "\\" + char
        else:
            jsonstr += char
#     Printing XPATH
    print(f'"{name}_xpath": "{jsonstr}",')
    print(f"element_data['{name}_xpath']")


