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

// Escape ALL </ sequences inside JSON to prevent browser HTML parser from
// seeing them as potential closing tags (not just </script>)
const jsonStr = JSON.stringify(template).replace(/<\//g, '<\\/');
const newMobile = before + '\n' + jsonStr + '\n  ' + after;

fs.writeFileSync(mobilePath, newMobile, 'utf8');
console.log('Rebundled mobile.html (' + Math.round(newMobile.length / 1024) + 'KB)');
