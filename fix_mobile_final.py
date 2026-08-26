with open("mobile.html", "r") as f:
    content = f.read()

content = content.replace(r'href=\"login.html\"', r'href=\"m-hub.html\"')
content = content.replace(r'href=\"m-login.html\"', r'href=\"m-hub.html\"')

with open("mobile.html", "w") as f:
    f.write(content)
