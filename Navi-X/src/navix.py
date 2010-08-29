#############################################################################
#
# Navi-X Playlist browser
# v3.4.1 by rodejo (rodejo16@gmail.com)
#
# -v1.01  (2007/04/01) first release
# -v1.2   (2007/05/10)
# -v1.21  (2007/05/20)
# -v1.22  (2007/05/26)
# -v1.3   (2007/06/15)
# -v1.31  (2007/06/30)
# -v1.4   (2007/07/04)
# -v1.4.1 (2007/07/21)
# -v1.5   (2007/09/14)
# -v1.5.1 (2007/09/17)
# -v1.5.2 (2007/09/22)
# -v1.6   (2007/09/29)
# -v1.6.1 (2007/10/19)
# -v1.7 beta (2007/11/14)
# -v1.7   (2007/11/xx)
# -v1.7.1 (2007/12/15)
# -v1.7.2 (2007/12/20)
# -v1.8 (2007/12/31)
# -v1.9 (2008/02/10)
# -v1.9.1 (2008/02/10)
# -v1.9.2 (2008/02/23)
# -v1.9.3 (2008/06/20)
# -v2.0   (2008/07/21)
# -v2.1   (2008/08/08)
# -v2.2   (2008/08/31)
# -v2.3   (2008/10/18)
# -v2.4   (2008/12/04)
# -v2.5   (2009/01/24)
# -v2.6   (2009/03/21)
# -v2.7   (2009/04/11)
# -v2.8   (2009/05/09)
# -v2.8.1 (2009/05/21)
# -v2.9   (2009/06/13)
# -v2.9.2 (2009/08/07)
# -v2.9.3 (2009/08/14)
# -v2.9.4 (2009/09/01)
# -v3.0 RC  (2009/10/03)
# -v3.0  (2009/11/08)
# -v3.0.1  (2009/11/14)
# -v3.0.2  (2009/12/20)
# -v3.1beta  (2009/12/30)
# -v3.1     (2010/01/16)
# -v3.1.1 (2010/02/07)
# -v3.1.2 (2010/03/27)
# -v3.2 (2010/04/01)
# -v3.3 (2010/05/31)
# -v3.4 (2010/07/04)
# -v3.4.1 (2010/07/23)
# -v3.4.2 (2010/07/27)
# -v3.4.3 (2010/08/28)
#
#todo: Dharma XML update
#############################################################################

from string import *
import sys, os.path
import urllib
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
import copy

sys.path.append(os.path.join(os.getcwd().replace(";",""),'src'))
from libs2 import *
from settings import *
from CPlayList import *
from CFileLoader import *
from CURLLoader import *
from CDownLoader import *
from CPlayer import *
from CDialogBrowse import *
from CTextView import *
from CInstaller import *
from skin import *
from CBackgroundLoader import *
from CServer import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

######################################################################
# Description: Main Window class
######################################################################
class MainWindow(xbmcgui.WindowXML):       
        def __init__(self,strXMLname, strFallbackPath):#, strDefaultName, forceFallback):
        
            self.delFiles(tempCacheDir) #clear the temp cache first            
            self.delFiles(imageViewCacheDir) #clear the image view cache first           

            #Create default DIRs if not existing.
            if not os.path.exists(cacheDir): 
                os.mkdir(cacheDir)
            if not os.path.exists(imageCacheDir): 
                os.mkdir(imageCacheDir)
            if not os.path.exists(tempCacheDir): 
                os.mkdir(tempCacheDir)                   
            if not os.path.exists(myDownloadsDir): 
                os.mkdir(myDownloadsDir)

            #Create playlist object contains the parsed playlist data. The self.list control displays
            #the content of this list
            self.playlist = CPlayList()
            #Create favorite object contains the parsed favorite data. The self.favorites control displays
            #the content of this list
            self.favoritelist = CPlayList()
            #fill the playlist with favorite data
            result = self.favoritelist.load_plx(favorite_file)
            if result != 0:
                shutil.copyfile(initDir+favorite_file, RootDir+favorite_file)
                self.favoritelist.load_plx(favorite_file)

            self.downloadslist = CPlayList()
            #fill the playlist with downloads data
            result = self.downloadslist.load_plx(downloads_complete)
            if result != 0:
                shutil.copyfile(initDir+downloads_complete, RootDir+downloads_complete)
                self.downloadslist.load_plx(downloads_complete)

            self.downloadqueue = CPlayList()
            #fill the playlist with downloads data
            result = self.downloadqueue.load_plx(downloads_queue)
            if result != 0:
                shutil.copyfile(initDir+downloads_queue, RootDir+downloads_queue)
                self.downloadqueue.load_plx(downloads_queue)
                
            self.parentlist = CPlayList()
            #fill the playlist with downloads data
            result = self.parentlist.load_plx(parent_list)
            if result != 0:
                shutil.copyfile(initDir+parent_list, RootDir+parent_list)
                self.parentlist.load_plx(parent_list)                
            
            self.history = CPlayList()
            #fill the playlist with history data
            result = self.history.load_plx(history_list)
            if result != 0:
                shutil.copyfile(initDir+history_list, RootDir+history_list)
                self.history.load_plx(history_list) 
              
            #check if My Playlists exists, otherwise copy it from the init dir
            if not os.path.exists(myPlaylistsDir + "My Playlists.plx"): 
                shutil.copyfile(initDir+"My Playlists.plx", myPlaylistsDir+"My Playlists.plx")

            #check if My Playlists exists, otherwise copy it from the init dir
            if not os.path.exists(myPlaylistsDir + "My Playlists.plx"): 
                shutil.copyfile(initDir+"My Playlists.plx", myPlaylistsDir+"My Playlists.plx")
            
            #Set the socket timeout.
            socket_setdefaulttimeout(url_open_timeout)
             
            #Next a number of class private variables
            self.home=home_URL
            self.dwnlddir=myDownloadsDir
            self.History = [] #contains the browse history
            self.history_count = 0 #number of entries in history array
            self.background = 0 #background image
            self.userthumb = '' #user thumb image
            self.state_busy = 0 # key handling busy state
            self.state2_busy = 0 # logo update busy state
            self.URL='http://'
            self.type=''
            #default player will be DVD player
            self.player_core=xbmc.PLAYER_CORE_DVDPLAYER
            self.pl_focus = self.playlist
            self.downlshutdown = False # shutdown after download flag
            self.mediaitem = 0
            self.thumb_visible = False # true if thumb shall be displayed
            self.vieworder = 'ascending' #ascending
            self.SearchHistory = [] #contains the search history
            self.background = '' #current background image
            self.password = "" #parental control password.
            self.hideblocked = "" #parental control hide blocked content
            self.access = False #parental control access.
            self.mediaitem_cutpaste = 0 # selected item for cut/paste
            self.page = 0 #selected page
            self.descr_view = False
                        
            #read the non volatile settings from the settings.dat file
            self.onReadSettings()
            
            #read the search history from the search.dat file
            self.onReadSearchHistory()
 
            #check if the home playlist points to the old website. If true then update the home URL.
            if self.home == home_URL_old:
                self.home = home_URL

            self.firsttime = False
                                    
            #xbmc.executebuiltin("xbmc.ActivateWindow(VideoOverlay)")
    
            #end of function

        ######################################################################
        # Description: class xbmcgui default member function.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onInit( self ):
            if self.firsttime == True:
                return
            
            self.firsttime = True
        
            load_skin(self)
            
            if nxserver.is_user_logged_in() == True:
                self.list3.getListItem(4).setLabel("Sign out")
                self.version.setLabel('version: '+ Version + '.' + SubVersion + " (signed in)")
                                  
            #thumb update task
            self.bkgndloadertask = CBackgroundLoader(window=self)
            self.bkgndloadertask.start()
            
            #background download task
            self.downloader = CDownLoader(window=self, playlist_src=self.downloadqueue, playlist_dst=self.downloadslist)
            self.downloader.start()

            #Configure the info text control
            SetInfoText(window=self.infotekst)

            #check if there is a startup playlist
            result=-1
            if os.path.exists(RootDir + "startup.plx"):               
                #yes there is a startup script, load it and use the first entry in the list.
                startuplist = CPlayList()
                result = startuplist.load_plx(RootDir + "startup.plx")
                os.remove(RootDir + "startup.plx")
                if result == 0:
                    result = self.ParsePlaylist(mediaitem=startuplist.list[0]) #always use the first playlist item
            
            if result != 0: 
                #there is no startup playlist, load the Navi-X home page
                result = self.ParsePlaylist(URL=self.home)
                if result != 0: #failed
                    self.ParsePlaylist(URL=home_URL_mirror) #mirror site              

            #end of function
             
        ######################################################################
        # Description: class xbmcgui default member function..
        # Parameters : action=user action
        # Return     : -
        ######################################################################
        def onAction(self, action):
            #select item is handled via other onClick().
            if not action.getId() == ACTION_SELECT_ITEM:
                self.onAction1(action)
            
            #end of function

        ######################################################################
        # Description: class xbmcgui default member function.
        # Parameters : action=user action
        # Return     : -
        ######################################################################        
        def onAction1(self, action):
            self.state_action = 1                          
                    
            #always allow Exit even if busy
            if (action == ACTION_SELECT_ITEM) and (self.getFocus() == self.list3):
                pos = self.list3.getSelectedPosition()
                if pos == 5:
                    self.setInfoText("Shutting Down Navi-X...") 
                    self.onSaveSettings()
                    self.bkgndloadertask.kill()
                    self.bkgndloadertask.join(10) #timeout after 10 seconds.
                    self.downloader.kill()
                    self.downloader.join(10) #timeout after 10 seconds.
                    self.close() #exit            
             
            if self.state_busy == 0:
                if action == ACTION_SELECT_ITEM:
                    #main list
                    if self.getFocus() == self.list:
                        #if self.URL == favorite_file:
                        if self.pl_focus == self.favoritelist:
                            self.onSelectFavorites()
                        elif (self.URL == downloads_file) or (self.URL == downloads_queue) or \
                              (self.URL == downloads_complete) or (self.URL == parent_list):
                            self.onSelectDownloads()
                        else:
                            pos = self.list.getSelectedPosition()
                            if pos >= 0:
                                self.SelectItem(self.playlist, pos)
                    #button option
                    if self.getFocus() == self.list3:
                        #Left side option menu
                        pos = self.list3.getSelectedPosition()
                        if pos == 0:
                            self.pl_focus = self.playlist
                            self.ParsePlaylist(URL=self.home)                            
                        elif pos == 1:
                            self.onOpenFavorites()
                        elif pos == 2:
                            self.onOpenDownloads()                      
                        elif pos == 3:
                            self.setFocus(self.list)
                            self.onSelectURL() 
#                        elif pos == 4:
#                            self.setInfoText("Shutting Down Navi-X...") 
#                            self.onSaveSettings()
#                            self.bkgndloadertask.kill()
#                            self.bkgndloadertask.join(10) #timeout after 10 seconds.
#                            self.downloader.kill()
#                            self.downloader.join(10) #timeout after 10 seconds.
#                            self.close() #exit
                        elif pos == 4: #sign in
                            self.setFocus(self.list)
                            if nxserver.is_user_logged_in() == False:           
                                result = nxserver.login()
                                if result == 0:
                                    dialog = xbmcgui.Dialog()                            
                                    dialog.ok(" Sign in", "Sign in Successful.")
                                    self.list3.getListItem(4).setLabel("Sign out")
                                    self.version.setLabel('version: '+ Version + '.' + SubVersion + " (signed in)")
                                elif result == -1:
                                    dialog = xbmcgui.Dialog()                            
                                    dialog.ok(" Sign in", "Sign in failed.")
                            else: #sign out
                                #user already logged in
                                dialog = xbmcgui.Dialog() 
                                if dialog.yesno("Message", "Sign out?") == True:
                                    nxserver.logout()
                                    self.list3.getListItem(4).setLabel("Sign in")
                                    dialog = xbmcgui.Dialog()                            
                                    dialog.ok(" Sign out", "Sign out successful.")
                                    self.version.setLabel('version: '+ Version + '.' + SubVersion)                              
                    if self.getFocus() == self.list4:
                        #Right side option menu
                        pos = self.list4.getSelectedPosition()
                        if self.descr_view == True:
                            #self.setFocus(self.list3tb)
                            self.setFocus(self.getControl(128))
                        else:
                            self.setFocus(self.list)
                        if pos == 0:
                            pos = self.list.getSelectedPosition()
                            if self.pl_focus.list[pos].rating == 'disabled':
                                dialog = xbmcgui.Dialog()                            
                                dialog.ok(" Error", "Not supported.")                      
                            elif self.pl_focus.URL.find(nxserver_URL) != -1:
                                nxserver.rate_item(self.pl_focus.list[pos])
                                self.UpdateRateingImage()
                            else:
                                dialog = xbmcgui.Dialog()                            
                                dialog.ok(" Error", "Only Navi-Xtreme playlists can be rated.")
                        elif pos == 1:
                            if self.URL == favorite_file:
                                self.selectBoxFavoriteList()
                            elif  (self.URL == downloads_file) or (self.URL == downloads_queue) or \
                                   (self.URL == downloads_complete) or (self.URL == parent_list):
                                self.selectBoxDownloadsList()
                            else:   
                                self.selectBoxMainList()                            

                elif (action == ACTION_PARENT_DIR) or (action == ACTION_PREVIOUS_MENU):
                    if self.descr_view == True:
                        self.list3tb.setVisible(0)                    
                        self.list.setVisible(1)
                        self.setFocus(self.list)
                        self.descr_view = False      
                    elif self.pl_focus == self.favoritelist:
                        self.onCloseFavorites()
                    elif (self.URL == downloads_queue) or (self.URL == downloads_complete) or (self.URL == parent_list):    
                        self.onCloseDownloads()
                    else:
                        #main list
                        if self.history_count > 0:
                            previous = self.History[len(self.History)-1]
                            result = self.ParsePlaylist(mediaitem=previous.mediaitem, start_index=previous.index, proxy="ENABLED")
                            if result == 0: #success
                                flush = self.History.pop()
                                self.history_count = self.history_count - 1
                        else:
                            self.setFocus(self.list3)
                elif action == ACTION_YBUTTON:
                    self.onPlayUsing()
                elif action == ACTION_MOVE_RIGHT:
                    if self.getFocus() == self.list:
                        result = self.onShowDescription()
                        if result != 0:
                            #No description available
                            self.setFocus(self.list4)
                    elif self.descr_view == False:
                            self.setFocus(self.list)
                elif action == ACTION_MOVE_LEFT:
                    if self.descr_view == True:
                        self.list3tb.setVisible(0)                    
                        self.list.setVisible(1)
                        self.setFocus(self.list)
                        self.descr_view = False
                    elif self.getFocus() == self.list:
                        self.setFocus(self.list3)
                    else:
                        self.setFocus(self.list)
                elif action == ACTION_MOVE_UP:
                    pos = self.list.getSelectedPosition()
                elif action == ACTION_MOUSEMOVE:
                    xpos = action.getAmount1()
                    ypos = action.getAmount2()
                    if (xpos < 20) and (ypos > 140):
                        self.setFocus(self.list3)
                    #elif (xpos > 500) and (ypos > 140):
                    #    self.setFocus(self.list4)                    
                elif self.ChkContextMenu(action) == True: #White
                    if self.URL == favorite_file:
                        self.selectBoxFavoriteList()
                    elif  (self.URL == downloads_file) or (self.URL == downloads_queue) or \
                           (self.URL == downloads_complete) or (self.URL == parent_list):
                        self.selectBoxDownloadsList()
                    else:
                        self.selectBoxMainList()
                
                #update index number    
                pos = self.getPlaylistPosition()
                if pos >= 0:
                    self.listpos.setLabel(str(pos+1) + '/' + str(self.pl_focus.size()))
                    
                #self.UpdateRateingImage()

                #self.DisplayMediaSource()
                        
            #end of function
             
        ######################################################################
        # Description: class xbmcgui default member function.
        # Parameters : TBD
        # Return     : TBD
        ######################################################################    
        def onFocus( self, controlId ):
            pass

        ######################################################################
        # Description: class xbmcgui default member function.
        # Parameters : TBD
        # Return     : TBD
        ######################################################################
        def onClick( self, controlId ):
            if controlId == BUTTON_LEFT:          
                self.onAction1(ACTION_PREVIOUS_MENU)
            else:
                self.onAction1(ACTION_SELECT_ITEM)       

        ######################################################################
        # Description: Sets the rating image.
        # Parameters : -
        # Return     : -
        ######################################################################        
        def UpdateRateingImage(self):
            pos = self.getPlaylistPosition()
            
            if pos >= 0:
                rating = self.pl_focus.list[pos].rating
                if rating != '':
                    self.rating.setImage('rating' + rating + '.png')
                    self.rating.setVisible(1)
                else:
                    self.rating.setVisible(0)
                    
        ######################################################################
        # Description: Display the media source for processor based entries.
        # Parameters : -
        # Return     : -
        ######################################################################        
        def DisplayMediaSource(self):
            pos = self.getPlaylistPosition()

            if pos >= 0:
                #Display media source
                str_url=self.pl_focus.list[pos].URL;
                str_server_report=""
                if str_url != "" and self.pl_focus.list[pos].type != "playlist":
                    match=re_server.search(str_url)
                    if match:
                        str_server_report="Source: " + match.group(1)
                        if self.pl_focus.list[pos].processor != "":
                            str_server_report = str_server_report + "+"
                SetInfoText(str_server_report)                                                  
    
        ######################################################################
        # Description: Checks if one of the context menu keys is pressed.
        # Parameters : action=handle to UI control
        # Return     : True if valid context menu key is pressed.
        ######################################################################
        def ChkContextMenu(self, action):
            result = False
               
            #Support for different remote controls.
        
            if action == 261:
                result = True
            elif action == ACTION_CONTEXT_MENU:
                result = True
            elif action == ACTION_CONTEXT_MENU2:
                result = True
            
            return result

        ######################################################################
        # Description: class xbmcgui default member function.
        # Parameters : control=handle to UI control
        # Return     : -
        ######################################################################
        def onControl(self, control):
            pass           
                                                          
        ######################################################################
        # Description: Parse playlist file. Playlist file can be a:
        #              -PLX file;
        #              -RSS v2.0 file (e.g. podcasts);
        #              -RSS daily Flick file (XML1.0);
        #              -html Youtube file;
        # Parameters : URL (optional) =URL of the playlist file.
        #              mediaitem (optional)=Playlist mediaitem containing 
        #              playlist info. Replaces URL parameter.
        #              start_index (optional) = cursor position after loading 
        #              playlist.
        #              reload (optional)= indicates if the playlist shall be 
        #              reloaded or only displayed.
        #              proxy = proxy to use for loading
        # Return     : 0 on success, -1 if failed.
        ######################################################################
        def ParsePlaylist(self, URL='', mediaitem=CMediaItem(), start_index=0, reload=True, proxy="CACHING"):
            #avoid recursive call of this function by setting state to busy.
            self.state_busy = 1

            #The application contains 4 CPlayList objects:
            #(1)main list, 
            #(2)favorites,
            #(3)download queue
            #(4)download completed list
            #Parameter 'self.pl_focus' points to the playlist in focus (1-4).
            playlist = self.pl_focus

            #The application contains one xbmcgui list control which displays 
            #the playlist in focus. 
            listcontrol = self.list

            listcontrol.setVisible(0)
            self.list2tb.setVisible(0)
            
            self.loading.setLabel("Please wait...")
            self.loading.setVisible(1)
                        
            #type = mediaitem.type
            type = mediaitem.GetType()
            if reload == True:
                #load the playlist
                if type == 'rss_flickr_daily':
                    result = playlist.load_rss_flickr_daily(URL, mediaitem, proxy)                
                elif type[0:3] == 'rss':
                    result = playlist.load_rss_20(URL, mediaitem, proxy)
                elif type[0:4] == 'atom':
                    result = playlist.load_atom_10(URL, mediaitem, proxy)
                elif type == 'html_youtube':
                    result = playlist.load_html_youtube(URL, mediaitem, proxy)
                elif type == 'xml_shoutcast':
                    result = playlist.load_xml_shoutcast(URL, mediaitem, proxy)
                elif type == 'xml_applemovie':
                    result = playlist.load_xml_applemovie(URL, mediaitem, proxy)
                elif type == 'directory':
                    result = playlist.load_dir(URL, mediaitem, proxy)
                else: #assume playlist file
                    result = playlist.load_plx(URL, mediaitem, proxy)
                
                if result == -1: #error
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "This playlist requires a newer Navi-X version")
                elif result == -2: #error
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Cannot open file.")
                
                if result != 0: #failure
                    self.loading.setVisible(0)
                    listcontrol.setVisible(1)
                    self.setFocus(listcontrol)
                    self.state_busy = 0            
                    return -1
            
            #succesful
#the next line is for used for debugging only            
#            playlist.save(RootDir + 'source.plx')
            
            #loading finished, display the list
            self.loading.setLabel("Please wait......")
            
            self.vieworder = 'ascending' #ascending by default
        
            if start_index == 0: 
                start_index = playlist.start_index
        
            self.URL = playlist.URL
            self.type = type
            if URL != '':
                mediaitem.URL = URL
            self.mediaitem = mediaitem
                        
            #display the new URL on top of the screen
            if len(playlist.title) > 0:
                title = playlist.title  + ' - (' + playlist.URL + ')'
            else:
                title = playlist.URL
            self.urllbl.setLabel(title)

            #set the background image
#always reload background image when loading playlist            
            m = self.playlist.background
            if m == 'default': #default BG image
                self.bg.setImage(imageDir + background_image1)
                self.bg1.setImage(imageDir + background_image2)
                self.background = m
            elif m != 'previous': #URL to image located elsewhere
                ext = getFileExtension(m)
                loader = CFileLoader2() #file loader
                #loader.load(m, imageCacheDir + "background." + ext, timeout=2, proxy="ENABLED", content_type='image')
                loader.load(m, imageCacheDir + "background." + ext, proxy="ENABLED", content_type='image')
                if loader.state == 0:
                    self.bg.setImage(loader.localfile)
                    self.bg1.setImage(imageDir + background_image2)
#                self.background = m                               
            
            if playlist.description != "":
                self.list = self.list2
                listcontrol = self.list2
            else:
                self.list = self.list1
                listcontrol = self.list1

            self.list2tb.controlDown(self.list)
            self.list2tb.controlUp(self.list)
            
            #filter the playlist for parental control.
            self.FilterPlaylist()
            
            #Display the playlist page
            self.SelectPage(start_index / page_size, start_index % page_size)           
            
            self.loading.setVisible(0)
            listcontrol.setVisible(1)
            
#            self.setFocus(listcontrol)

#            pos = self.list.getSelectedPosition()
#            self.listpos.setLabel(str(pos+1) + '/' + str(self.playlist.size()))
                 
            if playlist.description != '':
                self.list2tb.reset()
                self.list2tb.setText(playlist.description)
                self.list2tb.setVisible(1)      
           
            self.state_busy = 0
            
            return 0 #success

        ######################################################################
        # Description: Large playlists are splitup into pages to improve
        # performance. This function select one of the playlist pages. The
        # playlist size is defined by setting variable 'page_size'.
        # Parameters : page = page to display
        #              start_pos: cursor start position
        # Return     : -
        ######################################################################
        def SelectPage(self, page=0, start_pos=0):
            self.state_busy = 1 
            
            playlist = self.pl_focus
            listcontrol = self.list
            self.page = page

            listcontrol.setVisible(0)           
            self.loading.setLabel("Please wait......")
            self.loading.setVisible(1)

            listcontrol.reset() #clear the list control view

            if page > 0:
                item = xbmcgui.ListItem("<<<") #previous page item
                listcontrol.addItem(item)   
                start_pos = start_pos + 1

            today=datetime.date.today()
            n=0
            for i in range(page*page_size, playlist.size()):
                m = playlist.list[i]         
                if int(m.version) <= int(plxVersion):
                    thumb = self.getPlEntryThumb(m)
                    
                    label2=''
                    if m.date != '':
                        l=m.date.split('-')
                        
                        try:
                            entry_date = datetime.date(int(l[0]), int(l[1]), int(l[2]))

                            days_past = (today-entry_date).days
                            if days_past <= 10:
                                if days_past <= 0:
                                    label2 = 'NEW today'
                                elif days_past == 1:
                                    label2 = 'NEW yesterday'
                                else:
                                    label2 = 'NEW ('+ str(days_past) + ' days ago)'
                        except:
                            print "ERROR: Playlist contains invalid date at entry:  %d" %(n+1)
                            
                    if m.description != '':
                        label2 = label2 + ' >'
                      
                    item = xbmcgui.ListItem(unicode(m.name, "utf-8", "ignore" ), label2 ,"", thumb)
                    #item.setInfo( type="pictures", infoLabels={ "Title": m.name } )
                    listcontrol.addItem(item)   
                    
                    n=n+1
                    if n >= page_size:
                        break #m

            if ((page+1)*page_size < playlist.size()): #next page item
                item = xbmcgui.ListItem(">>>")
                listcontrol.addItem(item)   
                
            self.loading.setVisible(0)
            listcontrol.setVisible(1) 
            self.setFocus(listcontrol)

            pos = self.getPlaylistPosition()
            self.listpos.setLabel(str(pos+1) + '/' + str(self.pl_focus.size()))              

            listcontrol.selectItem(start_pos)      

            self.state_busy = 0            

        ######################################################################
        # Description: Filter playlist for parental control.
        # Parameters : -
        # Return     : -
        ######################################################################
        def FilterPlaylist(self):
            i=0
            while i < self.pl_focus.size():
            #for i in range(self.pl_focus.size()):
                m = self.pl_focus.list[i]        
                for p in self.parentlist.list:
                    if p.URL == m.URL:
                        #entry found in blocked list
                        if self.access == False:
                            if self.hideblocked == "Hided":
                                self.pl_focus.remove(i)
                                i = i - 1
                            else:
                                m.icon = imageDir+'lock-icon.png'
                        else: #access allowed
                            m.icon = imageDir+'unlock-icon.png'
                        break
                i = i + 1

        ######################################################################
        # Description: Gets the playlist entry thumb image for different types
        # Parameters : mediaitem: item for which to retrieve the thumb
        # Return     : thumb image (local) file name
        ######################################################################
        def getPlEntryThumb(self, mediaitem):            
            type = mediaitem.GetType()       
        
            #some types are overruled.
            if type[0:3] == 'rss':
                type = 'rss'
            elif type[0:4] == 'atom':
                type = 'rss'
            elif type[0:3] == 'xml':
                type = 'playlist'
            elif type == 'html_youtube':
                type = 'playlist'
            elif type[0:6] == 'search':
                type = 'search'               
            elif type == 'directory':
                type = 'playlist'
            elif type == 'window':
                type = 'playlist'             
            elif mediaitem.type == 'skin':
                type = 'script'                
    
            #we now know the image type. Check the playlist specific icon is set
            URL=''
            if type == 'playlist':
                if self.pl_focus.icon_playlist != 'default':
                    URL = self.pl_focus.icon_playlist
            elif type == 'rss':
                if self.pl_focus.icon_rss != 'default':
                    URL = self.pl_focus.icon_rss
            elif type == 'script':
                if self.pl_focus.icon_script != 'default':
                    URL = self.pl_focus.icon_script
            elif type == 'plugin':
                if self.pl_focus.icon_plugin != 'default':
                    URL = self.pl_focus.icon_plugin                    
            elif type == 'video':
                if self.pl_focus.icon_video != 'default':
                    URL = self.pl_focus.icon_video
            elif type == 'audio':
                if self.pl_focus.icon_audio != 'default':
                    URL = self.pl_focus.icon_audio
            elif type == 'image':
                if self.pl_focus.icon_image != 'default':
                    URL = self.pl_focus.icon_image
            elif type == 'text':
                if self.pl_focus.icon_text != 'default':
                    URL = self.pl_focus.icon_text
            elif type == 'search':
                if self.pl_focus.icon_search != 'default':
                    URL = self.pl_focus.icon_search
            elif type == 'download':
                if self.pl_focus.icon_download != 'default':
                    URL = self.pl_focus.icon_download

            #if the icon attribute has been set then use this for the icon.
            if mediaitem.icon != 'default':
                URL = mediaitem.icon

            if URL != '':
                ext = getFileExtension(URL)
                loader = CFileLoader2() #file loader
                loader.load(URL, imageCacheDir + "icon." + ext, timeout=2, proxy="ENABLED", content_type='image')
                if loader.state == 0:
                    return loader.localfile
            
            return imageDir+'icon_'+str(type)+'.png'
           
        ######################################################################
        # Description: Handles the selection of an item in the list.
        # Parameters : -
        # Return     : -
        ######################################################################  
        def getPlaylistPosition(self):
            pos = self.list.getSelectedPosition()
            
            if (self.page > 0):
                pos = pos + (self.page*page_size) - 1
            
            return pos
              
        ######################################################################
        # Description: Handles the selection of an item in the list.
        # Parameters : playlist(optional)=the source playlist;
        #              pos(optional)=media item position in the playlist;
        #              append(optional)=true is playlist must be added to 
        #              history list;
        #              URL(optional)=link to media file;
        # Return     : -
        ######################################################################
        def SelectItem(self, playlist=0, pos=0, append=True, iURL=''):
            if pos >= page_size: #next page
                self.page = self.page + 1
                self.SelectPage(page=self.page)
                return
            elif (self.page > 0):
                if pos == 0:
                    self.page = self.page - 1
                    self.SelectPage(page=self.page)
                    return
                else:
                    pos = (self.page*page_size) + pos - 1
        
            if iURL != '':
                mediaitem=CMediaItem()
                mediaitem.URL = iURL
                ext = getFileExtension(iURL)
                if ext == 'plx':
                    mediaitem.type = 'playlist'
                elif ext == 'xml' or ext == 'atom':
                    mediaitem.type = 'rss'        
                elif ext == 'jpg' or ext == 'png' or ext == 'gif':
                    mediaitem.type = 'image'
                elif ext == 'txt':
                    mediaitem.type == 'text'
                elif ext == 'zip':
                    mediaitem.type == 'script'
                else:
                    mediaitem.type = 'video' #same as audio
            else:
                if playlist.size() == 0:
                    #playlist is empty
                    return
               
                mediaitem = playlist.list[pos]
               
            #check if playlist item is on located in the blacklist
            if self.access == False:
                for m in self.parentlist.list:
                    if m.URL == mediaitem.URL:
                        if self.verifyPassword() == False:
                            return                    
            
            self.state_busy = 1                
            
            #type = mediaitem.type
            type = mediaitem.GetType()
            
            if type == 'playlist' or type == 'favorite' or type[0:3] == 'rss' or \
               type == 'rss_flickr_daily' or type == 'directory' or \
               type == 'html_youtube' or type == 'xml_shoutcast' or \
               type == 'xml_applemovie' or type == 'atom':
                #add new URL to the history array
                tmp = CHistorytem() #new history item
                #tmp.index = self.list.getSelectedPosition()
                tmp.index = pos
                tmp.mediaitem = self.mediaitem

                #exception case: Do not add Youtube pages to history list
                if self.mediaitem.GetType() == 'html_youtube':
                    append = False
                        
                self.pl_focus = self.playlist #switch back to main list
                result = self.ParsePlaylist(mediaitem=mediaitem)
                
                if result == 0 and append == True: #successful
                    self.History.append(tmp)
                    self.history_count = self.history_count + 1

            elif type == 'video' or type == 'audio' or type == 'html':
#these lines are used for debugging only
#                self.onDownload()
#                self.state_busy = 0
#                self.selectBoxMainList()
#                self.state_busy = 0                
#                return

                self.AddHistoryItem()

                self.setInfoText("Loading... ") #loading text

                if (playlist != 0) and (playlist.playmode == 'autonext'):
                    size = playlist.size()
                    if playlist.player == 'mplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                    elif playlist.player == 'dvdplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                    else:
                        MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)                
                    result = MyPlayer.play(playlist, pos, size-1)
                else:
                    if mediaitem.player == 'mplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                    elif mediaitem.player == 'dvdplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                    else:
                        MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)

                    result = MyPlayer.play_URL(mediaitem.URL, mediaitem)
                                                        
                self.setInfoText(visible=0)
                
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Cannot open file.")

            elif type == 'image':
                self.AddHistoryItem()
                self.viewImage(playlist, pos, 0, mediaitem.URL) #single file show
            elif type == 'text':
                self.AddHistoryItem()
                self.OpenTextFile(mediaitem=mediaitem)
            #elif (type[0:6] == 'script') or (type[0:6] == 'plugin') or (type == 'skin'):
            elif (type == 'script') or (type == 'plugin') or (type == 'skin'):
                self.AddHistoryItem()
                self.InstallApp(mediaitem=mediaitem)
            elif type == 'download':
                self.AddHistoryItem()
                self.onDownload()
            elif (type[0:6] == 'search'):
                self.AddHistoryItem()
                self.PlaylistSearch(mediaitem, append)
            elif type == 'window':
                xbmc.executebuiltin("xbmc.ActivateWindow(" + mediaitem.URL + ")")                
#            elif type == 'html':
#                #at this moment we do nothing with HTML files
#                pass
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Playlist format error", '"' + type + '"' + " is not a valid type.")
                
            self.state_busy = 0

        
        ######################################################################
        # Description: Add item to history
        # Parameters : -
        # Return     : -
        ######################################################################
        def AddHistoryItem(self):
            #the current playlist has no name, so don't add it.
            if self.mediaitem.name == '':
                return
        
            for i in range(self.history.size()):
                item = self.history.list[i]
                if item.URL == self.mediaitem.URL:
                    #object already in the list, remove existing entry
                    self.history.remove(i)
                    break
        
            item = copy.copy(self.mediaitem)
            if self.pl_focus.logo != 'none':
                item.thumb = self.pl_focus.logo
            item.background = self.pl_focus.background
            
            self.history.insert(item,0)
            
            if self.history.size() > history_size:
                self.history.remove(self.history.size()-1)
            
            self.history.save(RootDir + history_list)

        ######################################################################
        # Description: Player changed info can be catched here
        # Parameters : state=New XBMC player state
        # Return     : -
        ######################################################################
        def myPlayerChanged(self, state):
            #At this moment nothing to handle.
            pass

        ######################################################################
        # Description: view HTML page.
        # Parameters : URL: URL to the page.
        # Return     : -
        ######################################################################
        def viewHTML(self, URL):
            #At this moment we do not support HTML display.
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "HTML is not supported.")

        ######################################################################
        # Description: Handles the player selection menu which allows the user
        #              to select the player core to use for playback.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onPlayUsing(self):
            pos = self.getPlaylistPosition()
            if pos < 0: #invalid position
                return
               
            mediaitem = self.pl_focus.list[pos]
            URL = self.pl_focus.list[pos].URL
            autonext = False

            #check if the cursor is on a image
            if mediaitem.type == 'image':
                self.viewImage(self.pl_focus, pos, 1) #slide show show
                return
                     
            #not on an image, check if video or audio file
            if (mediaitem.type != 'video') and (mediaitem.type != 'audio'):
                return

            possibleChoices = ["Default Player", \
                               "Default Player (Auto Next)", \
                               "DVD Player", \
                               "DVD Player (Auto Next)", \
                               "MPlayer", \
                               "MPlayer (Auto Next)", \
                               "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Play...", possibleChoices)
            
            if (choice != -1) and (choice < 6): #if not cancel
                result = 0            
                if (choice == 0) or (choice == 1):
                    if mediaitem.player == 'mplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                    elif mediaitem.player == 'dvdplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                    else:
                        MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)                
                elif (choice == 2) or (choice == 3):
                    MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                elif (choice == 4) or (choice == 5):
                    MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)

                if (choice == 1) or (choice == 3) or (choice == 5):
                    autonext = True

                self.setInfoText("Loading...") 
                if autonext == False:
                    result = MyPlayer.play_URL(URL, mediaitem) 
                else:
                    size = self.pl_focus.size()
                    #play from current position to end of list.
                    result = MyPlayer.play(self.pl_focus, pos, size-1)                    
                self.setInfoText(visible=0)
                
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Cannot open file.")

        ######################################################################
        # Description: Handles the player selection menu which allows the user
        #              to select the player core to use for playback.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSetDefaultPlayer(self):
            if self.player_core == xbmc.PLAYER_CORE_AUTO: 
                choice1="[Auto Select]" 
            else: 
                choice1="Auto Select"
            if self.player_core == xbmc.PLAYER_CORE_DVDPLAYER: 
                choice2="[DVD Player]"
            else:
                choice2="DVD Player"
            if self.player_core == xbmc.PLAYER_CORE_MPLAYER: 
                choice3="[MPlayer]"
            else:
                choice3="MPlayer"
                
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Default Player...", [choice1, choice2, choice3])   

            if choice == 0:
                self.player_core=xbmc.PLAYER_CORE_AUTO
            elif choice == 1:
                self.player_core=xbmc.PLAYER_CORE_DVDPLAYER
            elif choice == 2:   
                self.player_core=xbmc.PLAYER_CORE_MPLAYER
            
            self.onSaveSettings()

        ######################################################################
        # Description: Handles the view selection menu.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onView(self):
            possibleChoices = ["Ascending (default)", \
                               "Descending",\
                               "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("View...", possibleChoices)
            
            if (choice == 0) and (self.vieworder != 'ascending'): #Ascending
                self.ParsePlaylist(mediaitem=self.mediaitem)
                self.vieworder = 'ascending'
            elif (choice == 1) and (self.vieworder != 'descending'): #Descending
                size = self.pl_focus.size()
                for i in range(size/2):
                    item = self.pl_focus.list[i]
                    self.pl_focus.list[i] = self.pl_focus.list[size-1-i]
                    self.pl_focus.list[size-1-i] = item
                self.ParsePlaylist(mediaitem=self.mediaitem, reload=False) #display download list
                self.vieworder = 'descending'
            
        ######################################################################
        # Description: Handles display of a text file.
        # Parameters : URL=URL to the text file.
        # Parameters : mediaitem=text file media item.
        # Return     : -
        ######################################################################
        def OpenTextFile( self, URL='', mediaitem=CMediaItem()):
            self.setInfoText("Loading...") #loading text on
                    
            if (mediaitem.background == 'default') and (self.pl_focus.background != 'default'):
                mediaitem = copy.copy(mediaitem)
                mediaitem.background = self.pl_focus.background
            
            textwnd = CTextView("CTextViewskin.xml", os.getcwd())
            result = textwnd.OpenDocument(URL, mediaitem)
            self.setInfoText(visible=0) #loading text off            

            if result == 0:
                textwnd.doModal()
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Cannot open file.")
                
        ######################################################################
        # Description: Handles image slideshow.
        # Parameters : playlist=the source playlist
        #              pos=media item position in the playlist
        #              mode=view mode (0=slideshow, 1=recursive slideshow)
        #              iURL(optional) = URL to image
        # Return     : -
        ######################################################################
        def viewImage(self, playlist, pos, mode, iURL=''):
            self.setInfoText("Loading...")
            #clear the imageview cache
            self.delFiles(imageViewCacheDir)

            if not os.path.exists(imageViewCacheDir): 
                os.mkdir(imageViewCacheDir) 

            loader = CFileLoader2() #create file loader instance

            if mode == 0: #single file show
                localfile= imageViewCacheDir + '0.'
                if iURL != '':
                    URL = iURL
                else:    
                    URL = playlist.list[pos].URL
                    
                    urlopener = CURLLoader()
                    result = urlopener.urlopen(URL, playlist.list[pos])
                    if result == 0:
                        URL = urlopener.loc_url                    
                                       
                ext = getFileExtension(URL)

                if URL[:4] == 'http':                   
                    loader.load(URL, localfile + ext, proxy="DISABLED")
                    if loader.state == 0:
                        xbmc.executebuiltin('xbmc.slideshow(' + imageViewCacheDir + ')')
                    else:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Error", "Cannot open image.")
                else:
                    #local file
                    shutil.copyfile(URL, localfile + ext)
                    xbmc.executebuiltin('xbmc.slideshow(' + imageViewCacheDir + ')')
            
            elif mode == 1: #recursive slideshow
                #in case of slideshow store default image
                count=0
                for i in range(self.list.size()):
                    if playlist.list[i].type == 'image':
                        localfile=imageViewCacheDir+'%d.'%(count)
                        URL = playlist.list[i].URL
                        ext = getFileExtension(URL)
                        shutil.copyfile(imageDir+'imageview.png', localfile + ext)
                        count = count + 1
                if count > 0:
                    count = 0
                    index = pos
                    for i in range(self.list.size()):
                        if count == 2:
                            xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageViewCacheDir + ')')
                            self.state_action = 0
                        elif (count > 2) and (self.state_action == 1):
                            break
                            
                        if playlist.list[index].type == 'image':
                            localfile=imageViewCacheDir+'%d.'%(count)
                            URL = playlist.list[index].URL
                            ext = getFileExtension(URL)
                            loader.load(URL, localfile + ext, proxy="DISABLED")
                            if loader.state == 0:
                                count = count + 1
                        index = (index + 1) % self.list.size()

                    if self.list.size() < 3:
                        #start the slideshow after the first two files. load the remaining files
                        #in the background
                        xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageViewCacheDir + ')')
                if count == 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "No images in playlist.")
            
            self.setInfoText(visible=0)
            
        ######################################################################
        # Description: Handles Installation of Applications
        # Parameters : URL=URL to the script ZIP file.
        # Parameters : mediaitem=media item containing application.        
        # Return     : -
        ######################################################################
        def InstallApp( self, URL='', mediaitem=CMediaItem()):
            dialog = xbmcgui.Dialog()
            
            type = mediaitem.GetType(0)
            attributes = mediaitem.GetType(1)
            
            if type == 'script':
                if dialog.yesno("Message", "Install Script?") == False:
                    return

                installer = CInstaller()
                if attributes == 'navi-x':
                    result = installer.InstallNaviX(URL, mediaitem)
                else:    
                    result = installer.InstallScript(URL, mediaitem)

            elif type == 'plugin':
                if dialog.yesno("Message", "Install " + attributes + " Plugin?") == False:
                    return

                installer = CInstaller()
                result = installer.InstallPlugin(URL, mediaitem)
            elif type == 'skin':
                if dialog.yesno("Message", "Install Skin?") == False:
                    return

                installer = CInstaller()
                result = installer.InstallSkin(URL, mediaitem)
            else:
                result = -1 #failure
            
            self.setInfoText(visible=0)
            
            if result == 0:
                dialog.ok(" Installer", "Installation successful.")
                if attributes == 'navi-x':
                    dialog.ok(" Installer", "Please restart Navi-X.")
            elif result == -1:
                dialog.ok(" Installer", "Installation aborted.")
            elif result == -3:
                dialog.ok(" Installer", "Invalid ZIP file.")
            else:
                dialog.ok(" Installer", "Installation failed.")
                
        ######################################################################
        # Description: Handle selection of playlist search item (e.g. Youtube)
        # Parameters : item=mediaitem
        #              append(optional)=true is playlist must be added to 
        #              history list;
        # Return     : -
        ######################################################################
        def PlaylistSearch(self, item, append):
            possibleChoices = []
            possibleChoices.append("New Search")
            for m in self.SearchHistory:
                possibleChoices.append(m)
            possibleChoices.append("Cancel")                
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Search: " + item.name, possibleChoices)

            if (choice == -1) or (choice == (len(possibleChoices)-1)):
                return #canceled

            if choice > 0:
                string = self.SearchHistory[choice-1]
            else:  #New search
                string = ''
            
            keyboard = xbmc.Keyboard(string, 'Search')
            keyboard.doModal()
            if (keyboard.isConfirmed() == False):
                return #canceled
            searchstring = keyboard.getText()
            if len(searchstring) == 0:
                return  #empty string search, cancel
            
            #if search string is different then we add it to the history list.
            if searchstring != string:
                self.SearchHistory.insert(0,searchstring)
                if len(self.SearchHistory) > 8: #maximum 8 items
                    self.SearchHistory.pop()
                self.onSaveSearchHistory()
        
            #get the search type:
            index=item.type.find(":")
            if index != -1:
                search_type = item.type[index+1:]
            else:
                search_type = ''
        
            #youtube search
            if (item.type == 'search_youtube') or (search_type == 'html_youtube'):
                fn = searchstring.replace(' ','+')
                if item.URL != '':
                    URL = item.URL
                else:
                    URL = 'http://www.youtube.com/results?search_query='
                URL = URL + fn
                  
                #ask the end user how to sort
                possibleChoices = ["Relevance", "Date Added", "View Count", "Rating"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Sort by", possibleChoices)

                #validate the selected item
                if choice == 1: #Date Added
                    URL = URL + '&search_sort=video_date_uploaded'
                elif choice == 2: #View Count
                    URL = URL + '&search_sort=video_view_count'
                elif choice == 3: #Rating
                    URL = URL + '&search_sort=video_avg_rating'
               
                mediaitem=CMediaItem()
                mediaitem.URL = URL
                mediaitem.type = 'html_youtube'
                mediaitem.name = 'search results: ' + searchstring
                mediaitem.player = item.player

                #create history item
                tmp = CHistorytem()

                tmp.index = self.getPlaylistPosition()
                tmp.mediaitem = self.mediaitem

                self.pl_focus = self.playlist
                result = self.ParsePlaylist(mediaitem=mediaitem)
                
                if result == 0 and append == True: #successful
                    self.History.append(tmp)
                    self.history_count = self.history_count + 1
            elif (item.type == 'search_shoutcast') or (search_type == 'xml_shoutcast'):
                    fn=urllib.quote(searchstring)
                    URL = 'http://www.shoutcast.com/sbin/newxml.phtml?search='
                    URL = URL + fn
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'xml_shoutcast'
                    mediaitem.name = 'search results: ' + searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()

                    tmp.index = self.getPlaylistPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1
            elif (item.type == 'search_flickr') or (search_type == 'html_flickr'):
                    fn = searchstring.replace(' ','+')
                    URL = 'http://www.flickr.com/search/?q='
                    URL = URL + fn
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'html_flickr'
                    mediaitem.name = 'search results: ' + searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()

                    tmp.index = self.getPlaylistPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1
            else: #generic search
                    fn = urllib.quote(searchstring)
                    URL = item.URL
                    URL = URL + fn
                       
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    if search_type != '':
                        mediaitem.type = search_type
                    else: #default
                        mediaitem.type = 'playlist'
                    
                    mediaitem.name = 'search results: ' + searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()

                    tmp.index = self.getPlaylistPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1                    

        ######################################################################
        # Description: Handles selection of 'Browse' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectURL(self):
            browsewnd = CDialogBrowse("CBrowseskin.xml", os.getcwd())
            browsewnd.SetFile('', self.URL, 1, "Browse File:")
            browsewnd.doModal()
            
            if browsewnd.state != 0:
                return
        
            self.pl_focus = self.playlist
        
            self.URL = browsewnd.dir + browsewnd.filename
            
            self.SelectItem(iURL=self.URL)
            
            
        ######################################################################
        # Description: Handles selection of 'Favorite' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onOpenFavorites(self):
            #Select the favorite playlist.
            self.pl_focus = self.favoritelist
              
            #Show the favorite list
            self.ParsePlaylist(reload=False) #display favorite list

        ######################################################################
        # Description: Handles selection within favorite list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectFavorites(self):
            if self.favoritelist.size() == 0:
                #playlist is empty
                return

            pos = self.getPlaylistPosition()
            self.SelectItem(self.favoritelist, pos, append=False)

        ######################################################################
        # Description: Handles closing of the favorite list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onCloseFavorites(self):
            #Select the main playlist.
            self.pl_focus = self.playlist
        
            self.ParsePlaylist(reload=False) #display main list

        ######################################################################
        # Description: Handles context menu within favorite list
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxFavoriteList(self):
            possibleChoices = ["Download...", \
                               "Play...", \
                               "Cut Item", \
                               "Paste Item", \
                               "Remove Item", \
                               "Rename", \
                               "Set Playlist as Home", \
                               "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Options", possibleChoices)

            if self.favoritelist.size() == 0:
                #playlist is empty
                return
            
            #validate the selected item
            if choice == 0: #Download
                self.onDownload()
            elif choice == 1: #Play...
                self.onPlayUsing()
            elif choice == 2: #Cut item
                pos = self.getPlaylistPosition()               
                self.mediaitem_cutpaste = self.favoritelist.list[pos]
                self.favoritelist.remove(pos)
                self.favoritelist.save(RootDir + favorite_file)                
                self.ParsePlaylist(reload=False) #display favorite list
                
            elif choice == 3: #Paste item
    
                pos = self.getPlaylistPosition()                 
                if self.mediaitem_cutpaste != 0:
                    self.favoritelist.insert(self.mediaitem_cutpaste, pos)
                    self.mediaitem_cutpaste = 0
                    self.favoritelist.save(RootDir + favorite_file)                
                    self.ParsePlaylist(reload=False) #display favorite list                    
                else:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Nothing to paste.")
            elif choice == 4: #Remove Item

                pos = self.getPlaylistPosition()
                self.favoritelist.remove(pos)
                self.favoritelist.save(RootDir + favorite_file)
                self.ParsePlaylist(reload=False) #display favorite list
            elif choice == 5: #Rename

                pos = self.getPlaylistPosition()
                item = self.favoritelist.list[pos]
                keyboard = xbmc.Keyboard(item.name, 'Rename')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    item.name = keyboard.getText()
                    self.favoritelist.save(RootDir + favorite_file)
                    self.ParsePlaylist(reload=False) #display favorite list
            elif choice == 6: #Set playlist as home
                if dialog.yesno("Message", "Overwrite current Home playlist?") == False:
                    return
                self.home = self.URL
            
        ######################################################################
        # Description: Handles selection of the 'downloads' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onOpenDownloads(self):
            #select main playlist
            self.pl_focus = self.playlist
            self.SelectItem(iURL=downloads_file)
         
        ######################################################################
        # Description: Handles selection within download list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectDownloads(self):
            if self.URL == downloads_file:
                pos = self.getPlaylistPosition()
                if pos >= 0:
                    if pos == 0:
                        #Select the DL queue playlist.
                        self.pl_focus = self.downloadqueue
                        #fill and show the download queue
                        self.ParsePlaylist(reload=False) #display download list
                    elif pos == 1:
                        #Select the download list playlist.
                        self.pl_focus = self.downloadslist
                        #fill and show the downloads list
                        self.ParsePlaylist(reload=False) #display download list
                    elif pos == 2:
                        #Parental control. first check password
                        if self.access == True:
                            #Select the parent list playlist.
                            self.pl_focus = self.parentlist
                            #fill and show the downloads list
                            self.ParsePlaylist(reload=False) #display download list
                        else:
                            if (self.password == '') or (self.verifyPassword() == True):
                                self.access = True #access granted
                                #Select the parent list playlist.
                                self.pl_focus = self.parentlist
                                #fill and show the downloads list
                                self.ParsePlaylist(reload=False) #display download list
                    
            elif self.URL == downloads_queue: #download queue
                if self.downloadqueue.size() == 0:
                    #playlist is empty
                    return

                pos = self.getPlaylistPosition()         
                self.SelectItem(self.downloadqueue, pos, append=False)
            elif self.URL == downloads_complete: #download completed
                if self.downloadslist.size() == 0:
                    #playlist is empty
                    return

                pos = self.getPlaylistPosition()
                self.SelectItem(self.downloadslist, pos, append=False)
            
            else: #parent list playlists
                if self.parentlist.size() == 0:
                    #playlist is empty
                    return      

                pos = self.getPlaylistPosition()
                self.SelectItem(self.parentlist, pos, append=False)
            
        ######################################################################
        # Description: Handles closing of the downloads list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onCloseDownloads(self):
            #select main playlist
            self.pl_focus = self.playlist
            
            self.ParsePlaylist(reload=False) #display main list

        ######################################################################
        # Description: Handles context menu within download list
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxDownloadsList(self):
            if self.URL == downloads_file:
                return #no menu
            elif self.URL == downloads_queue:
                possibleChoices = ["Download Queue", \
                                   "Download Queue + Shutdown", \
                                   "Stop Downloading", \
                                   "Cut Item", \
                                   "Paste Item", \
                                   "Remove Item", \
                                   "Clear List", \
                                   "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Options", possibleChoices)
            
                if self.downloadqueue.size() == 0:
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0 or choice == 1: #Download Queue / Shutdown
                    self.downlshutdown = False #Reset flag
                    if choice == 1: #Download Queue + Shutdown
                        self.downlshutdown = True #Set flag
                    
                    #Download all files in the queue (background)
                    self.downloader.download_start(self.downlshutdown)
                elif choice == 2: #Stop Downloading
                    self.downloader.download_stop()                   
                elif choice == 3: #Cut item

                    pos = self.getPlaylistPosition()                  
                    self.mediaitem_cutpaste = self.downloadqueue.list[pos]
                    self.downloadqueue.remove(pos)
                    self.downloadqueue.save(RootDir + downloads_queue)                
                    self.ParsePlaylist(reload=False) #display download queue list                                      
                    
                elif choice == 4: #Paste item

                    pos = self.getPlaylistPosition()  
                    if self.mediaitem_cutpaste != 0:
                        self.downloadqueue.insert(self.mediaitem_cutpaste, pos)
                        self.mediaitem_cutpaste = 0
                        self.downloadqueue.save(RootDir + downloads_queue)                
                        self.ParsePlaylist(reload=False) #display favorite list                    
                    else:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Error", "Nothing to paste.")
                  
                elif choice == 5: #Remove

                    pos = self.getPlaylistPosition()
                    self.downloadqueue.remove(pos)
                    self.downloadqueue.save(RootDir + downloads_queue)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 6: #Clear List
                    self.downloadqueue.clear()
                    self.downloadqueue.save(RootDir + downloads_queue)
                    self.ParsePlaylist(reload=False) #display download list
            elif self.URL == downloads_complete: #download completed
                possibleChoices = ["Play...", "Remove Item", "Clear List", "Delete Item", "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if self.downloadslist.size() == 0:
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0: #Play...
                    self.onPlayUsing()
                elif choice == 1: #Remove

                    pos = self.getPlaylistPosition()
                    self.downloadslist.remove(pos)
                    self.downloadslist.save(RootDir + downloads_complete)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 2: #Clear List
                    self.downloadslist.clear()
                    self.downloadslist.save(RootDir + downloads_complete)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 3: #Delete

                    pos = self.getPlaylistPosition()            
                    URL = self.downloadslist.list[pos].URL
                    dialog = xbmcgui.Dialog()                 
                    if dialog.yesno("Message", "Delete file from disk?", URL) == True:
                        if os.path.exists(URL):
                            try:        
                                os.remove(URL)
                            except IOError:
                                pass
                            
                        self.downloadslist.remove(pos)
                        self.downloadslist.save(RootDir + downloads_complete)
                        self.ParsePlaylist(reload=False) #display download list
            else: #Parental control list
                #first check password before opening list
                possibleChoices = ["Set Password", \
                                   "Hide blocked content in playlist", \
                                   "Show block content in playlist", \
                                   "Remove Item",  \
                                   "Clear List", \
                                   "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if (choice > 2) and (self.parentlist.size() == 0):
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0: #Set password
                    keyboard = xbmc.Keyboard(self.password, 'Set Password')
                    keyboard.doModal()
                    if (keyboard.isConfirmed() == True):
                        self.password = keyboard.getText()
                        self.onSaveSettings()
                        self.access = False
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Message", "Password changed.")
                        self.ParsePlaylist(reload=False) #refresh
                elif choice == 1: #Hide blocked content in playlist
                    self.hideblocked = "Hided"
                    self.ParsePlaylist(reload=False) #refresh                 
                elif choice == 2: #Show block content in playlist
                    self.hideblocked = ""
                    self.ParsePlaylist(reload=False) #refresh                          
                elif choice == 3: #Remove
                    pos = self.getPlaylistPosition()
                    self.parentlist.remove(pos)
                    self.parentlist.save(RootDir + parent_list)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 4: #Clear List
                    self.parentlist.clear()
                    self.parentlist.save(RootDir + parent_list)
                    self.ParsePlaylist(reload=False) #refresh

        ######################################################################
        # Description: Handle download context menu in main list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onDownload(self):
            self.state_busy = 1 #busy
            
            #first check if URL is a remote location

            pos = self.getPlaylistPosition()
            entry = copy.copy(self.pl_focus.list[pos])

            #if the entry has no thumb then use the logo
            if (entry.thumb == "default") and (self.pl_focus.logo != "none"):
                entry.thumb = self.pl_focus.logo
            
            if (entry.URL[:4] != 'http') and (entry.URL[:3] != 'ftp'):
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Cannot download file.")                    
                self.state_busy = 0 #busy
                return

            possibleChoices = ["Download", "Download + Shutdown", "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Download...", possibleChoices)
                       
            if (choice != -1) and (choice < 2):
                self.downlshutdown = False #Reset flag
                if choice == 1:
                    self.downlshutdown = True #Set flag
                   
                #select destination location for the file.
                self.downloader.browse(entry, self.dwnlddir)

                if self.downloader.state == 0:
                    #update download dir setting
                    self.dwnlddir = self.downloader.dir
                    
                    #Get playlist entry
                    #Set the download location field.
                    entry.DLloc = self.downloader.localfile
                
                    self.downloader.add_queue(entry)
                        
                    if self.downloader.download_isrunning() == False:
                        dialog = xbmcgui.Dialog()                 
                        if dialog.yesno("Message", "Start download now?") == True:
                            self.downloader.download_start(self.downlshutdown)
              
                elif self.downloader.state == -1:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Cannot locate file.")
                    
            self.state_busy = 0 #not busy            

        ######################################################################
        # Description: Handles parental control menu options.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onParentalControl(self):
            possibleChoices = ["Block Selected Item", \
                                "Unlock Navi-X", \
                                "Cancel"]
            
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)

            if choice == 0: #Block Selected Item          
                #pos = self.list.getSelectedPosition()
                pos = self.getPlaylistPosition()
                tmp = CMediaItem() #create new item
                tmp.type = self.playlist.list[pos].type
                tmp.name = self.playlist.list[pos].name
                tmp.thumb = self.playlist.list[pos].thumb
                if tmp.thumb == 'default' and self.playlist.logo != 'none':
                    tmp.thumb = self.playlist.logo
                tmp.URL = self.playlist.list[pos].URL
                tmp.player = self.playlist.list[pos].player
                self.parentlist.add(tmp)
                self.parentlist.save(RootDir + parent_list)
                self.ParsePlaylist(reload=False) #refresh        
            elif choice == 1: #Unlock Navi-X
                self.verifyPassword()
                self.ParsePlaylist(reload=False) #refresh   

        ######################################################################
        # Description: Handles Clear recent history menu options.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onClearHistory(self):
            possibleChoices = ["Clear Browse History", \
                                "Clear Image Cache", \
                                "Clear Search History", \
                                "Cancel"]
            
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)

            if choice == 0: #Clear Browse History 
                self.history.clear()
                self.history.save(RootDir + history_list)
                self.ParsePlaylist(mediaitem=self.mediaitem)
                dialog = xbmcgui.Dialog()
                dialog.ok("Message", "Cleared Browse History.")               
            elif choice == 1: #Clear Image Cache
                self.delFiles(imageCacheDir) #clear the temp cache first
                dialog = xbmcgui.Dialog()
                dialog.ok("Message", "Cleared Image Cache.")    
            elif choice == 2: #Clear Search History
                del self.SearchHistory[:]
                self.onSaveSearchHistory()
                dialog = xbmcgui.Dialog()
                dialog.ok("Message", "Cleared Search History.")             
                             
    
        ######################################################################
        # Description: Handles selection of the 'black' button in the main list.
        #              This will open a selection window.
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxMainList(self):      

            possibleChoices = ["Download...", \
                                "Play...", \
                                "View...", \
                                "Clear Recent History...", \
                                "Parental Control...", \
                                "Set Default Player...", \
                                "Image Slideshow", \
                                "Add Selected Item to Favorites", \
                                "Add Playlist to Favorites", \
                                "Create Playlist Shortcut", \
                                "Set Playlist as Home", \
                                "View Playlist Source", \
                                "About Navi-X", \
                                "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Options", possibleChoices)
            
            if choice == 0: #Download
                self.onDownload()
            elif choice == 1: #play...
                self.onPlayUsing()
            elif choice == 2: #view...
                self.onView()
            elif choice == 3: #Clear Recent History
                self.onClearHistory()                
            elif choice == 4: #Block selected playlist
                self.onParentalControl()   
            elif choice == 5: #Set default player
                self.onSetDefaultPlayer()     
            elif choice == 6: #Slideshow

                pos = self.getPlaylistPosition()            
                self.viewImage(self.playlist, pos, 1) #slide show show
            elif choice == 7: #Add selected file to Favorites

                pos = self.getPlaylistPosition()
                tmp = CMediaItem() #create new item
                tmp.type = self.playlist.list[pos].type
                keyboard = xbmc.Keyboard(self.playlist.list[pos].name, 'Add to Favorites')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    tmp.name = keyboard.getText()
                else:
                    tmp.name = self.playlist.list[pos].name
                tmp.thumb = self.playlist.list[pos].thumb
                if tmp.thumb == 'default' and self.playlist.logo != 'none':
                    tmp.thumb = self.playlist.logo
                tmp.URL = self.playlist.list[pos].URL
                tmp.player = self.playlist.list[pos].player
                tmp.processor = self.playlist.list[pos].processor
                self.favoritelist.add(tmp)
                self.favoritelist.save(RootDir + favorite_file)
            elif choice == 8: #Add playlist to Favorites
                tmp = CMediaItem() #create new item
                tmp.type = self.mediaitem.type
                keyboard = xbmc.Keyboard(self.playlist.title, 'Add to Favorites')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    tmp.name = keyboard.getText()
                else:
                    tmp.name = self.playlist.title
                if self.playlist.logo != 'none':
                    tmp.thumb = self.playlist.logo
                tmp.URL = self.URL
                tmp.player = self.mediaitem.player
                tmp.background = self.mediaitem.background
                tmp.processor = self.mediaitem.processor
                self.favoritelist.add(tmp)
                self.favoritelist.save(RootDir + favorite_file)
            elif choice == 9: # Create playlist shortcut
                self.CreateShortCut()
            elif choice == 10: #Set Playlist as Home
                if dialog.yesno("Message", "Overwrite current Home playlist?") == False:
                    return
                self.home = self.URL
 #               self.onSaveSettings()
            elif choice == 11: #View playlist source
                self.pl_focus.save(RootDir + 'source.plx')            
                self.OpenTextFile(RootDir + "source.plx")      
            elif choice == 12: #about Navi-X
                self.OpenTextFile('readme.txt')

        ######################################################################
        # Description: Create shortcut
        # Parameters : -
        # Return     : -
        ######################################################################       
        def CreateShortCut(self):
            pos = self.getPlaylistPosition()
            playlist = self.pl_focus
            mediaitem = playlist.list[pos]
            
            if mediaitem.type != 'playlist':
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Selected item not a playlist.")
                return
            
            keyboard = xbmc.Keyboard(mediaitem.name, 'Create Shortcut')
            keyboard.doModal()
            if (keyboard.isConfirmed() == True):
                name = keyboard.getText()
            else:
                return #abort
            
            directory = scriptDir + mediaitem.name
            if not os.path.exists(directory): 
                os.mkdir(directory)
          
            if mediaitem.thumb != 'default':
                loader = CFileLoader2()
                loader.load(mediaitem.thumb, directory + SEPARATOR + 'default.tbn', proxy='DISABLED')           
            elif playlist.logo != 'none':
                loader = CFileLoader2()
                loader.load(playlist.logo, directory + SEPARATOR + 'default.tbn', proxy='DISABLED') 
            else:
                shutil.copyfile(imageDir + 'shortcut.png' , directory + SEPARATOR + 'default.tbn')            
            
            shutil.copyfile(initDir+"default.py", directory + SEPARATOR + "default.py")
            
            playlist.save(directory + SEPARATOR + "startup.plx", pos, pos+1)
            
            dialog = xbmcgui.Dialog()
            dialog.ok("Message", "Created new shortcut in script folder.")
            

        ######################################################################
        # Description: Parental Control verify password.
        # Parameters : -
        # Return     : -
        ######################################################################
        def verifyPassword(self):       
            keyboard = xbmc.Keyboard("", 'Enter Password')
            keyboard.doModal()
            if (keyboard.isConfirmed() == True):
                if self.password == keyboard.getText():
                    self.access = True #access granted
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Message", "Navi-X Unlocked.")
                    return True
                else:
                      dialog = xbmcgui.Dialog()
                      dialog.ok("Error", "Wrong password. Access denied.")
            return False

        ######################################################################
        # Description: Read the home URL from disk. Called at program init. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onReadSettings(self):
            try:
                f=open(RootDir + 'settings.dat', 'r')
                data = f.read()
                data = data.split('\n')
                if data[0] != '': 
                    self.home=data[0]
                if data[1] != '': 
                    self.dwnlddir=data[1]
                if data[2] != '':
                    self.password=data[2]
                if data[3] != '': 
                    self.hideblocked=data[3]
                if data[4] != '': 
                    self.player_core=int(data[4])
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Saves the home URL to disk. Called at program exit. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSaveSettings(self):
            f=open(RootDir + 'settings.dat', 'w')
            #note: the newlines in the string are removed using replace().
            f.write(self.home.replace('\n',"")  + '\n')
            f.write(self.dwnlddir.replace('\n',"") + '\n')
            f.write(self.password.replace('\n',"") + '\n')
            f.write(self.hideblocked.replace('\n',"") + '\n')
            f.write(str(self.player_core).replace('\n',"") + '\n')
            f.close()

        ######################################################################
        # Description: Read the home URL from disk. Called at program init. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onReadSearchHistory(self):
            try:
                f=open(RootDir + 'search.dat', 'r')
                data = f.read()
                data = data.split('\n')
                for m in data:
                    if len(m) > 0:
                        self.SearchHistory.append(m)
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Saves the home URL to disk. Called at program exit. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSaveSearchHistory(self):
            try:
                f=open(RootDir + 'search.dat', 'w')
                for m in self.SearchHistory:
                    f.write(m + '\n')
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Deletes all files in a given folder and sub-folders.
        #              Note that the sub-folders itself are not deleted.
        # Parameters : folder=path to local folder
        # Return     : -
        ######################################################################
        def delFiles(self, folder):
            try:        
                for root, dirs, files in os.walk(folder , topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
            except IOError:
                return
                    

        ######################################################################
        # Description: Controls the info text label on the left bottom side
        #              of the screen.
        # Parameters : folder=path to local folder
        # Return     : -
        ######################################################################
        def setInfoText(self, text='', visible=1):
            if visible == 1:
                self.infotekst.setLabel(text)
                self.infotekst.setVisible(1)
            else:
                self.infotekst.setVisible(0)
                
        ######################################################################
        # Description: Controls the info text label on the left bottom side
        #              of the screen.
        # Parameters : element = playlist element to display
        #                        0 = playlist description
        #                        1 = entry description
        # Return     : 0 on success, -1 on false
        ######################################################################                        
        def onShowDescription(self):  
            pos = self.getPlaylistPosition()
            if pos < 0: #invalid position
                return -1
                
            mediaitem = self.pl_focus.list[pos]
            description = mediaitem.description
             
            if description == '':
                return -1
            
            description = re.sub("&lt;.*&gt;", "", description)              
            description = re.sub("&#.*39;", "'", description)              
            description = re.sub(r'<[^>]*?>', "", description)
                
            self.list.setVisible(0)
                
            self.list3tb.setText(description)
            self.list3tb.setVisible(1)
            self.setFocus(self.list3tb)
            self.descr_view = True
                
            self.setFocus(self.getControl(128))
            
            #success
            return 0

            #end of function                

#main window is created in default.py
#win = MainWindow()
#win.doModal()
#del win
