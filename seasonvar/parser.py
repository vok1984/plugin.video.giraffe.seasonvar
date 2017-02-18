# coding: utf-8

#
# Copyright © 2017 weirdgiraffe <giraffe@cyberzoo.xyz>
#
# Distributed under terms of the MIT license.
#
import re


def main_page_items(main_page_html, datestr):
    '''Collect all dayblock items(i.e episode changes) for a given date
    and yields dict {'url': ..., 'name': ..., 'changes': ...} for each
    episode for that date.

    datestr should be in format 'dd.mm.yyyy'
    '''
    print(type(main_page_html))
    for (date, dayblock) in _main_page_dayblocks(main_page_html):
        if datestr == date:
            for item in _main_page_dayblock_items(dayblock):
                yield item


def search_items(search_response):
    '''yield dict {'name':..., 'url': ...} for items in search_response

    search_response is dict representation of search response
    '''
    for name, url in zip(search_response['suggestions'],
                         search_response['data']):
        if url:
            yield {'name': name, 'url': '/' + url}


def seasons(season_page_html):
    '''takes content of season page and yields
    all seasons for the same show.

    season_page_html should be utf-8 encoded html content
    '''
    r = re.compile(
            r'<h2>.*?'
            r'href="(/serial-\d+-[^-.]+(:?-\d+-(sezon|season))?\.html)".*?',
            re.DOTALL)
    for url in r.findall(season_page_html):
        yield url


def playlists(season_page_html):
    '''takes content of season page and yield dict {'tr':..., 'url':...}
    where 'tr' is a translation name and 'url' is a playlist url.
    If no translations found on page, then search for playlist urls only
    will be done. In this case translation names will be None.

    season_page_html should be utf-8 encoded html content
    '''
    div = _translate_div(season_page_html)
    if div is not None:
        r = re.compile(r'<li\s+id="translate.*?>(.*?)</li>.*?'
                       r'var\s+pl\d+\s+=\s+"(.*?)";',
                       re.DOTALL)
        for name, url in r.findall(div):
            yield {'tr': name.strip(),
                   'url': url.strip()}
    else:
        r = re.compile(r'var\s+pl\d+\s+=\s+"(.+)";')
        for url in r.findall(season_page_html):
            yield {'tr': None,
                   'url': url.strip()}


def episodes(playlist_dict):
    '''yield dict {'name':..., 'url': ...} for items in playlist_dict

    playlist_dict is dict representation of repose playlist for playlist url
    '''
    playlist = playlist_dict['playlist']
    for entry in playlist:
        if 'playlist' in entry:
            for episode in entry['playlist']:
                yield {'url': episode['file'],
                       'name': episode['comment'].replace('<br>', ' ')}
        else:
            yield {'url': entry['file'],
                   'name': entry['comment'].replace('<br>', ' ')}


def _translate_div(season_page_html):
    r = re.compile(r'<ul\s+id="translateDiv"(.*?)</ul>', re.DOTALL)
    for b in r.findall(season_page_html):
        return b


def _main_page_dayblocks(full_page_html):
    '''Collect all dayblocks from full_page_html
    and yield (date, content) for every dayblock'''
    r = re.compile(
        r'<div class="ff1">(\d{2}\.\d{2}\.\d{4})(.*?)'
        r'(?=<div align="center"|<div class="film-list-block")',
        re.DOTALL)
    for group in r.findall(full_page_html):
        d, c = group
        yield group


def _main_page_dayblock_items(dayblock_content):
    '''Collect all series items from dayblock_content
    and for every item yield dict with description'''
    r = re.compile(
        r'<a href="(\/serial-.+?\.html)" class="film-list-item-link">'
        '(.+?)<\/a>(.*?)<span>(.+?)<\/span>',
        re.DOTALL)
    for (url, name, changes1, changes2) in r.findall(dayblock_content):
        changes = '{0} {1}'.format(changes1.strip(), changes2.strip())
        yield {'url': url,
               'name': name.strip(),
               'changes': changes.strip()}
