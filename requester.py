import sys
#import requests
import urllib2
from cookielib import CookieJar
import urlparse
import json
from Channel import *
from ChannelCategory import *
from ChannelExtras import *
from ElementChannel import *
from ItemPlayableChannel import *
from _warnings import filters
from _elementtree import Element
from SeasonEpisode import *
from ItemPlayableSeason import *
from xbmcswift2 import *

VVVVID_BASE_URL="https://www.vvvvid.it/vvvvid/ondemand/"
ANIME_CHANNELS_PATH= "anime/channels"
MOVIE_CHANNELS_PATH = "film/channels"
SHOW_CHANNELS_PATH = "show/channels"
SERIES_CHANNELS_PATH = "series/channels"
ANIME_SINGLE_CHANNEL_PATH = "anime/channel/"
MOVIE_SINGLE_CHANNEL_PATH = "film/channel/"
SHOW_SINGLE_CHANNEL_PATH = "show/channel/"
SERIES_SINGLE_CHANNEL_PATH = "series/channel/"
ANIME_SINGLE_ELEMENT_CHANNEL_PATH = 'anime/'
SHOW_SINGLE_ELEMENT_CHANNEL_PATH = 'show/'
MOVIE_SINGLE_ELEMENT_CHANNEL_PATH = 'film/'
SERIES_SINGLE_ELEMENT_CHANNEL_PATH = 'series/'

CHANNEL_MODE = "channel"
SINGLE_ELEMENT_CHANNEL_MODE = "elementchannel"
# plugin modes
MODE_MOVIES = '10'
MODE_ANIME = '20'
MODE_SHOWS = '30'
MODE_SERIES = '40'

# parameter keys
PARAMETER_KEY_MODE = "mode"


# menu item names
ROOT_LABEL_MOVIES = "Movies"
ROOT_LABEL_ANIME = "Anime"
ROOT_LABEL_SHOWS = "Shows"
ROOT_LABEL_SERIES = "Series"

# episode stream type
F4M_TYPE = '10'
M3U_TYPE = '20'     # .m3u8 is the unicode version of .m3u


def getChannelsPath(type):
    if type == MODE_MOVIES:
        return MOVIE_CHANNELS_PATH
    elif type == MODE_ANIME:
        return ANIME_CHANNELS_PATH
    elif type == MODE_SHOWS:
        return SHOW_CHANNELS_PATH
    elif type == MODE_SERIES:
        return SERIES_CHANNELS_PATH

def getSingleChannelPath(type):
    if type == MODE_MOVIES:
         return MOVIE_SINGLE_CHANNEL_PATH
    elif type == MODE_ANIME:
         return ANIME_SINGLE_CHANNEL_PATH
    elif type == MODE_SHOWS:
         return SHOW_SINGLE_CHANNEL_PATH
    elif type == MODE_SERIES:
         return SERIES_SINGLE_CHANNEL_PATH

def get_section_channels(modeType):
    channelUrl = VVVVID_BASE_URL + getChannelsPath(modeType) 
    response = getJsonDataFromUrl(channelUrl)    
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    channels = data['data']
    listChannels = []
    for channelData in channels:
        filter = ''
        path=''
        listCategory = []
        listFilters = []
        listExtras = []
        if(channelData.has_key('filter')):
            for filter in channelData['filter']:
                listFilters.append(filter)
        if(channelData.has_key('category')):
            for category in channelData['category']:
                channelCategoryElem = ChannelCategory(category['id'],category['name'])
                listCategory.append(channelCategoryElem)
        if(channelData.has_key('extras')):
            for extra in channelData['extras']:
                channelExtrasElem = ChannelExtra(extra['id'],extra['name'])
                listExtras.append(channelExtrasElem)

        channel = Channel(unicode(channelData['id']),channelData['name'],listFilters,listCategory,listExtras) 
        listChannels.append(channel)
    return listChannels

def get_elements_from_channel(idChannel,type,idFilter = '',idCategory = '',idExtra = ''):
    middlePath = getSingleChannelPath(type)
    urlPostFix = '/last/'
    if(idFilter != ''):
        urlPostFix += '?filter=' + idFilter
    elif(idCategory != ''):
        urlPostFix += '?category=' + idCategory
    elif(idExtra != ''):
        urlPostFix +='?extras=' + idExtra
    urlToLoad = VVVVID_BASE_URL+middlePath + str(idChannel) + urlPostFix
    response = getJsonDataFromUrl(urlToLoad)
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    if(data.has_key('data')):
        elements = data['data'];
    else:
        elements = []
    listElements = []
    for elementData in elements:
        elementChannel = ElementChannel(unicode(elementData['id']),unicode(elementData['show_id']),elementData['title'],elementData['thumbnail'],elementData['ondemand_type'],elementData['show_type'])
        listElements.append(elementChannel)
    return listElements

def get_item_playable(idItem):
    urlToLoad = VVVVID_BASE_URL+idItem + '/info'
    response = getJsonDataFromUrl(urlToLoad)
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    info = data['data']
    itemPlayable = ItemPlayableChannel()
    itemPlayable.title = info['title']
    itemPlayable.thumb = info['thumbnail']
    itemPlayable.id = info['id']
    itemPlayable.show_id = info['show_id']
    itemPlayable.ondemand_type = info['ondemand_type']
    itemPlayable.show_type = info['show_type']
    itemPlayable = get_seasons_for_item(itemPlayable)
    return itemPlayable
    
def get_seasons_for_item(itemPlayable):
    urlToLoad = VVVVID_BASE_URL+str(itemPlayable.show_id) + '/seasons'
    response = getJsonDataFromUrl(urlToLoad)
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    result = data['data']
    itemPlayable.seasons = []
    for seasonData in result:
        season = ItemPlayableSeason()
        season.id = seasonData['show_id']
        season.show_id = seasonData ['show_id']
        season.season_id = seasonData['season_id']
        if(seasonData.has_key('name')):
            season.title = seasonData['name']
        else:
            season.title = itemPlayable.title
        urlToLoadSeason = VVVVID_BASE_URL+str(itemPlayable.show_id) + '/season/' + str(season.season_id)
        responseSeason = getJsonDataFromUrl(urlToLoadSeason)
        dataSeason = json.loads(responseSeason.read().decode(responseSeason.info().getparam('charset') or 'utf-8'))
        resultSeason = dataSeason['data']
        listEpisode = []
        for episodeData in resultSeason:
            if(episodeData['video_id'] != '-1'):
                episode = SeasonEpisode()
                episode.show_id = season.show_id
                episode.season_id = season.season_id
                prefix = ''
                postfix= '?g=DRIEGSYPNOBI&hdcore=3.6.0&plugin=aasp-3.6.0.50.41'
                if('http' not in episodeData['embed_info']):
                    episode.stream_type = F4M_TYPE
                    prefix = 'http://wowzaondemand.top-ix.org/videomg/_definst_/mp4:'
                    postfix = '/manifest.f4m'
                if('.m3u' in episodeData['embed_info']):
                    episode.stream_type = M3U_TYPE
                    prefix = ''
                    postfix = ''
                '''
                try:
                    prefix = 'http://194.116.73.48/videomg/_definst_/mp4:'
                    postfix = '/manifest.f4m'
                    episode.stream_type = F4M_TYPE
                    episode.manifest = prefix + ((episodeData['thumbnail'].replace('https://static.vvvvid.it/img/thumbs/','')).replace('-t.jpg','.mp4/'))+postfix
                    urllib2.urlopen(episode.manifest)
                except urllib2.HTTPError, e:
                    try:
                        prefix = 'http://vvvvid-vh.akamaihd.net/z/'
                        postfix = '/manifest.f4m?g=DRIEGSYPNOBI&hdcore=3.6.0&plugin=aasp-3.6.0.50.41'
                        episode.stream_type = F4M_TYPE
                        episode.manifest = prefix + ((episodeData['thumbnail'].replace('https://static.vvvvid.it/img/thumbs/','')).replace('-t.jpg','.mp4/'))+postfix
                        urllib2.urlopen(episode.manifest)
                    except urllib2.HTTPError, e1:
                        postfix = '/manifest.f4m?g=DRIEGSYPNOBI&hdcore=3.6.0&plugin=aasp-3.6.0.50.41'
                        response = request.get('http://vvvvid-vh.akamaihd.net/crossdomain.xml')
                        plugin = Plugin();plugin.log.error("cookie: "+response.text)
                        xbmcgui.Dialog().ok('VVVVID.it','Impossibile riprodurre il flusso video')
                        sys.exit(0)
                '''
                #plugin = Plugin();plugin.log.error('manifest: '+ episode.manifest)
                episode.manifest = prefix +  episodeData['embed_info'] + postfix
                episode.title = ((episodeData['number'] + ' - ' + episodeData['title'])).encode('utf-8','replace')
                episode.thumb = episodeData['thumbnail']
                listEpisode.append(episode)
        season.episodes = listEpisode
        itemPlayable.seasons.append(season)
    return itemPlayable

def getJsonDataFromUrl(customUrl):
    plugin = Plugin()
    data_storage = plugin.get_storage('vvvvid')
    conn_id = data_storage['conn_id']
    #plugin.log.error('customUrl: '+ customUrl)
    customUrl += ('&' if ('?' in customUrl) else '?') +'conn_id='+conn_id
    #plugin.log.error('output:'+ customUrl)
    #req = urllib2.Request(customUrl)
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
    #page = urllib2.urlopen(req);response=page.read();page.close()
    cookie=data_storage['cookie']
    req = urllib2.Request(customUrl)#send the new url with the cookie.
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
    req.add_header('Cookie',cookie)
    response = urllib2.urlopen(req)
    return response
