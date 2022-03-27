from email.policy import default
from multiprocessing.spawn import get_executable
from shutil import ExecError
from win32gui import GetWindowText, GetForegroundWindow
import psutil, win32process, win32gui, re, time, os

from pynput.keyboard import Key, Controller

by = "by" # the word displayed between Song and artist (this is for language support)
on = "on" # the word displayed if the browser is on a known page (this is for language support)

def checkIfProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def getSpotifyHWND():     
    pidlist = []
    PROCNAME = "Spotify.exe" # you may change this if you use idk YT-Music.exe or something if it works the same way it may work (you will obviously have to change the color and icons and so on aswell)
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            pidlist.append(str(proc.pid))
    def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                for pid in pidlist:
                    if(str(win32process.GetWindowThreadProcessId(hwnd)[1]) == pid):
                        print(hwnd, win32gui.GetWindowText(hwnd), win32process.GetWindowThreadProcessId(hwnd)[1])
                        global spothwnd
                        spothwnd = hwnd
    win32gui.EnumWindows(winEnumHandler, None)
    return spothwnd

global actvar           # You can set here what is beeing displayed if nothing is being detected 
actvar  = ""            # default is just empty strings "" (so if spotify isnt running nothing is being displayed. but can change that if you want) 
global progvar          #   
progvar  = ""           #
global spotifyvar       # for spotifyvar its more ↓ (at the end of the function)
spotifyvar  = ""        #
# global timevar        # You can also add current time or even date if you want, but currently all Time/Date stuff is bot active
# timevar  = ""         #

def spofitfyfunc(hwnd_from_spotify):
    '''
    sets spotifyvar
    '''
    # the comments with #.. show what happens with the strings with all the RegEx substitutions
    if(hwnd_from_spotify != 0): # check if Spotify.exe is running
        spotify = GetWindowText(hwnd_from_spotify) #.. Amy Lee - Speak to Me (From "Voice from the Stone" Original Motion Picture Soundtrack)
        if(spotify == "Spotify Premium" or spotify == ""):
            return ""
        else:   
            artist = re.sub(r'^(.*?) - .*', r'\1', spotify)   #.. Amy Lee
            title = re.sub(artist + " - ", '', spotify)       #.. Speak to Me (From "Voice from the Stone" Original Motion Picture Soundtrack) 
            
            # ↓ removes brackets and content from brackets (you may comment that out if you want to keep the brackets, it often gets realy long with them tho)
            title = re.sub(r'(.*)\(.*\)(.*)', r'\1\2', title) #.. Speak to Me
             

            print('')           #
            print(artist)       # Prints some Spotify stuff in the console 
            print(title)        # not neccesary but it doesnt hurt
            print('')           #

            strspotify = f'<span style="color:#00ff26"> {title} <span style="color:#50a65c">{by}</span> {artist}</span>  ' #.. <span style="color:#00ff26"> Speak to Me <span style="color:#50a65c">by</span> Amy Lee</span>  
            return strspotify
    else:
        return "" # if spotify isnt running the variable is just an empty string

def activefunc():
    '''
    sets actvartouple with prog on 0 and active on 1 and subprogvar on 2
    '''
    active = GetWindowText(GetForegroundWindow()) # saves the window title of the activated as string in stractive
    stractive = str(active)                       # 

    stractive = re.sub("^(OBS ).*", r'<span style="color:#999ba1"> OBS</span>', stractive)  # cuts OBS
    stractive = re.sub('‎', r'', stractive) # removes wired rtm mark https://www.compart.com/de/unicode/U+200E

    stractive = re.sub(r'^([A-Z]:)(.*\\)+(.*)', r'\3', stractive)  # cuts noname programs' paths from drives A: 'till Z:

    stractive = re.sub(r'(.*)\([0-9]{1,2}\)(.*)', r'\1\2', stractive) # removes notification-brackets like (1) or (5)  

    # the comments with #.. show what happens with the strings with all the RegEx substitutions

    endstring = re.sub(r'(.*)( [—-] )(.*)$', r'\3', stractive) #.. The Video Title - YouTube — Mozilla Firefox
    progvar = "" 
    extension = "" 
    # ENDSTRINGS Switch Statement #.. The Video Title - YouTube — Mozilla Firefox
    match endstring:   
        case "Mozilla Firefox":
            progvar = re.sub(r'(.*) — Mozilla Firefox', r'<span style="color:#ff5405"> Firefox: </span>', stractive) #.. <span style="color:#ff5405"> Firefox: </span>
            stractive = re.sub(r'(.*) — Mozilla Firefox', r'\1', stractive) #.. The Video Title - YouTube
            endstringfox = re.sub(r'(.*)( - )(.*)$', r'\3', stractive) #.. Youtube
            match endstringfox:
                case "YouTube":
                    progvar = re.sub(r'Firefox:', r'Firefox ' + on + r' ', progvar) #.. <span style="color:#ff5405"> Firefox on </span>
                    stractive = re.sub(r'(.*)??( - )+?YouTube', r'<span style="color:#ff2e2e"> YouTube: </span> \1', stractive) #.. <span style="color:#ff2e2e"> YouTube: </span>The Video Title 
                case "Wikipedia" :
                    progvar = re.sub(r'Firefox:', r'Firefox ' + on + r' ', progvar)
                    stractive = re.sub(r'(.*)??( - )+?Wikipedia', r'<span style="color:#d1cdb6"> Wikipedia: </span> \1', stractive)
                case "Wikiwand" :
                    progvar = re.sub(r'Firefox:', r'Firefox ' + on + r' ', progvar)
                    stractive = re.sub(r'(.*)??( - )+?Wikiwand', r'<span style="color:#d1cdb6"> Wikiwand: </span> \1', stractive)
                case "Twitch" :
                    progvar = re.sub(r'Firefox:', r'Firefox ' + on + r' ', progvar)
                    stractive = re.sub(r'(.*)??( - )+?Twitch', r'<span style="color:#9036ff"> Twitch: </span> \1', stractive)                                
        case "Adobe Acrobat Reader DC (64-bit)":
            progvar = re.sub(r'(.*) - Adobe Acrobat Reader DC \(64-bit\)', r'<span style="color:#ff6161"> Acrobat: </span>', stractive)
            stractive = re.sub(r'(.*) - Adobe Acrobat Reader DC \(64-bit\)', r'\1', stractive)
        case "Discord":
            progvar = re.sub(r'(.*) - Discord', r'<span style="color:#5865f1">ﭮ Discord: </span>', stractive)
            stractive = re.sub(r'(.*) - Discord', r'\1', stractive)
        case "Visual Studio Code":
            # symbols for certain extensions (if you set the font to a nerdfont in your editor to can see them here too)
            extension = re.sub(r'(.*)\.([a-z]*) - (.*)',r'\2', stractive) #.. py
            match extension:        
                    case "py":
                        extension = "  " #..    
                    case "html":
                        extension = "  " 
                    case "java":
                        extension = "  " 
                    case "ini":
                        extension = " 煉 " 
                    case "txt":
                        extension = "  " 
                    case "htm":
                        extension = "  " 
                    case "json":
                        extension = " ﬥ " 
                    case "ahk":
                        extension = "  " 
                    case "js":
                        extension = "  "  
                    case "css":
                        extension = "  "   
                    case "sh":
                        extension = "  " 
                    case _:
                        extension = ""   
            progvar = re.sub("(.*) - Visual Studio Code", r'<span style="color:#21a1e4"> VS Code: </span>', stractive)
            stractive = re.sub("(●)? ?(.*) - Visual Studio Code", r'\2' + extension + r'<span style="color:#21a1e4">\1</span>', stractive)
             
        case "OneNote":
            progvar = re.sub(r'(.*) - OneNote', r'<span style="color:#ca64ea">ﱅ OneNote: </span>', stractive)
            stractive = re.sub(r'(●)? ?(.*) - OneNote', r'\2 <span style="color:#21a1e4">\1</span>', stractive)
        case "Word":
            progvar = re.sub(r'(.*) - Word', r'<span style="color:#4d79ff"> Word: </span>', stractive)
            stractive = re.sub(r'(●)? ?(.*) - Word', r'\2 <span style="color:#21a1e4">\1</span>', stractive)
        case "Excel":
            progvar = re.sub(r'(.*) - Excel', r'<span style="color:#2aad2a"> Excel: </span>', stractive)
            stractive = re.sub(r'(●)? ?(.*) - Excel', r'\2 <span style="color:#21a1e4">\1</span>', stractive)
        case "PowerPoint":
            progvar = re.sub(r'(.*) - PowerPoint', r'<span style="color:#ffb300"> PowerPoint: </span>', stractive)
            stractive = re.sub(r'(●)? ?(.*) - PowerPoint', r'\2 <span style="color:#21a1e4">\1</span>', stractive)
        case "Notepads":
            progvar = re.sub(r'(.*) - Notepads', r'<span style="color:#ff002b"> Notepads: </span>', stractive)
            stractive = re.sub(r'(●)? ?(.*) - Notepads', r'\2 <span style="color:#21a1e4">\1</span>', stractive)

 
    if(progvar == stractive): # for programs that dont say what program they are in the window title or programs not yet implented 
        progvar = ""
    return progvar, stractive # as touple


# def timefunc():  # this is commented out by default, this is the declaration of the 
#     '''
#     sets timevar
#     '''
#     now = datetime.datetime.now()
#     timeme = now.strftime("%H:%M") # Current format is like 21:32 
#     return timeme

if(checkIfProcessRunning("Spotify.exe")):
    getSpotifyHWND() # sets spothwnd to one PID of "Spotify.exe"
else:
    spothwnd = 0
   
__path = re.sub(r'\\', "/", __file__[:-11]) # swaping backslashes for normal ones + 11 because stringme.py is 11 chars long
def main():
    spotifyold = "" # empty string
    keyboard = Controller() # makes a keyboard for key emulation
    try:
        while(checkIfProcessRunning("obs64.exe")):
            # timevar = timefunc() # this is commented out by default, it is the call of the time/date function
            for x in range(3):                      # ↓
                # evry 10 sec
                spotifyvar = spofitfyfunc(spothwnd)
                if(spotifyvar == spotifyold):
                    print('spotify remains unchanged')
                else:
                    spotifyold = spotifyvar
                    print('updated spotify')
                    keyboard.press(Key.f13) # this is for telling OBS when spotify changed (you may do with that what youw want (I use it to display the cover image with the plugin Tuna))
                    time.sleep(0.05)
                    keyboard.release(Key.f13)
                            
                

                for y in range(5):                 # these for-loops + the time.sleep(1) determine how fast the program runs. If you change it, dont forget to change the miliseconds in stringme_tamplate.htm in the <script> tags (default is 1000} 
                    time.sleep(1)                   # here time.sleep(0.5) and 500 in stringme_tamplate.htm would speed up the program 2x in comparison to default      
                    actvartuple = activefunc() 
                    print('updated active')
                    # The following is what is actually beeing dispayed. (is is placed in the paragraph tags (<p></p>) in the stringme.html)
                    # you can change the order, or add some spaces or characters to seperate stuff.
                    # 
                    writeme =  spotifyvar + str(actvartuple[0]) + str(actvartuple[1])

                    f = open(__path + "assets/stringme_tamplate.htm", "r", encoding="utf-8") # somehow it crashes here without literal path if not run in vs code on my machine
                    fstring = f.read()
                    f.close()


                    f = open(__path + "stringme.htm", "w", encoding="utf-8")
                    fstring = re.sub(r'<p class="n">(.*)</p>', r'<p class="n">' + writeme + r'</p>', fstring)
                    f.write(fstring)
                    f.close()
    except Exception as e:
        f = open("errorlog.txt", "a")
        f.write('\n')
        f.write(e)
        f.close()               

if __name__ == "__main__":
    main() 
