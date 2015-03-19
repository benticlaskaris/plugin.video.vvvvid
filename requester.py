import urllib2
import urlparse
import json
from Channel import *
from ChannelCategory import *
from ElementChannel import *
from _warnings import filters

VVVVID_BASE_URL="http://www.vvvvid.it/vvvvid/ondemand/"
ANIME_CHANNELS_PATH= "anime/channels"
MOVIE_CHANNELS_PATH = "film/channels"
SHOW_CHANNELS_PATH = "show/channels"
ANIME_SINGLE_CHANNEL_PATH = "anime/channel/"
MOVIE_SINGLE_CHANNEL_PATH = "film/channel/"
SHOW_SINGLE_CHANNEL_PATH = "show/channel/"
ANIME_SINGLE_ELEMENT_CHANNEL_PATH = 'anime/'
SHOW_SINGLE_ELEMENT_CHANNEL_PATH = 'show/'
MOVIE_SINGLE_ELEMENT_CHANNEL_PATH = 'film/'

CHANNEL_MODE = "channel"
SINGLE_ELEMENT_CHANNEL_MODE = "elementchannel"
# plugin modes
MODE_MOVIES = '10'
MODE_ANIME = '20'
MODE_SHOWS = '30'

# parameter keys
PARAMETER_KEY_MODE = "mode"


# menu item names
ROOT_LABEL_MOVIES = "Movies"
ROOT_LABEL_ANIME = "Anime"
ROOT_LABEL_SHOWS = "Shows"


def getChannelsPath(type):
    if type == MODE_MOVIES:
        return MOVIE_CHANNELS_PATH
    elif type == MODE_ANIME:
        return ANIME_CHANNELS_PATH
    elif type == MODE_SHOWS:
        return SHOW_CHANNELS_PATH

def getSingleChannelPath(type):
     if type == MODE_MOVIES:
         return MOVIE_SINGLE_CHANNEL_PATH
     elif type == MODE_ANIME:
         return ANIME_SINGLE_CHANNEL_PATH
     elif type == MODE_SHOWS:
         return SHOW_SINGLE_CHANNEL_PATH

def get_section_channels(modeType,filtersSearch = False,categoriesSearch = False):
    channelUrl = getChannelsPath(modeType)
    response = urllib2.urlopen(VVVVID_BASE_URL+channelUrl)
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    print data
    channels = data['data']
    listChannels = []
    for channelData in channels:
        filter = ''
        path=''
        listCategory = []
        listFilters = []
        filters = False
        categories = False
        if(channelData.has_key('filter')):
            for filter in channelData['filter']:
                listFilters.append(filter)
                filters = True
                if(filtersSearch == True):
                    singleChannelPath = getSingleChannelPath(modeType)
                    channel = Channel(channelData['id'],filter,path,channelData['type'],listFilters,listCategory,None) 
                    params = build_params_for_channels(channel.id,channel.type,path,singleChannelPath,None,None,modeType,True,False,filter)
                    channel.parameters= params
                    listChannels.append(channel)
        if(channelData.has_key('path_name')):
            path = channelData['path_name']
        if(channelData.has_key('category')):
            for category in channelData['category']:
                channelCategoryElem = ChannelCategory(category['id'],category['name'])
                listCategory.append(channelCategoryElem)
                categories = True
                if(categoriesSearch == True):
                    singleChannelPath = getSingleChannelPath(modeType)
                    channel = Channel(channelData['id'],channelCategoryElem.name,path,channelData['type'],None,None,None) 
                    params = build_params_for_channels(channel.id,channel.type,path,singleChannelPath,None,None,modeType,False,True,channelCategoryElem.id)
                    channel.parameters = params
                    listChannels.append(channel)
                    
        if(filtersSearch == False and categoriesSearch == False):
            singleChannelPath = getSingleChannelPath(modeType)
            channel = Channel(channelData['id'],channelData['name'],path,channelData['type'],listFilters,listCategory,None) 
            params = build_params_for_channels(channel.id,channel.type,path,singleChannelPath,filters,categories,modeType)
            channel.parameters = params
            listChannels.append(channel)
    return listChannels

def build_params_for_channels(id,type,path,middle_path,filters,categories,globalMode,filterSearch = False,categorySearch = False,idValue = 0):
    params = dict()
    params['id'] = id
    params['type'] = type
    params['path'] = path
    params['mode'] = CHANNEL_MODE
    params['middle_path'] = middle_path
    params['filters'] = filters
    params['categories'] = categories
    if((params.has_key('filters') and params['filters'] == True) or (params.has_key('categories') and params['categories'] == True)):
        params['mode'] = globalMode
    if filterSearch == True:
        params['filterSearch'] = filterSearch
        params['filterValue'] = idValue
    if categorySearch == True:
        params['categorySearch'] = categorySearch
        params['categoryValue'] = idValue
    return params

def build_params_for_channel_element(id,show_id,show_type,middle_path):
    params = dict()
    params['id'] = id
    params['show_id'] = show_id
    params['show_type'] = show_type
    params['mode'] = SINGLE_ELEMENT_CHANNEL_MODE
    params['middle_path'] = middle_path
    return params

def get_elements_from_channel(id,type,middle_path,additionalPath):
    response = urllib2.urlopen(VVVVID_BASE_URL+middle_path + id + additionalPath)
    data = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
    print data
    elements = data['data']
    listElements = []
    for elementData in elements:
        elementChannel = ElementChannel(elementData['id'],elementData['show_id'],elementData['title'],elementData['thumbnail'],elementData['ondemand_type'],elementData['show_type'])
        params = build_params_for_channel_element(elementChannel.id,elementChannel.show_id,elementChannel.show_type,ANIME_SINGLE_ELEMENT_CHANNEL_PATH)
        elementChannel.parameters = params
        listElements.append(elementChannel)
    return listElements