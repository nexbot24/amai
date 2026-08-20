import re

def build_index():
    with open('index.html', 'r') as f:
        content = f.read()

    treatments = [
        {"name": "First visit — consultation & treatment", "time": "60 min", "price": "from £30"},
        {"name": "Full leg wax", "time": "45 min", "price": "£38"},
        {"name": "Half leg wax", "time": "30 min", "price": "£26"},
        {"name": "Underarm wax", "time": "15 min", "price": "£14"},
        {"name": "Bikini / Hollywood", "time": "30–45 min", "price": "£28–£42"},
        {"name": "Brow shape & tidy", "time": "20 min", "price": "£16"}
    ]

    sc_for_pattern = re.compile(r'<sc-for list="\{\{ treatments \}\}".*?>(.*?)</sc-for>', re.DOTALL)
    def replace_treatments(match):
        template = match.group(1)
        res = ""
        for t in treatments:
            s = template.replace("{{ t.name }}", t["name"]).replace("{{ t.time }}", t["time"]).replace("{{ t.price }}", t["price"])
            res += s
        return res

    content = sc_for_pattern.sub(replace_treatments, content)
    
    # Hide the "sent" message
    content = content.replace('<sc-if value="{{ sent }}"', '<sc-if style="display:none" id="sent-message" value="{{ sent }}"')
    content = content.replace('assets/c7902623-1ddf-461c-8032-6e8901b5005f.jpg', 'images/wax-pot.jpg')
    
    lenis_script = '''<script src="https://unpkg.com/@studio-freight/lenis@1.0.39/dist/lenis.min.js"></script>
<style>
.fade-up { opacity: 0; transform: translateY(20px); transition: all 0.8s ease-out; }
.fade-up.visible { opacity: 1; transform: translateY(0); }
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
    const lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
    function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
    
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
    content = content.replace('</head>', lenis_script + '\\n' + redirect_script + '\\n</head>')
    
    with open('index.html', 'w') as f:
        f.write(content)

def build_mobile():
    with open('mobile.html', 'r') as f:
        content = f.read()

    treatments = [
        {"name": "First visit — consultation & treatment", "time": "60 min", "price": "from £30"},
        {"name": "Full leg wax", "time": "45 min", "price": "£38"},
        {"name": "Half leg wax", "time": "30 min", "price": "£26"},
        {"name": "Underarm wax", "time": "15 min", "price": "£14"},
        {"name": "Bikini / Hollywood", "time": "30–45 min", "price": "£28–£42"},
        {"name": "Brow shape & tidy", "time": "20 min", "price": "£16"}
    ]
    popular = treatments[1:5]

    def render_loop(m, data_list, is_popular=False):
        t = m.group(1)
        res = ""
        for item in data_list:
            s = t.replace("{{ t.name }}", item["name"]).replace("{{ t.time }}", item["time"]).replace("{{ t.price }}", item["price"])
            s = s.replace('sc-camel-on-click="{{ t.pick }}"', f'onclick="selectTreatment(\'{item["name"]}\')"')
            s = s.replace('sc-camel-on-click="{{ t.select }}"', f'onclick="selectTreatmentOption(\'{item["name"]}\')"')
            res += s
        return res

    content = re.sub(r'<sc-for list="\{\{ popular \}\}".*?>(.*?)</sc-for>', lambda m: render_loop(m, popular, True), content, flags=re.DOTALL)
    content = re.sub(r'<sc-for list="\{\{ treatments \}\}".*?>(.*?)</sc-for>', lambda m: render_loop(m, treatments), content, flags=re.DOTALL)

    # Replace all sc-if tags with appropriate divs
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isHome\s*\}\}"[^>]*>', '<div id="view-home" style="display:block" class="view-section">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isTreatments\s*\}\}"[^>]*>', '<div id="view-treatments" style="display:none" class="view-section">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isBook\s*\}\}"[^>]*>', '<div id="view-book" style="display:none" class="view-section">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStudio\s*\}\}"[^>]*>', '<div id="view-studio" style="display:none" class="view-section">', content)
    
    # Generic replacement for remaining sc-if tags
    content = re.sub(r'<sc-if[^>]*>', '<div>', content)
    
    # Replace all closing sc-if tags
    content = content.replace('</sc-if>', '</div>')
    
    tabs_html = '''
    <button onclick="switchTab('home')" class="nav-tab" data-tab="home" style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:none;border:none;cursor:pointer;gap:4px;padding-top:10px">
        <div class="nav-mark" style="width:20px;height:24px;border:1px solid #CBB49E;border-bottom:none;border-radius:10px 10px 0 0;opacity:1"></div>
        <span class="nav-label" style="color:#CBB49E;font-size:10px;font-family:Marcellus,serif;letter-spacing:1px;opacity:1">HOME</span>
    </button>
    <button onclick="switchTab('treatments')" class="nav-tab" data-tab="treatments" style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:none;border:none;cursor:pointer;gap:4px;padding-top:10px">
        <div class="nav-mark" style="width:20px;height:24px;border:1px solid #CBB49E;border-bottom:none;border-radius:10px 10px 0 0;opacity:0.4"></div>
        <span class="nav-label" style="color:#CBB49E;font-size:10px;font-family:Marcellus,serif;letter-spacing:1px;opacity:0.4">TREATMENTS</span>
    </button>
    <button onclick="switchTab('book')" class="nav-tab" data-tab="book" style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:none;border:none;cursor:pointer;gap:4px;padding-top:10px">
        <div class="nav-mark" style="width:20px;height:24px;border:1px solid #CBB49E;border-bottom:none;border-radius:10px 10px 0 0;opacity:0.4"></div>
        <span class="nav-label" style="color:#CBB49E;font-size:10px;font-family:Marcellus,serif;letter-spacing:1px;opacity:0.4">BOOK</span>
    </button>
    <button onclick="switchTab('studio')" class="nav-tab" data-tab="studio" style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:none;border:none;cursor:pointer;gap:4px;padding-top:10px">
        <div class="nav-mark" style="width:20px;height:24px;border:1px solid #CBB49E;border-bottom:none;border-radius:10px 10px 0 0;opacity:0.4"></div>
        <span class="nav-label" style="color:#CBB49E;font-size:10px;font-family:Marcellus,serif;letter-spacing:1px;opacity:0.4">STUDIO</span>
    </button>
    '''
    content = re.sub(r'<sc-for list="\{\{\s*tabs\s*\}\}".*?>.*?</sc-for>', tabs_html, content, flags=re.DOTALL)
    
    js_logic = '''
<script>
function switchTab(tabId) {
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    const view = document.getElementById('view-' + tabId);
    if (view) view.style.display = 'block';
    
    document.querySelectorAll('.nav-tab').forEach(el => {
        const isActive = el.dataset.tab === tabId;
        const opacity = isActive ? '1' : '0.4';
        el.querySelector('.nav-mark').style.opacity = opacity;
        el.querySelector('.nav-label').style.opacity = opacity;
    });
}
function selectTreatment(name) {
    switchTab('book');
    // Basic logic for selecting treatment if needed
}
function selectTreatmentOption(name) {
    selectTreatment(name);
}
</script>
'''
    content = content.replace('</body>', js_logic + '\\n</body>')
    content = content.replace('100vh', '100dvh')

    with open('mobile.html', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    build_index()
    build_mobile()
