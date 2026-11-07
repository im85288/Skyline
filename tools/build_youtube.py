#!/usr/bin/env python3
"""Write xml/Custom_1198_SiloYouTube.xml: a YouTube page as the YouTube app
on Android TV lays one out, in Silo's look, from the YouTube add-on:

    python3 tools/build_youtube.py

Skyline's YouTube page (Home's YouTube tab, tools/build_home.py) has the app's
rows; its Subscriptions and Search pills open this window on that section
(silo.youtube.open), and Back returns to the page. Subscriptions: the channels
at the left (All first), the newest videos at the right, both as KodiConnect-
ForSilo published them (at once), or a chosen channel's videos (loaded then).
Search: the YouTube add-on's own search history at the left (New search
first), a grid of the chosen search's results at the right. OK plays a video, or
opens a folder, as the add-on does. Focus is Skyline's own, as Home's rows
(no selection box).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import (BACKGROUND, PILLS_TOP, ROOT, SAFE_X, SUB_DIM,  # noqa: E402
                        TEXT, TEXT_DIM, TITLE_DIM, focus_sheen)

WINDOW_ID = 1198
ADDON = 'plugin.video.youtube'
YT = 'plugin://%s/' % ADDON
# A row's list: videos only, no "Next page" (the app's rows end too).
ROW_PARAMS = '?hide_folders=true&amp;hide_next_page=true'
SECTION = 'Window(Home).Property(silo.youtube.section)'
# A section opened this visit: Kodi loads even a hidden list as the window
# opens, so Library's lists have no path until then (Subscriptions' load at
# once: Home's old Recently uploaded row was the same list, loaded twice).
LOADED = 'Window(Home).Property(silo.youtube.loaded.%s)'
# Search: the YouTube add-on's search history at
# the left (its New search first), the chosen search's results at the right.
# KodiConnectForSilo (mode=youtubepick) opens the keyboard for New search, and
# puts the words and their results' path in properties for either.
QUERY = 'Window(Home).Property(silo.youtube.query)'
# The section to open on, set by Skyline's YouTube page's pills (build_home.py).
OPEN = 'Window(Home).Property(silo.youtube.open)'
RESULTS = 'Window(Home).Property(silo.youtube.search)'
# Changed by KodiConnectForSilo after each search, so the history list reloads
# with it (Kodi reloads a list only when its path changes).
HISTORY_TOKEN = 'Window(Home).Property(silo.youtube.history)'
HISTORY_ID = 620
RESULTS_ID = 610
CONTENT_X = SAFE_X
CONTENT_W = 1920 - CONTENT_X
TOP = PILLS_TOP + 8  # under the title

# The grids' cards (GRID_W), 16:9 as the app's.
CARD_GAP = 40  # as Home's: the focused card's growth stays inside it
# A focused card grows from its left edge, so all its growth is to the right,
# and must stay inside the gap.
CARD_ZOOM = 105
TEXT_H = 16 + 70 + 34 + 34 + 24  # a two-line title, the channel, the date

# Subscriptions: All and the channels, then a grid of a channel's videos.
ALL_ID, CHANNELS_ID, SUBS_GRID = 401, 402, 410
CHANNELS_W = 400
CHANNEL_ROW = 72
GRID_X = CONTENT_X + CHANNELS_W + 40
GRID_COLS = 3
GRID_ITEM_W = (1920 - GRID_X - 24) // GRID_COLS
GRID_W = GRID_ITEM_W - CARD_GAP
GRID_H = GRID_W * 9 // 16
GRID_ITEM_H = GRID_H + TEXT_H
CHANNEL = 'Window(Home).Property(silo.youtube.channel)'
# Subscriptions at once: the channels and the newest videos KodiConnectForSilo
# published (ytrows.screen_properties), not the YouTube add-on's lists (3-4 s
# each); only a chosen channel's videos load (SUBS_GRID).
RECENT_GRID = 411
PUBLISHED = 'Window(Home).Property(silo.youtube.%s)'
CHANNELS_MAX, RECENT_MAX = 100, 30  # ytrows.CHANNELS and RECENT


def channel_items():
    return ''.join('''
                    <item>
                        <label>$INFO[%(p)s]</label>
                        <icon>$INFO[%(thumb)s]</icon>
                        <property name="path">$INFO[%(path)s]</property>
                        <visible>!String.IsEmpty(%(p)s)</visible>
                    </item>''' % {'p': PUBLISHED % ('channels.%d.label' % n), 'thumb': PUBLISHED % ('channels.%d.thumb' % n),
                                  'path': PUBLISHED % ('channels.%d.path' % n)} for n in range(1, CHANNELS_MAX + 1))


def recent_items():
    def field(n, name):
        return PUBLISHED % ('recent.%d.%s' % (n, name))
    return ''.join('''
                    <item>
                        <label>$INFO[%(label)s]</label>
                        <thumb>$INFO[%(thumb)s]</thumb>
                        <property name="channel">$INFO[%(channel)s]</property>
                        <property name="when">$INFO[%(when)s]</property>
                        <property name="length">$INFO[%(length)s]</property>
                        <onclick>PlayMedia($INFO[%(play)s])</onclick>
                        <visible>!String.IsEmpty(%(label)s)</visible>
                    </item>''' % {name: field(n, name) for name in ('label', 'thumb', 'channel', 'when', 'length', 'play')}
                   for n in range(1, RECENT_MAX + 1))

def shown(section):
    """A section shows while it's the chosen one (Subscriptions at first)."""
    if section == 'subscriptions':
        return '[String.IsEmpty(%s) | String.IsEqual(%s,subscriptions)]' % (SECTION, SECTION)
    return 'String.IsEqual(%s,%s)' % (SECTION, section)


def card(width, height, focused, view_id):
    """A video as the app shows one: its picture with the duration in the
    corner, then a two-line title, the channel and the date."""
    has_focus = 'Control.HasFocus(%d)' % view_id
    # Skyline's focus zoom, as Home's cards, grown from the card's left edge so
    # it stays in line with the row's title (from its centre it stood out left).
    zoom = ('\n                    <animation effect="zoom" start="100" end="%d" time="180" tween="sine" easing="out" '
            'center="6,%d" condition="%s">Conditional</animation>' % (CARD_ZOOM, 6 + height // 2, has_focus)) if focused else ''
    # Skyline's focus, as Home's rows: the zoom, a faint veil and a hairline rim.
    ring = focus_sheen(width, height, 'silo/card_landscape_mask.png', 'silo/card_landscape_rim.png',
                       has_focus, 20) if focused else ''
    return '''
                <control type="group">%(zoom)s
                    <!-- Behind the picture, the video's smaller one YouTube always has:
                         the add-on asks for its largest 16:9 (hq720) without checking,
                         and older videos have none, which left the card grey. -->
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="colors/grey.png">$VAR[SiloYouTubeThumbBehind]</texture>
                    </control>
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png">$VAR[SiloYouTubeThumb]</texture>
                    </control>
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="24" colordiffuse="%(page)s">silo/card_corners.png</texture>
                    </control>
                    <control type="progress">
                        <left>20</left><top>%(pt)d</top><width>%(pw)d</width><height>6</height>
                        <texturebg colordiffuse="66000000">colors/white.png</texturebg>
                        <midtexture colordiffuse="FFFF0033">colors/white.png</midtexture>
                        <info>ListItem.PercentPlayed</info>
                        <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                    </control>
                    <!-- The duration in the picture's corner, as the app's. -->
                    <control type="label">
                        <left>%(bx)d</left><top>%(bt)d</top><width>110</width><height>34</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_badge</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Duration]$INFO[ListItem.Property(length)]</label>
                        <visible>[!String.IsEmpty(ListItem.Duration) | !String.IsEmpty(ListItem.Property(length))] + !ListItem.IsFolder</visible>
                    </control>%(ring)s
                    <control type="textbox">
                        <left>6</left><top>%(t1)d</top><width>%(w)d</width><height>64</height>
                        <font>silo_card_title</font>
                        <textcolor>%(title)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                    <control type="label">
                        <left>6</left><top>%(t2)d</top><width>%(w)d</width><height>34</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(sub)s</textcolor>
                        <label>$VAR[SiloYouTubeChannel]</label>
                    </control>
                    <control type="label">
                        <left>6</left><top>%(t3)d</top><width>%(w)d</width><height>34</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(sub)s</textcolor>
                        <label>$VAR[SiloYouTubeWhen]</label>
                    </control>
                </control>''' % {
        'zoom': zoom, 'w': width, 'h': height, 'pt': height - 2, 'pw': width - 28, 'text': TEXT, 'ring': ring,
        'page': BACKGROUND,
        'bx': width + 6 - 110 - 14, 'bt': height - 36,
        't1': height + 20, 't2': height + 90, 't3': height + 124,
        'title': TEXT if focused else TITLE_DIM, 'sub': TEXT_DIM if focused else SUB_DIM}


def has_items(list_id):
    return 'Integer.IsGreater(Container(%d).NumItems,0)' % list_id


def lazy_variables():
    """Search's history: no path (Kodi waits) until Search is chosen, from the
    menu or Skyline's YouTube page's pill (silo.youtube.open): a list is a run
    of the YouTube add-on."""
    return '''    <variable name="SiloYouTubeHistoryPath">
        <value condition="!String.IsEmpty(%s)">%skodion/search/list/?silo_reload=$INFO[%s]</value>
    </variable>
''' % (LOADED % 'search', YT, HISTORY_TOKEN)


def plugin(mode, **params):
    """A KodiConnectForSilo call, as an action."""
    query = ''.join('&amp;%s=%s' % (key, value) for key, value in params.items())
    return 'RunPlugin(plugin://plugin.video.kodiconnectforsilo/?mode=%s%s)' % (mode, query)


def wait_focus(section, ids, controls=()):
    """Focus a section's first list with videos once it has loaded (or a
    plain control once it shows): Kodi can't focus a list still loading or
    empty, and a SetFocus it can't do drops focus, so KodiConnectForSilo waits."""
    params = {'section': section, 'ids': ','.join(str(i) for i in ids)}
    if controls:
        params['controls'] = ','.join(str(i) for i in controls)
    return plugin('youtubefocus', **params)


def to_grid(grid, section):
    """Actions into a grid: at once when it has videos, else once it has."""
    return [('%s' % has_items(grid), 'SetFocus(%d)' % grid), ('!%s' % has_items(grid), wait_focus(section, [grid]))]


def search_section():
    """The app's Search, as Subscriptions: the YouTube add-on's own search
    history at the left (its New search first, then the searches it saved),
    the chosen search's results at the right."""
    return '''
        <!-- Search -->
        <control type="group">
            <visible>%(shown)s</visible>
            <control type="label">
                <left>%(x)d</left><top>%(top)d</top><width>%(cw)d</width><height>40</height>
                <font>silo_badge</font>
                <textcolor>%(dim)s</textcolor>
                <label>SEARCHES</label>
            </control>
            <control type="list" id="%(history)d">
                <visible>%(shown)s</visible>
                <left>%(x)d</left><top>%(ltop)d</top><width>%(cw)d</width><height>%(lh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <onleft>%(menu)s</onleft><onup>noop</onup>
                <onright condition="%(has_results)s">%(grid)d</onright>
                <!-- New search opens the keyboard; a past search shows its results. -->
                <onclick>%(pick)s</onclick>
                <itemlayout width="%(cw)d" height="%(row)d">%(item)s
                </itemlayout>
                <focusedlayout width="%(cw)d" height="%(row)d">%(item_focused)s
                </focusedlayout>
                <content>$VAR[SiloYouTubeHistoryPath]</content>
            </control>
            <control type="label">
                <left>%(gx)d</left><top>%(top)d</top><width>%(gw)d</width><height>%(rh)d</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloYouTubeResultsTitle]</label>
            </control>
            <control type="label">
                <left>%(gx)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>80</height>
                <font>silo_detail</font>
                <textcolor>%(sub)s</textcolor>
                <label>Nothing found</label>
                <visible>!String.IsEmpty(%(results)s) + !Container(%(grid)d).IsUpdating + Integer.IsEqual(Container(%(grid)d).NumItems,0)</visible>
            </control>
            <control type="panel" id="%(grid)d">
                <visible>%(shown)s</visible>
                <left>%(gx6)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">280</scrolltime>
                <onleft>%(history)d</onleft><onup>noop</onup>
                <itemlayout width="%(giw)d" height="%(gih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(giw)d" height="%(gih)d">%(card_focused)s
                </focusedlayout>
                <content target="videos">$INFO[%(results)s]</content>
            </control>
        </control>''' % {
        'shown': shown('search'), 'history': HISTORY_ID, 'grid': RESULTS_ID, 'menu': 'noop',
        'x': CONTENT_X, 'top': TOP, 'cw': CHANNELS_W, 'rh': CHANNEL_ROW - 8, 'dim': TEXT_DIM, 'sub': SUB_DIM,
        'ltop': TOP + 44, 'lh': 1080 - TOP - 44, 'row': CHANNEL_ROW, 'item': history_row(False),
        'item_focused': history_row(True), 'pick': plugin('youtubepick'), 'has_results': has_items(RESULTS_ID),
        'results': RESULTS,
        'gx': GRID_X, 'gx6': GRID_X - 6, 'gtop': TOP + CHANNEL_ROW, 'gw': 1920 - GRID_X, 'gh': 1080 - TOP - CHANNEL_ROW,
        'giw': GRID_ITEM_W, 'gih': GRID_ITEM_H, 'card': card(GRID_W, GRID_H, False, RESULTS_ID),
        'card_focused': card(GRID_W, GRID_H, True, RESULTS_ID)}


def history_row(focused):
    """A search in the history list: the add-on's icon and the words."""
    pill = '''
                    <control type="image">
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture border="30" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'w': CHANNELS_W, 'h': CHANNEL_ROW - 8, 'text': TEXT, 'id': HISTORY_ID} if focused else ''
    return '''%(pill)s
                    <control type="image">
                        <left>22</left><top>16</top><width>32</width><height>32</height>
                        <aspectratio>keep</aspectratio>
                        <texture colordiffuse="%(c)s">$VAR[SiloYouTubeHistoryIcon]</texture>
                    </control>
                    <control type="label">
                        <left>74</left><top>0</top><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(c)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>''' % {'pill': pill, 'lw': CHANNELS_W - 92, 'h': CHANNEL_ROW - 8,
                                     'c': '$VAR[SiloYouTubeHistoryText]' if focused else TEXT}


# What KodiConnectForSilo focuses when a section is chosen: its rows' first with
# videos, Search's history, or Subscriptions' All (a button, once it shows).
WAIT_IDS = {'search': [HISTORY_ID],
            'subscriptions': []}
WAIT_CONTROLS = {'subscriptions': [ALL_ID]}


def choose_section(key):
    """Opening on a section (the window's onload): it shows, and KodiConnectForSilo
    focuses it once it can. Not a SetFocus here: the section shows only from the
    next frame, and a SetFocus Kodi can't do drops focus altogether."""
    return ['SetProperty(silo.youtube.section,%s,home)' % key, 'SetProperty(silo.youtube.loaded.%s,1,home)' % key,
            wait_focus(key, WAIT_IDS[key], WAIT_CONTROLS.get(key, []))]


def channel_row(focused):
    pill_image = ''
    if focused:
        pill_image = '''
                    <control type="image">
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture border="30" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'w': CHANNELS_W, 'h': CHANNEL_ROW - 8, 'text': TEXT, 'id': CHANNELS_ID}
    return '''%(pill)s
                    <control type="image">
                        <left>14</left><top>8</top><width>48</width><height>48</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/avatar_mask.png" fallback="colors/grey.png">$INFO[ListItem.Icon]</texture>
                    </control>
                    <control type="label">
                        <left>78</left><top>0</top><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(c)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>''' % {'pill': pill_image, 'lw': CHANNELS_W - 96, 'h': CHANNEL_ROW - 8,
                                     'c': '$VAR[SiloYouTubeRowText]' if focused else TEXT}


def subscriptions():
    """The app's Subscriptions: All and the channels, then the newest videos
    (All, published) or the chosen channel's."""
    chosen = '!String.IsEmpty(%s)' % CHANNEL
    return '''
        <!-- Subscriptions -->
        <control type="group">
            <visible>%(shown)s</visible>
            <control type="button" id="%(all)d">
                <visible>%(shown)s</visible>
                <left>%(x)d</left><top>%(top)d</top><width>%(cw)d</width><height>%(rh)d</height>
                <label>All</label>
                <font>silo_meta</font>
                <textoffsetx>78</textoffsetx>
                <aligny>center</aligny>
                <textcolor>%(text)s</textcolor>
                <focusedcolor>FF000000</focusedcolor>
                <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                <texturenofocus border="30" colordiffuse="$VAR[SiloYouTubeAllPill]">silo/pill.png</texturenofocus>
                <onleft>%(menu)s</onleft><onup>noop</onup>
                <ondown>%(channels)d</ondown>
                <!-- Right: the newest (published), or a channel's, waiting while they load. -->%(right)s
                <onclick>ClearProperty(silo.youtube.channel,home)</onclick>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(atop)d</top><width>%(cw)d</width><height>40</height>
                <font>silo_badge</font>
                <textcolor>%(dim)s</textcolor>
                <label>CHANNELS</label>
            </control>
            <control type="list" id="%(channels)d">
                <visible>%(shown)s</visible>
                <left>%(x)d</left><top>%(ltop)d</top><width>%(cw)d</width><height>%(lh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <onleft>%(menu)s</onleft><onup>%(all)d</onup>%(right)s
                <!-- A channel's videos at the right, as the app's (not its page),
                     focused once they have loaded. -->
                <onclick>SetProperty(silo.youtube.channel,$INFO[ListItem.Property(path)],home)</onclick>
                <onclick>%(wait)s</onclick>
                <itemlayout width="%(cw)d" height="%(row)d">%(channel)s
                </itemlayout>
                <focusedlayout width="%(cw)d" height="%(row)d">%(channel_focused)s
                </focusedlayout>
                <content>%(channel_items)s
                </content>
            </control>
            <control type="label">
                <left>%(gx)d</left><top>%(top)d</top><width>%(gw)d</width><height>%(rh)d</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloYouTubeChannelTitle]</label>
            </control>
            <control type="label">
                <left>%(gx)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>80</height>
                <font>silo_detail</font>
                <textcolor>%(sub)s</textcolor>
                <label>Nothing here yet</label>
                <visible>[%(chosen)s + !Container(%(grid)d).IsUpdating + Integer.IsEqual(Container(%(grid)d).NumItems,0)] | [!%(chosen)s + String.IsEmpty(%(recent1)s)]</visible>
            </control>
            <control type="panel" id="%(recent)d">
                <visible>%(shown)s + !%(chosen)s</visible>
                <left>%(gx6)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">280</scrolltime>
                <onleft>%(all)d</onleft><onup>noop</onup>
                <itemlayout width="%(giw)d" height="%(gih)d">%(rcard)s
                </itemlayout>
                <focusedlayout width="%(giw)d" height="%(gih)d">%(rcard_focused)s
                </focusedlayout>
                <content>%(recent_items)s
                </content>
            </control>
            <control type="panel" id="%(grid)d">
                <visible>%(shown)s + %(chosen)s</visible>
                <left>%(gx6)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">280</scrolltime>
                <onleft>%(channels)d</onleft><onup>noop</onup>
                <itemlayout width="%(giw)d" height="%(gih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(giw)d" height="%(gih)d">%(card_focused)s
                </focusedlayout>
                <content target="videos">$VAR[SiloYouTubeChannelPath]</content>
            </control>
        </control>''' % {
        'shown': shown('subscriptions'), 'all': ALL_ID, 'channels': CHANNELS_ID, 'grid': SUBS_GRID, 'menu': 'noop',
        'wait': wait_focus('subscriptions', [SUBS_GRID]),
        'right': '\n                <onright condition="!%s + %s">SetFocus(%d)</onright>' % (chosen, has_items(RECENT_GRID), RECENT_GRID)
                 + ''.join('\n                <onright condition="%s + %s">%s</onright>' % (chosen, condition, action)
                           for condition, action in to_grid(SUBS_GRID, 'subscriptions')),
        'chosen': chosen, 'recent': RECENT_GRID, 'recent1': PUBLISHED % 'recent.1.label',
        'channel_items': channel_items(), 'recent_items': recent_items(),
        'rcard': card(GRID_W, GRID_H, False, RECENT_GRID), 'rcard_focused': card(GRID_W, GRID_H, True, RECENT_GRID),
        'x': CONTENT_X, 'top': TOP, 'cw': CHANNELS_W, 'rh': CHANNEL_ROW - 8, 'text': TEXT, 'dim': TEXT_DIM, 'sub': SUB_DIM,
        'atop': TOP + CHANNEL_ROW + 8, 'ltop': TOP + CHANNEL_ROW + 52, 'lh': 1080 - TOP - CHANNEL_ROW - 52,
        'row': CHANNEL_ROW, 'channel': channel_row(False), 'channel_focused': channel_row(True),
        'gx': GRID_X, 'gx6': GRID_X - 6, 'gtop': TOP + CHANNEL_ROW, 'gw': 1920 - GRID_X, 'gh': 1080 - TOP - CHANNEL_ROW,
        'giw': GRID_ITEM_W, 'gih': GRID_ITEM_H, 'card': card(GRID_W, GRID_H, False, SUBS_GRID),
        'card_focused': card(GRID_W, GRID_H, True, SUBS_GRID)}


def build():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_youtube.py: edit that, not this. -->
<window id="%(window)d" type="window">
    <defaultcontrol always="true">%(first)d</defaultcontrol>
    <!-- A video left playing behind the page (Back from the player): stopped,
         as Skyline's other pages do; the YouTube add-on keeps its place. -->
    <onload condition="Player.HasVideo">PlayerControl(Stop)</onload>
    <!-- Home, its first row focused, as the app opens. -->
    <onload>ClearProperty(silo.youtube.section,home)</onload>
%(loaded)s
    <onload>ClearProperty(silo.youtube.channel,home)</onload>
    <onload>ClearProperty(silo.youtube.query,home)</onload>
    <onload>ClearProperty(silo.youtube.search,home)</onload>
    <!-- The section Skyline's YouTube page's pill chose (silo.youtube.open), else Home. -->%(open)s
    <onload>ClearProperty(silo.youtube.open,home)</onload>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <include content="SiloFrame">
            <param name="title">YouTube</param>
            <param name="sub">$VAR[SiloYouTubeSection]</param>
        </include>
%(subscriptions)s
%(search)s
    </controls>
</window>
''' % {'window': WINDOW_ID, 'first': ALL_ID, 'background': BACKGROUND,
       'loaded': '\n'.join('    <onload>ClearProperty(%s,home)</onload>' % (LOADED % key).replace('Window(Home).Property(', '')[:-1]
                            for key in ('subscriptions', 'search')),
       'open': ''.join('\n    <onload condition="%s">%s</onload>' % (condition, action)
                       # Search when its pill chose it, else Subscriptions.
                       for key in ('search', 'subscriptions')
                       for condition in ['%sString.IsEqual(%s,search)' % ('' if key == 'search' else '!', OPEN)]
                       for action in choose_section(key)),
       'subscriptions': subscriptions(), 'search': search_section()}


VARIABLES = '''
    <!-- Silo Skyline YouTube (tools/build_youtube.py) -->
%(lazy)s    <variable name="SiloYouTubeSection">
        <value condition="String.IsEqual(%(section)s,search)">Search</value>
        <value condition="String.IsEqual(%(section)s,subscriptions)">Subscriptions</value>
        <value condition="String.IsEqual(%(section)s,library)">Library</value>
        <value>Home</value>
    </variable>
    <variable name="SiloYouTubeThumbBehind">
        <value condition="!String.IsEmpty(ListItem.Property(video_id))">https://i.ytimg.com/vi/$INFO[ListItem.Property(video_id)]/hqdefault.jpg</value>
        <value>colors/grey.png</value>
    </variable>
    <variable name="SiloYouTubeThumb">
        <value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
        <value>$INFO[ListItem.Icon]</value>
    </variable>
    <!-- The app's second line, the channel; the add-on names it as the studio (or the artist). -->
    <variable name="SiloYouTubeChannel">
        <value condition="!String.IsEmpty(ListItem.Property(channel))">$INFO[ListItem.Property(channel)]</value>
        <value condition="String.IsEqual(ListItem.Studio,Untitled) | String.IsEqual(ListItem.Artist,Untitled)"></value>
        <value condition="!String.IsEmpty(ListItem.Studio)">$INFO[ListItem.Studio]</value>
        <value>$INFO[ListItem.Artist]</value>
    </variable>
    <variable name="SiloYouTubeWhen">
        <value condition="!String.IsEmpty(ListItem.Property(when))">$INFO[ListItem.Property(when)]</value>
        <value condition="!String.IsEmpty(ListItem.Premiered)">$INFO[ListItem.Premiered]</value>
        <value>$INFO[ListItem.Date]</value>
    </variable>
    <variable name="SiloYouTubeRowText">
        <value condition="Control.HasFocus(%(channels)d)">FF000000</value>
        <value>%(text)s</value>
    </variable>
    <variable name="SiloYouTubeAllPill">
        <value condition="String.IsEmpty(%(channel)s)">33FFFFFF</value>
        <value>00FFFFFF</value>
    </variable>
    <!-- The chosen channel's videos (All's are published: RECENT_GRID). -->
    <variable name="SiloYouTubeChannelPath">
        <value condition="String.Contains(%(channel)s,?)">$INFO[%(channel)s]%(more)s</value>
        <value condition="!String.IsEmpty(%(channel)s)">$INFO[%(channel)s]%(params)s</value>
    </variable>
    <variable name="SiloYouTubeChannelTitle">
        <value condition="!String.IsEmpty(%(channel)s)">Latest</value>
        <value>Most recent</value>
    </variable>
    <variable name="SiloYouTubeResultsTitle">
        <value condition="!String.IsEmpty(%(query)s)">$INFO[%(query)s,Results for “,”]</value>
        <value>Pick a search, or start a new one</value>
    </variable>
    <!-- The add-on's New search item opens its keyboard (kodion/search/input). -->
    <variable name="SiloYouTubeHistoryIcon">
        <value condition="String.Contains(ListItem.FolderPath,/search/input)">icons/search.png</value>
        <value>silo/menu_history.png</value>
    </variable>
    <variable name="SiloYouTubeHistoryText">
        <value condition="Control.HasFocus(%(history)d)">FF000000</value>
        <value>%(text)s</value>
    </variable>
    <!-- end Silo Skyline YouTube -->
''' % {'lazy': lazy_variables(), 'query': QUERY, 'history': HISTORY_ID,
       'section': SECTION, 'channels': CHANNELS_ID, 'text': TEXT, 'channel': CHANNEL,
       'params': ROW_PARAMS, 'more': ROW_PARAMS.replace('?', '&amp;', 1)}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline YouTube (tools/build_youtube.py) -->', '    <!-- end Silo Skyline YouTube -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloYouTube.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/Custom_%d_SiloYouTube.xml and its variables in xml/Variables.xml' % WINDOW_ID)
