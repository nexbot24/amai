const fs = require('fs');
const html = fs.readFileSync('login.html', 'utf8');
const { JSDOM } = require('jsdom');
const dom = new JSDOM(html, { runScripts: "dangerously" });
console.log("Success");
