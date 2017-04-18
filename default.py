import re
import urllib, urllib2
import re, string
import threading
import os
import base64
import sys
#from t0mm0.common.addon import Addon
#from t0mm0.common.net import Net
import urlparse
import json
from requester import  *
from xbmcswift2 import *
from  resources.lib.F4mProxy import f4mProxyHelper
#from xbmcswift2 import xbmcplugin
import xbmcplugin

# plugin constants
__plugin__ = "plugin.video.vvvvid"
__author__ = "evilsephiroth"

plugin = Plugin()
handleAddon = int(sys.argv[1])


@plugin.route('/',name="root")
def show_main_channels():
    items = [{
        'label': ROOT_LABEL_ANIME,
        'path' : plugin.url_for('animeChannels'),
        'is_playable': False
    },
    {
        'label': ROOT_LABEL_MOVIES,
        'path' : plugin.url_for('movieChannels'),
        'is_playable': False
    },
    {
        'label': ROOT_LABEL_SHOWS,
        'path' : plugin.url_for('tvChannels'),
        'is_playable': False
    },
    {
        'label': ROOT_LABEL_SERIES,
        'path' : plugin.url_for('seriesChannels'),
        'is_playable': False
    }];
    return items;

@plugin.route('/movie/channels',name="movieChannels")
def showMovieChannels():
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item['label'] = channel.title
        item['is_playable'] = False
        if(len(channel.filterList) != 0):
            item['path'] = plugin.url_for('showMovieChannelFilters',idChannel=channel.id)
        elif(len(channel.categoryList) != 0):
            item['path'] = plugin.url_for('showMovieChannelCategories',idChannel=channel.id)
        elif(len(channel.extraList) != 0):
            item['path'] = plugin.url_for('showMovieChannelExtras',idChannel=channel.id)
        else:
           item['path'] = plugin.url_for('showMovieSingleChannel',idChannel=channel.id)
        items.append(item)
    return items

@plugin.route('/movie/channel/<idChannel>/filter/<filter>',name="showMovieSingleChannelFilter")
@plugin.route('/movie/channel/<idChannel>/category/<category>',name="showMovieSingleChannelCategory")
@plugin.route('/movie/channel/<idChannel>/extra/<extra>',name="showMovieSingleChannelExtra")
@plugin.route('/movie/channel/<idChannel>',name="showMovieSingleChannel")
def showMovieSingleChannel(idChannel,filter = '',category = '',extra = ''):
    channelsElements = get_elements_from_channel(idChannel,MODE_MOVIES,filter,category,extra) 
    items = []
    for element in channelsElements:
        item = dict()
        item['label'] = element.title
        item['is_playable'] = False
        item['icon']= element.thumb
        item['thumbnail']= element.thumb
        item['path'] = plugin.url_for('showSingleMovieItem',idItem = element.show_id)
        items.append(item)
    return items

@plugin.route('/movie/channel/<idChannel>/filters',name="showMovieChannelFilters")
def showMovieChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for filter in channel.filterList:
                item = dict()
                item['label'] = str(filter)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showMovieSingleChannelFilter',idChannel=channel.id,filter = str(filter))
                items.append(item)
    return items

@plugin.route('/movie/channel/<idChannel>/categories',name="showMovieChannelCategories")
def showMovieChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for category in channel.categoryList:
                item = dict()
                item['label'] = str(category.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showMovieSingleChannelCategory',idChannel=channel.id,category = str(category.id))
                items.append(item)
    return items     

@plugin.route('/movie/channel/<idChannel>/extras',name="showMovieChannelExtras")
def showMovieChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for extra in channel.extraList:
                item = dict()
                item['label'] = str(extra.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showMovieSingleChannelExtra',idChannel=extra.id,extra = str(extra.id))
                items.append(item)
    return items     

@plugin.route('/movie/item/<idItem>',name='showSingleMovieItem')
def showSingleMovieItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if(len(itemPlayable.seasons) > 1):
        for season in itemPlayable.seasons:
            item = dict()
            item['label'] = season.title
            item['is_playable'] = False
            item['path'] = plugin.url_for('showSingleMovieItemSeason',idItem=idItem,seasonId = season.season_id)
            items.append(item)  
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(handleAddon, 'movies')
        for episode in episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

@plugin.route('/movie/item/<seasonId>/<idItem>',name='showSingleMovieItemSeason')
def showSingleMovieItemSeason(seasonId,idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(handleAddon, 'movies')
    for season in itemPlayable.seasons:
        if(unicode(season.season_id) == seasonId):
            for episode in season.episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

@plugin.route('/show/channels',name="showChannels")
def showTvShowsChannels():
    channels = get_section_channels(MODE_SHOWS)
    items = []
    for channel in channels:
        print
'''

Start tv
'''
@plugin.route('/tv/channels',name="tvChannels")
def showTvChannels():
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item['label'] = channel.title
        item['is_playable'] = False
        if(len(channel.filterList) != 0):
            item['path'] = plugin.url_for('showTvChannelFilters',idChannel=channel.id)
        elif(len(channel.categoryList) != 0):
            item['path'] = plugin.url_for('showTvChannelCategories',idChannel=channel.id)
        elif(len(channel.extraList) != 0):
            item['path'] = plugin.url_for('showTvChannelExtras',idChannel=channel.id)
        else:
           item['path'] = plugin.url_for('showTvSingleChannel',idChannel=channel.id)
        items.append(item)
    return items
        
@plugin.route('/tv/channel/<idChannel>/filter/<filter>',name="showTvSingleChannelFilter")
@plugin.route('/tv/channel/<idChannel>/category/<category>',name="showTvSingleChannelCategory")
@plugin.route('/tv/channel/<idChannel>/extra/<extra>',name="showTvSingleChannelExtra")
@plugin.route('/tv/channel/<idChannel>',name="showTvSingleChannel")
def showTvSingleChannel(idChannel,filter = '',category = '',extra = ''):
    channelsElements = get_elements_from_channel(idChannel,MODE_SHOWS,filter,category,extra) 
    items = []
    for element in channelsElements:
        item = dict()
        item['label'] = element.title
        item['is_playable'] = False
        item['icon']= element.thumb
        item['thumbnail']= element.thumb
        item['path'] = plugin.url_for('showSingleTvItem',idItem = element.show_id)
        items.append(item)
    return items

@plugin.route('/tv/channel/<idChannel>/filters',name="showTvChannelFilters")
def showTvChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for filter in channel.filterList:
                item = dict()
                item['label'] = str(filter)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showTvSingleChannelFilter',idChannel=channel.id,filter = str(filter))
                items.append(item)
    return items

@plugin.route('/tv/channel/<idChannel>/categories',name="showTvChannelCategories")
def showTvChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for category in channel.categoryList:
                item = dict()
                item['label'] = str(category.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showTvSingleChannelCategory',idChannel=channel.id,category = str(category.id))
                items.append(item)
    return items     

@plugin.route('/tv/channel/<idChannel>/extras',name="showTvChannelExtras")
def showTvChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for extra in channel.extraList:
                item = dict()
                item['label'] = str(extra.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showTvSingleChannelExtra',idChannel=extra.id,extra = str(extra.id))
                items.append(item)
    return items     

@plugin.route('/tv/item/<idItem>',name='showSingleTvItem')
def showSingleTvItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if(len(itemPlayable.seasons) > 1):
        for season in itemPlayable.seasons:
            item = dict()
            item['label'] = season.title
            item['is_playable'] = False
            item['path'] = plugin.url_for('showSingleTvItemSeason',idItem=idItem,seasonId = season.season_id)
            items.append(item)  
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(handleAddon, 'tvshows')
        for episode in episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

@plugin.route('/tv/item/<seasonId>/<idItem>',name='showSingleTvItemSeason')
def showSingleTvItemSeason(seasonId,idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(handleAddon, 'tvshows')
    for season in itemPlayable.seasons:
        if(unicode(season.season_id) == seasonId):
            for episode in season.episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

'''
end tv
'''

'''
start anime
'''
@plugin.route('/anime/channels',name="animeChannels")
def showAnimeChannels():
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item['label'] = channel.title
        item['is_playable'] = False
        if(len(channel.filterList) != 0):
            item['path'] = plugin.url_for('showAnimeChannelFilters',idChannel=channel.id)
        elif(len(channel.categoryList) != 0):
            item['path'] = plugin.url_for('showAnimeChannelCategories',idChannel=channel.id)
        elif(len(channel.extraList) != 0):
            item['path'] = plugin.url_for('showAnimeChannelExtras',idChannel=channel.id)
        else:
           item['path'] = plugin.url_for('showAnimeSingleChannel',idChannel=channel.id)
        items.append(item)
    return items
        
@plugin.route('/anime/channel/<idChannel>/filter/<filter>',name="showAnimeSingleChannelFilter")
@plugin.route('/anime/channel/<idChannel>/category/<category>',name="showAnimeSingleChannelCategory")
@plugin.route('/anime/channel/<idChannel>/extra/<extra>',name="showAnimeSingleChannelExtra")
@plugin.route('/anime/channel/<idChannel>',name="showAnimeSingleChannel")
def showAnimeSingleChannel(idChannel,filter = '',category = '',extra = ''):
    channelsElements = get_elements_from_channel(idChannel,MODE_ANIME,filter,category,extra) 
    items = []
    for element in channelsElements:
        item = dict()
        item['label'] = element.title
        item['is_playable'] = False
        item['icon']= element.thumb
        item['thumbnail']= element.thumb
        item['path'] = plugin.url_for('showSingleAnimeItem',idItem = element.show_id)
        items.append(item)
    return items

@plugin.route('/anime/channel/<idChannel>/filters',name="showAnimeChannelFilters")
def showAnimeChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for filter in channel.filterList:
                item = dict()
                item['label'] = str(filter)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showAnimeSingleChannelFilter',idChannel=channel.id,filter = str(filter))
                items.append(item)
    return items

@plugin.route('/anime/channel/<idChannel>/categories',name="showAnimeChannelCategories")
def showAnimeChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for category in channel.categoryList:
                item = dict()
                item['label'] = str(category.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showAnimeSingleChannelCategory',idChannel=channel.id,category = str(category.id))
                items.append(item)
    return items     

@plugin.route('/anime/channel/<idChannel>/extras',name="showAnimeChannelExtras")
def showAnimeChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for extra in channel.extraList:
                item = dict()
                item['label'] = str(extra.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showAnimeSingleChannelExtra',idChannel=extra.id,extra = str(extra.id))
                items.append(item)
    return items     

@plugin.route('/anime/item/<idItem>',name='showSingleAnimeItem')
def showSingleAnimeItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if(len(itemPlayable.seasons) > 1):
        for season in itemPlayable.seasons:
            item = dict()
            item['label'] = season.title
            item['is_playable'] = False
            item['path'] = plugin.url_for('showSingleAnimeItemSeason',idItem=idItem,seasonId = season.season_id)
            items.append(item)  
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(handleAddon, 'tvshows')
        for episode in episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

@plugin.route('/anime/item/<seasonId>/<idItem>',name='showSingleAnimeItemSeason')
def showSingleAnimeItemSeason(seasonId,idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(handleAddon, 'tvshows')
    for season in itemPlayable.seasons:
        if(unicode(season.season_id) == seasonId):
            for episode in season.episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items
'''

end anime
'''
'''

Start series
'''
@plugin.route('/series/channels',name="seriesChannels")
def showSeriesChannels():
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item['label'] = channel.title
        item['is_playable'] = False
        if(len(channel.filterList) != 0):
            item['path'] = plugin.url_for('showSeriesChannelFilters',idChannel=channel.id)
        elif(len(channel.categoryList) != 0):
            item['path'] = plugin.url_for('showSeriesChannelCategories',idChannel=channel.id)
        elif(len(channel.extraList) != 0):
            item['path'] = plugin.url_for('showSeriesChannelExtras',idChannel=channel.id)
        else:
           item['path'] = plugin.url_for('showSeriesSingleChannel',idChannel=channel.id)
        items.append(item)
    return items
        
@plugin.route('/series/channel/<idChannel>/filter/<filter>',name="showSeriesSingleChannelFilter")
@plugin.route('/series/channel/<idChannel>/category/<category>',name="showSeriesSingleChannelCategory")
@plugin.route('/series/channel/<idChannel>/extra/<extra>',name="showSeriesSingleChannelExtra")
@plugin.route('/series/channel/<idChannel>',name="showSeriesSingleChannel")
def showSeriesSingleChannel(idChannel,filter = '',category = '',extra = ''):
    channelsElements = get_elements_from_channel(idChannel,MODE_SERIES,filter,category,extra) 
    items = []
    for element in channelsElements:
        item = dict()
        item['label'] = element.title
        item['is_playable'] = False
        item['icon']= element.thumb
        item['thumbnail']= element.thumb
        item['path'] = plugin.url_for('showSingleSeriesItem',idItem = element.show_id)
        items.append(item)
    return items

@plugin.route('/series/channel/<idChannel>/filters',name="showSeriesChannelFilters")
def showSeriesChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for filter in channel.filterList:
                item = dict()
                item['label'] = str(filter)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showSeriesSingleChannelFilter',idChannel=channel.id,filter = str(filter))
                items.append(item)
    return items

@plugin.route('/series/channel/<idChannel>/categories',name="showSeriesChannelCategories")
def showSeriesChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for category in channel.categoryList:
                item = dict()
                item['label'] = str(category.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showSeriesSingleChannelCategory',idChannel=channel.id,category = str(category.id))
                items.append(item)
    return items     

@plugin.route('/series/channel/<idChannel>/extras',name="showSeriesChannelExtras")
def showSeriesChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if(channel.id == idChannel):
            for extra in channel.extraList:
                item = dict()
                item['label'] = str(extra.name)
                item['is_playable'] = False
                item['path'] = plugin.url_for('showSeriesSingleChannelExtra',idChannel=extra.id,extra = str(extra.id))
                items.append(item)
    return items     

@plugin.route('/series/item/<idItem>',name='showSingleSeriesItem')
def showSingleSeriesItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if(len(itemPlayable.seasons) > 1):
        for season in itemPlayable.seasons:
            item = dict()
            item['label'] = season.title
            item['is_playable'] = False
            item['path'] = plugin.url_for('showSingleSeriesItemSeason',idItem=idItem,seasonId = season.season_id)
            items.append(item)  
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(handleAddon, 'series')
        for episode in episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

@plugin.route('/series/item/<seasonId>/<idItem>',name='showSingleSeriesItemSeason')
def showSingleSeriesItemSeason(seasonId,idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(handleAddon, 'series')
    for season in itemPlayable.seasons:
        if(unicode(season.season_id) == seasonId):
            for episode in season.episodes:
                item = dict()
                item['label'] = episode.title
                item['icon']= episode.thumb
                item['thumbnail']= episode.thumb
                props = dict()
                props.update(fanart_image = item['thumbnail'])
                item['properties'] = props
                if(episode.stream_type == F4M_TYPE):
                    item['path'] = plugin.url_for('playManifest',manifest=episode.manifest,title = episode.title)
                    item['is_playable'] = False
                elif(episode.stream_type == M3U_TYPE):
                    item['path'] = episode.manifest
                    item['is_playable'] = True
                items.append(item)
    return items

'''
end series
'''

@plugin.route('/watch/<manifest>/<title>',name='playManifest')
def playManifest(manifest,title):
    print manifest
    print manifest
    print manifest
    print manifest
    print manifest
    print manifest
    print manifest
    player=f4mProxyHelper()
    player.playF4mLink(manifest,title)
    print

if __name__ == '__main__':
    if not plugin.get_setting('username') or not plugin.get_setting('password'):
        xbmcgui.Dialog().ok('VVVVID.it','Configurare il plugin inserendo email e password')
        sys.exit(0)
    data_storage = plugin.get_storage('vvvvid')
    #conn_id = data_storage['conn_id']
    if data_storage.get('cookie'):
        cookie = data_storage['cookie']
    else:
        cookie = None
    req = urllib2.Request('http://www.vvvvid.it/user/login')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36')
    if cookie:
        req.add_header('Cookie',cookie)
    response = urllib2.urlopen(req)
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    #plugin.log.error('check login:'+ str(data))
    if data['result'] != 'ok':
        post_data = urllib.urlencode({u'action':u'login',u'email':plugin.get_setting('username'),u'password':plugin.get_setting('password'),u'login_type':u'force','reminder':'true'})
        req.add_data(post_data)
        response = urllib2.urlopen(req)
        data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
        #plugin.log.error('output:'+ str(data))
        if data['result'] != 'first' and data['result'] !='ok':
            xbmcgui.Dialog().ok('VVVVID.it','Impossibile eseguire login')
            sys.exit(0)
        data_storage['conn_id'] = data['data']['conn_id']
        if 'set-cookie' in response.info().keys():
            data_storage['cookie'] = response.info()['Set-Cookie']
    else:
        data_storage['conn_id'] = data['data']['conn_id']
        #plugin.log.error('output: non devo loggare')
    
    handleAddon = int(sys.argv[1])
    xbmcplugin.setContent(handleAddon, 'files')
    plugin.run()
""""
kwargs = {
            'label': label,
            'label2': label2,
            'iconImage': icon,
            'thumbnailImage': thumbnail,
            'path': path,
        }
"""
 
