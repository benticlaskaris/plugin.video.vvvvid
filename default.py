import xbmc, xbmcgui, xbmcaddon, xbmcplugin, re
import urllib, urllib2
import re, string
import threading
import os
import base64
import sys
#from t0mm0.common.addon import Addon
#from t0mm0.common.net import Net
import urlparse
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcgui
import urllib2
import json
from requester import  *

handleAddon = int(sys.argv[1])
global channels
# plugin constants
__plugin__ = "plugin.video.vvvvid"
__author__ = "evilsephiroth"

Addon = xbmcaddon.Addon(id=__plugin__)

global sectionType

# utility functions
def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = dict(urlparse.parse_qsl(parameters[1:]))
    return paramDict

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def addDirectoryItem(name, thumb = '',isFolder=True, parameters={}):
    li = xbmcgui.ListItem(label=name,thumbnailImage=thumb)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    print 'urlforitem'
    print url
    return xbmcplugin.addDirectoryItem(handle=handleAddon, url=url, listitem=li, isFolder=isFolder)

def show_root_menu():
    ''' Show the plugin root menu. '''
    addDirectoryItem(name=ROOT_LABEL_MOVIES, parameters={ PARAMETER_KEY_MODE: MODE_MOVIES }, isFolder=True)
    addDirectoryItem(name=ROOT_LABEL_ANIME, parameters={ PARAMETER_KEY_MODE: MODE_ANIME }, isFolder=True)
    addDirectoryItem(name=ROOT_LABEL_SHOWS, parameters={ PARAMETER_KEY_MODE: MODE_SHOWS }, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handleAddon, succeeded=True)
   
def show_section(type,params):
    print 'show_anime'
    if((params.has_key('filters') and str2bool(params['filters']) == True)):
        channels = get_section_channels(type,True,False)
    elif (params.has_key('categories') and str2bool(params['categories']) == True):
        channels = get_section_channels(type,False,True)
    else:
        channels = get_section_channels(type)
    for channel in channels:
        addDirectoryItem(name=channel.title,isFolder=True,parameters=channel.parameters)
    xbmcplugin.endOfDirectory(handle=handleAddon, succeeded=True)
    
def show_channel_elements(id,path,middle_path,additionalPath):
    print 'show_channel_content'
    channelsElements = get_elements_from_channel(id,path,middle_path,additionalPath) 
    for elem in channelsElements:
        print 'channelparamselem',elem.parameters
        addDirectoryItem(name=elem.title,isFolder=True,thumb=elem.thumb,parameters=elem.parameters)
    xbmcplugin.endOfDirectory(handle=handleAddon, succeeded=True)
    
    
# Depending on the mode, call the appropriate function to build the UI.

REMOTE_DBG = False 

    # append pydev remote debugger
if REMOTE_DBG:
    try:
        sys.path.append("/Users/evilsephiroth/eclipsePython/plugins/org.python.pydev_3.9.2.201502050007/pysrc")
        import pydevd # with the addon script.module.pydevd, only use `import pydevd`
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
         sys.stderr.write("Error: " + "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
         sys.exit(1)
         
params = parameters_string_to_dict(sys.argv[2])
print 'myparams',params
print sys.argv[2]

if not sys.argv[2]:
    # new start
    ok = show_root_menu()  
elif (params.has_key(PARAMETER_KEY_MODE)):
    if params[PARAMETER_KEY_MODE]==CHANNEL_MODE:
        print 'showchannel'
        additionalPath = ''
        if(params.has_key('filterSearch')):
            additionalPath = '?filter=' + params['filterValue']
        elif(params.has_key('categorySearch')):
            additionalPath = '?category=' + params['categoryValue']
        
        show_channel_elements(params['id'],params['type'],params['middle_path'],additionalPath)
    else:
        if params[PARAMETER_KEY_MODE]==MODE_MOVIES:
            ok = show_section(MODE_MOVIES,params)
        elif params[PARAMETER_KEY_MODE]==MODE_ANIME:
            ok = show_section(MODE_ANIME,params)
        elif params[PARAMETER_KEY_MODE]==MODE_SHOWS:
           ok = show_section(MODE_SHOWS,params)

 
