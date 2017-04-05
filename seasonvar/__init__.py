# coding: utf-8

#
# Copyright © 2017 weirdgiraffe <giraffe@cyberzoo.xyz>
#
# Distributed under terms of the MIT license.
#

import seasonvar.parser as parser
from seasonvar.requester import Requester


def day_items(datestr):
    r = Requester()
    page = r.main_page()
    return parser.main_page_items(page, datestr)


def season_info(season_url):
    r = Requester()
    p = r.season_page(season_url)
    params = parser.player_params(p)
    if params is None:
        return {}
    seasons = list(parser.seasons(p))
    snum = [n for n, u in enumerate(seasons, 1) if u == season_url][0]
    p = r.player(season_url, params)
    if p is not None:
        return {
            'number': snum,
            'total': seasons,
            'playlist': list(parser.playlists(p)),
        }


def episodes(playlist_url):
    r = Requester()
    p = r.playlist(playlist_url)
    return list(parser.episodes(p))
