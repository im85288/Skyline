"""Live TV's frosted glass, as Sky Stream's banner: one recipe shared by the
banner, the mini guide, the overlay's options sheet, channel number entry and
notices over live TV (tools/build_tv.py, build_options.py, build_glass.py)."""

GLASS = '80485A78'           # the banner's frosted blue-grey (50 per cent)
GLASS_TEXT = 'B3' + GLASS[2:]  # less see-through (70 per cent), for a panel of text

# Shown over live TV only: elsewhere these keep the skin's usual panels.
LIVE = 'VideoPlayer.Content(LiveTV) + Window.IsActive(fullscreenvideo)'


def raised_glass(x, y, w, h, fill=GLASS, visible=None, indent='        '):
    """A card of raised glass: a dark hairline just outside, the frosted fill,
    a soft glow down from the top edge and a bright rim."""
    p = indent
    out = '''
%(p)s<control type="group">%(visible)s
%(p)s    <left>%(x)d</left><top>%(y)d</top>
%(p)s    <control type="image">
%(p)s        <left>-2</left><top>-2</top><width>%(w4)d</width><height>%(h4)d</height>
%(p)s        <texture border="8" colordiffuse="8C000000">silo/guide_rim.png</texture>
%(p)s    </control>
%(p)s    <control type="image">
%(p)s        <width>%(w)d</width><height>%(h)d</height>
%(p)s        <texture border="8" colordiffuse="%(fill)s">silo/guide_cell.png</texture>
%(p)s    </control>
%(p)s    <control type="image">
%(p)s        <left>3</left><top>3</top><width>%(w6)d</width><height>40</height>
%(p)s        <texture flipy="true" colordiffuse="1AFFFFFF">silo/scrim_bottom_white.png</texture>
%(p)s    </control>
%(p)s    <control type="image">
%(p)s        <width>%(w)d</width><height>%(h)d</height>
%(p)s        <texture border="8" colordiffuse="B3E6EEFF">silo/guide_rim.png</texture>
%(p)s    </control>
%(p)s</control>'''
    return out % {'p': p, 'x': x, 'y': y, 'w': w, 'h': h, 'w4': w + 4, 'h4': h + 4, 'w6': w - 6, 'fill': fill,
                  'visible': '\n%s    <visible>%s</visible>' % (p, visible) if visible else ''}
