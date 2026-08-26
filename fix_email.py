import re

with open('email-otp.html', 'r') as f:
    content = f.read()

# Change the main wrapper to be 100% width with a max-width
content = content.replace('width="600" style="width:600px;max-width:600px;"', 'width="100%" style="max-width:600px;"')

# Let's fix the 2-column layout so it stacks nicely or doesn't squish
old_table = """<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td width="50%" valign="top" style="width:50%;padding:0 10px 12px 0;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">Move or cancel a visit yourself</td>
          <td width="50%" valign="top" style="width:50%;padding:0 0 12px 10px;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">See your loyalty stamps</td>
        </tr>
        <tr>
          <td width="50%" valign="top" style="width:50%;padding:0 10px 0 0;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">Book again in two taps</td>
          <td width="50%" valign="top" style="width:50%;padding:0 0 0 10px;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">Keep your aftercare notes</td>
        </tr>
        </table>"""

new_table = """<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td valign="top" style="padding:0 0 12px 0;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">Move or cancel a visit yourself</td>
        </tr>
        <tr>
          <td valign="top" style="padding:0 0 12px 0;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">See your loyalty stamps</td>
        </tr>
        <tr>
          <td valign="top" style="padding:0 0 12px 0;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">Book again in two taps</td>
        </tr>
        <tr>
          <td valign="top" style="padding:0 0 0 0;font-family:Mulish,Arial,Helvetica,sans-serif;font-size:14px;line-height:23px;mso-line-height-rule:exactly;color:#4A3F36;">Keep your aftercare notes</td>
        </tr>
        </table>"""

content = content.replace(old_table, new_table)

with open('email-otp.html', 'w') as f:
    f.write(content)
