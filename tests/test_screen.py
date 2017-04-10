# coding: utf-8

#
# Copyright © 2017 weirdgiraffe <giraffe@cyberzoo.xyz>
#
# Distributed under terms of the MIT license.
#
import pytest
import re
from datetime import datetime, timedelta
import screen
from kodi import Plugin
from mock_kodi.xbmcplugin import directory, resolved, clear_resolved

assert pytest


def strip_colors(instr):
    return re.sub(r'\[COLOR [A-F0-9]{8}\](.+?)\[\/COLOR\]', r'\1', instr)


def test_screen_week():
    plugin = Plugin('plugin://url', '1', 'plugin://url?screen=week')
    del directory[:]

    screen.render(plugin)

    # expect list of 8 entries for last 7 days and one entry for search
    assert len(directory) == 8
    checked_date = datetime.today()
    for i in directory[:-1]:
        datestr = checked_date.strftime('%d.%m.%Y')
        assert i.list_item.name == datestr
        assert i.directory is True
        assert i.url_params['screen'] == 'day'
        assert i.url_params['date'] == datestr
        checked_date -= timedelta(days=1)

    assert directory[-1].directory is True
    assert directory[-1].url_params['screen'] == 'search'
    assert strip_colors(directory[-1].list_item.name) == 'поиск'


def test_screen_day(requests_mock):
    requests_mock.respond(r'http:\/\/seasonvar.ru$', 'assets/index.html')
    args = 'plugin://url?screen=day&date=06.04.2017'
    plugin = Plugin('plugin://url', '1', args)
    del directory[:]

    screen.render(plugin)

    assert len(directory) == 58
    for i in directory:
        assert i.list_item.name != ''
        assert i.directory is True
        assert i.url_params['screen'] == 'episodes'
        assert i.url_params['url'] != ''
        assert i.list_item.property['Art'] != ''


def test_screen_episodes(requests_mock):
    requests_mock.respond(r'seasonvar.ru\/.*Skorpion.*\.html$',
                          'assets/scorpion.html')
    requests_mock.respond(r'seasonvar.ru\/player\.php$',
                          'assets/scorpion-player.html', methods=['POST'])
    requests_mock.respond(r'seasonvar.ru\/playls2.*/list\.xml.*$',
                          'assets/scorpion-playlist.json')
    del directory[:]
    url = '/serial-14354-Skorpion-3-season.html'
    args = 'plugin://url?screen=episodes&url={0}'.format(url)
    plugin = Plugin('plugin://url', '1', args)

    screen.render(plugin)

    assert len(directory) == 21
    for i in directory[2:]:
        assert i.list_item.name != ''
        assert i.directory is False
        assert i.url_params['play'] != ''
        assert i.list_item.property['Art'] != ''

    assert strip_colors(directory[0].list_item.name) == 'сезон: 3 / 3'
    assert directory[0].directory is True
    assert directory[0].url_params['screen'] == 'seasons'
    assert directory[0].url_params['url'] != ''

    assert strip_colors(directory[1].list_item.name) == 'озвучка: Стандартная'
    assert directory[1].directory is True
    assert directory[1].url_params['screen'] == 'translations'
    assert directory[1].url_params['url'] != ''


def test_screen_seasons(requests_mock):
    requests_mock.respond(r'seasonvar.ru\/.*Skorpion.*\.html$',
                          'assets/scorpion.html')
    del directory[:]
    url = '/serial-14354-Skorpion-3-season.html'
    args = 'plugin://url?screen=seasons&url={0}'.format(url)
    plugin = Plugin('plugin://url', '1', args)

    screen.render(plugin)

    assert len(directory) == 3
    assert directory[2].list_item.name == '* сезон 3'

    for i in directory:
        assert i.list_item.name != ''
        assert i.directory is True
        assert i.url_params['screen'] == 'episodes'
        assert i.url_params['url'] != ''
        assert i.list_item.property['Art'] != ''


def test_screen_translations(requests_mock):
    requests_mock.respond(r'seasonvar.ru\/.*Skorpion.*\.html$',
                          'assets/scorpion.html')
    requests_mock.respond(r'seasonvar.ru\/player\.php$',
                          'assets/scorpion-player.html', methods=['POST'])
    del directory[:]
    url = '/serial-14354-Skorpion-3-season.html'
    args = 'plugin://url?screen=translations&url={0}'.format(url)
    plugin = Plugin('plugin://url', '1', args)

    screen.render(plugin)

    assert len(directory) == 3
    assert directory[0].list_item.name == '* Стандартная'
    for i in directory:
        assert i.list_item.name != ''
        assert i.directory is True
        assert i.url_params['screen'] == 'episodes'
        assert i.url_params['url'] != ''
        assert i.list_item.property['Art'] != ''


def test_play():
    del directory[:]
    clear_resolved()
    args = 'plugin://url?play=someurl'
    plugin = Plugin('plugin://url', '1', args)

    screen.render(plugin)

    assert resolved() == 'someurl'
