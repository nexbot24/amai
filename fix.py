import re

def fix_index():
    with open("index.html", "r") as f:
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
    content = content.replace('<sc-if value="{{ sent }}"', '<sc-if style="display:none" value="{{ sent }}"')

    with open("index.html", "w") as f:
        f.write(content)

def fix_mobile():
    with open("mobile.html", "r") as f:
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

    def render_loop(match, data_list):
        template = match.group(1)
        res = ""
        for t in data_list:
            s = template.replace("{{ t.name }}", t["name"]).replace("{{ t.time }}", t["time"]).replace("{{ t.price }}", t["price"])
            res += s
        return res

    content = re.sub(r'<sc-for list="\{\{ popular \}\}".*?>(.*?)</sc-for>', lambda m: render_loop(m, popular), content, flags=re.DOTALL)
    content = re.sub(r'<sc-for list="\{\{ treatments \}\}".*?>(.*?)</sc-for>', lambda m: render_loop(m, treatments), content, flags=re.DOTALL)

    content = content.replace('<sc-if value="{{ isTreatments }}"', '<sc-if style="display:none" value="{{ isTreatments }}"')
    content = content.replace('<sc-if value="{{ isBook }}"', '<sc-if style="display:none" value="{{ isBook }}"')
    content = content.replace('<sc-if value="{{ isStudio }}"', '<sc-if style="display:none" value="{{ isStudio }}"')

    with open("mobile.html", "w") as f:
        f.write(content)

if __name__ == "__main__":
    fix_index()
    fix_mobile()
