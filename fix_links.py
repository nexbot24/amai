import os

for filename in ['manifest.json', 'm-hub.html', 'm-login.html', 'mobile.html']:
    if not os.path.exists(filename): continue
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace m-home.html with mobile.html
    new_content = content.replace('m-home.html', 'mobile.html')
    # Replace m-about.html with mobile.html
    new_content = new_content.replace('m-about.html', 'mobile.html')
    # Replace m-services.html with mobile.html
    new_content = new_content.replace('m-services.html', 'mobile.html')
    # Replace m-contact.html with mobile.html
    new_content = new_content.replace('m-contact.html', 'mobile.html')

    with open(filename, 'w') as f:
        f.write(new_content)

