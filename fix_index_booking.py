import re
with open('index.html', 'r') as f:
    content = f.read()

# I will find the step 3 block in index.html and update it.
step3 = content[content.find('<!-- 3. details -->'):content.find('<!-- 4. pay -->')]
print(step3)
