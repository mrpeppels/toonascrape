from bs4 import BeautifulSoup
import sys
import requests
from Tkinter import *
import tkMessageBox
import tkFileDialog
import subprocess
import os
import json
from PIL import Image, ImageTk
from io import BytesIO
import pygame


testing = 0

fish = """
                 |
                 |
                 
                ,|.
               ,\|/.
             ,' .V. `.
            / .     . \\
           /_`       '_\\
          ,' .:     ;, `.
          |@)|  . .  |(@|
     ,-._ `._';  .  :`_,' _,-.
    '--  `-\ /,-===-.\ /-'  --`
   (----  _|  ||___||  |_  ----)
    `._,-'  \  `-.-'  /  `-._,'
             `-.___,-'

        ,----,                                                             
      ,/   .`|                                                             
    ,`   .'  :                                                             
  ;    ;     /                                                             
.'___,/    ,'  ,---.     ,---.        ,---,                                
|    :     |  '   ,'\   '   ,'\   ,-+-. /  |                               
;    |.';  ; /   /   | /   /   | ,--.'|'   |  ,--.--.                      
`----'  |  |.   ; ,. :.   ; ,. :|   |  ,"' | /       \                     
    '   :  ;'   | |: :'   | |: :|   | /  | |.--.  .-. |                    
    |   |  ''   | .; :'   | .; :|   | |  | | \__\/: . .                    
    '   :  ||   :    ||   :    ||   | |  |/  ," .--.; |                    
    ;   |.'  \   \  /  \   \  / |   | |--'  /  /  ,.  |                    
    '---'     `----'    `----'  |   |/     ;  :   .'   \                   
                                '---'      |  ,     .-./                   
  .--.--.                                   `--`---'             ,---,     
 /  /    '.                              ,-.----.              ,--.' |     
|  :  /`. /            __  ,-.           \    /  \             |  |  :     
;  |  |--`           ,' ,'/ /|           |   :    |            :  :  :     
|  :  ;_       ,---. '  | |' | ,--.--.   |   | .\ :  ,--.--.   :  |  |,--. 
 \  \    `.   /     \|  |   ,'/       \  .   : |: | /       \  |  :  '   | 
  `----.   \ /    / ''  :  / .--.  .-. | |   |  \ :.--.  .-. | |  |   /' : 
  __ \  \  |.    ' / |  | '   \__\/: . . |   : .  | \__\/: . . '  :  | | | 
 /  /`--'  /'   ; :__;  : |   ," .--.; | :     |`-' ," .--.; | |  |  ' | : 
'--'.     / '   | '.'|  , ;  /  /  ,.  | :   : :   /  /  ,.  | |  :  :_:,' 
  `--'---'  |   :    :---'  ;  :   .'   \|   | :  ;  :   .'   \|  | ,'     
             \   \  /       |  ,     .-./`---'.|  |  ,     .-./`--''       
              `----'         `--`---'      `---`   `--`---'    """



import Tkinter as tk


class MainWindow:
    def __init__(self, master):
        self.root = master
        self.root.configure(background = 'darkgrey')
        self.autoclip = True
        self.song_length = 120
        self.preview_start = 0
        self.preview_stop = 120000
        self.slider_offset = 0
        self.song_obj = {}
        self.slider_lastpos = 0
        self.query_manager_open = False
        self.busy_sliding = False
        self.clock = ""
        self.genre_stringvar = tk.StringVar(master = root, value = "drum-and-bass")
        self.testhtml = open("./test.html", "r").read()
        self.url = "https://www.beatport.com/genre/{}/1/releases?per-page={}"
        self.query_file = "./etc/queries"
        self.genre_list = ['drum-and-bass', 'house', 'techno']
        self.song_dict = {}
        self.create_widgets()
        pygame.init()
        pygame.mixer.init()

    def updatetasks(self):
        if pygame.mixer.music.get_busy():
            song_pos = pygame.mixer.music.get_pos()
        else:
            song_pos = 0
        if not self.busy_sliding:
            slider_pos = song_pos + self.slider_offset + self.preview_start
            if slider_pos > self.preview_stop:
                slider_pos = self.preview_stop
            if slider_pos < self.preview_start:
                slider_pos = self.preview_start
                self.slider_offset = 0
            
            self.preview_searchbar.set(slider_pos)
            time = int(song_pos + self.slider_offset+ self.preview_start)/1000
            m, s = divmod(time, 60)
            h, m = divmod(m, 60)
            self.clock = "%d:%02d:%02d" % (h, m, s)
            self.time_elapsed.configure(text=self.clock)
        if pygame.mixer.music.get_busy():
            self.log_status( " {}- {}".format(self.song_obj[0]['name'], self.clock))
        
        self.root.after(1000, self.updatetasks)
        
    def play_preview(self, url):
        self.update_player()
        pygame.mixer.init()
        self.preview_offset = 0
        if not testing:
            self.log_status('Getting preview: ' + url)
            self.mp3 = requests.get(url).content
            self.log_status('Loading mp3...')
            pygame.mixer.music.load(BytesIO(self.mp3))
            pygame.mixer.music.play()
            #self.song_length = pygame.mixer.Sound(BytesIO(response.content).read()).get_length()
        else:
            self.log_status('Loading test mp3...')
            pygame.mixer.music.load('preview.mp3')
            #self.song_length = pygame.mixer.Sound('previewtest.mp3').get_length() * 1000000
        self.preview_searchbar.config(to = self.song_length)
        self.log_status('Mp3 loaded, playing...')
        pygame.mixer.music.play()

    def pause_update(self,event):
        self.slider_lastpos = self.preview_searchbar.get()
        self.busy_sliding = True
        
    def update_song_pos(self, event):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.init()
            if not testing and hasattr(self, 'mp3') :
                self.log_status('Reloading mp3...')
                pygame.mixer.music.load(BytesIO(self.mp3))
                pygame.mixer.music.play()
            elif testing:
                self.log_status('Reloading test mp3...')
                pygame.mixer.music.load('preview.mp3')
                pygame.mixer.music.play()
        slider_pos = self.preview_searchbar.get() 
        print(str(slider_pos) + str(self.preview_start))
        delta = slider_pos - self.slider_lastpos
        self.slider_offset += delta
        start_time = 0
        if slider_pos > self.preview_stop:
             start_time = self.preview_stop  
        elif slider_pos < self.preview_start  :
             start_time = self.preview_start
        else:
            start_time = slider_pos
        start_time = (start_time - self.preview_start) / 1000
        print("starttime: {}".format(start_time))
        pygame.mixer.music.rewind()
        if  pygame.mixer.music.get_busy():
            pygame.mixer.music.set_pos(start_time)
        self.busy_sliding = False
        
    def log_info(self, string):
        print( string )
        self.info_textbox.insert(END, string+"\n")
        root.update()

    def log_status(self, string):
        self.status_bar.config(text="")
        self.status_bar.config(text = string)
        root.update_idletasks()

    def display_songinfo(self, event):
        sel = self.song_select_listbox.curselection()
        if sel:
            index = sel[0]
            seltext = self.song_select_listbox.get(index)
            self.song_obj = self.song_dict[seltext.strip()]
            selsongdisplay = self.song_obj[1]
            self.info_textbox.delete('1.0', END) 
            self.info_textbox.insert(END, selsongdisplay)
            self.update_player()
            self.play_preview(self.song_obj[0]['preview']['mp3']['url'])
            if not testing: self.display_waveform(self.song_obj[0]['waveform']['large']['url'])
            

    def update_player(self):
        self.song_length = self.song_obj[0]['duration']['milliseconds']
        self.preview_start = self.song_obj[0]['preview']['mp3']['offset']['start']
        self.preview_stop = self.song_obj[0]['preview']['mp3']['offset']['end'] + self.preview_start
        
            
    def display_waveform(self, url):
        self.log_status('getting ' + url)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        self.log_status('resizing...')
        img = img.resize((850, 125), Image.ANTIALIAS)
        self.log_status('Generating waveform... ')
        img = ImageTk.PhotoImage(img)
        self.waveform_view.configure(image = img)
        self.waveform_view.img = img
        self.log_status('Waveform loaded')
        
    def open_query_manager(self):
        if self.query_manager_open:
            self.query_manager.focus_force()

        else:
            self.query_manager = Toplevel()
            self.query_manager.wm_title("Query manager")
            self.app = QueryManager(master = self.query_manager, parent = self)
            self.query_manager_open = True

        
    def display(self, song, matching_artist):
        global song_dict
        if len(song['artists'])>1:
            fmt_song = "{} (VA)".format(song['title'])
            
            artist_row = "List of Various Artists:    {}\n".format(",  ".join(song['artists']))
            title_row = 'Title:   {}\n\n'.format(song['title'])
        else:
            fmt_song = '{} - {}'.format(matching_artist, song['title'])
            artist_row= "Artist:    {}\n".format(song['artists'][0]['name'])
            title_row = 'Title:   {}\n\n'.format(fmt_song)
                
        songdisplay = ""
        songdisplay += "-"*10 + "FRE$H T00NAH" + "-"*10 + '\n'
        songdisplay += title_row
        songdisplay += 'Search query:   {}\n\n'.format(matching_artist)
        songdisplay += 'Labels:  {}\n'.format(song['label']['name'])
        songdisplay += 'Date:    {}\n'.format(song['date']['released'])
        songdisplay += 'Image:   {}\n'.format(song['images']['large']['url'])
        songdisplay += 'Preview  {}\n'.format(song['preview']['mp3']['url'])
        songdisplay += artist_row 

        if fmt_song not in self.song_dict.keys():
            self.song_select_listbox.insert(END, fmt_song)
            self.song_obj = [song, songdisplay]
            self.song_dict[fmt_song.strip()] = self.song_obj
            self.log_info(songdisplay + "\n"*2)
        
        
    def get_releasepage(self):
        per_page = str(150)
        genre = self.genre_stringvar.get()
        #genre_url = self.genre_list[genre]
        self.log_info("Getting BeatPort " + genre.capitalize() + " release page (last " + per_page + " results)")
        release_url = self.url.format(genre, per_page )
        self.log_info("GET {}".format(release_url))
        r  = requests.get(release_url)
        self.log_info("Done. Page Length: {} Parsing...".format(len(r.text)))
        return r.text

    def parse_song(self, row):
        items = row.find_all('p')
        song = {
                   "title" : "",
                   "artists" : [],
                   "labels" : "",
                   "date" : ""
               }

        for item in items:
            name = item['class'][0]
            if 'title' in name:
                song['title'] = item.text
            if 'released' in name:
                song['date'] = item.text
            if 'labels' in name:
                song['label'] = item.text.strip( "\n" )
            if 'artists' in name:
                artists = list(item.find_all('a'))
                song['artists'] = [a.string.rstrip() for a in artists if "," not in a]
        if len(song['artists']) > 1:
            artist_paceholder = "VA"
        elif len(song['artists']) > 0:
            artist_paceholder = song['artists'][0]
        else:
            artist_paceholder = "No artist found"
        p_txt = "processing    {} - {}".format(artist_paceholder, song['title'].encode( 'utf-8' ))
        self.log_info( p_txt )
        self.log_status( p_txt )
        return song


    def match_songs_old(self, soup, queries):
        row_objects = soup.find_all('li', class_= "bucket-item")
        print("Starting search of {} releases...".format(str(len(row_objects))))
        for row in row_objects:
            song = self.parse_song(row)
            for artist in song['artists']:
                if artist.lower() in [query.lower() for query in queries]:
                    self.display(song, artist)
                    break
                
    def match_songs(self, soup, queries):
        data_objects_tag = soup.find('script', {'id':'data-objects'}).contents
        json_string = re.search(r"(?s)window.Playables\s*=\s*(\{.*?\});", data_objects_tag[0] )
        json_string = json_string.group(1)
        data_dict = json.loads(json_string)
        songs = data_dict['tracks']
        print("Starting search of {} releases...".format(str(len(songs))))
        for song in songs:
            artists = song['artists']
            if len(artists) > 1:
                artist_paceholder = "VA"
            elif len(artists) > 0:
                artist_paceholder = artists[0]['name']
            else:
                artist_paceholder = "No artist found"
            p_txt = "processing    {} - {}".format(artist_paceholder, song['title'].encode( 'utf-8' ))
            self.log_info( p_txt )
            self.log_status( p_txt )
            for artist in artists:
                artist = artist['name']
                if artist.lower() in [query.lower() for query in queries]:
                    self.display(song, artist)
                    break
                        
    def readln(self, filename="./etc/artists.txt"):
        self.data_file = open(filename, "r")
        self.stored_queries = [x.strip() for x in self.data_file.readlines()]
        self.data_file.close()
        return self.stored_queries

    def refresh(self):
        self.info_textbox.delete('1.0', END) 
        self.queries = self.readln("./etc/artists.txt")
        if not testing:
            data = self.get_releasepage()
        else:
            data = self.testhtml
        self.soup = BeautifulSoup(data, "lxml")
        self.log_status("Parsing done, processing")
        self.match_songs(self.soup, self.queries)

    def add_clip(self):
        index = -1
        """Copy song listbox selection to clipboard"""
        try:
            index = self.song_select_listbox.curselection()[0]
        except IndexError:
            pass
        if index != -1:
            text = self.song_select_listbox.get(index)
            text = text.strip()
            command = 'echo ' + text + '| clip'
            self.log_status("Copying {} to clipboard...".format(text))
            subprocess.Popen(command, shell=True)

    def song_select(self, event):
        if self.autoclip:
            self.add_clip()
        self.display_songinfo(event)

    def toggle_play_pause(self):
        if 'pause' in self.play_pause_button.config('text')[-1]:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.init()
                if not testing:
                    self.log_status('Reloading mp3...')
                    pygame.mixer.music.load(BytesIO(self.mp3))
            else:
                pygame.mixer.music.pause()
            self.play_pause_button.config( text = "play", relief="raised")
            self.log_status("Paused")
        else:
            
            pygame.mixer.music.unpause()
            self.play_pause_button.config( text = "pause", relief="sunken")
            self.log_status("Playing preview....")

    def toggle_clip(self):
        self.log_status(" ")
        if "ON" in self.clipboard_button.config('text')[-1]:
            self.clipboard_button.config( text = "AutoClip OFF", relief="raised")
            self.autoclip = False
        else:
            self.clipboard_button.config(text = "AutoClip ON", relief="sunken" )
            self.autoclip = True



    def create_widgets(self):
        """Create Tkinter widget objects"""
        self.info_scroll = tk.Scrollbar(root)
        self.select_scroll_1 = tk.Scrollbar(root)
        self.info_textbox = tk.Text(root, height=45, width=80)
        self.url_bar = tk.Text(root, height=1, width=80)
        self.song_select_listbox = tk.Listbox(root, height=45, width=40)
        #v = StringVar()
        #v.set('L')
        #for val in self.genre_list:
        #    self.genre_radio = Radiobutton(root, variable = v, value = val)
        #    self.genre_radio.grid( row = 3, column = 2, sticky = SW, pady = 5, padx = 10 )
        self.genre_dropdown = tk.OptionMenu(root, self.genre_stringvar, *self.genre_list)

        self.status_bar = Label(root, bd = 2, relief = "sunken", anchor = "w")
        self.time_elapsed = Label(text="0:00:00")
        self.preview_searchbar = Scale( root, from_=0, to=100, orient=HORIZONTAL, width = 10, bg='darkgrey', highlightcolor='black', relief='sunken', resolution=0.1, troughcolor='darkgrey', showvalue=0)
        img_o = Image.open('wave.png')
        img_o = img_o.resize((850, 125), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img_o)
        self.waveform_view = Label(root, image = img, background = 'darkgrey')
        self.waveform_view.image = img

        """Buttons"""
        self.refresh_button = tk.Button(root, text = "Get Releases", command = self.refresh)
        self.query_manager_button = tk.Button(root, text = "Query Manager", command =lambda: self.open_query_manager())
        self.clipboard_button = tk.Button(root, text = "AutoClip ON", relief="sunken", command =lambda: self.toggle_clip())
        self.play_pause_button = tk.Button(root, text = "pause", relief = 'sunken', command =lambda: self.toggle_play_pause()) 
        
        """Place widgets in root window"""
        self.url_bar.grid( row = 0, sticky = NW, padx = (10, 20) )
        self.info_scroll.grid( row = 0, column = 0, sticky = N+E+S, pady=20)
        self.select_scroll_1.grid( row = 0, column = 3, sticky = N+E+S, padx=3)
         
        self.info_textbox.grid( row = 0, column = 0, pady = (25, 0) , padx = (10, 20), sticky = N+E+S+W)
        self.song_select_listbox.grid( row = 0 , column = 1, columnspan = 2, padx = 5, rowspan = 2, sticky = N+E+S+W )
        self.status_bar.grid( row = 4, column = 0, sticky = E+S+W, pady = 5 )
        self.waveform_view.grid(row = 2, column = 0, sticky = E+W, pady = 1)
        self.preview_searchbar.grid(row = 3, column = 0, sticky = E+N+W, pady = 0 )
        self.time_elapsed.grid(row = 3, column = 0, sticky = S+E, pady = 0 )

        
        """Buttons"""
        self.query_manager_button.grid( row = 3, column = 1, sticky = SW, pady = 5, padx = 10 )
        self.genre_dropdown.grid( row = 3, column = 2, sticky = SW, pady = 5, padx = 10 )
        self.clipboard_button.grid( row = 2, column = 2, sticky = SW, pady = 5, padx = 10)
        self.refresh_button.grid( row = 2, column = 1, sticky = SW, pady = 5, padx = 10)
        self.play_pause_button.grid( row = 3, column = 0, sticky = SW, pady = 2, padx =5)

        for i in range(2):
            tk.Grid.columnconfigure(root, i, weight = 1)
            self.root.grid_columnconfigure(i , weight = 1)
            tk.Grid.rowconfigure(root, i, weight = 1)

        self.info_textbox.columnconfigure(1, weight = 2)
            
        self.info_scroll.config(command=self.info_textbox.yview)
        self.select_scroll_1.config(command=self.song_select_listbox.yview)
        self.info_textbox.config(yscrollcommand=self.info_scroll.set)
        self.song_select_listbox.config(yscrollcommand=self.select_scroll_1.set)
        self.url_bar.insert(END, self.url)
        self.song_select_listbox.bind('<ButtonRelease-1>', self.song_select)
        self.preview_searchbar.bind("<ButtonRelease-1>", self.update_song_pos)
        self.preview_searchbar.bind("<Button-1>", self.pause_update)
        self.menubar = tk.Menu( root )

        self.menu = tk.Menu( self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.menu)
        self.menu.add_command(label="New")

        self.menu = tk.Menu( self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Genre", menu=self.menu)
        self.menu.add_command(label="Cut")
        self.menu.add_command(label="Copy")
        self.menu.add_command(label="Paste")
        #root.config(menu=self.menubar)

class QueryManager:
    def __init__(self, master, parent):
        self.query_manager = master
        self.parent = parent
        self.create_widgets()

    def readln(self, filename="./etc/artists.txt"):
        self.data_file = open(filename, "r")
        self.stored_queries = [x.strip() for x in self.data_file.readlines()]
        self.data_file.close()
        return self.stored_queries

    def update_search(self):
        search_term = self.search_var.get()
        current_queries = list(self.query_listbox.get(0, END))       
        #self.query_listbox.delete(0, END)
        for i,item in enumerate(current_queries):
            if search_term.lower() in item.lower() and search_term.lower() != "":
                self.query_listbox.selection_set(i)
            else:
                self.query_listbox.selection_clear(i)
                
    def add_query(self):
        self.query_listbox.insert(END, self.search_bar.get())

    def create_widgets(self):
        self.search_var = StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_search())
        self.search_bar = tk.Entry(self.query_manager, textvariable=self.search_var, width=13)

        self.query_scroll = tk.Scrollbar(self.query_manager)
        

        self.query_listbox = tk.Listbox(self.query_manager, width=80, height = 30, selectmode=EXTENDED)
        self.del_button = tk.Button(self.query_manager, text="Delete Query",
                   command=lambda lb=self.query_listbox: [lb.delete(index) for index in lb.curselection()[::-1]])
        self.save_button = tk.Button(self.query_manager, text ="Save (with delete)", command =lambda: self.writequeries(self.query_listbox.get(0,END), 'save'))
        self.add_button = tk.Button(self.query_manager, text ="Save (no delete)", command =lambda: self.writequeries(self.query_listbox.get(0,END), 'add'))
        self.add_search_button = tk.Button(self.query_manager, text ="Add Search", command =lambda: self.add_query())
        self.scan_button = tk.Button(self.query_manager, text ="Scan Folder", command =lambda: self.info_from_local_library())                                  
        self.cancel_button = tk.Button(self.query_manager, text="Cancel", command=self.query_manager.destroy)
        self.load_button = tk.Button(self.query_manager, text="Load Stored", command= lambda: [self.query_listbox.insert(END, item) for item in self.readln() if item not in self.query_listbox.get(0,END)])
        self.clear_button = tk.Button(self.query_manager, text="Clear", command=lambda: self.query_listbox.delete(0, END))
        self.query_scroll.grid( row = 0, column = 4, sticky = N+E+S, padx=3)
        self.search_bar.grid( row = 3, columnspan = 4, sticky = W+E+S, padx=3)
        self.query_listbox.grid(  row = 0, columnspan=4, sticky = N+E+S+W )
        
        self.scan_button.grid( row = 2, column = 0, sticky = SW, padx = 10, pady = 10  )
        self.load_button.grid(row=1, column=0, sticky = SW, padx = 10, pady = 10 )
        self.del_button.grid( row = 1, column = 1, sticky = SW, padx = 10, pady = 10  )
        self.add_button.grid( row = 1, column = 2, sticky = SW, padx = 10, pady = 10 )
        self.add_search_button.grid( row = 2, column = 1, sticky = SW, padx = 10, pady = 10 )
        self.save_button.grid( row = 2, column = 2, sticky = SW, padx = 10, pady = 10 )
        self.clear_button.grid(row=1, column = 3, sticky = SE, padx = 10, pady = 10 )
        self.cancel_button.grid(row= 2, column = 3, sticky = SE, padx = 10, pady = 10 )

        self.query_scroll.config(command=self.query_listbox.yview)
        self.query_listbox.config(yscrollcommand=self.query_scroll.set)
        for i in range(3):
            self.query_manager.grid_columnconfigure( i, weight = 2-i)
        self.query_manager.grid_rowconfigure( 0, weight = 1)   
        

    def info_from_local_library(self, mode = "artist"):    
        self.pstags = "./etc/getTag.ps1"
        self.tempfile = "./etc/local_lib_info.txt"
        self.rootfolder = tkFileDialog.askdirectory()
        if not self.rootfolder:
            return -1
        self.arglist = ["powershell", "-file", self.pstags, "-rootfolder", self.rootfolder, "-mode", mode]
        self.process = subprocess.Popen(self.arglist)
        self.process.wait()
        self.local_lib_list = self.readln(self.tempfile)
        os.remove(self.tempfile)
        self.uniq_list = list(set(self.local_lib_list))
        for item in self.uniq_list:
            if len(item) > 1:
                self.query_listbox.insert(END, item.lower())
        self.query_listbox.lift()
        self.query_listbox.focus_force()


    def writequeries(self, queries, mode = 'add', filename="./etc/artists.txt"):
        #print("Saving queries... " + queries)
        confirm_delete = False
        stored_queries = self.readln(filename)
        try:
            data_file = open(filename, "w")
            volatile_queries = list(self.query_listbox.get(0, END))            
            write_list = []

            if mode == 'save':
                deleted_queries = 0
                for q in stored_queries:
                    if q not in volatile_queries:
                        deleted_queries += 1

                if deleted_queries>0:
                    """queries are being deleted, first confirm"""
                    confirm_delete = tkMessageBox.askyesno(message="Are you sure you want to delete {} queries?".format(str(deleted_queries)))
                    
                    if confirm_delete:
                        write_list = volatile_queries
                        self.parent.log_info("Query list total deleted: {}".format(str(deleted_queries)))
                    else:
                        write_list = stored_queries
                else:
                    write_list = volatile_queries
                    new_queries = 0
                    for q in volatile_queries:
                        if q not in stored_queries:
                            new_queries += 1
                    self.parent.log_info("Query list total added: {}".format(str(new_queries)))
            else:
                new_queries = 0
                for q in volatile_queries:
                    if q not in stored_queries:
                        new_queries += 1
                write_list = stored_queries
                for item in volatile_queries:
                    item = item.lower()
                    if item not in stored_queries:
                        write_list.append(item)
                self.parent.log_info("Query list total added: {}".format(str(new_queries)))
                
            print(write_list)            
            data_file.writelines("\n".join(write_list))
            data_file.close()
        except Exception,e:
            print str(e)
            data_file.writelines("\n".join(stored_queries))
            data_file.close()
            return 0

        
if __name__ == '__main__':
    root = tk.Tk()
    root.title("ToonahScrapah - ontworpen voor klaakilicious kanneelpantoffel. Copyright sleppep niwla 420")
    app = MainWindow(root)
    root.after(0, app.updatetasks)
    app.log_info("Welkom heer Klaak."  + fish)
    mainloop()

