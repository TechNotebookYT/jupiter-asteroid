name = input("name: ")
data = input("data: ")

if input("type (x or u): ") == 'u':
    print(f'"{name}": "{data}",')
    print(f"url_data['{name}']")
else:
    jsonstr = ''
    for char in data:
        if char == '"':
            jsonstr += "\\" + char
        else:
            jsonstr += char
    print(f'"{name}_xpath": "{jsonstr}",')
    print(f"element_data['{name}_xpath']")


