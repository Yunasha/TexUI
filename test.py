def update_body(body: list, symbol: str):
    body.pop(0)
    body.append(symbol)
    return body

body = ["-"] * 5
while 1:
    print(body)
    body = update_body(body, input("> "))    
