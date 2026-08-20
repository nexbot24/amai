import json
import re
import os
import base64

def extract():
    os.makedirs('assets', exist_ok=True)
    
    with open('/Users/jd/Downloads/Amai Landing (standalone).html', 'r') as f:
        content = f.read()

    manifest_match = re.search(r'<script type="__bundler/manifest">(.*?)</script>', content, re.DOTALL)
    if not manifest_match:
        print("No manifest found")
        return
        
    manifest = json.loads(manifest_match.group(1))
    uuid_map = {}
    
    for uuid, asset in manifest.items():
        ext = 'bin'
        mime = asset.get('mime', '')
        if 'jpeg' in mime: ext = 'jpg'
        elif 'png' in mime: ext = 'png'
        elif 'svg+xml' in mime: ext = 'svg'
        elif 'svg' in mime: ext = 'svg'
        elif 'woff2' in mime: ext = 'woff2'
        elif 'woff' in mime: ext = 'woff'
        elif 'ttf' in mime: ext = 'ttf'
        elif 'json' in mime: ext = 'json'
        elif 'javascript' in mime: ext = 'js'
        elif 'gif' in mime: ext = 'gif'
        elif 'webp' in mime: ext = 'webp'
        
        filename = f"assets/{uuid}.{ext}"
        uuid_map[uuid] = filename
        
        data_str = asset.get('data', '')
        if data_str:
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(data_str))

    def process_file(source_filename, dest_filename):
        with open(source_filename, 'r') as f:
            content = f.read()

        match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
        if not match:
            return
            
        json_str = match.group(1)
        template = json.loads(json_str)

        # Replace all UUIDs with local paths
        for uuid, path in uuid_map.items():
            template = template.replace(uuid, path)
            
        with open(dest_filename, 'w') as f:
            f.write(template)

    process_file('/Users/jd/Downloads/Amai Landing (standalone).html', 'index.html')
    process_file('/Users/jd/Downloads/Amai Mobile (standalone).html', 'mobile.html')

if __name__ == '__main__':
    extract()
