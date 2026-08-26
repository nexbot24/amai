with open("mobile.html", "r") as f:
    content = f.read()

# Replace any instance of hub.html with m-hub.html (excluding when it's already m-hub.html)
content = content.replace('hub.html', 'm-hub.html')
content = content.replace('m-m-hub.html', 'm-hub.html')

with open("mobile.html", "w") as f:
    f.write(content)
