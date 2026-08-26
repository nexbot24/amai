import re
with open('/Users/jd/Downloads/m-hub-3.html', 'r') as f:
    text = f.read()

funcs_to_extract = ['dayStamp', 'unreadChat', 'clock', 'fitChat', 'renderSugg', 'buildChat', 'renderThread', 'sendMsg']

for func in funcs_to_extract:
    match = re.search(r'function ' + func + r'\b[^\{]*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
    if match:
        print(f"--- {func} ---")
        print(match.group(0))

