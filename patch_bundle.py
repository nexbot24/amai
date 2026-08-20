import json
import re

def process(filename):
    with open(filename, 'r') as f:
        content = f.read()

    match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
    if not match:
        print("No template found in " + filename)
        return

    json_str = match.group(1)
    template = json.loads(json_str)

    treatments = [
        {"name": "First visit — consultation & treatment", "time": "60 min", "price": "from £30"},
        {"name": "Full leg wax", "time": "45 min", "price": "£38"},
        {"name": "Half leg wax", "time": "30 min", "price": "£26"},
        {"name": "Underarm wax", "time": "15 min", "price": "£14"},
        {"name": "Bikini / Hollywood", "time": "30–45 min", "price": "£28–£42"},
        {"name": "Brow shape & tidy", "time": "20 min", "price": "£16"}
    ]
    popular = treatments[1:5]

    def render_loop(m, data_list):
        t = m.group(1)
        res = ""
        for item in data_list:
            s = t.replace("{{ t.name }}", item["name"]).replace("{{ t.time }}", item["time"]).replace("{{ t.price }}", item["price"])
            res += s
        return res

    template = re.sub(r'<sc-for list="\{\{ popular \}\}".*?>(.*?)</sc-for>', lambda m: render_loop(m, popular), template, flags=re.DOTALL)
    template = re.sub(r'<sc-for list="\{\{ treatments \}\}".*?>(.*?)</sc-for>', lambda m: render_loop(m, treatments), template, flags=re.DOTALL)

    template = template.replace('<sc-if value="{{ sent }}"', '<sc-if style="display:none" value="{{ sent }}"')
    
    if "mobile" in filename:
        template = template.replace('<sc-if value="{{ isTreatments }}"', '<sc-if style="display:none" value="{{ isTreatments }}"')
        template = template.replace('<sc-if value="{{ isBook }}"', '<sc-if style="display:none" value="{{ isBook }}"')
        template = template.replace('<sc-if value="{{ isStudio }}"', '<sc-if style="display:none" value="{{ isStudio }}"')

    if "index" in filename:
        lenis_script = '''<script src="https://unpkg.com/@studio-freight/lenis@1.0.39/dist/lenis.min.js"></script>
<style>
.fade-up { opacity: 0; transform: translateY(20px); transition: all 0.8s ease-out; }
.fade-up.visible { opacity: 1; transform: translateY(0); }
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
    // Lenis smooth scroll
    const lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
    function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
    
    // Intersection Observer for scroll animations
    const elements = document.querySelectorAll('h1, h2, p, img, button, .treatment-row');
    elements.forEach(el => el.classList.add('fade-up'));
    
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => observer.observe(el));
});
</script>'''
        redirect_script = "<script>if (window.innerWidth <= 768) { window.location.href = 'mobile.html'; }</script>"
        template = template.replace('</head>', lenis_script + '\\n' + redirect_script + '\\n</head>')

    new_json_str = json.dumps(template)
    new_content = content[:match.start(1)] + new_json_str + content[match.end(1):]

    with open(filename, 'w') as f:
        f.write(new_content)

process('index.html')
process('mobile.html')
