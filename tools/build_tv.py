#!/usr/bin/env python3
"""Generate Skyline's TV guide (xml/MyPVRGuide.xml) and programme information
(xml/DialogPVRInfo.xml), the guide as Sky Stream lays one out
in Silo's look:

    python3 tools/build_tv.py

The focused programme at the top (channel, title, Sky's line, plot) over its
picture, which fills the top right; the channel groups as Silo's pills; then
the timeline on the skin's glass: channel names down the left,
programme titles across (finished ones dimmed), the focused one a lighter
band, a white line at the current time. Kodi fills the
groups (control 11) and the grid; the bar's TV tab opens it (Live TV only).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import BACKGROUND, ROOT, SAFE_X, TEXT, focus_zoom  # noqa: E402

GROUPS_ID, GRID_ID = 11, 51
DIM = '99EDEDED'
RAIL_ID = 52                # the guide's "Restart what's on now" row (KodiConnectForSilo's restart_now)
RAIL_HEAD_Y, RAIL_Y = 400, 446
RAIL_CARD_W, RAIL_CARD_H, RAIL_GAP = 384, 216, 24
RAIL_SHIFT = 222            # how far the grid sits lower while the row has focus (Sky's)
ON_RAIL = 'Control.HasFocus(%d)' % RAIL_ID
# The row's layout (the grid lower) unless the grid has focus: so while the row
# loads as the guide opens, nothing jumps to full screen and back.
OFF_GRID = '!Control.HasFocus(%d)' % GRID_ID
PILLS_Y = 408               # under the programme's details (Sky Stream's top half)
GRID_Y = PILLS_Y + 74      # 482: the ruler and 8 rows of 69 end at the screen's foot
CHANNEL_W = 400             # Sky OS 2.0's: the channel's logo (its name without one); no number (no number keys)
GUIDE_LOGO_W, GUIDE_LOGO_H = 160, 44
GUIDE_VIDEO_W, GUIDE_VIDEO_H = 352, 198   # what's playing, bottom right (Sky OS 2.0's)
ROW_H = 69                  # 8 channels on screen
GRID_ROWS = 8
BAND = 'CC272A30'           # the glass: the skin's Live TV veil (themed: SkylineLiveVeil), the picture faint behind
CHANNEL_BAND = BAND         # the channels' glass: the programmes' own
TILE = '1AFFFFFF'           # Sky's: each channel and programme a faint tile of its own, apart from the next
PANEL_X = SAFE_X - 16       # the glass starts just left of the channel names (the focus outline's edge)
RULER_H = 46
PREVIEW_W, PREVIEW_H = 496, 279
BLOCK_W = 60                # a 5-minute block
# Sky's blue (its highlight, brightened to read on the dark glass): the
# playing channel, the programme on now, today (TiviMate's places, in its
# yellow before).
ACCENT = 'FF3A9DFF'
# Progress bars white, as the player's (DialogSeekBar's SkylineFocus).
PROGRESS = 'FFEDEDED'
PLAYING = 'ListItem.IsPlaying'
# The guide's playing channel: its tile in the accent, softer as one of the
# rows, stronger with focus on it (over the lighter focused tile).
PLAYING_TILE, PLAYING_TILE_LIT = '523A9DFF', '993A9DFF'
# Kodi's Live TV banner hidden: Back hid it (silo.live.hidden, the channel it
# hid), or it's the one Kodi shows as a channel starts (KodiConnectForSilo's
# live.switched; Skyline's timers end it as the viewer browses, or once Kodi's
# own has gone). Kodi's banner can't be closed early, only timed.
LIVE_HIDDEN = '[String.IsEqual(Window(Home).Property(silo.live.hidden),VideoPlayer.ChannelName) | !String.IsEmpty(Window(Home).Property(silokodi.live.switched))]'

PILL_BG = 'E6262A33'          # the group pills' dark fill
ENDED = 'Integer.IsEqual(ListItem.Progress,100)'  # a programme that has finished


def playing_mark(left, top, size=24, colour=ACCENT, also='true'):
    """TiviMate's ▶ by the playing channel (also: when else it shows)."""
    return '''
                        <control type="label">
                            <left>%(x)d</left><top>%(y)d</top><width>%(s)d</width><height>%(s)d</height>
                            <align>center</align><aligny>center</aligny>
                            <font>silo_detail</font>
                            <textcolor>%(colour)s</textcolor>
                            <!-- Kodi marks the playing channel selected: the same colour then. -->
                            <selectedcolor>%(colour)s</selectedcolor>
                            <label>▶</label>
                            <visible>%(playing)s + %(also)s</visible>
                        </control>''' % {'x': left, 'y': top, 's': size, 'colour': colour, 'playing': PLAYING, 'also': also}


def channel(focused):
    """A channel down the left, as Sky OS 2.0's: its logo (its name without
    one) on a tile of its own, no number (the remote has no number keys);
    the playing channel's
    tile tinted blue, its name and TiviMate's ▶ white; the focused row's
    tile lighter, as its programme's,
    while the timeline has focus."""
    colour = TEXT if focused else 'C7EDEDED'
    tile = '''
                    <control type="image">
                        <left>%d</left><top>6</top><width>%d</width><height>%d</height>
                        <texture border="8" colordiffuse="%s">silo/guide_cell.png</texture>
                    </control>''' % (SAFE_X - 16, CHANNEL_W - SAFE_X + 4, ROW_H - 12,
                         '$VAR[SiloGuideCell]' if focused else TILE)
    # The playing channel's tile in a soft blue (the accent), a stronger one
    # with focus on it, over the usual tile: per row, by a visible condition
    # (Kodi works a $VAR colour out once per list).
    tile += '''
                    <control type="image">
                        <left>%d</left><top>6</top><width>%d</width><height>%d</height>
                        <texture border="8" colordiffuse="%s">silo/guide_cell.png</texture>
                        <visible>%s</visible>
                    </control>''' % (SAFE_X - 16, CHANNEL_W - SAFE_X + 4, ROW_H - 12,
                         '$VAR[SiloGuidePlaying]' if focused else PLAYING_TILE, PLAYING)
    # The channel's logo (Kodi's channel icon), as Sky OS 2.0's guide; a channel
    # without one (Kodi's default icon) shows its name instead.
    no_logo = '[String.IsEmpty(ListItem.Icon) | String.Contains(ListItem.Icon,DefaultTV)]'
    mark_x = CHANNEL_W - 12 - 44
    return tile + '''
                    <control type="image">
                        <left>%(x)d</left><top>%(ly)d</top><width>%(lw)d</width><height>%(lh)d</height>
                        <aspectratio align="left">keep</aspectratio>
                        <texture background="true">$INFO[ListItem.Icon]</texture>
                        <visible>!%(no_logo)s</visible>
                    </control>''' % {'x': SAFE_X, 'ly': (ROW_H - GUIDE_LOGO_H) // 2, 'lw': GUIDE_LOGO_W, 'lh': GUIDE_LOGO_H,
                        'no_logo': no_logo} + ''.join('''
                    <control type="label">
                        <left>%(x)d</left><top>0</top><width>%(w)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(c)s</textcolor>
                        <selectedcolor>%(c)s</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>%(no_logo)s + %(when)s</visible>
                    </control>''' % {'x': SAFE_X, 'w': mark_x - 8 - SAFE_X, 'h': ROW_H, 'c': c, 'no_logo': no_logo, 'when': when}
                    for c, when in (('FFFFFFFF', PLAYING), (colour, '!' + PLAYING))) + \
        playing_mark(mark_x, (ROW_H - 28) // 2, 28, 'FFFFFFFF')


def programme(focused):
    """A programme, as Sky Stream's: its title on a faint tile of its own,
    a gap from the next (Kodi widens the image with id 2 and the label with
    id 1 by the programme's length less the layout's, so its 3 px either
    side stay); focused (the timeline having focus), a lighter tile. The
    colours come from variables."""
    return '''
                    <control type="image" id="2">
                        <left>3</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="8" colordiffuse="%(fill)s">silo/guide_cell.png</texture>
                    </control>
                    <control type="label" id="1">
                        <left>18</left><top>6</top><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <label>%(label)s</label>
                    </control>''' % {'w': BLOCK_W - 6, 'lw': BLOCK_W - 30, 'h': ROW_H - 12,
                                      'fill': '$VAR[SiloGuideCell]' if focused else TILE,
                                      'label': '$VAR[SiloGuideTitle]' if focused else '$VAR[SiloGuideTitleRest]'}


def variables():
    """The focused programme's block and title: white with dark text while
    the grid has focus, as the others otherwise."""
    lit = 'Control.HasFocus(%d)' % GRID_ID
    return ('    <!-- Silo Skyline TV guide (tools/build_tv.py) -->\n'
            # The theme's names: tools/build_colours.py doesn't reach a variable's values.
            '    <variable name="SiloGuidePlaying">\n'
            '        <value condition="%(lit)s">%(playing_lit)s</value>\n'
            '        <value>%(playing)s</value>\n'
            '    </variable>\n'
            '    <variable name="SiloGuideCell">\n'
            '        <value condition="%(lit)s">40FFFFFF</value>\n'
            '        <value>%(tile)s</value>\n'
            '    </variable>\n'
            # A channel with no guide data: "No information", as TiviMate. What has
            # finished is dimmed, as Sky's.
            '    <variable name="SiloGuideTitle">\n'
            '        <value condition="%(lit)s + String.IsEmpty(ListItem.Label)">[COLOR B3FFFFFF]No information[/COLOR]</value>\n'
            '        <value condition="%(lit)s">[COLOR FFFFFFFF]$INFO[ListItem.Label][/COLOR]</value>\n'
            '        <value condition="String.IsEmpty(ListItem.Label)">[COLOR 80EDEDED]No information[/COLOR]</value>\n'
            '        <value condition="%(ended)s">[COLOR 66EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '        <value>[COLOR D9EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloGuideTitleRest">\n'
            '        <value condition="String.IsEmpty(ListItem.Label)">[COLOR 80EDEDED]No information[/COLOR]</value>\n'
            '        <value condition="%(ended)s">[COLOR 66EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '        <value>[COLOR D9EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '    </variable>\n'
            # The picture and plot of what has focus: a restart card's, else the programme's.
            '    <variable name="SiloGuidePicture">\n'
            '        <value condition="%(on_rail)s">$INFO[Container(%(rail)d).ListItem.Art(thumb)]</value>\n'
            '        <value>$INFO[ListItem.EpgEventIcon]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloGuidePlot">\n'
            '        <value condition="%(on_rail)s">$INFO[Container(%(rail)d).ListItem.Property(silo.plot)]</value>\n'
            '        <value>$INFO[ListItem.Plot]</value>\n'
            '    </variable>\n'
            # Sky's length: "30m", "2h", "1h 30m".
            '    <variable name="SiloGuideLength">\n'
            '        <value condition="String.IsEmpty(ListItem.Duration)"></value>\n'
            '        <value condition="Integer.IsGreater(ListItem.Duration(h),0) + Integer.IsGreater(ListItem.Duration(m),0)">$INFO[ListItem.Duration(h)]h $INFO[ListItem.Duration(m)]m</value>\n'
            '        <value condition="Integer.IsGreater(ListItem.Duration(h),0)">$INFO[ListItem.Duration(h)]h</value>\n'
            '        <value>$INFO[ListItem.Duration(m)]m</value>\n'
            '    </variable>\n'
            # Sky's "Started at 1.00pm": when the focused programme starts or started.
            '    <variable name="SiloGuideWhen">\n'
            '        <value condition="%(ended)s">Was on at $INFO[ListItem.StartTime]</value>\n'
            '        <value condition="Integer.IsGreater(ListItem.Progress,0)">Started at $INFO[ListItem.StartTime]</value>\n'
            '        <value condition="!String.IsEmpty(ListItem.StartTime)">Starts at $INFO[ListItem.StartTime]</value>\n'
            '    </variable>\n'
            ) % {'lit': lit, 'tile': TILE, 'playing': PLAYING_TILE, 'playing_lit': PLAYING_TILE_LIT, 'ended': ENDED, 'on_rail': ON_RAIL, 'rail': RAIL_ID} + stream_variables() + banner_variables() + '    <!-- end Silo Skyline TV guide -->\n'


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline TV guide (tools/build_tv.py) -->', '    <!-- end Silo Skyline TV guide -->\n'
    if start in text:
        text = text[:text.index(start)] + text[text.index(end) + len(end):]
    open(path, 'w', encoding='utf-8').write(text.replace('</includes>', variables() + '</includes>'))


def group_pill(focused, width=290):
    """A channel group: Silo's pill, the chosen group outlined, the focused
    one white. Dark, not see-through: they sit on the programme's picture.
    The pills share the full width between them (pill_layouts): width is a
    pill's slot, 12 px of it the gap."""
    chosen = 'ListItem.IsSelected'
    if focused:
        return '''
                    <control type="image">
                        <width>%(pw)d</width><height>52</height>
                        <texture border="26" colordiffuse="%(text)s">silo/pill_26.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="label">
                        <left>16</left><width>%(lw)d</width><height>52</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>FF000000</textcolor>
                        <selectedcolor>FF000000</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="image">
                        <width>%(pw)d</width><height>52</height>
                        <texture border="26" colordiffuse="%(pill_bg)s">silo/pill_26.png</texture>
                        <visible>!Control.HasFocus(%(id)d)</visible>
                    </control>                    <control type="image">
                        <width>%(pw)d</width><height>52</height>
                        <texture border="28" colordiffuse="D9FFFFFF">silo/season_ring.png</texture>
                        <visible>!Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="label">
                        <left>16</left><width>%(lw)d</width><height>52</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(text)s</textcolor>
                        <selectedcolor>%(text)s</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>!Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'text': TEXT, 'id': GROUPS_ID, 'pill_bg': PILL_BG, 'pw': width - 12, 'lw': width - 44}
    return '''
                    <control type="image">
                        <width>%(pw)d</width><height>52</height>
                        <texture border="26" colordiffuse="%(pill_bg)s">silo/pill_26.png</texture>
                    </control>
                    <control type="image">
                        <width>%(pw)d</width><height>52</height>
                        <texture border="28" colordiffuse="D9FFFFFF">silo/season_ring.png</texture>
                        <visible>%(chosen)s</visible>
                    </control>
                    <control type="label">
                        <left>16</left><width>%(lw)d</width><height>52</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <selectedcolor>%(dim)s</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>''' % {'chosen': chosen, 'dim': DIM, 'pill_bg': PILL_BG, 'pw': width - 12, 'lw': width - 44}


def pill_layouts():
    """The groups' layouts: as many pills as there are groups share the
    guide's width (Kodi picks a list's layout by its condition), up to
    eight; more scroll at 290 px."""
    full = 1920 - 2 * SAFE_X + 12  # the last pill's gap runs past the edge
    out = ''
    for count in range(2, 9):
        condition = 'Integer.IsEqual(Container(%d).NumItems,%d)' % (GROUPS_ID, count)
        width = full // count
        out += ('''
            <itemlayout width="%(w)d" height="52" condition="%(c)s">%(pill)s
            </itemlayout>
            <focusedlayout width="%(w)d" height="52" condition="%(c)s">%(focused)s
            </focusedlayout>''' % {'w': width, 'c': condition, 'pill': group_pill(False, width),
                                     'focused': group_pill(True, width)})
    return out + '''
            <itemlayout width="290" height="52">%s
            </itemlayout>
            <focusedlayout width="290" height="52">%s
            </focusedlayout>''' % (group_pill(False), group_pill(True))


RAIL_CARDS = 24  # KodiConnectForSilo's plugin.RESTART_CARDS


def rail_items():
    """The restart row's cards: one static item each, from silokodi.restart.N.*,
    shown while it has a title; OK plays it from its start."""
    out = ''
    for n in range(1, RAIL_CARDS + 1):
        p = 'Window(Home).Property(silokodi.restart.%d.%%s)' % n
        out += '''
                <item>
                    <label>$INFO[%(title)s]</label>
                    <thumb>$INFO[%(thumb)s]</thumb>
                    <property name="silo.logo">$INFO[%(logo)s]</property>
                    <property name="silo.started">$INFO[%(started)s]</property>
                    <property name="silo.plot">$INFO[%(plot)s]</property>
                    <property name="silo.minutes">$INFO[%(minutes)s]</property>
                    <property name="silo.length">$INFO[%(length)s]</property>
                    <property name="silo.quality">$INFO[%(quality)s]</property>
                    <property name="silo.live">$INFO[%(live)s]</property>
                    <onclick>RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=play_catchup&amp;channel=$INFO[%(channelid)s]&amp;start=$INFO[%(start)s])</onclick>
                    <visible>!String.IsEmpty(%(title)s)</visible>
                </item>''' % {k: p % k for k in ('title', 'thumb', 'logo', 'started', 'plot', 'minutes', 'length',
                                                  'quality', 'live', 'channelid', 'start')}
    return out


def rail_card(focused):
    """A restart card, as Sky Stream's: the programme's picture, the channel's
    logo on a dark tag at its top left, its title and "Started at 19:00" over
    a shade along its foot; focused, larger, as the skin's other cards."""
    zoom = focus_zoom('Control.HasFocus(%d)' % RAIL_ID, indent=20) if focused else ''
    return '''
                <control type="group">
                    <left>12</left><top>12</top>%(zoom)s
                    <control type="image">
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture border="8" colordiffuse="FF1A1D24">silo/guide_cell.png</texture>
                    </control>
                    <control type="image">
                        <width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png">$INFO[ListItem.Art(thumb)]</texture>
                    </control>
                    <control type="image">
                        <top>%(shade_y)d</top><width>%(w)d</width><height>%(shade_h)d</height>
                        <texture diffuse="silo/card_landscape_mask.png" colordiffuse="E6000000">silo/scrim_bottom.png</texture>
                    </control>
                    <control type="image">
                        <left>18</left><top>16</top><width>112</width><height>36</height>
                        <aspectratio>keep</aspectratio>
                        <texture background="true">$INFO[ListItem.Property(silo.logo)]</texture>
                    </control>
                    <control type="label">
                        <left>16</left><top>%(title_y)d</top><width>%(tw)d</width><height>40</height>
                        <aligny>center</aligny>
                        <font>silo_card_title</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                    <control type="label">
                        <left>16</left><top>%(sub_y)d</top><width>%(tw)d</width><height>32</height>
                        <aligny>center</aligny>
                        <font>silo_card_sub</font>
                        <textcolor>D9EDEDED</textcolor>
                        <label>$INFO[ListItem.Property(silo.started)]</label>
                    </control>
                </control>''' % {'zoom': zoom, 'w': RAIL_CARD_W, 'h': RAIL_CARD_H, 'shade_y': RAIL_CARD_H - 110, 'shade_h': 110,
                                         'title_y': RAIL_CARD_H - 82, 'sub_y': RAIL_CARD_H - 44, 'tw': RAIL_CARD_W - 32,
                                         'text': TEXT}


def build():
    # Whole rows: Kodi's page is the rows that fit in full, and it loads the
    # logo of a row past the page only once scrolled to. 1080 - GRID_Y held
    # 7 rows and most of an 8th, which showed its programmes but no logo.
    grid_h = RULER_H + GRID_ROWS * ROW_H
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <!-- Opens on the restart row, as Sky's (timer silo_guide_rail: the grid if it has no cards). -->
    <defaultcontrol always="true">%(rail)d</defaultcontrol>
    <views>%(grid)d</views>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>

        <!-- Sky Stream's guide: the focused programme's picture across the top
             right, faded into the page as the Home hero's art (Sky's, from the
             playlist's guide: ListItem.EpgEventIcon). No live video: the channel
             plays on in sound only while the guide is open, as Sky's. -->
        <!-- Full screen (guide_mask): faded to the left in the top half for the
             details, edge to edge behind the rows, so it shows through both
             sides of the glass. -->
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <aspectratio>scale</aspectratio>
            <fadetime>200</fadetime>
            <texture background="true" diffuse="silo/guide_mask.png">$VAR[SiloGuidePicture]</texture>
        </control>
        <!-- The day and times on a dark backing (a little see-through), faded in
             from above, so they read over the picture. -->
        <control type="image">
            <left>%(panel_x)d</left><top>%(ruler_fade_y)d</top><width>%(panel_w)d</width><height>%(ruler_fade_h)d</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <texture colordiffuse="%(background)s">silo/scrim_bottom.png</texture>
        </control>
        <control type="image">
            <left>%(panel_x)d</left><top>%(grid_y)d</top><width>%(panel_w)d</width><height>%(ruler_h)d</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <texture colordiffuse="%(ruler_bg)s">colors/white.png</texture>
        </control>
        <!-- Left of the restart row, the time row and the glass, the page: the
             picture's edge showed there. It stays put as the grid slides. -->
        <control type="image">
            <left>0</left><top>%(left_y)d</top><width>%(panel_x)d</width><height>%(left_h)d</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>

        <!-- Sky's glass under the rows (the day and times above stay on the
             picture): the programmes on see-through navy, the channels on the
             same a little less see-through, from just left of their names (a
             rounded corner there); a sheen and a fine light edge along the top.
             Kodi can't blur what's behind, so the glass is this. -->
        <control type="image">
            <left>%(panel_x)d</left><top>%(band_y)d</top><width>%(cw_panel)d</width><height>%(band_h)d</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <!-- Square: a rounded corner let the picture show through as coloured triangles. -->
            <texture colordiffuse="%(channel_band)s">colors/white.png</texture>
        </control>
        <control type="image">
            <left>%(cw)d</left><top>%(band_y)d</top><width>%(pw_band)d</width><height>%(band_h)d</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <texture colordiffuse="%(band)s">colors/white.png</texture>
        </control>
        <control type="image">
            <left>%(panel_x)d</left><top>%(band_y)d</top><width>%(panel_w)d</width><height>180</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <texture flipy="true" colordiffuse="17FFFFFF">silo/scrim_bottom.png</texture>
        </control>
        <control type="image">
            <left>%(edge_x)d</left><top>%(band_y)d</top><width>%(edge_w)d</width><height>2</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <texture colordiffuse="2EFFFFFF">colors/white.png</texture>
        </control>
        <!-- A dark fade along the top, so the clock reads over a bright picture. -->
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>200</height>
            <texture flipy="true" colordiffuse="%(top_fade)s">silo/scrim_bottom.png</texture>
        </control>
        <control type="label">
            <right>%(x)d</right><top>40</top><width>400</width><height>48</height>
            <align>right</align><aligny>center</aligny>
            <font>silo_meta</font>
            <textcolor>%(text)s</textcolor>
            <label>$INFO[System.Time]</label>
        </control>

        <!-- At the left, over the picture's fade: the channel, the title, Sky's
             line (LIVE, length, when it started) and the plot. -->
        <control type="group">
            <left>%(x)d</left><top>36</top>
            <!-- The channel's logo, as Sky's (KodiConnectForSilo publishes it:
                 Kodi 21 has no logo label for guide programmes), else its name. -->
            <control type="image">
                <width>320</width><height>72</height>
                <aspectratio align="left">keep</aspectratio>
                <texture background="true">$INFO[Window(Home).Property(silokodi.guide.logo)]</texture>
                <visible>%(logo_shown)s + !%(on_rail)s</visible>
            </control>
            <control type="image">
                <width>320</width><height>72</height>
                <aspectratio align="left">keep</aspectratio>
                <texture background="true">$INFO[Container(%(rail)d).ListItem.Property(silo.logo)]</texture>
                <visible>%(on_rail)s</visible>
            </control>
            <control type="label">
                <width>%(dw)d</width><height>72</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[ListItem.ChannelName]</label>
                <visible>%(name_shown)s + !%(on_rail)s</visible>
            </control>
            <control type="label">
                <top>80</top><width>%(dw)d</width><height>72</height>
                <aligny>center</aligny>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.Label]</label>
                <visible>!String.IsEmpty(ListItem.Label) + !%(on_rail)s</visible>
            </control>
            <!-- In the guide window ListItem is the grid's, whatever has focus: the row's
                 card is Container(%(rail)d)'s. -->
            <control type="label">
                <top>80</top><width>%(dw)d</width><height>72</height>
                <aligny>center</aligny>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[Container(%(rail)d).ListItem.Label]</label>
                <visible>%(on_rail)s</visible>
            </control>
            <!-- No programme (the guide has none): the channel's name, which on an
                 event channel says what's on. -->
            <control type="label">
                <top>80</top><width>%(dw)d</width><height>72</height>
                <aligny>center</aligny>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.ChannelName]</label>
                <visible>String.IsEmpty(ListItem.Label) + !%(on_rail)s</visible>
            </control>
            <control type="grouplist">
                <top>164</top><width>%(dw)d</width><height>36</height>
                <orientation>horizontal</orientation>
                <itemgap>20</itemgap>
                <visible>%(on_rail)s</visible>%(rail_live)s
                <control type="label">
                    <width>auto</width><height>36</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[Container(%(rail)d).ListItem.Property(silo.length)]</label>
                </control>%(rail_quality)s
                <control type="label">
                    <width>auto</width><height>36</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[Container(%(rail)d).ListItem.Property(silo.started)]</label>
                </control>
            </control>
            <control type="grouplist">
                <top>164</top><width>%(dw)d</width><height>36</height>
                <orientation>horizontal</orientation>
                <itemgap>20</itemgap>
                <visible>!%(on_rail)s</visible>%(guide_live)s
                <control type="label">
                    <width>auto</width><height>36</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloGuideLength]</label>
                </control>%(guide_quality)s
                <control type="label">
                    <width>auto</width><height>36</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloGuideWhen]</label>
                </control>
            </control>
            <control type="textbox">
                <top>214</top><width>%(dw)d</width><height>%(plot_h)d</height>
                <font>silo_plot</font>
                <textcolor>%(soft)s</textcolor>
                <label>$VAR[SiloGuidePlot]</label>
                <autoscroll>false</autoscroll>
            </control>
        </control>

        <!-- Sky Stream's "Restart what's on now": programmes on now on catch-up
             channels (KodiConnectForSilo's restart_now), OK from the start. The
             guide opens on it (timer silo_guide_rail); Down to the grid, which
             then takes the screen, Up from its first channel back here. -->
        <control type="label">
            <left>%(x)d</left><top>%(rail_head_y)d</top><width>800</width><height>40</height>
            <aligny>center</aligny>
            <font>silo_meta</font>
            <textcolor>%(text)s</textcolor>
            <label>Restart what's on now</label>
            <visible>%(off_grid)s</visible>
            <animation effect="fade" start="0" end="100" time="200">Visible</animation>
            <animation effect="fade" start="100" end="0" time="160">Hidden</animation>
        </control>
        <control type="list" id="%(rail)d">
            <left>%(rail_x)d</left><top>%(rail_y)d</top><width>%(rail_w)d</width><height>%(rail_h)d</height>
            <orientation>horizontal</orientation>
            <visible allowhiddenfocus="true">%(off_grid)s</visible>
            <animation effect="fade" start="0" end="100" time="200">Visible</animation>
            <animation effect="fade" start="100" end="0" time="160">Hidden</animation>
            <ondown>SetFocus(%(grid)d)</ondown>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
            <!-- The service keeps the cards ready (silokodi.restart.N.*): a plugin
                 listing took about 5 s to arrive as the guide opened. -->
            <content>%(rail_items)s
            </content>
            <itemlayout width="%(slot)d" height="%(rail_h)d">%(rail_card)s
            </itemlayout>
            <focusedlayout width="%(slot)d" height="%(rail_h)d">%(rail_card_focused)s
            </focusedlayout>
        </control>

        <!-- Channel groups (Kodi fills list 11): Silo's pills. Down to the
             timeline goes to now (Kodi's 0 on the grid): a new group keeps the
             time of the programme selected before, which can be hours ago.
             Back: window 1189 (GUIDE_BACK). -->
        <control type="list" id="%(groups)d">
            <!-- Hidden, as Sky Stream's guide has none (Kodi still fills it). -->
            <visible>false</visible>
            <left>%(x)d</left><top>%(pills_y)d</top><width>%(gw)d</width><height>52</height>
            <orientation>horizontal</orientation>
            <ondown>SetFocus(%(grid)d)</ondown>
            <ondown>Action(Number0)</ondown>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
%(pill_layouts)s
        </control>

        <!-- The timeline: channels down the left, programmes across. -->
        <control type="epggrid" id="%(grid)d">
            <left>0</left><top>%(grid_y)d</top><width>1920</width><height>%(grid_h)d</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <!-- Kodi's "vertical": channels down, time across (TiviMate's timeline). -->
            <orientation>vertical</orientation>
            <viewtype label="19298">list</viewtype>
            <timeblocks>%(blocks)d</timeblocks>
            <rulerunit>6</rulerunit>
            <onup>SetFocus(%(rail)d)</onup>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <!-- Now: a white line at the current time from the rows down (clear over
                 the time row), its dot at the rows' top; what has aired isn't shaded
                 (Sky's dims its titles instead). -->
            <progresstexture border="0,58,18,0" colordiffuse="F2FFFFFF">silo/epg_now_line.png</progresstexture>
            <!-- The ruler's first cell is the day, above the channels; the others
                 are the times (the only cells with a colon). -->
            <rulerlayout height="%(ruler_h)d" width="1400">
                <control type="label">
                    <left>14</left><width>%(half_hour)d</width><height>%(ruler_h)d</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(dim)s</textcolor>
                    <selectedcolor>%(dim)s</selectedcolor>
                    <label>$INFO[ListItem.Label]</label>
                    <visible>String.Contains(ListItem.Label,:)</visible>
                </control>
                <!-- The ruler's first cell is the day shown (Kodi's long date, as
                     System.Date's): "Today" for today, as Sky's, in white. -->
                <control type="label">
                    <left>%(date_x)d</left><width>%(date_w)d</width><height>%(ruler_h)d</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <label>$LOCALIZE[33006]</label>
                    <visible>!String.Contains(ListItem.Label,:) + String.IsEqual(ListItem.Label,System.Date)</visible>
                </control>
                <control type="label">
                    <left>%(date_x)d</left><width>%(date_w)d</width><height>%(ruler_h)d</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <label>$INFO[ListItem.Label]</label>
                    <visible>!String.Contains(ListItem.Label,:) + !String.IsEqual(ListItem.Label,System.Date)</visible>
                </control>
            </rulerlayout>
            <channellayout height="%(row_h)d" width="%(cw)d">%(channel)s
            </channellayout>
            <focusedchannellayout height="%(row_h)d" width="%(cw)d">%(channel_focused)s
            </focusedchannellayout>
            <itemlayout height="%(row_h)d" width="%(block)d">%(item)s
            </itemlayout>
            <focusedlayout height="%(row_h)d" width="%(block)d">%(item_focused)s
            </focusedlayout>
        </control>

        <!-- The time row's first, cut-off time (")0" of 22:00) faded into the
             row's dark backing: Kodi clips a half-hour that began before the
             grid's left edge; 56 px, the most a cut-off label reaches in (wider, it faded
             a whole time sitting near the edge). -->
        <control type="image">
            <left>%(cw)d</left><top>%(grid_y)d</top><width>56</width><height>%(ruler_h)d</height>
            <animation effect="slide" end="0,%(shift)d" time="240" tween="cubic" easing="out" condition="%(off_grid)s">Conditional</animation>
            <texture colordiffuse="%(background)s">silo/scrim_side.png</texture>
        </control>

        <!-- What's playing, in a box at the bottom right over the grid, as Sky
             OS 2.0's guide: a dark tile behind it (a channel still starting, or
             letterboxed), the video, then the faint rim the guide's tiles have. -->
        <control type="group">
            <left>%(vx)d</left><top>%(vy)d</top>
            <visible>Player.HasVideo</visible>
            <control type="image">
                <left>-4</left><top>-4</top><width>%(vbw)d</width><height>%(vbh)d</height>
                <texture border="8" colordiffuse="FF0D0F12">silo/guide_cell.png</texture>
            </control>
            <control type="videowindow">
                <width>%(vw)d</width><height>%(vh)d</height>
            </control>
            <control type="image">
                <left>-4</left><top>-4</top><width>%(vbw)d</width><height>%(vbh)d</height>
                <texture border="8" colordiffuse="66FFFFFF">silo/guide_rim.png</texture>
            </control>
        </control>

        <!-- Kodi's labels for the window's own use. -->
        <control type="label" id="29"><visible>false</visible></control>
        <control type="label" id="30"><visible>false</visible></control>
    </controls>
</window>
''' % {'grid': GRID_ID, 'groups': GROUPS_ID, 'background': BACKGROUND, 'x': SAFE_X, 'text': TEXT, 'dim': DIM,
       'logo_shown': '[!String.IsEmpty(Window(Home).Property(silokodi.guide.logo)) + '
                     'String.IsEqual(Window(Home).Property(silokodi.guide.logo_for),ListItem.ChannelName)]',
       # Only a channel with no logo shows its name: until the logo is known, neither.
       'name_shown': '[String.IsEmpty(Window(Home).Property(silokodi.guide.logo)) + '
                     'String.IsEqual(Window(Home).Property(silokodi.guide.logo_for),ListItem.ChannelName)]',
       'pills_y': PILLS_Y, 'dw': 1000, 'plot_h': 112,
       'vx': 1920 - SAFE_X - GUIDE_VIDEO_W, 'vy': 1080 - 40 - GUIDE_VIDEO_H, 'vw': GUIDE_VIDEO_W, 'vh': GUIDE_VIDEO_H,
       'vbw': GUIDE_VIDEO_W + 8, 'vbh': GUIDE_VIDEO_H + 8,
       'rail': RAIL_ID, 'on_rail': ON_RAIL, 'off_grid': OFF_GRID, 'shift': RAIL_SHIFT, 'rail_head_y': RAIL_HEAD_Y, 'rail_y': RAIL_Y,
       # The row's cards from the glass's left edge: no gap there for the picture to show through.
       'rail_x': PANEL_X - 12, 'rail_w': 1920 - PANEL_X + 12, 'rail_h': RAIL_CARD_H + 24, 'slot': RAIL_CARD_W + RAIL_GAP,
       'rail_card': rail_card(False), 'rail_card_focused': rail_card(True), 'rail_items': rail_items(),
       'rail_live': live_tag('!String.IsEmpty(Container(%d).ListItem.Property(silo.live))' % RAIL_ID, top=2,
                             indent='                '),
       'band': BAND, 'band_y': GRID_Y + RULER_H, 'ruler_fade_y': GRID_Y - 90, 'ruler_fade_h': 90,
       'ruler_bg': 'D9' + BACKGROUND[2:], 'top_fade': 'B3' + BACKGROUND[2:],
       'band_h': 1080 - GRID_Y - RULER_H + 40, 'pw_band': 1920 - CHANNEL_W, 'channel_band': CHANNEL_BAND,
       'panel_x': PANEL_X, 'cw_panel': CHANNEL_W - PANEL_X, 'panel_w': 1920 - PANEL_X,
       'edge_x': PANEL_X, 'edge_w': 1920 - PANEL_X, 'left_y': RAIL_Y - 12, 'left_h': 1080 - RAIL_Y + 12,

       'guide_live': live_tag(genre_live('ListItem'), top=2, indent='                '),
       'guide_quality': quality_badge('String.Contains(Window(Home).Property(silokodi.tv.uhd),ListItem.ChannelName)',
                                      '!String.IsEmpty(ListItem.ChannelName)'),
       'rail_quality': quality_badge('String.IsEqual(Container(%d).ListItem.Property(silo.quality),UHD)' % RAIL_ID,
                                     '!String.IsEmpty(Container(%d).ListItem.Property(silo.quality))' % RAIL_ID),
       'soft': 'D9EDEDED',
       'gw': 1920 - 2 * SAFE_X, 'pill_layouts': pill_layouts(),
       'grid_y': GRID_Y, 'grid_h': grid_h, 'ruler_h': RULER_H, 'row_h': ROW_H, 'cw': CHANNEL_W,
       'date_x': SAFE_X + 4, 'date_w': CHANNEL_W - SAFE_X - 4,
       'channel': channel(False), 'channel_focused': channel(True),
       'item': programme(False), 'item_focused': programme(True),
       # 5 minutes a block, half an hour 360 px (TiviMate's scale); as many as fit.
       'block': BLOCK_W, 'half_hour': 6 * BLOCK_W, 'blocks': (1920 - CHANNEL_W) // BLOCK_W}


# Kodi's programme information buttons (DialogPVRInfo): id, label (None: Kodi
# sets it, as Record's), and when it shows.
GUIDE_INFO = 'Window.IsActive(PVRGuideInfo)'
INFO_BUTTONS = ((5, '$LOCALIZE[19165]', GUIDE_INFO),                                       # Switch
                (10, '$LOCALIZE[19190]', GUIDE_INFO),                                      # Play programme
                (8, '$LOCALIZE[19687]', GUIDE_INFO + ' | Window.IsActive(PVRRecordingInfo)'),  # Play recording
                (6, None, GUIDE_INFO),                                                     # Record
                (9, '$LOCALIZE[19061]', GUIDE_INFO),                                       # Add timer
                (11, '$LOCALIZE[826]', GUIDE_INFO),                                        # Reminder
                (4, '$LOCALIZE[19003]', GUIDE_INFO + ' | Window.IsActive(PVRRecordingInfo)'))  # Find similar


def info_button(control_id, label, visible):
    """A programme action as Silo's pill: white with dark text on focus."""
    return '''
                <control type="button" id="%(id)d">
                    <width>auto</width><height>64</height>%(label)s
                    <font>silo_tab</font>
                    <textoffsetx>36</textoffsetx>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="30" colordiffuse="2EFFFFFF">silo/pill.png</texturenofocus>
                    <visible>%(visible)s</visible>
                </control>''' % {'id': control_id, 'text': TEXT, 'visible': visible,
                                  'label': '\n                    <label>%s</label>' % label if label else ''}


def build_info():
    """Kodi's programme information (from the guide, or a recording's), as
    Silo's details page: the channel, title, time and plot at the left, the
    programme's picture at the right, its actions as Silo's pills."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">9000</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="160">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
            <control type="image">
                <left>0</left><top>0</top><width>1920</width><height>1080</height>
                <texture colordiffuse="%(background)s">colors/white.png</texture>
            </control>
            <control type="group">
                <left>%(x)d</left><top>120</top>
                <control type="grouplist">
                    <width>1000</width><height>64</height>
                    <orientation>horizontal</orientation>
                    <itemgap>18</itemgap>
                    <control type="image">
                        <width>112</width><height>64</height>
                        <aspectratio align="left">keep</aspectratio>
                        <texture>$INFO[ListItem.ChannelLogo]</texture>
                        <visible>!String.IsEmpty(ListItem.ChannelLogo)</visible>
                    </control>
                    <control type="label">
                        <width>auto</width><height>64</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(dim)s</textcolor>
                        <selectedcolor>%(dim)s</selectedcolor>
                        <label>$INFO[ListItem.ChannelNumberLabel,,  ·  ]$INFO[ListItem.ChannelName]</label>
                    </control>
                </control>
                <control type="textbox">
                    <top>90</top><width>1000</width><height>132</height>
                    <font>silo_osd_title</font>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <label>$INFO[ListItem.Title]$INFO[ListItem.EpisodeName,[CR][COLOR B3EDEDED],[/COLOR]]</label>
                </control>
                <control type="grouplist">
                    <top>236</top><width>1000</width><height>36</height>
                    <orientation>horizontal</orientation>
                    <itemgap>18</itemgap>
                    <control type="label">
                        <width>auto</width><height>36</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <selectedcolor>%(text)s</selectedcolor>
                        <label>$INFO[ListItem.Date]$INFO[ListItem.EndTime, – ,]$INFO[ListItem.Genre,  ·  ,]</label>
                    </control>
                    <control type="progress">
                        <top>15</top><width>180</width><height>6</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>ListItem.Progress</info>
                        <visible>Integer.IsGreater(ListItem.Progress,0) + Integer.IsLess(ListItem.Progress,100)</visible>
                    </control>
                </control>
                <control type="textbox">
                    <top>296</top><width>1000</width><height>290</height>
                    <font>silo_plot</font>
                    <textcolor>B3EDEDED</textcolor>
                    <selectedcolor>B3EDEDED</selectedcolor>
                    <label>$INFO[ListItem.Plot]</label>
                </control>
            </control>
            <control type="group">
                <left>%(px)d</left><top>120</top>
                <control type="image">
                    <width>%(pw)d</width><height>%(ph)d</height>
                    <texture border="20" colordiffuse="FF000000">silo/card_landscape_mask.png</texture>
                </control>
                <control type="image">
                    <width>%(pw)d</width><height>%(ph)d</height>
                    <aspectratio>keep</aspectratio>
                    <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                </control>
            </control>
            <!-- The programme's actions (Kodi's ids: it acts on them and sets Record's label). -->
            <control type="grouplist" id="9000">
                <left>%(x)d</left><top>760</top><width>%(bw)d</width><height>64</height>
                <orientation>horizontal</orientation>
                <itemgap>16</itemgap>%(buttons)s
            </control>
        </control>
    </controls>
</window>
''' % {'x': SAFE_X, 'background': BACKGROUND, 'text': TEXT, 'dim': DIM, 'px': 1920 - SAFE_X - PREVIEW_W,
       'pw': PREVIEW_W, 'ph': PREVIEW_H, 'bw': 1920 - 2 * SAFE_X,
       'buttons': ''.join(info_button(*button) for button in INFO_BUTTONS)}


# KodiConnectForSilo's picture and live flag for the channel the banner shows,
# browsed (Up/Down) or playing: Kodi gives only the playing programme's.
BANNER_PICTURE = '!String.IsEmpty(Window(Home).Property(silokodi.tv.banner_picture))'
BANNER_LIVE = 'String.IsEqual(Window(Home).Property(silokodi.tv.banner_live),1)'
# Left/Right while browsing channels, as Sky's: the shown channel's earlier or
# later programme (KodiConnectForSilo's banner.py, silokodi.banner.*).
BANNER_STEPPED = '!String.IsEmpty(Window(Home).Property(silokodi.banner.title))'
STEPPED = 'Window(Home).Property(silokodi.banner.%s)'
BANNER_HAS_PICTURE = '[[%s + !String.IsEmpty(%s)] | [!%s + %s]]' % (
    BANNER_STEPPED, STEPPED % 'picture', BANNER_STEPPED, BANNER_PICTURE)
BANNER_SHOWS_LIVE = '[[%s + String.IsEqual(%s,1)] | [!%s + %s]]' % (
    BANNER_STEPPED, STEPPED % 'live', BANNER_STEPPED, BANNER_LIVE)


# Live TV's banner: one glass card across the screen (Sky Stream's had a
# channel column at the left and its next programmes off the screen's edge):
# the channel's logo, name, day and time along its top; the programme's
# picture, title and plot; the next two programmes inside its right end.
SKY_H = 360
SKY_Y = 1080 - 36 - SKY_H                     # the card
SKY_CARD_X, SKY_CARD_W = SAFE_X - 40, 1920 - 2 * (SAFE_X - 40)
SKY_HEAD_H = 56                               # the channel's row, at the card's top
SKY_PIC_W, SKY_PIC_H = 400, 225
SKY_NEXT_W, SKY_NEXT_GAP = 230, 20
SKY_NEXT_H = SKY_NEXT_W * 9 // 16
SKY_NEXT_X = SKY_CARD_X + SKY_CARD_W - 24 - 2 * SKY_NEXT_W - SKY_NEXT_GAP


def outline_badge(label, condition, top=4):
    """Sky's badge (HD, UHD, 5.1): white text in a thin white outline, as wide as its text."""
    return """
                    <control type="button">
                        <top>%(top)d</top><width>auto</width><height>30</height>
                        <label>%(label)s</label>
                        <font>silo_badge</font>
                        <textoffsetx>8</textoffsetx>
                        <aligny>center</aligny>
                        <enable>false</enable>
                        <disabledcolor>%(text)s</disabledcolor>
                        <texturenofocus border="8" colordiffuse="%(text)s">silo/badge_outline.png</texturenofocus>
                        <texturefocus border="8" colordiffuse="%(text)s">silo/badge_outline.png</texturefocus>
                        <visible>%(condition)s</visible>
                    </control>""" % {'top': top, 'label': label, 'condition': condition, 'text': TEXT}


def sky_next(n, y):
    """A next programme inside the banner's right end, as Sky's: title above, picture, time below."""
    x = SKY_NEXT_X + (n - 1) * (SKY_NEXT_W + SKY_NEXT_GAP)
    shown = ('[[%(s)s + !String.IsEmpty(Window(Home).Property(silokodi.banner.next%(n)d.title))] | '
             '[!%(s)s + !String.IsEmpty(Window(Home).Property(silokodi.tv.next%(n)d.title))]]'
             % {'s': BANNER_STEPPED, 'n': n})
    return """
            <control type="group">
                <left>%(x)d</left><top>%(y)d</top>
                <visible>%(shown)s</visible>
                <control type="label">
                    <top>4</top><width>%(w)d</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$VAR[SiloBannerNext%(n)dTitle]</label>
                </control>
                <control type="image">
                    <top>52</top><width>%(w)d</width><height>%(h)d</height>
                    <texture border="8" colordiffuse="CC1A1D24">silo/guide_cell.png</texture>
                </control>
                <control type="image">
                    <top>52</top><width>%(w)d</width><height>%(h)d</height>
                    <aspectratio>scale</aspectratio>
                    <texture background="true" diffuse="silo/card_landscape_mask.png">$VAR[SiloBannerNext%(n)dPicture]</texture>
                </control>
                <control type="image">
                    <left>40</left><top>82</top><width>%(lw)d</width><height>%(lh)d</height>
                    <aspectratio>keep</aspectratio>
                    <texture>$VAR[SiloBannerLogo]</texture>
                    <visible>%(no_picture)s</visible>
                </control>
                <control type="label">
                    <top>%(time_y)d</top><width>%(w)d</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$VAR[SiloBannerNext%(n)dTime]</label>
                </control>
            </control>""" % {'x': x, 'y': y + SKY_HEAD_H + 12, 'shown': shown, 'n': n, 'w': SKY_NEXT_W, 'h': SKY_NEXT_H,
                             'lw': SKY_NEXT_W - 80, 'lh': SKY_NEXT_H - 60,
                             'no_picture': ('[[%(s)s + String.IsEmpty(Window(Home).Property(silokodi.banner.next%(n)d.picture))] | '
                                            '[!%(s)s + String.IsEmpty(Window(Home).Property(silokodi.tv.next%(n)d.picture))]]'
                                            % {'s': BANNER_STEPPED, 'n': n}),
                             'time_y': 52 + SKY_NEXT_H + 10, 'text': TEXT, 'shadow': 'CC000000'}


HINT = 'Window(Home).Property(silokodi.banner.hint)'
# KodiConnectForSilo's hints (banner.py hint()) as Sky shows a key: the key
# in an outline, then what it does, in white.
HINT_ACTIONS = (('OK  Watch from the start', 'Watch from the start'), ('OK  Remind me', 'Remind me'),
                ('OK  Watch', 'Watch'), ('Reminder set  ·  OK to remove', 'Remove reminder'))


def sky_key(key, text, condition):
    """A key and what it does, as Sky's: the key outlined, the words in white."""
    return outline_badge(key, condition) + """
                <control type="label">
                    <width>auto</width><height>38</height>
                    <aligny>center</aligny>
                    <font>silo_card_sub</font>
                    <textcolor>%s</textcolor><shadowcolor>CC000000</shadowcolor>
                    <label>%s</label>
                    <visible>%s</visible>
                </control>""" % (TEXT, text, condition)


def sky_keys():
    """The row's keys: OK (watch, remind, watch from the start) and Left/Right
    while stepping; OK to watch while browsing channels."""
    ok = '%s + [%s]' % (BANNER_STEPPED, ' | '.join('String.IsEqual(%s,%s)' % (HINT, h) for h, _ in HINT_ACTIONS))
    return (sky_key('OK', '$VAR[SiloBannerAction]', ok) +
            sky_key('OK', 'Watch', 'Player.ChannelPreviewActive + !%s' % BANNER_STEPPED) + """
                <control type="label">
                    <width>auto</width><height>38</height>
                    <aligny>center</aligny>
                    <font>silo_card_sub</font>
                    <textcolor>D9EDEDED</textcolor><shadowcolor>CC000000</shadowcolor>
                    <label>Not on catch-up</label>
                    <visible>%s + String.IsEqual(%s,Not on catch-up)</visible>
                </control>""" % (BANNER_STEPPED, HINT) +
            sky_key('◀ ▶', 'Earlier, later', BANNER_STEPPED))


def sky_banner():
    """Live TV's banner: one glass card across the screen, in the programme's
    colour. Along its top the channel's logo, its name, the day and the time;
    under them the programme's picture (the progress line, its times and HD/UHD
    under it), its title (two lines at most), its plot and a row of LIVE, the
    time left and the sound and HDR badges; the next two programmes in the
    card's right end. Left/Right's stepped programme (silokodi.banner.*) shows
    in the card, with its hint on the row."""
    y, px = SKY_Y, SKY_CARD_X + 24
    pic_y = y + SKY_HEAD_H + 16
    tx = px + SKY_PIC_W + 32
    tw = SKY_NEXT_X - 32 - tx
    times_y = pic_y + SKY_PIC_H + 18
    playing = '!String.IsEmpty(VideoPlayer.EndTime) + !%s' % BANNER_STEPPED
    return """
            <!-- The card: glass with a faint rim, as Sky's, in the programme's colour
                 (KodiConnectForSilo's tv.playing_tint, the browsed channel's while
                 browsing, as the OK screen's shade) at the glass's 65 per cent; else navy. -->
            <control type="image">
                <left>%(card_x)d</left><top>%(y)d</top><width>%(card_w)d</width><height>%(card_h)d</height>
                <texture border="8" colordiffuse="A6141820">silo/guide_cell.png</texture>
                <visible>String.IsEmpty(Window(Home).Property(silokodi.tv.playing_tint))</visible>
            </control>
            <control type="image">
                <left>%(card_x)d</left><top>%(y)d</top><width>%(card_w)d</width><height>%(card_h)d</height>
                <texture border="8" colordiffuse="$INFO[Window(Home).Property(silokodi.tv.playing_tint)]">silo/guide_cell.png</texture>
                <animation effect="fade" start="65" end="65" time="0" condition="true">Conditional</animation>
                <visible>!String.IsEmpty(Window(Home).Property(silokodi.tv.playing_tint))</visible>
            </control>
            <control type="image">
                <left>%(card_x)d</left><top>%(y)d</top><width>%(card_w)d</width><height>%(card_h)d</height>
                <texture border="8" colordiffuse="66FFFFFF">silo/guide_rim.png</texture>
            </control>
            <!-- The channel's row: its logo, then its name, the day and the time. -->
            <control type="image">
                <left>%(px)d</left><top>%(head_y)d</top><width>120</width><height>44</height>
                <aspectratio align="left">keep</aspectratio>
                <texture>$VAR[SiloBannerLogo]</texture>
            </control>
            <control type="label">
                <left>%(head_x)d</left><top>%(head_y)d</top><width>%(head_w)d</width><height>44</height>
                <aligny>center</aligny>
                <font>silo_card_sub</font>
                <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                <label>[B]$VAR[SiloBannerChannelName][/B]$INFO[System.Date(dddd),     ,]$INFO[System.Time,  ·  ,]</label>
            </control>
            <!-- The picture; no picture, the channel's logo alone. -->
            <control type="image">
                <left>%(px)d</left><top>%(pic_y)d</top><width>%(pw)d</width><height>%(ph)d</height>
                <texture border="8" colordiffuse="CC1A1D24">silo/guide_cell.png</texture>
            </control>
            <control type="image">
                <left>%(px)d</left><top>%(pic_y)d</top><width>%(pw)d</width><height>%(ph)d</height>
                <aspectratio>scale</aspectratio>
                <texture background="true" diffuse="silo/card_landscape_mask.png">$VAR[SiloBannerPicture]</texture>
                <visible>%(picture)s</visible>
            </control>
            <control type="image">
                <left>%(logo_alone_x)d</left><top>%(logo_alone_y)d</top><width>%(logo_alone_w)d</width><height>%(logo_alone_h)d</height>
                <aspectratio>keep</aspectratio>
                <texture>$VAR[SiloBannerLogo]</texture>
                <visible>!%(picture_or)s</visible>
            </control>
            <control type="progress">
                <left>%(px)d</left><top>%(bar_y)d</top><width>%(pw)d</width><height>4</height>
                <texturebg colordiffuse="40FFFFFF">colors/white.png</texturebg>
                <midtexture colordiffuse="%(progress)s">colors/white.png</midtexture>
                <info>PVR.EpgEventProgress</info>
                <visible>%(playing)s</visible>
            </control>
            <control type="label">
                <left>%(px)d</left><top>%(times_y)d</top><width>%(pw)d</width><height>36</height>
                <aligny>center</aligny>
                <font>silo_card_sub</font>
                <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                <label>$VAR[SiloBannerTimes]</label>
            </control>
            <control type="grouplist">
                <left>%(px)d</left><top>%(times_y)d</top><width>%(pw)d</width><height>36</height>
                <orientation>horizontal</orientation><align>right</align>
                <itemgap>8</itemgap>%(quality)s
            </control>
            <!-- The title (a long one on two lines, as no scrolling) and the plot
                 under it, as much as fits; then the row. -->
            <control type="grouplist">
                <left>%(tx)d</left><top>%(pic_y)d</top><width>%(tw)d</width><height>%(text_h)d</height>
                <orientation>vertical</orientation>
                <itemgap>8</itemgap>
                <usecontrolcoords>false</usecontrolcoords>
                <control type="textbox">
                    <width>%(tw)d</width><height max="88">auto</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$VAR[SiloBannerTitle]</label>
                    <autoscroll>false</autoscroll>
                </control>
                <control type="textbox">
                    <width>%(tw)d</width><height max="144">auto</height>
                    <font>silo_plot</font>
                    <textcolor>E6EDEDED</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$VAR[SiloBannerPlot]</label>
                    <autoscroll>false</autoscroll>
                </control>
            </control>
            <control type="grouplist">
                <left>%(tx)d</left><top>%(times_y)d</top><width>%(row_w)d</width><height>38</height>
                <orientation>horizontal</orientation>
                <itemgap>16</itemgap>%(live)s
                <control type="label">
                    <width>auto</width><height>38</height>
                    <aligny>center</aligny>
                    <font>silo_card_sub</font>
                    <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$VAR[SiloBannerLeft]</label>
                    <visible>%(playing)s</visible>
                </control>%(badges)s
%(keys)s
            </control>%(nexts)s""" % {
        'y': y, 'card_x': SKY_CARD_X, 'card_w': SKY_CARD_W, 'card_h': SKY_H,
        'head_y': y + 14, 'head_x': px + 136, 'head_w': SKY_CARD_W - 48 - 136,
        'px': px, 'pic_y': pic_y, 'pw': SKY_PIC_W, 'ph': SKY_PIC_H,
        'logo_alone_x': px + 40, 'logo_alone_y': pic_y + 30, 'logo_alone_w': SKY_PIC_W - 80,
        'logo_alone_h': SKY_PIC_H - 60,
        'bar_y': pic_y + SKY_PIC_H + 8, 'times_y': times_y,
        'tx': tx, 'tw': tw, 'text_h': times_y - pic_y - 8,
        'row_w': SKY_CARD_X + SKY_CARD_W - 24 - tx,
        'text': TEXT, 'shadow': 'CC000000', 'progress': PROGRESS, 'playing': playing,
        'picture': BANNER_HAS_PICTURE, 'picture_or': '[%s]' % BANNER_HAS_PICTURE,
        'live': live_tag(BANNER_SHOWS_LIVE, top=4, indent='                '),
        'quality': outline_badge('$VAR[SiloBannerQuality]',
                                 '[Player.ChannelPreviewActive | !String.IsEmpty(VideoPlayer.VideoResolution)] + !%s'
                                 % BANNER_STEPPED),
        'badges': ''.join(outline_badge(label, '%s + !%s + !Player.ChannelPreviewActive' % (cond, BANNER_STEPPED))
                          for label, cond in (('$VAR[SiloLiveHdr]', '!String.IsEmpty(VideoPlayer.HdrType)'),
                                              ('$VAR[SiloLiveAudio]', '!String.IsEmpty(VideoPlayer.AudioChannels)'))),
        'keys': sky_keys(),
        'nexts': sky_next(1, y) + sky_next(2, y)}


FPS = (('59.9', '60'), ('60', '60'), ('50', '50'), ('48', '48'), ('29.9', '30'), ('30', '30'), ('25', '25'),
       ('23.9', '24'), ('24', '24'))


def quality_badge(uhd, shown):
    """Sky's HD / UHD badge beside a programme's length: outlined, in a
    grouplist (UHD for the channels the playlist plays in UHD: uhd)."""
    return ''.join('''
                <control type="group">
                    <width>%(w)d</width><height>36</height>
                    <visible>%(when)s</visible>
                    <control type="image">
                        <top>4</top><width>%(w)d</width><height>28</height>
                        <texture border="8" colordiffuse="%(text)s">silo/badge_outline.png</texture>
                    </control>
                    <control type="label">
                        <top>4</top><width>%(w)d</width><height>28</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_badge</font>
                        <textcolor>%(text)s</textcolor>
                        <label>%(label)s</label>
                    </control>
                </control>''' % {'w': w, 'label': label, 'text': TEXT, 'when': '%s + %s' % (shown, when)}
                   for label, w, when in (('UHD', 62, uhd), ('HD', 46, '!' + uhd)))


LIVE_RED = 'FFE0262F'  # Sky's red for a live event


def live_tag(condition, top=4, indent='                    '):
    """Sky's LIVE tag: white on red, a rounded tag for a programme shown as it
    happens (the guide's Live category: Kodi's genre, with IPTV Simple's
    useEpgGenreText), a disabled button so it fits any row of facts."""
    return '''
%(p)s<control type="button">
%(p)s    <top>%(top)d</top><width>auto</width><height>32</height>
%(p)s    <label>LIVE</label>
%(p)s    <font>silo_badge</font>
%(p)s    <textoffsetx>10</textoffsetx>
%(p)s    <aligny>center</aligny>
%(p)s    <enable>false</enable>
%(p)s    <disabledcolor>FFFFFFFF</disabledcolor>
%(p)s    <texturenofocus border="8" colordiffuse="%(red)s">silo/badge_solid.png</texturenofocus>
%(p)s    <texturefocus border="8" colordiffuse="%(red)s">silo/badge_solid.png</texturefocus>
%(p)s    <visible>%(condition)s</visible>
%(p)s</control>''' % {'p': indent, 'top': top, 'red': LIVE_RED, 'condition': condition}


def live_badge(condition, indent='                        '):
    """The LIVE tag inside a list's item layout, where Kodi draws no buttons:
    an image and a label."""
    return '''
%(p)s<control type="image">
%(p)s    <width>60</width><height>28</height>
%(p)s    <texture border="8" colordiffuse="%(red)s">silo/badge_solid.png</texture>
%(p)s    <visible>%(c)s</visible>
%(p)s</control>
%(p)s<control type="label">
%(p)s    <width>60</width><height>28</height>
%(p)s    <align>center</align><aligny>center</aligny>
%(p)s    <font>silo_badge</font>
%(p)s    <textcolor>FFFFFFFF</textcolor>
%(p)s    <label>LIVE</label>
%(p)s    <visible>%(c)s</visible>
%(p)s</control>''' % {'p': indent, 'red': LIVE_RED, 'c': condition}


def genre_live(item):
    """An item shown live: the guide's Live category in its genre."""
    return 'String.Contains(%s.Genre,Live)' % item


def banner_variables():
    """The banner's text and picture: the programme Left/Right stepped to, else Kodi's."""
    def var(name, stepped, kodi):
        return ('    <variable name="%s">\n        <value condition="%s">$INFO[%s]</value>\n'
                '        <value>%s</value>\n    </variable>\n' % (name, BANNER_STEPPED, STEPPED % stepped, kodi))
    # The OK screen's shade: the playing programme's colour (KodiConnectForSilo's
    # tv.playing_tint, the TV page's tint for its picture), else the page's near-black.
    tint = ('    <variable name="SiloLiveTint">\n'
            '        <value condition="!String.IsEmpty(Window(Home).Property(silokodi.tv.playing_tint))">'
            '$INFO[Window(Home).Property(silokodi.tv.playing_tint)]</value>\n'
            '        <value>F2%s</value>\n    </variable>\n' % BACKGROUND[2:] +
            '    <variable name="SiloNoteTint">\n'
            '        <value condition="!String.IsEmpty(Window(Home).Property(silokodi.next.tint))">'
            '$INFO[Window(Home).Property(silokodi.next.tint)]</value>\n'
            '        <value condition="!String.IsEmpty(Window(Home).Property(silokodi.tv.playing_tint))">'
            '$INFO[Window(Home).Property(silokodi.tv.playing_tint)]</value>\n'
            '        <value>SkylineGlass</value>\n    </variable>\n'
            # Its label: white on a tinted panel (the blue read poorly on a blue one), else the accent.
            '    <variable name="SiloNoteLabel">\n'
            '        <value condition="!String.IsEmpty(Window(Home).Property(silokodi.next.tint)) | '
            '!String.IsEmpty(Window(Home).Property(silokodi.tv.playing_tint))">FFEDEDED</value>\n'
            '        <value>%s</value>\n    </variable>\n' % ACCENT)
    return (tint + var('SiloBannerTitle', 'title', '$INFO[VideoPlayer.Title]') +
            var('SiloBannerTimes', 'times', '$INFO[VideoPlayer.StartTime]$INFO[VideoPlayer.EndTime, — ,]') +
            var('SiloBannerPlot', 'plot', '$INFO[VideoPlayer.Plot]') +
            var('SiloBannerPicture', 'picture', '$INFO[Window(Home).Property(silokodi.tv.banner_picture)]') +
            var('SiloBannerLogo', 'logo', '$INFO[Player.Icon]') +
            ''.join(var('SiloBannerNext%d%s' % (n, key.title()), 'next%d.%s' % (n, key),
                        '$INFO[Window(Home).Property(silokodi.tv.next%d.%s)]' % (n, key))
                    for n in (1, 2) for key in ('title', 'time', 'picture')) +
            '    <variable name="SiloBannerAction">\n' + ''.join(
                '        <value condition="String.IsEqual(%s,%s)">%s</value>\n' % (HINT, h, a) for h, a in HINT_ACTIONS) +
            '    </variable>\n' +
            '    <variable name="SiloBannerChannelName">\n        <value condition="%s">$INFO[%s]</value>\n'
            '        <value>$INFO[VideoPlayer.ChannelName]</value>\n    </variable>\n' % (BANNER_STEPPED, STEPPED % 'channel') +
            # Sky's time left: "55m left", "1h 20m left".
            '    <variable name="SiloBannerLeft">\n'
            '        <value condition="Integer.IsGreater(PVR.EpgEventRemainingTime(h),0) + Integer.IsGreater(PVR.EpgEventRemainingTime(m),0)">$INFO[PVR.EpgEventRemainingTime(h)]h $INFO[PVR.EpgEventRemainingTime(m)]m left</value>\n'
            '        <value condition="Integer.IsGreater(PVR.EpgEventRemainingTime(h),0)">$INFO[PVR.EpgEventRemainingTime(h)]h left</value>\n'
            '        <value condition="!String.IsEmpty(PVR.EpgEventRemainingTime(m))">$INFO[PVR.EpgEventRemainingTime(m)]m left</value>\n'
            '    </variable>\n' +
            '    <variable name="SiloBannerChannel">\n        <value condition="%s">$INFO[%s,,  ]$INFO[%s]</value>\n'
            '        <value>$INFO[VideoPlayer.ChannelNumberLabel,,  ]$INFO[VideoPlayer.ChannelName]</value>\n'
            '    </variable>\n' % (BANNER_STEPPED, STEPPED % 'number', STEPPED % 'channel'))


def stream_variables():
    fps = ''.join('        <value condition="String.StartsWith(Player.Process(videofps),%s)">%s</value>\n' % pair for pair in FPS)
    # TiviMate's names: 4K, FHD (1080), HD (720), SD; STEREO for 2.0.
    return ('    <variable name="SiloBannerQuality">\n'  # a browsed channel's: the playlist's UHD ones (KodiConnectForSilo's tv.uhd)
            '        <value condition="Player.ChannelPreviewActive + String.Contains(Window(Home).Property(silokodi.tv.uhd),VideoPlayer.ChannelName)">UHD</value>\n'
            '        <value condition="Player.ChannelPreviewActive">HD</value>\n'
            '        <value>$VAR[SiloLiveQuality]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloLiveQuality">\n'  # Sky's badge: UHD, HD or SD
            '        <value condition="String.IsEqual(VideoPlayer.VideoResolution,4K)">UHD</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.VideoResolution,1080) | String.IsEqual(VideoPlayer.VideoResolution,720)">HD</value>\n'
            '        <value>SD</value>\n'
            '    </variable>\n'
            '    <variable name="SiloLiveResolution">\n'
            '        <value condition="String.IsEqual(VideoPlayer.VideoResolution,1080)">FHD</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.VideoResolution,720)">HD</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.VideoResolution,576) | String.IsEqual(VideoPlayer.VideoResolution,540) | String.IsEqual(VideoPlayer.VideoResolution,480)">SD</value>\n'
            '        <value>$INFO[VideoPlayer.VideoResolution]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloLiveFps">\n' + fps + '    </variable>\n'
            '    <variable name="SiloLiveHdr">\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,dolbyvision)">DOLBY VISION</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,hdr10plus)">HDR10+</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,hdr10)">HDR10</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,hlg)">HLG</value>\n'
            '        <value>[UPPERCASE]$INFO[VideoPlayer.HdrType][/UPPERCASE]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloLiveAudio">\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,1)">MONO</value>\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,2)">STEREO</value>\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,6)">5.1</value>\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,8)">7.1</value>\n'
            '        <value>$INFO[VideoPlayer.AudioChannels,, CH]</value>\n'
            '    </variable>\n')


def corners():
    """The playing channel's group at the top left and the time at the right, as TiviMate's."""
    return '''
            <control type="label">
                <left>88</left><top>40</top><width>900</width><height>56</height>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[VideoPlayer.ChannelGroup]</label>
            </control>
            <control type="label">
                <right>88</right><top>40</top><width>600</width><height>56</height>
                <align>right</align>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[System.Date(ddd d mmm)]$INFO[System.Time,  ·  ,]</label>
            </control>''' % {'text': TEXT}


def banner():
    """Live TV's banner (a channel change, Info) in Kodi's seek bar window,
    as TiviMate's in Silo's look; Estuary's stays for its own OSD."""
    return '''		<!-- Silo Skyline Live TV banner (tools/build_tv.py) -->
		<control type="group">
			<!-- Not under the banner window (1183, Left/Right), which draws its own. -->
			<visible>VideoPlayer.Content(LiveTV) + [Player.ShowInfo | Window.IsActive(fullscreeninfo) | Player.ChannelPreviewActive] + !%(hidden)s + !Window.IsActive(videoosd) + !Window.IsActive(pvrosdchannels) + !Window.IsActive(%(ok)d) + !Window.IsActive(%(banner_window)d)</visible>
			<animation effect="slide" start="0,120" end="0,0" time="220" tween="cubic" easing="out">Visible</animation>
			<animation effect="fade" start="100" end="0" time="160">Hidden</animation>
			<!-- As Sky's: a light fade under the banner, no black band, nothing at the top. -->
			<control type="image">
				<left>0</left><top>560</top><width>1920</width><height>520</height>
				<texture colordiffuse="B3FFFFFF">silo/scrim_bottom.png</texture>
			</control>%(info)s
		</control>
		<!-- end Silo Skyline Live TV banner -->
''' % {'ok': OK_ID, 'banner_window': BANNER_WINDOW, 'info': sky_banner(), 'hidden': LIVE_HIDDEN}


TIMER_START, TIMER_END = '    <!-- Silo Skyline TV (tools/build_tv.py) -->\n', '    <!-- end Silo Skyline TV -->\n'
# The OK screen closes after 5 s without a key (TiviMate: 3 s, too quick from the sofa).
TIMERS = '''    <!-- Left and Right in Live TV (KodiConnectForSilo's keymap sets silo.live.step),
         while watching, the Live TV overlay (window 1198) on its recent channels, the channel
         watched before selected: OK switches to it (a new silokodi.recent_changed reloads the row,
         so it starts on the first tile in the current order, whatever switched
         the channel); with the banner up (Info or browsing), the banner's
         programmes, as Sky Stream's: note the
         channel it shows, open Skyline's banner window (it holds the keys after)
         and step. -->
    <!-- Held Left / Right (silo.live.step -2 / 2): skip 5 minutes back or on, as Sky's. -->
    <timer>
        <name>silo_live_skip_back</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.live.step),-2)</start>
        <onstart>ClearProperty(silo.live.step,home)</onstart>
        <onstart>Seek(-300)</onstart>
        <stop>true</stop>
    </timer>
    <timer>
        <name>silo_live_skip_on</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.live.step),2)</start>
        <onstart>ClearProperty(silo.live.step,home)</onstart>
        <onstart>Seek(300)</onstart>
        <stop>true</stop>
    </timer>
    <!-- Back hid Kodi's banner (window 1188 or 1183 noted the channel in
         silo.live.hidden; Kodi's banner can't be closed early, only timed, by
         Display channel info): once Kodi's own has gone, forget it. Browsing
         to another channel shows the banner again (the names differ). -->
    <timer>
        <name>silo_live_switch_seen</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silokodi.live.switched),1) + Player.ShowInfo</start>
        <onstart>SetProperty(silokodi.live.switched,2,home)</onstart>
        <stop>true</stop>
    </timer>
    <timer>
        <name>silo_live_switch_end</name>
        <start reset="true">!String.IsEmpty(Window(Home).Property(silokodi.live.switched)) + [Player.ChannelPreviewActive | [String.IsEqual(Window(Home).Property(silokodi.live.switched),2) + !Player.ShowInfo]]</start>
        <onstart>ClearProperty(silokodi.live.switched,home)</onstart>
        <stop>true</stop>
    </timer>
    <!-- The Live TV overlay (OK, Left/Right) closes after %(idle)d s without a key, unless paused. -->
    <timer>
        <name>silo_recent_idle</name>
        <start reset="true">Window.IsActive(%(window)d) + System.IdleTime(%(idle)d) + !Player.Paused</start>
        <onstart>Dialog.Close(%(window)d)</onstart>
        <stop>true</stop>
    </timer>
    <!-- Kodi keeps a reloaded list on the item it had, so the row would open on
         the tile chosen last time: once loaded, the first tile (the channel
         watched before), then play/pause unless Left/Right opened it. The row stays
         unseen until then (card_row). -->
    <timer>
        <name>silo_recent_first</name>
        <start reset="true">Window.IsActive(%(window)d) + Integer.IsGreater(Container(%(list)d).NumItems,0) + String.IsEmpty(Window(Home).Property(silo.recent.placed))</start>
        <onstart>SetFocus(%(list)d,0,absolute)</onstart>
        <onstart condition="!String.IsEqual(Window(Home).Property(silo.ok.from),row)">SetFocus(%(play)d)</onstart>
        <onstart>SetProperty(silo.recent.placed,1,home)</onstart>
        <stop>true</stop>
    </timer>
    <timer>
        <name>silo_live_unhide</name>
        <start reset="true">!String.IsEmpty(Window(Home).Property(silo.live.hidden)) + !Player.ShowInfo + !Player.ChannelPreviewActive</start>
        <onstart>ClearProperty(silo.live.hidden,home)</onstart>
        <stop>true</stop>
    </timer>
    <timer>
        <name>silo_live_left</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.live.step),-1)</start>
        <onstart>ClearProperty(silo.live.step,home)</onstart>
        <onstart condition="!%(banner_up)s">SetProperty(silo.ok.from,row,home)</onstart>
        <onstart condition="!%(banner_up)s">ActivateWindow(%(window)d)</onstart>
        <onstart condition="%(banner_up)s + !Window.IsActive(%(banner_window)d)">SetProperty(silo.live.for,$INFO[VideoPlayer.ChannelName],home)</onstart>
        <onstart condition="%(banner_up)s + !Window.IsActive(%(banner_window)d)">ActivateWindow(%(banner_window)d)</onstart>
        <onstart condition="%(banner_up)s">RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=banner_step&amp;dir=-1)</onstart>
        <stop>true</stop>
    </timer>
    <timer>
        <name>silo_live_right</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.live.step),1)</start>
        <onstart>ClearProperty(silo.live.step,home)</onstart>
        <onstart condition="!%(banner_up)s">SetProperty(silo.ok.from,row,home)</onstart>
        <onstart condition="!%(banner_up)s">ActivateWindow(%(window)d)</onstart>
        <onstart condition="%(banner_up)s + !Window.IsActive(%(banner_window)d)">SetProperty(silo.live.for,$INFO[VideoPlayer.ChannelName],home)</onstart>
        <onstart condition="%(banner_up)s + !Window.IsActive(%(banner_window)d)">ActivateWindow(%(banner_window)d)</onstart>
        <onstart condition="%(banner_up)s">RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=banner_step&amp;dir=1)</onstart>
        <stop>true</stop>
    </timer>
    <!-- Long OK in Live TV (KodiConnectForSilo's keymap sets silo.live.longok):
         the OK screen's channel menu (Remove from recent channels) while it's
         open, else the TV guide. The keymap's Live TV section catches long OK
         in the OK screen too, so it can't tell them apart itself. -->
    <timer>
        <name>silo_live_longok</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.live.longok),1)</start>
        <onstart>ClearProperty(silo.live.longok,home)</onstart>
        <onstart condition="Window.IsActive(%(window)d)">Action(ContextMenu)</onstart>
        <onstart condition="!Window.IsActive(%(window)d)">ActivateWindow(TVGuide)</onstart>
        <stop>true</stop>
    </timer>
    <!-- The guide opens on its restart row (the window's default); with no cards
         once it has loaded, nothing can have focus there: the grid. -->
    <timer>
        <name>silo_guide_rail</name>
        <start reset="true">Window.IsActive(tvguide) + !Control.HasFocus(%(rail)d) + !Control.HasFocus(%(grid)d) + Integer.IsEqual(Container(%(rail)d).NumItems,0)</start>
        <onstart>SetFocus(%(grid)d)</onstart>
        <stop>true</stop>
    </timer>
'''


def add_timers():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', TIMER_START + TIMERS % {'grid': GRID_ID, 'banner_up': BANNER_UP, 'rail': RAIL_ID, 'banner_window': BANNER_WINDOW, 'window': OK_ID, 'list': RECENT_LIST, 'idle': OVERLAY_IDLE, 'play': PLAY_PAUSE, 'sched': SCHEDULE_ID, 'days': DAYS_ID, 'controls': CONTROLS}
                        + TIMER_END + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


def add_banner():
    path = os.path.join(ROOT, 'xml', 'DialogSeekBar.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '\t\t<!-- Silo Skyline Live TV banner (tools/build_tv.py) -->', '\t\t<!-- end Silo Skyline Live TV banner -->\n'
    text = text[:text.index(start)] + banner() + text[text.index(end) + len(end):]
    open(path, 'w', encoding='utf-8').write(text)


PANEL = '272A30'             # the panels' grey: the programme card's (silo/menu_panel.png), as TiviMate's match
OK_ID = 1198                 # OK in Live TV: what's on and the playback buttons
RECENT_LIST = 5600
CONTROLS = 5610               # the OK screen's playback bar (Up from the tiles)
# The OK screen's row of channels, as TiviMate's: compact tiles at the bottom.
TILE_W, TILE_GAP = 290, 20
TILE_PIC_H = TILE_W * 9 // 16  # the tile's picture, 16:9, with what's on under it
TILE_H = TILE_PIC_H + 49
# The row's top: what's on under the pictures ends where the banner's and the
# OK screen's card does (SKY_Y + SKY_H, 36 from the bottom).
ROW_Y = SKY_Y + SKY_H - (TILE_PIC_H + 40)


SCHEDULE_ID, DAYS_ID = 14, 13


def build_quick_guide():
    """Kodi's channel list while Live TV plays (DialogPVRChannelsOSD: the C
    key, a Playlist button, Estuary's OSD Channels button) opens the TV guide
    instead. It was TiviMate's quick guide (channels, their schedule and
    days); retired 2026-11-25 for the TV guide, which marks the playing
    channel and restarts what's on."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <onload>Dialog.Close(pvrosdchannels,true)</onload>
    <onload>ActivateWindow(TVGuide)</onload>
    <controls />
</window>
'''


# TiviMate's playback bar (Up from the OK screen's tiles), over the shade:
# the time at the left, the transport buttons in the middle, restart and
# LIVE at the right; the information block moves down to it and the tiles
# peek out below. Positions from TiviMate's screen at 1080p.
BAND_Y, BAND_H = 885, 108
BUTTON = 84
RESTART, LIVE_BUTTON = 5617, 5618
# Back to live also plays again if paused (TiviMate's).
UNPAUSE = '<onclick condition="Player.Paused">PlayerControl(Play)</onclick>'


def round_button(control_id, icons, action, left, right, caption='', x=None, live=False, down=None):
    """A round button: a white disc with a dark icon when focused, else the
    icon in white, and its caption, if any, under it while focused (TiviMate's). Its
    neighbours are named (Kodi doesn't step between buttons nested in a
    grouplist's groups). live: TiviMate's outlined LIVE tag for its icon."""
    lit = 'Control.HasFocus(%d)' % control_id
    if live:
        icons = ()
    images = ''.join('''
                        <control type="image">
                            <left>22</left><top>22</top><width>40</width><height>40</height>
                            <texture colordiffuse="%(colour)s">%(icon)s</texture>
                            <visible>%(visible)s</visible>
                        </control>''' % {'icon': icon, 'colour': colour,
                                        'visible': ' + '.join(part for part in (when, shown) if part)}
                     for icon, shown in icons for colour, when in (('FF000000', lit), (TEXT, '!' + lit)))
    if live:
        images = ''.join('''
                        <control type="image">
                            <left>13</left><top>27</top><width>58</width><height>30</height>
                            <texture border="8" colordiffuse="%(colour)s">silo/badge_outline.png</texture>
                            <visible>%(when)s</visible>
                        </control>
                        <control type="label">
                            <left>13</left><top>27</top><width>58</width><height>30</height>
                            <align>center</align><aligny>center</aligny>
                            <font>silo_badge</font>
                            <textcolor>%(colour)s</textcolor>
                            <label>LIVE</label>
                            <visible>%(when)s</visible>
                        </control>''' % {'colour': colour, 'when': when}
                         for colour, when in (('FF000000', lit), (TEXT, '!' + lit)))
    if caption:
        images += '''
                        <control type="label">
                            <left>-60</left><top>%(y)d</top><width>%(w)d</width><height>34</height>
                            <align>center</align>
                            <font>silo_detail</font>
                            <textcolor>%(text)s</textcolor>
                            <label>%(caption)s</label>
                            <visible>%(lit)s</visible>
                        </control>''' % {'y': BUTTON + 6, 'w': BUTTON + 120, 'text': TEXT, 'caption': caption, 'lit': lit}
    extra = UNPAUSE if action == 'PVR.SeekPercentage(100)' else ''
    return '''
                    <control type="group">%(pos)s
                        <width>%(b)d</width><height>%(b)d</height>
                        <control type="button" id="%(id)d">
                            <width>%(b)d</width><height>%(b)d</height>
                            <texturefocus colordiffuse="%(text)s">silo/round_button.png</texturefocus>
                            <texturenofocus />
                            <onleft>%(left)s</onleft>
                            <onright>%(right)s</onright>
                            <onup>noop</onup>
                            <ondown>%(list)s</ondown>
                            <onclick>%(action)s</onclick>%(extra)s
                        </control>%(images)s
                    </control>''' % {'id': control_id, 'action': action, 'text': TEXT, 'images': images, 'b': BUTTON,
                                     'left': left, 'right': right, 'list': RECENT_LIST if down is None else down, 'extra': extra,
                                     'pos': '\n                        <left>%d</left>' % x if x is not None else ''}


def recent_card(focused, list_id=None):
    """A recently watched channel, as the TV page's cards: the programme's
    picture (Sky's) with the channel's logo in its corner, how far through
    and LIVE; with no picture, the logo on the panel. What's on under it."""
    from build_home import focus_sheen, focus_zoom
    lit = 'Control.HasFocus(%d)' % (list_id or RECENT_LIST)
    has = '!String.IsEmpty(ListItem.Property(silo.picture))'
    return '''
                <control type="group">%(zoom)s
                    <control type="image">
                        <width>%(w)d</width><height>%(ph)d</height>
                        <texture border="20" colordiffuse="E6%(panel)s">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="image">
                        <width>%(w)d</width><height>%(ph)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png">$INFO[ListItem.Property(silo.picture)]</texture>
                        <visible>%(has)s</visible>
                    </control>
                    <control type="image">
                        <width>%(w)d</width><height>%(ph)d</height>
                        <texture diffuse="silo/card_landscape_mask.png">silo/card_scrim.png</texture>
                        <visible>%(has)s</visible>
                    </control>
                    <control type="image">
                        <left>12</left><top>%(ly)d</top><width>116</width><height>40</height>
                        <aspectratio align="left" aligny="bottom">keep</aspectratio>
                        <texture>$INFO[ListItem.Icon]</texture>
                        <visible>%(has)s</visible>
                    </control>
                    <control type="image">
                        <left>22</left><top>16</top><width>%(lw)d</width><height>%(lh)d</height>
                        <aspectratio>keep</aspectratio>
                        <texture fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                        <visible>!%(has)s</visible>
                    </control>
                    <control type="group">
                        <left>10</left><top>10</top>%(live)s
                    </control>
                    <control type="progress">
                        <left>14</left><top>%(bar)d</top><width>%(bw)d</width><height>5</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>ListItem.Property(silo.progress)</info>
                        <visible>Integer.IsGreater(ListItem.Property(silo.progress),0)</visible>
                    </control>%(sheen)s
                    <control type="label">
                        <left>4</left><top>%(ty)d</top><width>%(tw)d</width><height>34</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(colour)s</textcolor>
                        <selectedcolor>%(colour)s</selectedcolor>
                        <label>$INFO[ListItem.Property(silo.now)]</label>
                    </control>
                </control>''' % {'zoom': focus_zoom(lit, 16) if focused else '', 'w': TILE_W, 'ph': TILE_PIC_H,
                                  'panel': PANEL, 'lw': TILE_W - 44, 'lh': TILE_PIC_H - 32, 'has': has,
                                  'ly': TILE_PIC_H - 12 - 40, 'bar': TILE_PIC_H - 5, 'bw': TILE_W - 28,
                                  'tw': TILE_W - 8, 'ty': TILE_PIC_H + 6, 'text': TEXT,
                                  'live': live_badge('String.IsEqual(ListItem.Property(silo.live),1)'),
                                  'sheen': focus_sheen(TILE_W, TILE_PIC_H, 'silo/card_landscape_mask.png',
                                                       'silo/card_landscape_rim.png', lit, 16) if focused else '',
                                  'colour': TEXT if focused else 'D9EDEDED'}


NEXT_UP = '!String.IsEmpty(Window(Home).Property(silokodi.next.title))'
NOTES_ID = 1182  # the notes' dialog
NOTE_W, NOTE_X, NOTE_Y = 640, 88, 120  # under the banner's clock, top right
NOTES_START, NOTES_END = '\t\t<!-- Silo Skyline Live TV notes (tools/build_tv.py) -->\n', '\t\t<!-- end Silo Skyline Live TV notes -->\n'


def live_notes():
    """Sky's Coming up next over full-screen Live TV, top right (KodiConnectForSilo's
    liveprompts.py says when), in a programme's last two minutes (window %d:
    the Live TV overlay, which hides it). Not over the menus
    Live TV opens, nor while browsing channels. A dialog of their own: drawn
    in Kodi's player window (VideoFullScreen.xml), they never showed. On the
    skin's glass (menu_panel.png, themed), as the player's other panels.""" % OK_ID
    hidden = ('VideoPlayer.Content(LiveTV) + !Player.ChannelPreviewActive + !Window.IsActive(videoosd) + '
              '!Window.IsActive(pvrosdchannels) + !Window.IsActive(%d) + !Window.IsActive(%d) + '
              '!Window.IsActive(tvguide)' % (OK_ID, BANNER_WINDOW))
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<!-- Kodi opens and closes this dialog by its visible condition; with nothing
     to focus, the keys go on to the player. -->
<window type="dialog" id="%(id)d">
	<visible>Window.IsActive(fullscreenvideo) + VideoPlayer.Content(LiveTV) + %(next)s</visible>
	<zorder>1</zorder>
	<controls>
		<control type="group">
			<left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>150</height>
			<visible>%(hidden)s + %(next)s</visible>
			<animation effect="slide" start="0,-40" end="0,0" time="220" tween="cubic" easing="out">Visible</animation>
			<animation effect="fade" start="0" end="100" time="220">Visible</animation>
			<animation effect="fade" start="100" end="0" time="160">Hidden</animation>
			<!-- The glass in the next programme's colour, else the playing one's
			     (KodiConnectForSilo's next.tint, tv.playing_tint), else the theme's. -->
			<control type="image">
				<width>%(w)d</width><height>150</height>
				<texture border="28" colordiffuse="$VAR[SiloNoteTint]">silo/menu_panel.png</texture>
			</control>
			<!-- The next programme's picture, else the channel's logo. -->
			<control type="image">
				<left>20</left><top>20</top><width>196</width><height>110</height>
				<aspectratio>keep</aspectratio>
				<texture>$INFO[Player.Icon]</texture>
				<visible>String.IsEmpty(Window(Home).Property(silokodi.next.picture))</visible>
			</control>
			<control type="image">
				<left>20</left><top>20</top><width>196</width><height>110</height>
				<aspectratio>scale</aspectratio>
				<texture background="true">$INFO[Window(Home).Property(silokodi.next.picture)]</texture>
			</control>
			<control type="label">
				<left>240</left><top>18</top><width>%(nw)d</width><height>34</height>
				<font>silo_card_sub</font>
				<textcolor>$VAR[SiloNoteLabel]</textcolor>
				<label>COMING UP NEXT</label>
			</control>
			<control type="label">
				<left>240</left><top>52</top><width>%(nw)d</width><height>44</height>
				<font>silo_card_title</font>
				<textcolor>%(text)s</textcolor>
				<label>$INFO[Window(Home).Property(silokodi.next.title)]</label>
			</control>
			<control type="label">
				<left>240</left><top>96</top><width>%(nw)d</width><height>36</height>
				<font>silo_card_sub</font>
				<textcolor>%(dim)s</textcolor>
				<label>$INFO[Window(Home).Property(silokodi.next.time),at ,]</label>
			</control>
		</control>
	</controls>
</window>
''' % {'id': NOTES_ID, 'x': 1920 - NOTE_X - NOTE_W, 'y': NOTE_Y, 'w': NOTE_W, 'nw': NOTE_W - 264, 'hidden': hidden,
       'next': NEXT_UP, 'text': TEXT, 'dim': DIM}


def add_live_notes():
    path = os.path.join(ROOT, 'xml', 'VideoFullScreen.xml')
    text = open(path, encoding='utf-8').read()
    if NOTES_START in text:
        text = text[:text.index(NOTES_START)] + text[text.index(NOTES_END) + len(NOTES_END):]
    open(path, 'w', encoding='utf-8').write(text)  # once drawn here: Kodi's player window drew none of it
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloLiveNotes.xml' % NOTES_ID), 'w', encoding='utf-8') as handle:
        handle.write(live_notes())


# OK, Left or Right in Live TV, as YouTube's player (option C, 2026-11-26): what's
# on at the top, the progress bar, the buttons (Restart and Live, previous /
# play-pause / next channel, Guide and Options), then chips that switch the
# row of cards below between Recent, On now and Coming up on this channel.
# OK opens it on play/pause, Left/Right on the recent channels (the one
# watched before first). It closes after OVERLAY_IDLE s without a key unless
# paused. Browsing channels (Up/Down) OK watches the one shown; on a programme
# Left/Right stepped to, OK plays it from catch-up or sets its reminder: not this.
OVERLAY_IDLE = 6
PLAY_PAUSE, PREV_CHANNEL, NEXT_CHANNEL = 5613, 5611, 5614
RESTART_PILL, LIVE_PILL, GUIDE_PILL, OPTIONS_PILL = 5615, 5616, 5617, 5619
SEEK_BAR = 5630
CHIPS = ((5620, 'Recent', 'recent', 5600, 'recent_channels'),
         (5621, 'On now', 'now', 5601, 'on_now_channels'),
         (5622, 'Coming up', 'next', 5602, 'next_on'))
OK_FIRST = PLAY_PAUSE
ROW_PROP = 'Window(Home).Property(silo.ok.row)'
TITLE_Y, BAR_Y, BUTTONS_Y, CHIPS_Y = 70, 580, 620, 764
CARDS_Y = CHIPS_Y + 64
PILL = 64


def row_shown(key):
    """The chips' row: Recent unless another chip chose it."""
    if key == 'recent':
        return '[String.IsEmpty(%s) | String.IsEqual(%s,recent)]' % (ROW_PROP, ROW_PROP)
    return 'String.IsEqual(%s,%s)' % (ROW_PROP, key)


def opened_by(label):
    """How much wider a pill opens for its name (as the info page's: silo_tab, ~16 px a character)."""
    return 16 * len(label) + 30


PILL_XML = """
            <control type="group">
                <left>%(x)d</left><top>%(y)d</top><width>%(p)d</width><height>%(p)d</height>%(slides)s
                <control type="button" id="%(id)d">
                    <width>%(p)d</width><height>%(p)d</height>
                    <label />
                    <texturefocus />
                    <texturenofocus border="32" colordiffuse="33FFFFFF">silo/pill_32.png</texturenofocus>
                    <onleft>%(left)s</onleft><onright>%(right)s</onright>
                    <onup>%(up)s</onup>%(down)s%(clicks)s
                </control>
                <control type="group">
                    <visible>%(lit)s</visible>
                    <animation effect="zoom" start="40,100" end="100,100" center="0,32" time="180" tween="sine" easing="out">Visible</animation>
                    <control type="image">
                        <width>%(open_w)d</width><height>%(p)d</height>
                        <texture border="32" colordiffuse="%(text)s">silo/pill_32.png</texture>
                    </control>
                    <control type="label">
                        <left>62</left><width>%(label_w)d</width><height>%(p)d</height>
                        <aligny>center</aligny>
                        <font>silo_tab</font>
                        <textcolor>FF000000</textcolor>
                        <label>%(name)s</label>
                    </control>
                </control>
                <control type="image">
                    <left>16</left><top>16</top><width>32</width><height>32</height>
                    <texture colordiffuse="FF000000">%(icon)s</texture>
                    <visible>%(lit)s</visible>
                </control>
                <control type="image">
                    <left>16</left><top>16</top><width>32</width><height>32</height>
                    <texture colordiffuse="%(text)s">%(icon)s</texture>
                    <visible>!%(lit)s</visible>
                </control>
            </control>"""


def pill_button(control_id, icon, label, onclick, x, left, right, up, down, after=()):
    """The info page's round icon: with focus, a white pill with its name.
    onclick: [(action, condition or '')]. after: the buttons before it in
    its group, whose pills push it along."""
    lit = 'Control.HasFocus(%d)' % control_id
    slides = ''.join('\n                <animation effect="slide" end="%d,0" time="180" tween="sine" easing="out" '
                     'condition="Control.HasFocus(%d)">Conditional</animation>' % (opened_by(name), other)
                     for other, name in after)
    clicks = ''.join('\n                    <onclick%s>%s</onclick>' % (' condition="%s"' % when if when else '', action)
                     for action, when in onclick)
    return PILL_XML % {'id': control_id, 'x': x, 'y': BUTTONS_Y + (BUTTON - PILL) // 2, 'p': PILL, 'slides': slides,
                       'left': left, 'right': right, 'up': up, 'down': down, 'clicks': clicks, 'lit': lit,
                       'icon': icon, 'text': TEXT, 'name': label,
                       'open_w': PILL + opened_by(label), 'label_w': opened_by(label) - 4}


def down_to_row():
    """Down from the buttons: the chip of the row shown."""
    return ''.join('\n                    <ondown condition="%s">%d</ondown>' % (row_shown(key), chip_id)
                   for chip_id, _, key, _, _ in CHIPS)


CHIP_XML = """
            <control type="group">
                <width>%(w)d</width><height>48</height>
                <control type="image">
                    <width>%(w)d</width><height>48</height>
                    <texture border="24" colordiffuse="%(text)s">silo/pill_24.png</texture>
                    <visible>Control.HasFocus(%(id)d)</visible>
                </control>
                <control type="image">
                    <width>%(w)d</width><height>48</height>
                    <texture border="24" colordiffuse="66FFFFFF">silo/pill_24.png</texture>
                    <visible>!Control.HasFocus(%(id)d) + %(shown)s</visible>
                </control>
                <control type="button" id="%(id)d">
                    <width>%(w)d</width><height>48</height>
                    <label>%(label)s</label>
                    <font>silo_detail</font>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(text)s</textcolor><focusedcolor>FF000000</focusedcolor>
                    <texturefocus /><texturenofocus border="24" colordiffuse="26FFFFFF">silo/pill_24.png</texturenofocus>
                    <onfocus>SetProperty(silo.ok.row,%(key)s,home)</onfocus>
                    <onleft>%(left)s</onleft><onright>%(right)s</onright>
                    <onup>%(play)d</onup><ondown>%(list)d</ondown>
                </control>
            </control>"""


def chip(control_id, label, key, list_id, left, right):
    """A chip, as YouTube's: white when focused, a lighter wash when its row
    is shown, else glass; focusing it shows its row. 48 high on pill_24.png:
    pill.png's 30 px ends, cut to a 22 px border, came out pointed."""
    return CHIP_XML % {'id': control_id, 'label': label, 'key': key, 'list': list_id, 'w': 180, 'text': TEXT,
                       'shown': row_shown(key), 'left': left, 'right': right, 'play': PLAY_PAUSE}


ROW_XML = """
            <control type="list" id="%(list)d">%(placed)s
                <left>%(lx)d</left><top>%(y)d</top><width>%(lw)d</width><height>%(ih)d</height>
                <visible>%(shown)s</visible>
                <orientation>horizontal</orientation>
                <onup>%(chip)d</onup><ondown>noop</ondown>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <content target="videos">plugin://plugin.video.kodiconnectforsilo/?mode=%(mode)s&amp;v=$INFO[Window(Home).Property(silokodi.recent_changed)]</content>%(closes)s
                <onclick>%(click)s</onclick>
                <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
                </focusedlayout>
            </control>"""


def card_row(chip_id, key, list_id, mode):
    """A chip's row of cards (the recent row's), from KodiConnectForSilo; a
    new silokodi.recent_changed reloads it as the overlay opens. OK on a
    channel watches it; on a later programme (Coming up), sets its reminder."""
    if mode == 'next_on':
        click, closes = 'RunPlugin($INFO[ListItem.FileNameAndPath])', ''
    else:
        click = ('RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=play_channel&amp;'
                 'id=$INFO[ListItem.Property(silo.channelid)])')
        closes = ('\n                <onclick>Dialog.Close(%d)</onclick>'
                  '\n                <onclick>SetProperty(silo.live.hide,1,home)</onclick>' % OK_ID)
    # The recent row stays unseen until its first card is selected (timer silo_recent_first).
    placed = ('\n                <animation effect="fade" start="100" end="0" time="0" condition="String.IsEmpty('
              'Window(Home).Property(silo.recent.placed))">Conditional</animation>') if key == 'recent' else ''
    return ROW_XML % {'list': list_id, 'placed': placed, 'lx': SAFE_X - 8, 'y': CARDS_Y, 'lw': 1920 - SAFE_X + 8,
                      'ih': TILE_H, 'iw': TILE_W + TILE_GAP, 'shown': row_shown(key), 'chip': chip_id,
                      'mode': mode, 'closes': closes, 'click': click,
                      'card': recent_card(False, list_id), 'card_focused': recent_card(True, list_id)}


OK_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. OK, Left or Right in Live TV. -->
<window id="%(window)d" type="dialog">
    <defaultcontrol always="true">%(first)d</defaultcontrol>
    <!-- Browsing channels in the banner (Up/Down, Kodi's Confirm channel switch):
         OK watches the one shown, as Sky's mini guide, not this screen. -->
    <onload condition="Player.ChannelPreviewActive + !%(hidden)s">Dialog.Close(%(window)d,true)</onload>
    <onload condition="Player.ChannelPreviewActive + !%(hidden)s + String.IsEmpty(Window(Home).Property(silokodi.banner.title))">SetProperty(silo.live.hide,1,home)</onload>
    <onload condition="Player.ChannelPreviewActive + !%(hidden)s + String.IsEmpty(Window(Home).Property(silokodi.banner.title))">Action(Select)</onload>
    <!-- On an earlier or later programme the banner stepped to (Left/Right):
         catch-up or a reminder, not this screen. -->
    <onload condition="!Player.ChannelPreviewActive + !String.IsEmpty(Window(Home).Property(silokodi.banner.title))">Dialog.Close(%(window)d,true)</onload>
    <onload condition="!String.IsEmpty(Window(Home).Property(silokodi.banner.title))">RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=banner_play)</onload>
    <!-- The rows reload as it opens (timer silo_recent_first selects the first card). -->
    <onload>ClearProperty(silo.recent.placed,home)</onload>
    <onload>SetProperty(silo.ok.row,recent,home)</onload>
    <onload>SetProperty(silokodi.recent_changed,$INFO[System.Time(hh:mm:ss)],home)</onload>
    <onunload>ClearProperty(silo.ok.from,home)</onunload>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="8C000000">colors/white.png</texture>
            <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="140">WindowClose</animation>
        </control>
        <!-- The playing channel's tint from the bar down (as the old recent row's),
             so the buttons, chips and card names read over a bright picture. -->
        <control type="image">
            <left>0</left><top>%(tint_y)d</top><width>1920</width><height>%(tint_h)d</height>
            <texture colordiffuse="$VAR[SiloLiveTint]">silo/scrim_bottom_white.png</texture>
            <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="140">WindowClose</animation>
        </control>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="140">WindowClose</animation>
            <!-- What's on, as YouTube's title and channel line. -->
            <control type="label">
                <left>%(x)d</left><top>%(ty)d</top><width>1400</width><height>70</height>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor><shadowcolor>CC000000</shadowcolor>
                <label>$INFO[VideoPlayer.Title]</label>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(my)d</top><width>1400</width><height>40</height>
                <font>silo_meta</font>
                <textcolor>CCEDEDED</textcolor><shadowcolor>CC000000</shadowcolor>
                <label>$INFO[VideoPlayer.ChannelName]$INFO[VideoPlayer.StartTime,  ·  ]$INFO[VideoPlayer.EndTime, – ]</label>
            </control>
            <!-- The bar, as YouTube's: Up from the buttons; Left / Right seek. -->
            <control type="label">
                <left>%(x)d</left><top>%(tly)d</top><width>600</width><height>34</height>
                <font>silo_detail</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[PVR.EpgEventElapsedTime]$INFO[PVR.EpgEventDuration,[COLOR 99EDEDED] / ,[/COLOR]]</label>
            </control>
            <!-- LIVE ends where the bar does (the tag is 60 wide), level with the time. -->
            <control type="group">
                <left>%(lx)d</left><top>%(livey)d</top><visible>!PVR.IsTimeShift</visible>%(live)s
            </control>
            <control type="label">
                <left>%(rx)d</left><top>%(tly)d</top><width>600</width><height>34</height>
                <align>right</align>
                <font>silo_detail</font>
                <textcolor>CCEDEDED</textcolor>
                <label>$INFO[PVR.TimeShiftOffset,,  behind live]</label>
                <visible>PVR.IsTimeShift</visible>
            </control>
            <control type="progress">
                <left>%(x)d</left><top>%(by)d</top><width>%(bw)d</width><height>6</height>
                <texturebg colordiffuse="40FFFFFF">colors/white.png</texturebg>
                <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                <info>PVR.EpgEventProgress</info>
                <visible>!Control.HasFocus(%(bar)d)</visible>
            </control>
            <control type="progress">
                <left>%(x)d</left><top>%(by2)d</top><width>%(bw)d</width><height>12</height>
                <texturebg colordiffuse="40FFFFFF">colors/white.png</texturebg>
                <midtexture colordiffuse="FFE53935">colors/white.png</midtexture>
                <info>PVR.EpgEventProgress</info>
                <visible>Control.HasFocus(%(bar)d)</visible>
            </control>
            <control type="button" id="%(bar)d">
                <left>%(x)d</left><top>%(bfy)d</top><width>%(bw)d</width><height>30</height>
                <texturefocus /><texturenofocus /><label />
                <onleft>Seek(-10)</onleft><onright>Seek(10)</onright>
                <onup>noop</onup><ondown>%(play)d</ondown>
            </control>%(pills)s%(transport)s
            <!-- The chips and their rows of cards. -->
            <control type="grouplist">
                <left>%(x)d</left><top>%(cy)d</top><width>800</width><height>48</height>
                <orientation>horizontal</orientation>
                <itemgap>16</itemgap>%(chips)s
            </control>%(rows)s
        </control>
    </controls>
</window>
"""


def build_ok():
    centre = (1920 - 3 * BUTTON - 2 * 24) // 2
    left_x, right_x = SAFE_X, 1920 - SAFE_X - 2 * PILL - 16 - opened_by('Options')
    down = down_to_row()
    pills = (pill_button(RESTART_PILL, 'silo/skip_back.png', 'Restart',
                         [('PVR.SeekPercentage(0)', '')], left_x, 'noop', LIVE_PILL, SEEK_BAR, down)
             + pill_button(LIVE_PILL, 'osd/fullscreen/buttons/record-white.png', 'Live',
                           [('PVR.SeekPercentage(100)', ''), ('PlayerControl(Play)', 'Player.Paused')],
                           left_x + PILL + 16, RESTART_PILL, PREV_CHANNEL, SEEK_BAR, down,
                           after=((RESTART_PILL, 'Restart'),))
             + pill_button(GUIDE_PILL, 'osd/fullscreen/buttons/guide.png', 'Guide',
                           [('Dialog.Close(%d,true)' % OK_ID, ''), ('ActivateWindow(TVGuide)', '')],
                           right_x, NEXT_CHANNEL, OPTIONS_PILL, SEEK_BAR, down)
             + pill_button(OPTIONS_PILL, 'osd/fullscreen/buttons/settings.png', 'Options',
                           [('ActivateWindow(1180)', '')], right_x + PILL + 16, GUIDE_PILL, 'noop', SEEK_BAR, down,
                           after=((GUIDE_PILL, 'Guide'),)))
    transport = ''
    steps = (
        (PREV_CHANNEL, (('osd/fullscreen/buttons/previous.png', ''),),
         'RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=channel_step&amp;dir=-1)', 'Previous channel'),
        (PLAY_PAUSE, (('osd/fullscreen/buttons/pause.png', '!Player.Paused'),
                      ('osd/fullscreen/buttons/play.png', 'Player.Paused')), 'PlayerControl(Play)', 'Play / pause'),
        (NEXT_CHANNEL, (('osd/fullscreen/buttons/next.png', ''),),
         'RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=channel_step&amp;dir=1)', 'Next channel'))
    neighbours = ((LIVE_PILL, PLAY_PAUSE), (PREV_CHANNEL, NEXT_CHANNEL), (PLAY_PAUSE, GUIDE_PILL))
    for n, (cid, icons, action, caption) in enumerate(steps):
        button = round_button(cid, icons, action, neighbours[n][0], neighbours[n][1], caption=caption,
                              x=centre + n * (BUTTON + 24), down='noop')
        # round_button names no Up or Down: the bar above, the row's chip below.
        button = button.replace('<onup>noop</onup>', '<onup>%d</onup>' % SEEK_BAR, 1)
        button = button.replace('<ondown>noop</ondown>', down.strip(), 1)
        transport += button.replace('<control type="group">', '<control type="group">\n                        <top>%d</top>' % BUTTONS_Y, 1)
    chips = ''.join(chip(cid, label, key, list_id, CHIPS[n - 1][0] if n else 'noop',
                         CHIPS[n + 1][0] if n + 1 < len(CHIPS) else 'noop')
                    for n, (cid, label, key, list_id, _) in enumerate(CHIPS))
    rows = ''.join(card_row(cid, key, list_id, mode) for cid, _, key, list_id, mode in CHIPS)
    return OK_XML % {'window': OK_ID, 'first': OK_FIRST, 'hidden': LIVE_HIDDEN, 'text': TEXT, 'x': SAFE_X,
                     'ty': TITLE_Y, 'my': TITLE_Y + 76, 'tly': BAR_Y - 42, 'livey': BAR_Y - 42 + 3, 'lx': 1920 - SAFE_X - 60,
                     'rx': 1920 - SAFE_X - 600, 'live': live_badge('true', indent='                '),
                     'by': BAR_Y, 'by2': BAR_Y - 3, 'bfy': BAR_Y - 12, 'bw': 1920 - 2 * SAFE_X, 'bar': SEEK_BAR,
                     'play': PLAY_PAUSE, 'pills': pills, 'transport': transport, 'cy': CHIPS_Y, 'chips': chips,
                     'rows': rows, 'tint_y': BAR_Y - 200, 'tint_h': 1080 - BAR_Y + 200}


# Back in the guide (KodiConnectForSilo's player keymap opens this dialog,
# as Back in the video window opens 1188): to what's playing, else Kodi's own
# Back (leave the guide). Kodi's guide window takes Back before any control's
# onback sees it, so the guide's controls can't do this themselves.
GUIDE_BACK = 1189
GUIDE_BACK_WINDOW = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. Back in the TV guide. -->
<!-- focus lands in MyPVRGuide.xml -->
<window type="dialog" id="%(id)d">
    <onload>Dialog.Close(%(id)d,true)</onload>
    <onload condition="Player.HasVideo + !PVR.IsPlayingEpgTag">Action(FullScreen)</onload>
    <!-- A catch-up programme playing behind: stop it (back to it was a loop). -->
    <onload condition="Player.HasVideo + PVR.IsPlayingEpgTag">PlayerControl(Stop)</onload>
    <!-- Nothing playing: Kodi's own Back (leave the guide); its groups no longer show. -->
    <onload condition="!Player.HasVideo">Action(Back)</onload>
    <controls />
</window>
'''


# Left and Right in Live TV, as Sky's banner: skin timers (TIMERS,
# silo_live_left/right) note the channel shown, open this window and step;
# the window draws the banner and holds the keys (Left/Right step, OK plays
# or reminds, Back/Up/Down close; Back hides Kodi's banner beneath too).
# It has no timer: it stays until a key closes it. Kodi's own
# banner (DialogSeekBar) timed out mid-step, and holding it open gave the
# keys to its seek bar.
BANNER_WINDOW = 1183
# The banner is up: Kodi's (Info, a channel change, browsing) or Skyline's window.
BANNER_UP = ('[Window.IsActive(%d) | [[Player.ShowInfo | Player.ChannelPreviewActive | Window.IsActive(fullscreeninfo)] + !%s]]'
             % (BANNER_WINDOW, LIVE_HIDDEN))
LIVE_BANNER_WINDOW = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. Live TV's banner for Left/Right. -->
<window type="dialog" id="%(id)d">
    <defaultcontrol always="true">100</defaultcontrol>
    <onunload condition="String.IsEmpty(Window(Home).Property(silo.live.keep))">SetProperty(silo.live.hidden,$INFO[VideoPlayer.ChannelName],home)</onunload>
    <onunload>ClearProperty(silo.live.keep,home)</onunload>
    <controls>
        <control type="image">
            <left>0</left><top>560</top><width>1920</width><height>520</height>
            <texture colordiffuse="B3FFFFFF">silo/scrim_bottom.png</texture>
        </control>%(info)s
        <!-- The keys: an unseen button with focus. -->
        <control type="button" id="100">
            <left>-20</left><top>-20</top><width>1</width><height>1</height>
            <texturefocus /><texturenofocus />
            <onleft>RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=banner_step&amp;dir=-1)</onleft>
            <onright>RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=banner_step&amp;dir=1)</onright>
            <onclick>RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=banner_play)</onclick>
            <onup>SetProperty(silo.live.keep,1,home)</onup>
            <onup>Dialog.Close(%(id)d)</onup>
            <ondown>SetProperty(silo.live.keep,1,home)</ondown>
            <ondown>Dialog.Close(%(id)d)</ondown>
        </control>
    </controls>
</window>
'''


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'MyPVRGuide.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloGuideBack.xml' % GUIDE_BACK), 'w', encoding='utf-8') as handle:
        handle.write(GUIDE_BACK_WINDOW % {'id': GUIDE_BACK, 'groups': GROUPS_ID})
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloLiveBanner.xml' % BANNER_WINDOW), 'w', encoding='utf-8') as handle:
        handle.write(LIVE_BANNER_WINDOW % {'id': BANNER_WINDOW, 'info': sky_banner()})
    with open(os.path.join(ROOT, 'xml', 'DialogPVRInfo.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build_info())
    with open(os.path.join(ROOT, 'xml', 'DialogPVRChannelsOSD.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build_quick_guide())
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloLiveOK.xml' % OK_ID), 'w', encoding='utf-8') as handle:
        handle.write(build_ok())
    add_banner()
    add_live_notes()
    add_timers()
    add_variables()
    print('Wrote xml/MyPVRGuide.xml, DialogPVRInfo.xml and their variables in xml/Variables.xml')
