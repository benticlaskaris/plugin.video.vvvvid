import re
import urllib, urllib2
import re, string
import threading
import os
import base64
import sys
import urlparse
import json
from requester import *
from resources.lib.F4mProxy import f4mProxyHelper
import xbmcplugin
import xbmcaddon
import xbmcgui
import routing as routing_plugin

# plugin constants
__plugin__ = "plugin.video.vvvvid"
__author__ = "evilsephiroth"

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo("path").decode("utf-8")
routing = routing_plugin.Plugin()


def add_items(items, isFolder=False):
    for item in items:
        label = None
        label2 = None
        iconImage = None
        thumbnailImage = None
        path = None
        offscreen = False

        for property, value in item.items():
            if property == "label":
                label = value
            elif property == "label2":
                label2 = value
            elif property == "iconImage":
                iconImage = value
            elif property == "thumbnailImage":
                thumbnailImage = value
            elif property == "path":
                path = value
            elif property == "offscreen":
                offscreen = value
            else:
                # TODO: properties
                pass
        item = xbmcgui.ListItem(
            label, label2, iconImage, thumbnailImage, path, offscreen
        )
        xbmcplugin.addDirectoryItem(__handle__, path, item, True)
    xbmcplugin.endOfDirectory(__handle__)


@routing.route("/")
def show_main_channels():
    items = [
        {
            "label": ROOT_LABEL_ANIME,
            "path": routing.url_for(showAnimeChannels),
            "is_playable": False,
        },
        {
            "label": ROOT_LABEL_MOVIES,
            "path": routing.url_for(showMovieChannels),
            "is_playable": False,
        },
        {
            "label": ROOT_LABEL_SHOWS,
            "path": routing.url_for(showTvChannels),
            "is_playable": False,
        },
        {
            "label": ROOT_LABEL_SERIES,
            "path": routing.url_for(showSeriesChannels),
            "is_playable": False,
        },
    ]

    add_items(items)


@routing.route("/movie/channels")
def showMovieChannels():
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(
                showMovieChannelFilters, idChannel=channel.id
            )
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showMovieChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(showMovieChannelExtras, idChannel=channel.id)
        else:
            item["path"] = routing.url_for(showMovieSingleChannel, idChannel=channel.id)
        items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/filter/<filter>")
@routing.route("/movie/channel/<idChannel>/category/<category>")
@routing.route("/movie/channel/<idChannel>/extra/<extra>")
@routing.route("/movie/channel/<idChannel>")
def showMovieSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_MOVIES, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumbnail"] = element.thumb
        item["path"] = routing.url_for(showSingleMovieItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/filters")
def showMovieChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showMovieSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/categories")
def showMovieChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showMovieSingleChannel,
                    idChannel=channel.id,
                    category=str(category.id),
                )
                items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/extras")
def showMovieChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showMovieSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/movie/item/<idItem>")
def showSingleMovieItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            item["path"] = routing.url_for(
                showSingleMovieItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "movies")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumbnail"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumbnail"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=urllib.quote_plus(episode.manifest),
                    title=urllib.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/movie/item/<seasonId>/<idItem>")
def showSingleMovieItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "movies")
    for season in itemPlayable.seasons:
        if unicode(season.season_id) == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumbnail"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumbnail"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=urllib.quote_plus(episode.manifest),
                        title=urllib.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


@routing.route("/show/channels")
def showTvShowsChannels():
    channels = get_section_channels(MODE_SHOWS)
    items = []
    for channel in channels:
        print


"""

Start tv
"""


@routing.route("/tv/channels")
def showTvChannels():
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(showTvChannelFilters, idChannel=channel.id)
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showTvChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(showTvChannelExtras, idChannel=channel.id)
        else:
            item["path"] = routing.url_for(showTvSingleChannel, idChannel=channel.id)
        items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/filter/<filter>")
@routing.route("/tv/channel/<idChannel>/category/<category>")
@routing.route("/tv/channel/<idChannel>/extra/<extra>")
@routing.route("/tv/channel/<idChannel>")
def showTvSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_SHOWS, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumbnail"] = element.thumb
        item["path"] = routing.url_for(showSingleTvItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/filters")
def showTvChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showTvSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/categories")
def showTvChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showTvSingleChannel, idChannel=channel.id, category=str(category.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/extras")
def showTvChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showTvSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/tv/item/<idItem>")
def showSingleTvItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            item["path"] = routing.url_for(
                showSingleTvItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "tvshows")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumbnail"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumbnail"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=urllib.quote_plus(episode.manifest),
                    title=urllib.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/tv/item/<seasonId>/<idItem>")
def showSingleTvItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "tvshows")
    for season in itemPlayable.seasons:
        if unicode(season.season_id) == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumbnail"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumbnail"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=urllib.quote_plus(episode.manifest),
                        title=urllib.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


"""
end tv
"""

"""
start anime
"""


@routing.route("/anime/channels")
def showAnimeChannels():
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(
                showAnimeChannelFilters, idChannel=channel.id
            )
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showAnimeChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(showAnimeChannelExtras, idChannel=channel.id)
        else:
            item["path"] = routing.url_for(showAnimeSingleChannel, idChannel=channel.id)
        items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/filter/<filter>")
@routing.route("/anime/channel/<idChannel>/category/<category>")
@routing.route("/anime/channel/<idChannel>/extra/<extra>")
@routing.route("/anime/channel/<idChannel>")
def showAnimeSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_ANIME, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumbnail"] = element.thumb
        item["path"] = routing.url_for(showSingleAnimeItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/filters")
def showAnimeChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showAnimeSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/categories")
def showAnimeChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showAnimeSingleChannel,
                    idChannel=channel.id,
                    category=str(category.id),
                )
                items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/extras")
def showAnimeChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showAnimeSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/anime/item/<idItem>")
def showSingleAnimeItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            print(
                "showSingleAnimeItem: {} id={} season={}".format(
                    season.title, idItem, season.season_id
                )
            )
            item["path"] = routing.url_for(
                showSingleAnimeItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "tvshows")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumbnail"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumbnail"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=urllib.quote_plus(episode.manifest),
                    title=urllib.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/anime/item/<seasonId>/<idItem>")
def showSingleAnimeItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "tvshows")
    for season in itemPlayable.seasons:
        if unicode(season.season_id) == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumbnail"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumbnail"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=urllib.quote_plus(episode.manifest),
                        title=urllib.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


"""

end anime
"""
"""

Start series
"""


@routing.route("/series/channels")
def showSeriesChannels():
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(
                showSeriesChannelFilters, idChannel=channel.id
            )
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showSeriesChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(
                showSeriesChannelExtras, idChannel=channel.id
            )
        else:
            item["path"] = routing.url_for(
                showSeriesSingleChannel, idChannel=channel.id
            )
        items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/filter/<filter>")
@routing.route("/series/channel/<idChannel>/category/<category>")
@routing.route("/series/channel/<idChannel>/extra/<extra>")
@routing.route("/series/channel/<idChannel>")
def showSeriesSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_SERIES, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumbnail"] = element.thumb
        item["path"] = routing.url_for(showSingleSeriesItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/filters")
def showSeriesChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showSeriesSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/categories")
def showSeriesChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showSeriesSingleChannel,
                    idChannel=channel.id,
                    category=str(category.id),
                )
                items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/extras")
def showSeriesChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showSeriesSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/series/item/<idItem>")
def showSingleSeriesItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            item["path"] = routing.url_for(
                showSingleSeriesItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "series")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumbnail"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumbnail"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=urllib.quote_plus(episode.manifest),
                    title=urllib.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/series/item/<seasonId>/<idItem>")
def showSingleSeriesItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "series")
    for season in itemPlayable.seasons:
        if unicode(season.season_id) == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumbnail"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumbnail"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=urllib.quote_plus(episode.manifest),
                        title=urllib.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


"""
end series
"""


@routing.route("/watch/<manifest>/<title>")
def playManifest(manifest, title):
    manifest = urllib.unquote_plus(manifest)
    title = urllib.unquote_plus(title)

    player = f4mProxyHelper()
    player.playF4mLink(manifest, title)


def set_credentials_dialog():
    username = xbmcgui.Dialog().input("Inserire email:")
    password = xbmcgui.Dialog().input(
        "Inserire password:", option=xbmcgui.ALPHANUM_HIDE_INPUT
    )

    if not username or not password:
        return None

    ADDON.setSettingString(id="username", value=username)
    ADDON.setSettingString(id="password", value=password)

    return {"username": username, "password": password}


def get_credentials():
    username = ADDON.getSettingString("username")
    if not username:
        return None

    password = ADDON.getSettingString("password")
    if not password:
        return None

    return {"username": username, "password": password}


if __name__ == "__main__":
    credentials = get_credentials()
    if not credentials:
        xbmcgui.Dialog().ok(
            "VVVVID.it", "Configurare il routing inserendo email e password"
        )
        credentials = set_credentials_dialog()

    if not credentials:
        xbmcgui.Dialog().ok("VVVVID.it", "ERRORE: email e/o password non validi")
        sys.exit(0)

    data_storage = Storage()
    cookie = data_storage.get("cookie")
    req = urllib2.Request("http://www.vvvvid.it/user/login")
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
    )
    if cookie:
        req.add_header("Cookie", cookie)
    response = urllib2.urlopen(req)
    data = json.loads(
        response.read().decode(response.info().getparam("charset") or "utf-8")
    )
    if data["result"] != "ok":
        post_data = urllib.urlencode(
            {
                u"action": u"login",
                u"email": credentials["username"],
                u"password": credentials["password"],
                u"login_type": u"force",
                "reminder": "true",
            }
        )
        req.add_data(post_data)
        response = urllib2.urlopen(req)
        data = json.loads(
            response.read().decode(response.info().getparam("charset") or "utf-8")
        )
        if data["result"] != "first" and data["result"] != "ok":
            xbmcgui.Dialog().ok("VVVVID.it", "Impossibile eseguire login")
            sys.exit(0)
        data_storage.set("conn_id", data["data"]["conn_id"])
        if "set-cookie" in response.info().keys():
            data_storage.set("cookie", response.info()["Set-Cookie"])
    else:
        data_storage.set("conn_id", data["data"]["conn_id"])

    xbmcplugin.setContent(__handle__, "files")
    routing.run()
