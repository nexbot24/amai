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
    
    lenis_script = '''<style>
.fade-up { opacity: 0; transform: translateY(20px); transition: all 0.8s ease-out; }
.fade-up.visible { opacity: 1; transform: translateY(0); }
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
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
    
    # Template engine for sc-for loops
    context = {
        'groups': [
            {'title': 'Waxing', 'blurb': 'Professional waxing delivered with care, precision and comfort.', 'tabStyle': 'width:100%;text-align:left;background:#443B36;border:none;padding:24px 28px;cursor:pointer;color:#E8D5C4;display:flex;flex-direction:column;gap:12px', 'blurbStyle': 'font-size:14.5px;line-height:1.6;color:#B39C88'},
            {'title': 'Intimate Care', 'blurb': 'Thoughtful intimate beauty support focused on confidence, sensitivity and aftercare.', 'tabStyle': 'width:100%;text-align:left;background:#EBE3D8;border:none;padding:24px 28px;cursor:pointer;color:#241F1C;display:flex;flex-direction:column;gap:12px', 'blurbStyle': 'font-size:14.5px;line-height:1.6;color:#5C5148'},
            {'title': 'Skin, Body & Wellness', 'blurb': 'Future skin, body and wellness treatments created to elevate your self-care.', 'tabStyle': 'width:100%;text-align:left;background:#EBE3D8;border:none;padding:24px 28px;cursor:pointer;color:#241F1C;display:flex;flex-direction:column;gap:12px', 'blurbStyle': 'font-size:14.5px;line-height:1.6;color:#5C5148'}
        ],
        'activeItems': [
            {'name': 'First visit — consultation & treatment', 'price': 'from £30', 'time': '60 min'},
            {'name': 'Full leg wax', 'price': '£38', 'time': '45 min'},
            {'name': 'Half leg wax', 'price': '£26', 'time': '30 min'},
            {'name': 'Underarm wax', 'price': '£14', 'time': '15 min'},
            {'name': 'Arm wax', 'price': '£22', 'time': '25 min'},
            {'name': 'Facial waxing', 'price': 'from £12', 'time': '15 min'},
            {'name': 'Brow shape & tidy', 'price': '£16', 'time': '20 min'},
        ],
        'reasons': [
            {'n': '1', 'title': 'No double dipping', 'copy': "We never re-dip the spatula. It's a fresh one every time for complete hygiene."},
            {'n': '2', 'title': 'Premium hot wax', 'copy': 'We use advanced hot wax for sensitive areas, which shrink-wraps the hair without gripping the skin.'},
            {'n': '3', 'title': 'Expert therapists', 'copy': 'Our team specializes exclusively in waxing. No nails, no lashes, just exceptional waxing.'}
        ],
        'steps': [
            {'n': '1', 'title': 'Choose treatment', 'value': 'Full leg wax', 'rowStyle': 'display:grid;grid-template-columns:40px 1fr;gap:18px;padding:24px 0;border-top:1px solid rgba(232,213,196,0.2)', 'numStyle': 'width:40px;height:40px;border-radius:20px;background:#332C28;color:#B39C88;display:flex;align-items:center;justify-content:center;font-family:Marcellus,serif;font-size:18px'},
            {'n': '2', 'title': 'Pick a time', 'value': 'Tomorrow, 2:00 PM', 'rowStyle': 'display:grid;grid-template-columns:40px 1fr;gap:18px;padding:24px 0;border-top:1px solid rgba(232,213,196,0.2)', 'numStyle': 'width:40px;height:40px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);color:#B39C88;display:flex;align-items:center;justify-content:center;font-family:Marcellus,serif;font-size:18px'},
            {'n': '3', 'title': 'Confirm', 'value': '£10 deposit', 'rowStyle': 'display:grid;grid-template-columns:40px 1fr;gap:18px;padding:24px 0;border-top:1px solid rgba(232,213,196,0.2)', 'numStyle': 'width:40px;height:40px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);color:#B39C88;display:flex;align-items:center;justify-content:center;font-family:Marcellus,serif;font-size:18px'}
        ],
        'bars': [
            {'style': 'flex:1;height:3px;border-radius:1.5px;background:#E8D5C4'},
            {'style': 'flex:1;height:3px;border-radius:1.5px;background:rgba(232,213,196,0.18)'},
            {'style': 'flex:1;height:3px;border-radius:1.5px;background:rgba(232,213,196,0.18)'},
            {'style': 'flex:1;height:3px;border-radius:1.5px;background:rgba(232,213,196,0.18)'}
        ],
        'bookable': [
            {'name': 'First visit — consultation & treatment', 'time': '60 min', 'price': 'from £30', 'style': 'background:transparent;border:1px solid rgba(232,213,196,0.3);color:#F7F1EA;padding:16px 20px;display:flex;align-items:center;gap:12px;cursor:pointer', 'tick': 'width:18px;height:18px;border:none;background:#E8D5C4;border-radius:9px;margin-left:14px'},
            {'name': 'Full leg wax', 'time': '45 min', 'price': '£38', 'style': 'background:transparent;border:1px solid rgba(232,213,196,0.12);color:#B39C88;padding:16px 20px;display:flex;align-items:center;gap:12px;cursor:pointer', 'tick': 'width:18px;height:18px;border:1px solid rgba(232,213,196,0.25);border-radius:9px;margin-left:14px'},
            {'name': 'Half leg wax', 'time': '30 min', 'price': '£26', 'style': 'background:transparent;border:1px solid rgba(232,213,196,0.12);color:#B39C88;padding:16px 20px;display:flex;align-items:center;gap:12px;cursor:pointer', 'tick': 'width:18px;height:18px;border:1px solid rgba(232,213,196,0.25);border-radius:9px;margin-left:14px'},
            {'name': 'Underarm wax', 'time': '15 min', 'price': '£14', 'style': 'background:transparent;border:1px solid rgba(232,213,196,0.12);color:#B39C88;padding:16px 20px;display:flex;align-items:center;gap:12px;cursor:pointer', 'tick': 'width:18px;height:18px;border:1px solid rgba(232,213,196,0.25);border-radius:9px;margin-left:14px'},
            {'name': 'Arm wax', 'time': '25 min', 'price': '£22', 'style': 'background:transparent;border:1px solid rgba(232,213,196,0.12);color:#B39C88;padding:16px 20px;display:flex;align-items:center;gap:12px;cursor:pointer', 'tick': 'width:18px;height:18px;border:1px solid rgba(232,213,196,0.25);border-radius:9px;margin-left:14px'},
        ],
        'weekdays': ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
        'cells': [{'label': str(i), 'style': 'aspect-ratio:1;border:1px solid rgba(232,213,196,0.2);border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:15px;cursor:pointer;color:#E8D5C4;background:transparent'} for i in range(1, 29)],
        'slots': [{'label': '9:00 AM', 'style': 'padding:10px 16px;border:1px solid rgba(232,213,196,0.2);border-radius:4px;font-size:14px;cursor:pointer;color:#E8D5C4;background:transparent'}, {'label': '10:00 AM', 'style': 'padding:10px 16px;border:1px solid rgba(232,213,196,0.2);border-radius:4px;font-size:14px;cursor:pointer;color:#E8D5C4;background:transparent'}]
    }
    
    pattern = re.compile(r'<sc-for\s+list="\{\{\s*(\w+)\s*\}\}"\s+as="(\w+)"[^>]*>(.*?)</sc-for>', re.DOTALL)
    def replacer(match):
        list_name = match.group(1)
        item_name = match.group(2)
        inner_html = match.group(3)
        items = context.get(list_name, [])
        out = ""
        for item in items:
            rendered = inner_html
            if isinstance(item, dict):
                for k, v in item.items():
                    rendered = rendered.replace(f'{{{{ {item_name}.{k} }}}}', str(v))
            else:
                rendered = rendered.replace(f'{{{{ {item_name} }}}}', str(item))
            out += rendered
        return out
        
    while pattern.search(content):
        content = pattern.sub(replacer, content)
        
    content = content.replace('{{ activeHeading }}', 'Professional waxing, elevated.')
    content = content.replace('{{ activeCopy }}', 'Every appointment focuses on comfort, hygiene, detail and results — helping you leave feeling smooth, confident and cared for.')
    content = content.replace('{{ activeFootnote }}', 'We use premium hot wax for sensitive areas.')
    
    # Fix booking steps and tags in index.html
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep1\s*\}\}"[^>]*>', '<div id="booking-step-1" class="booking-step" style="display:block">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep2\s*\}\}"[^>]*>', '<div id="booking-step-2" class="booking-step" style="display:none">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep3\s*\}\}"[^>]*>', '<div id="booking-step-3" class="booking-step" style="display:none">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep4\s*\}\}"[^>]*>', '<div id="booking-step-4" class="booking-step" style="display:none">', content)
    
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*notSent\s*\}\}"[^>]*>', '<div style="display:contents">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*canGoBack\s*\}\}"[^>]*>', '<div style="display:contents">', content)
    content = re.sub(r'<sc-if[^>]*>', '<div style="display:contents">', content)
    content = content.replace('</sc-if>', '</div>')
    
    content = content.replace('{{ query }}', '')
    content = content.replace('{{ stepLabel }}', 'Step 1 of 4')
    content = content.replace('{{ helper }}', '')
    content = content.replace('{{ note }}', '')
    content = content.replace('{{ treatment }}', 'Treatment')
    content = content.replace('{{ whenLabel }}', 'Any day · any time')
    content = content.replace('{{ payApple }}', '')
    content = content.replace('{{ cardNum }}', '')
    content = content.replace('{{ cardExp }}', '')
    content = content.replace('{{ cardCvc }}', '')
    content = content.replace('{{ treatmentPrice }}', '£30')
    content = content.replace('{{ nameLabel }}', 'Your name')
    content = content.replace('{{ balance }}', '£20')
    content = content.replace('{{ nextLabel }}', 'Continue')
    content = content.replace('{{ confirmName }}', 'Thank you')
    
    content = re.sub(r'sc-camel-on-[a-z]+="[^"]*"', '', content)
    
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
    
    # Fix Booking Steps divs
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep1\s*\}\}"[^>]*>', '<div id="booking-step-1" class="booking-step" style="display:block">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep2\s*\}\}"[^>]*>', '<div id="booking-step-2" class="booking-step" style="display:none">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*isStep3\s*\}\}"[^>]*>', '<div id="booking-step-3" class="booking-step" style="display:none">', content)
    
    # Replace Generic sc-if tags left over
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*notSent\s*\}\}"[^>]*>', '<div id="booking-form-container" style="display:contents">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*showStepBar\s*\}\}"[^>]*>', '<div id="booking-step-bar" style="display:none; width:100%; justify-content:center; background:#241F1C">', content)
    content = re.sub(r'<sc-if[^>]*value="\{\{\s*canGoBack\s*\}\}"[^>]*>', '<div style="display:contents">', content)
    content = re.sub(r'<sc-if[^>]*>', '<div style="display:contents">', content)
    
    # Replace days and times loops
    days_html = '''
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid #E8D5C4;background:#E8D5C4;color:#3A322E;font-size:14px">Any day</button>
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Monday</button>
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Tuesday</button>
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Wednesday</button>
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Thursday</button>
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Friday</button>
    <button type="button" onclick="selectDay(this)" class="day-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Saturday</button>
    '''
    content = re.sub(r'<sc-for list="\{\{\s*days\s*\}\}".*?>.*?</sc-for>', days_html, content, flags=re.DOTALL)
    
    times_html = '''
    <button type="button" onclick="selectTime(this)" class="time-btn" style="padding:8px 16px;border-radius:20px;border:1px solid #E8D5C4;background:#E8D5C4;color:#3A322E;font-size:14px">Any time</button>
    <button type="button" onclick="selectTime(this)" class="time-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Morning</button>
    <button type="button" onclick="selectTime(this)" class="time-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:background:transparent;color:#E8D5C4;font-size:14px">Afternoon</button>
    <button type="button" onclick="selectTime(this)" class="time-btn" style="padding:8px 16px;border-radius:20px;border:1px solid rgba(232,213,196,0.25);background:transparent;color:#E8D5C4;font-size:14px">Evening</button>
    '''
    content = re.sub(r'<sc-for list="\{\{\s*times\s*\}\}".*?>.*?</sc-for>', times_html, content, flags=re.DOTALL)
    
    # Fix form placeholders and buttons
    # Save the buttons before stripping the camel case tags!
    content = content.replace('{{ nextLabel }}', 'Next')
    content = re.sub(r'<button[^>]*\{\{\s*back\s*\}\}[^>]*>.*?</button>', '<button onclick="prevStep()" style="min-height:52px;padding:0 20px;background:#3A322E;border:1px solid rgba(232,213,196,0.28);border-radius:26px 26px 0 0;color:#E8D5C4;font-family:Marcellus,serif;font-size:16px;cursor:pointer">Back</button>', content)
    content = re.sub(r'<button[^>]*\{\{\s*next\s*\}\}[^>]*>.*?</button>', '<button id="next-btn" onclick="nextStep()" style="min-height:52px;padding:0 24px;background:#E8D5C4;border:none;border-radius:26px 26px 0 0;color:#3A322E;font-family:Marcellus,serif;font-size:16px;cursor:pointer">Next</button>', content)
    content = re.sub(r'<button[^>]*\{\{\s*reset\s*\}\}[^>]*>.*?</button>', '<button onclick="resetBooking()" style="background:none;border:none;border-bottom:1px solid rgba(179,156,136,0.45);color:#B39C88;font-family:Marcellus,serif;font-size:15px;padding:10px 4px;margin-top:6px;cursor:pointer">Send another request</button>', content)

    content = content.replace('{{ chosenTreatment }}', '<span id="display-treatment">Treatment</span>')
    content = content.replace('{{ chosenTime }}', '<span id="display-time">Any day · any time</span>')
    content = content.replace('value="{{ name }}"', 'id="input-name"')
    content = content.replace('value="{{ contact }}"', 'id="input-contact"')
    content = content.replace('value="{{ note }}"', 'id="input-note"')
    content = re.sub(r'sc-camel-on-[a-z]+="[^"]*"', '', content)
    content = content.replace('{{ confirmName }}', '<span id="display-name">Thank you</span>')
    content = content.replace('{{ chosenWhen }}', '<span id="display-when">Any day · any time</span>')
    content = content.replace('{{ stepLabel }}', '<span id="display-step">Step 1 of 3</span>')
    
    # Replace stepDots loop
    step_dots_html = '''
    <div class="step-dot" style="width:6px;height:6px;border-radius:3px;background:#E8D5C4"></div>
    <div class="step-dot" style="width:6px;height:6px;border-radius:3px;background:rgba(232,213,196,0.25)"></div>
    <div class="step-dot" style="width:6px;height:6px;border-radius:3px;background:rgba(232,213,196,0.25)"></div>
    '''
    content = re.sub(r'<sc-for list="\{\{\s*stepDots\s*\}\}".*?>.*?</sc-for>', step_dots_html, content, flags=re.DOTALL)
    
    content = content.replace('{{ t.rowStyle }}', 'border:1px solid rgba(232,213,196,0.16);padding:16px 18px;display:flex;align-items:center;gap:14px;min-height:64px;cursor:pointer')
    content = content.replace('{{ t.tickStyle }}', 'width:24px;height:24px;border:1px solid rgba(232,213,196,0.25);border-radius:12px;margin-left:auto')
    
    content = content.replace('<sc-if style="display:none" value="{{ sent }}"', '<div id="view-sent" style="display:none">')
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
    
    const stepBar = document.getElementById('booking-step-bar');
    if (stepBar) stepBar.style.display = (tabId === 'book' && currentStep < 3 && !isSent) ? 'flex' : 'none';
}

let currentStep = 1;
let selectedTreatment = "First visit — consultation & treatment";
let isSent = false;

function selectTreatment(name) {
    selectedTreatment = name;
    document.getElementById('display-treatment').innerText = name;
    switchTab('book');
}

function selectTreatmentOption(name) {
    selectTreatment(name);
}

function updateStepView() {
    document.querySelectorAll('.booking-step').forEach(el => el.style.display = 'none');
    document.getElementById('booking-step-' + currentStep).style.display = 'block';
    const stepBar = document.getElementById('booking-step-bar');
    if (stepBar) stepBar.style.display = (currentStep < 3 && !isSent) ? 'flex' : 'none';
    
    if (currentStep === 2) {
        document.getElementById('next-btn').innerText = 'Send request';
    } else {
        document.getElementById('next-btn').innerText = 'Next';
    }
    
    const stepLabel = document.getElementById('display-step');
    if (stepLabel) stepLabel.innerText = 'Step ' + currentStep + ' of 3';
    
    const dots = document.querySelectorAll('.step-dot');
    dots.forEach((dot, index) => {
        dot.style.background = (index === currentStep - 1) ? '#E8D5C4' : 'rgba(232,213,196,0.25)';
    });
}

function nextStep() {
    if (currentStep === 1) {
        currentStep = 2;
        updateStepView();
    } else if (currentStep === 2) {
        currentStep = 3;
        isSent = true;
        const name = document.getElementById('input-name').value || "Thank you";
        document.getElementById('display-name').innerText = name.split(' ')[0];
        document.getElementById('booking-form-container').style.display = 'none';
        document.getElementById('view-sent').style.display = 'block';
        updateStepView();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepView();
    }
}

let selectedDay = "Any day";
let selectedTime = "Any time";

function selectDay(btn) {
    document.querySelectorAll('.day-btn').forEach(b => {
        b.style.background = 'transparent'; b.style.color = '#E8D5C4'; b.style.borderColor = 'rgba(232,213,196,0.25)';
    });
    btn.style.background = '#E8D5C4'; btn.style.color = '#3A322E'; btn.style.borderColor = '#E8D5C4';
    selectedDay = btn.innerText;
    updateWhen();
}

function selectTime(btn) {
    document.querySelectorAll('.time-btn').forEach(b => {
        b.style.background = 'transparent'; b.style.color = '#E8D5C4'; b.style.borderColor = 'rgba(232,213,196,0.25)';
    });
    btn.style.background = '#E8D5C4'; btn.style.color = '#3A322E'; btn.style.borderColor = '#E8D5C4';
    selectedTime = btn.innerText;
    updateWhen();
}

function updateWhen() {
    const when = selectedDay + ' · ' + selectedTime.toLowerCase();
    document.querySelectorAll('#display-when').forEach(el => el.innerText = when);
    document.getElementById('display-time').innerText = when;
}

function resetBooking() {
    currentStep = 1;
    isSent = false;
    document.getElementById('booking-form-container').style.display = 'block';
    document.getElementById('view-sent').style.display = 'none';
    document.getElementById('input-name').value = '';
    document.getElementById('input-contact').value = '';
    document.getElementById('input-note').value = '';
    updateStepView();
}
</script>
'''
    content = content.replace('</body>', js_logic + '\n</body>')
    content = content.replace('100vh', '100dvh')

    with open('mobile.html', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    build_index()
    build_mobile()
