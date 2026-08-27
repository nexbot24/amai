#!/usr/bin/env node
// Rebundle mobile.html from unpacked_template.html
// Usage: node rebundle.js

const fs = require('fs');
const path = require('path');

const dir = __dirname;
const templatePath = path.join(dir, 'unpacked_template.html');
const mobilePath = path.join(dir, 'mobile.html');

const template = fs.readFileSync(templatePath, 'utf8');
const mobile = fs.readFileSync(mobilePath, 'utf8');

// The template is stored as a JSON string between:
//   <script type="__bundler/template">
//   </script>
const startTag = '<script type="__bundler/template">';
const endTag = '  </script>';

const startIdx = mobile.indexOf(startTag);
if (startIdx === -1) {
  console.error('Could not find __bundler/template tag in mobile.html');
  process.exit(1);
}

// Find the closing </script> after the template start
const searchFrom = startIdx + startTag.length;
const endIdx = mobile.indexOf(endTag, searchFrom);
if (endIdx === -1) {
  console.error('Could not find closing script tag after template');
  process.exit(1);
}

// Build new mobile.html
const before = mobile.substring(0, startIdx + startTag.length);
const after = mobile.substring(endIdx);

// Encode template as base64 to completely avoid HTML parser issues.
// The bundler script will decode this before JSON.parse.
const jsonStr = JSON.stringify(template);
const b64 = Buffer.from(jsonStr).toString('base64');

// Split base64 into chunks of 76 chars per line to avoid
// ultra-long lines that some mobile browsers may truncate
const lines = [];
for (let i = 0; i < b64.length; i += 76) {
  lines.push(b64.substring(i, i + 76));
}
const b64Content = lines.join('\n');

const newMobile = before + '\n' + b64Content + '\n  ' + after;

fs.writeFileSync(mobilePath, newMobile, 'utf8');
console.log('Rebundled mobile.html (' + Math.round(newMobile.length / 1024) + 'KB)');
