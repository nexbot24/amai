import json
import re
import os
import base64

def extract():
    os.makedirs('assets', exist_ok=True)
    
    uuid_map = {}
    
    def process_manifest(filename):
        with open(filename, 'r') as f:
            content = f.read()
        manifest_match = re.search(r'<script type="__bundler/manifest">(.*?)</script>', content, re.DOTALL)
        if not manifest_match: return
        manifest = json.loads(manifest_match.group(1))
        
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
            
            out_name = f"assets/{uuid}.{ext}"
            uuid_map[uuid] = out_name
            
            data_str = asset.get('data', '')
            if data_str:
                with open(out_name, 'wb') as f:
                    f.write(base64.b64decode(data_str))

    process_manifest('/Users/jd/Downloads/Amai Landing (standalone).html')
    process_manifest('/Users/jd/Downloads/Amai Mobile (standalone).html')

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
            
        # Strip DC engine tags
        template = re.sub(r'<script src=".*?\.js"></script>', '', template)
        template = re.sub(r'<script src="[0-9a-fA-F-]+"></script>', '', template)
        template = re.sub(r'<script type="text/x-dc"[^>]*>.*?</script>', '', template, flags=re.DOTALL)
        template = template.replace('<x-dc>', '').replace('</x-dc>', '')
            
        with open(dest_filename, 'w') as f:
            f.write(template)

    process_file('/Users/jd/Downloads/Amai Landing (standalone).html', 'index.html')
    process_file('/Users/jd/Downloads/Amai Mobile (standalone).html', 'mobile.html')

if __name__ == '__main__':
    extract()
