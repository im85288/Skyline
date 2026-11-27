#!/usr/bin/env python3
"""Live TV's raised glass (tools/glass.py) in two hand-written files: behind
channel number entry (Includes_PVR.xml) and behind notices while live TV is
full screen (DialogNotification.xml, which keeps its usual panel elsewhere).
Each piece sits between marker comments and is rewritten on every build."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import ROOT  # noqa: E402
from glass import GLASS, GLASS_TEXT, LIVE, raised_glass  # noqa: E402

# Channel number entry: the number on a small card in the middle of the screen.
NUMBER_W, NUMBER_H = 300, 180
NUMBER = ('\n\t\t<!-- Silo glass: number -->' +
          raised_glass((1920 - NUMBER_W) // 2, (1080 - NUMBER_H) // 2, NUMBER_W, NUMBER_H, GLASS,
                       '!String.IsEmpty(PVR.ChannelNumberInput)', indent='\t\t') +
          '\n\t\t<!-- end Silo glass: number -->')

# A notice over live TV: the panel's size (640 x 128) in the banner's glass.
NOTICE = ('\n\t\t\t<!-- Silo glass: notice -->' +
          raised_glass(0, 0, 640, 128, GLASS_TEXT, LIVE, indent='\t\t\t') +
          '\n\t\t\t<!-- end Silo glass: notice -->')


def patch(name, key, piece, anchor):
    """Puts piece between its markers, or the first time right after anchor."""
    path = os.path.join(ROOT, 'xml', name)
    text = open(path, encoding='utf-8').read()
    start, end = '<!-- Silo glass: %s -->' % key, '<!-- end Silo glass: %s -->' % key
    if start in text:
        a = text.rindex('\n', 0, text.index(start))
        text = text[:a] + text[text.index(end) + len(end):]
    if anchor not in text:
        sys.exit('build_glass: %s has no %r' % (name, anchor))
    text = text.replace(anchor, anchor + piece, 1)
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    patch('Includes_PVR.xml', 'number', NUMBER, '\t<include name="PVRChannelNumberInput">')
    # The usual panel stays everywhere else; the glass goes over it while watching live TV.
    path = os.path.join(ROOT, 'xml', 'DialogNotification.xml')
    text = open(path, encoding='utf-8').read()
    old = '<texture border="28" colordiffuse="SkylineGlass">silo/menu_panel.png</texture>\n\t\t\t</control>'
    if old in text:
        text = text.replace(old, old.replace('\n\t\t\t</control>', '\n\t\t\t\t<visible>![%s]</visible>\n\t\t\t</control>' % LIVE), 1)
        open(path, 'w', encoding='utf-8').write(text)
    patch('DialogNotification.xml', 'notice', NOTICE,
          '<visible>![%s]</visible>\n\t\t\t</control>' % LIVE)
    print('Wrote the raised glass into xml/Includes_PVR.xml and xml/DialogNotification.xml')
