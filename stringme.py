from win32gui import GetWindowText, GetForegroundWindow
from pynput.keyboard import Key, Controller
import psutil, win32process, win32gui, re, time, json

# This is the path the fil is run at. 
# But one has to swap backslashes for normal ones. 
# Also 11 chars are removed because i want the path not the 'path+stringme.py'
# Somehow the script crashes without literal path for the stringme.htm on my machine 
# therefore I implemented this workaround. And it needs this.
__path = re.sub(r'\\', "/", __file__[:-11])

# geitng data from settings.json
# and implementing it as settings dict 
with open(__path + '/assets/settigns.json', "r", encoding="utf-8") as settingsString:  
    settings = json.load(settingsString)                                    

def checkIfProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() == proc.name().lower():
                # print(f'{processName} is running...')
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # print(f'{processName} is not running.')
    return False

def getMusicHWND():
    pidlist = []
    PROCNAME = settings['strings']['musicSource'] 
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            pidlist.append(str(proc.pid))
    def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                for pid in pidlist:
                    if str(win32process.GetWindowThreadProcessId(hwnd)[1]) == pid:
                        print(f'{PROCNAME}\'s HWND:   {hwnd}\n{PROCNAME}\'s PID :   {win32process.GetWindowThreadProcessId(hwnd)[1]}')
                        global musicHWND
                        musicHWND = hwnd
    win32gui.EnumWindows(winEnumHandler, None)
    return musicHWND

def getMusicTouple(musicHwnd):
    # This function is to set and return the currently playing Song and its artist as Touple.
    # (You can see Window-Titles by pressing and holding Alt+Tab)
    # This is achived by looking at the Window Title of the .exe set as musicSource in settings.json.
    # The Program has to have both infos in the title, otherwise this method doesnt work.
    # Spotify (my Program of choice) has the format 
    # Artist - Title
    # The re.sub lines are here to cut the musicWindowTitle to format
    # and split it into the variables artist and title
    # the comments to the side stering with #.. are an example what happens to a string ao each step.
    musicWindowTitle = GetWindowText(musicHwnd)                                             #.. Amy Lee - Speak to Me (From "Voice from the Stone" Original Motion Picture Soundtrack)
    if musicWindowTitle == settings['strings']['musicIdle'] or musicWindowTitle == "":
        print("\nNothing is currently playing.\n")
        return "", "", ""
    else:   
        artist = re.sub(r'^(.*?) - .*', r'\1', musicWindowTitle)                            #.. Amy Lee
        title = re.sub(artist + " - ", '', musicWindowTitle)                                #.. Speak to Me (From "Voice from the Stone" Original Motion Picture Soundtrack) 
        
        # This removes brackets and content from brackets 
        # This is not neccessary, you may comment that out
        # if you want to keep the brackets
        # it often gets realy long with them (see example)
        title = re.sub(r'(.*)\(.*\)(.*)', r'\1\2', title)                                   #.. Speak to Me

        # This is just for the Terminal. 
        # It shows whats playing.
        print('')
        print(f"Artist: {artist}")
        print(f"Title: {title}")
        print('')                           

        # The next 2 lines "inject" HTML/CSS in the string. 
        # later it will be written to a htm file,
        # so the colors (set in settings.json) will be displayed. 
        artist = '<span style="color:' + settings['colors']['musicArtist'] + '">' + artist + '</span>' 
        title = '<span style="color:' + settings['colors']['musicTitle'] + '">' + title + '</span>'
    
        # returns touple
        return title, artist, musicWindowTitle

def getActiveTouple(musicToupleOld):
    # This function is to return currently activated window.
    # (The Active window is the one "marked" on the taskbar)
    # It not just returns the Window Title but reorders the content and
    # "beautifies" it by "injecting" HTML/CSS and icons in the string.
    # Colors just work with normal hexcodes (settings.json)

    # Icons work with using some obscure UniCode symbols with a font that changes these to symbols.
    # I here use assets/casnf.woff2. Its from Nerdfonts.com.
    # You don't have to use woff2s. otfs or ttfs should also work. 
    # The font you set in settings.json will not change the icons. 
    # The Icons allways use assets\casnf.woff2.  

    # Sets activeWindow to the active window Title (String)
    activeWindow = GetWindowText(GetForegroundWindow()) 
    activeWindowText = activeWindow                    

    # Now to the reordering and beautifying.
    # First there are some general things that i just "cut short" 
    # All of these steps are done with RegEx Substitution.
    # There is also in the same step HTML/CSS injected, for colors.

    #old activeWindow: OBS 27.2.4 (64-bit, windows) - Profile: Nx2 - Scenes: V-Cam
    #new activeWindow: <span style="color:#8f8f8f"> OBS</span>
    activeWindow = re.sub("^(OBS ).*", r'<span style="color:' + settings['colors']['OBS'] + r'"> OBS</span>', activeWindow)

    # This removes a wired rtm mark https://www.compart.com/de/unicode/U+200E
    # that casued problems (occurs with notepads) 
    activeWindow = re.sub('‎', '', activeWindow)

    # removes unesserary complication with UNICODE
    activeWindow = re.sub('–', '-', activeWindow) 

    # Removes path from No-Name programs
    # (Programs with no defined Window-Title have the Path as Title) 
    activeWindow = re.sub(r'^([A-Z]:)(.*\\)+(.*)', r'\3', activeWindow)  

    # removes notification-brackets like (1) or (58) 
    # For example Reddit has these in the title
    activeWindow = re.sub(r'(.*)\([0-9]{1,3}\) (.*)', r'\1\2', activeWindow)   #.. The Video Title - YouTube — Mozilla Firefox

   
    # The following stuff is to seperate the Program out of the window title.
    # Many programs have their name at the end of the Window-Title. For example
    # qna - Discord
    # (= Discord in a channel called qna)
    # So I just define a string "endstring" that is this chars behind the hyphen.
    # not every Program has a normal  Ascii 45 as dash, so the regex is a bit more complicated.

    endString = re.sub(r'(.*)( [—-] )(.*)$', r'\3', activeWindow, re.UNICODE)  #.. Mozilla Firefox
    programPrefix = "" 
    extensionSuffix = "" 
    # Now a fat mach (switch) case. 
    # This does all the programs reordering (splitting into programPrefix)and HTML/CSS injecting 
    # For Browsers it has a nested machcase for websides
    # For IDEs/Editors it has a nested machcase for filetypes  
    match endString:   
        case "Mozilla Firefox":
            programPrefix = re.sub(r'(.*) — Mozilla Firefox', r'<span style="color:' + settings['colors']['Firefox'] + r'"> Firefox:</span> ', activeWindow)  #.. <span style="color:#hexfromsettings"> Firefox:</span> 
            activeWindow = re.sub(r'(.*) — Mozilla Firefox', r'\1', activeWindow)                                                                         #.. The Video Title - YouTube
            website = re.sub(r'(.*)( [-\|] )(.*)$', r'\3', activeWindow) #.. Youtube                                                                   
            match activeWindow:
                case "YouTube": activeWindow = '<span style="color:' + settings['colors']['YouTube'] + '"> YouTube</span>'
                case "Twitch": activeWindow = '<span style="color:' + settings['colors']['Twitch'] + '"> Twitch</span>'
                case "Wikipedia": activeWindow = '<span style="color:' + settings['colors']['Wikipedia'] + '"> Wikipedia</span>'
                case "Wikiwand": activeWindow = '<span style="color:' + settings['colors']['Wikiwand'] + '"> Wikiwand</span>'
                case "Netflix": activeWindow = '<span style="color:' + settings['colors']['Netflix'] + '">ﱄ Netflix</span>'
                case "Google": activeWindow = '<span style="color:' + settings['colors']['Google'] + '"> Google</span>'
                case _:
                    # Google changes Titles in diffrent languages
                    # This is to accompany this.                    
                    if website == settings['strings']['googleSearchInYourLanguage']:
                        website = "Google Search"

                    match website:
                        case "Google Search": 
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??- Google Suche', r'<span style="color:' + settings['colors']['Google'] + r'"> Google:</span> \1', activeWindow)      
                        case "YouTube":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)                                                          #.. <span style="color:#ff5405"> Firefox on</span> 
                            activeWindow = re.sub(r'(.*)??( - )+?YouTube', r'<span style="color:' + settings['colors']['YouTube'] + r'"> YouTube:</span> \1', activeWindow) #.. <span style="color:#ff2e2e"> YouTube:</span> The Video Title 
                        case "Wikipedia":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( - )+?Wikipedia', r'<span style="color:' + settings['colors']['Wikipedia'] + r'"> Wikipedia:</span> \1', activeWindow)
                        case "Wikiwand":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( - )+?Wikiwand', r'<span style="color:' + settings['colors']['Wikiwand'] + r'"> Wikiwand:</span> \1', activeWindow)
                        case "Twitch":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( - )+?Twitch', r'<span style="color:' + settings['colors']['Twitch'] + r'"> Twitch:</span> \1', activeWindow)   
                        case "IMDb":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( - )+?IMDb', r'<span style="color:' + settings['colors']['IMDb'] + r'"> IMDb:</span> \1', activeWindow) 
                        case "Netflix":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( - )+?Netflix', r'<span style="color:' + settings['colors']['Netflix'] + r'">ﱄ Netflix:</span> \1', activeWindow)
                        case "HS Mittweida":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( \| )+?', r'<span style="color:' + settings['colors']['HSMW'] + r'"> HSMW:</span> \1', activeWindow) 
                        case "Stack Overflow":
                            programPrefix = re.sub(r'Firefox:', r'Firefox ' + settings['strings']['on'] + r' ', programPrefix)
                            activeWindow = re.sub(r'(.*)??( \ )+?Stack Overflow', r'<span style="color:' + settings['colors']['StackOverflow'] + r'">  Stack Overflow:</span> \1', activeWindow)  
                        case _: pass

        case "Adobe Acrobat Reader DC (64-bit)":
            programPrefix = re.sub(r'(.*) - Adobe Acrobat Reader DC \(64-bit\)', r'<span style="color:' + settings['colors']['AdobeAcrobatReaderDC'] + r'"> Acrobat:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Adobe Acrobat Reader DC \(64-bit\)', r'\1', activeWindow)
        case "Discord":
            programPrefix = re.sub(r'(.*) - Discord', r'<span style="color:' + settings['colors']['Discord'] + r'">ﭮ Discord:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Discord', r'\1', activeWindow)
        case "Visual Studio Code":
            # symbols for certain extensions (if you set the font to a nerdfont in your editor to can see them here too)
            extensionSuffix = re.sub(r'(.*)\.([a-z]*) - (.*)',r'\2', activeWindow) #.. py
            match extensionSuffix:        
                    case "py":
                        extensionSuffix = "  "                                         #..    
                    case "html":
                        extensionSuffix = "  " 
                    case "java":
                        extensionSuffix = "  " 
                    case "ini":
                        extensionSuffix = " 煉 " 
                    case "txt":
                        extensionSuffix = "  " 
                    case "htm":
                        extensionSuffix = "  " 
                    case "json":
                        extensionSuffix = " ﬥ " 
                    case "ahk":
                        extensionSuffix = "  "  
                    case "js":
                        extensionSuffix = "  "  
                    case "css":
                        extensionSuffix = "  "    
                    case "sh":
                        extensionSuffix = "  "  
                    case _:
                        extensionSuffix = ""   
            programPrefix = re.sub(r'(.*) - Visual Studio Code', r'<span style="color:' + settings['colors']['VSCode'] + r'"> VS Code:</span> ', activeWindow)
            activeWindow = re.sub(r'(●)? ?(.*) - Visual Studio Code', r'\2' + extensionSuffix + r'<span style="color:' + settings['colors']['VSCodeUnsaved'] + r'">\1</span>', activeWindow)
            activeWindow = re.sub(r'●', settings['strings']['VSCodeUnsaved'], activeWindow)
        case "OneNote":
            programPrefix = re.sub(r'(.*) - OneNote', r'<span style="color:' + settings['colors']['MSOneNote'] + r'">ﱅ OneNote:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - OneNote', r'\1', activeWindow)
        case "Word":
            programPrefix = re.sub(r'(.*) - Word', r'<span style="color:' + settings['colors']['MSWord'] + r'"> Word:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Word', r'\1', activeWindow)
        case "Excel":
            programPrefix = re.sub(r'(.*) - Excel', r'<span style="color:' + settings['colors']['MSExcel'] + r'"> Excel:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Excel', r'\1', activeWindow)
        case "PowerPoint":
            programPrefix = re.sub(r'(.*) - PowerPoint', r'<span style="color:' + settings['colors']['MSPowerPoint'] + r'"> PowerPoint:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - PowerPoint', r'\1', activeWindow)
        case "Notepads":
            programPrefix = re.sub(r'(.*) - Notepads', r'<span style="color:' + settings['colors']['Notepads'] + r'"> Notepads:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Notepads', r'\1', activeWindow)
        case "Mozilla Thunderbird":
            programPrefix = re.sub(r'(.*) - Mozilla Thunderbird', r'<span style="color:' + settings['colors']['Thunderbird'] + r'"> Thunderbird:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Mozilla Thunderbird', r'\1', activeWindow)
        case "GIMP":
            programPrefix = re.sub(r'(.*) - GIMP', r'<span style="color:' + settings['colors']['GIMP'] + r'"> GIMP:</span> ', activeWindow)
            activeWindow = re.sub(r'\[(.+?)\].+? ([0-9]+x[0-9]+) - GIMP', r'\1 \2', activeWindow)   
        case "Paint":
            programPrefix = re.sub(r'(.*) - Paint', r'<span style="color:' + settings['colors']['Paint'] + r'"> Paint:</span> ', activeWindow)
            activeWindow = re.sub(r'(.*) - Paint', r'\1', activeWindow)
        case _: pass
     
    if programPrefix == activeWindow: # for programs that dont say what programPrefix they are in the window title or programs not yet implented 
        programPrefix = ""
    if activeWindow == musicToupleOld:
        activeWindow = ""
     
    # Some Programs only have the Program in the Title 
    # So they are beautifyed here 
    activeWindow = re.sub('Joplin', '<span style="color:' + settings['colors']['Joplin'] + '"> Joplin</span>', activeWindow)
    activeWindow = re.sub('Mozilla Firefox', '<span style="color:' + settings['colors']['Firefox'] + '"> Firefox</span>', activeWindow)
    activeWindow = re.sub('PowerShell', '<span style="color:' + settings['colors']['PowerShellCore'] + '"> PowerShell Core</span>', activeWindow) 
    activeWindow = re.sub(r'(Select )?Python 3.[0-9][0-9]? \(64-bit\)', r'<span style="color:' + settings['colors']['Python3'] + r'"> Python 3</span>', activeWindow) 
    activeWindow = re.sub('GNU Image Manipulation Program', '<span style="color:' + settings['colors']['GIMP'] + '"> GIMP</span>', activeWindow)
    activeWindow = re.sub('python3\.10\.exe', '<span style="color:' + settings['colors']['Python3'] + '"> Python 3</span>', activeWindow)
    activeWindow = re.sub('Spotify Premium', '<span style="color:' + settings['colors']['musicIconColor'] + '">' + settings['strings']['musicIcon'] + settings['strings']['musicSource'][:-4] + '</span>', activeWindow)
    
    return programPrefix, activeWindow, activeWindowText # returns touple 

def main(): 

    # Set unused Strings empty to initialize
    musicIcon = title = musicWord = artist = musicToupleOld  = musicActiveDivide = programPrefix = activeWindow = musicWindowTitle = ""

    # This makes a keyboard for key emulation 
    # This will be used later to tell OBS that something happened through the use of Hotkeys
    keyboard = Controller() 

            
    # CSS styling is "injected" for the musicIcon and the musicWord,
    # so that colors are there
    musicWord = '<span style="color:'+ settings['colors']['musicWordColor'] + '">' + settings['strings']['musicWord'] + '</span>'
    musicIcon = '<span style="color:'+ settings['colors']['musicIconColor'] + '">' + settings['strings']['musicIcon'] + '</span>'

    # initialzes musicActiveDivide
    musicActiveDivide = settings['strings']['musicActiveDivider'] 



    # This is to determine if the script is to display Music Info
    # It checks for the settings boolean from the json, if the Process is running and
    # if there is a song playing 
    # If not, music info will not be displayed.
    # So to say it sets the doMusic boolean. 
    if settings["showMusicByDefault"] == True: 
        if checkIfProcessRunning(settings['strings']['musicSource']):
            musicHWND = getMusicHWND()
            doMusic = True
            
        else:
            print(f"{settings['strings']['musicSource']} was not detected.") 
            doMusic = False
            musicToupleOld = musicWord = musicIcon = musicActiveDivide = "" 
    else:
        print("Music displaying is disabled in Settings.json.")
        doMusic = False
        musicToupleOld = musicWord = musicIcon = musicActiveDivide = "" 


    # This is the loop that Runns all the time.
    try:
        while(True):
            if doMusic:
                # sets musicTouple to the current (Artist, Title)
                musicTouple = getMusicTouple(musicHWND)

                # This is to determine if the Song has changed.
                # it does that by comparing the new musicTouple to the old one 
                # the old one is at first just "" and then
                # overwritten when they are different
                if musicTouple == musicToupleOld:
                    print('Music remains unchanged.')
                else:
                    # old one overwritten (see)
                    musicToupleOld = musicTouple

                    # if the Song has changed,
                    # the Stings artist and title are set.
                    # they will be written to file later.
                    # They allready have the CSS and HTML "injected"
                    # This is done in the getMusicTouple function.
                    title = musicTouple[0]
                    artist = musicTouple[1]
                    musicWindowTitle = musicTouple[2]
                    
                    # if the music is idle, make all music related strings empty
                    if artist == "" and title == "":
                        print("Music is idle. (Nothing is playing)") 
                        musicIcon = ""
                        musicWord = "" 
                        musicActiveDivide = ""
                    else: 
                        # "reset" the the variables
                        musicWord = '<span style="color:'+ settings['colors']['musicWordColor'] + '">' + settings['strings']['musicWord'] + '</span>'
                        musicIcon = '<span style="color:'+ settings['colors']['musicIconColor'] + '">' + settings['strings']['musicIcon'] + '</span>'
                        musicActiveDivide = settings['strings']['musicActiveDivider']
                    # This is for telling OBS when musicWindowTitle changed.
                    # You may do with that what youw want.
                    # I use it to display the cover image of the song with an OBS plugin called Tuna.
                    # It presses RAlt+F15
                    keyboard.press(Key.alt_r)   
                    time.sleep(0.05)            
                    keyboard.press(Key.f15)     
                    time.sleep(0.05)            
                    keyboard.release(Key.f15)   
                    time.sleep(0.05)            
                    keyboard.release(Key.alt_r) 

                    print('Music Updated.')
            else:
                musicToupleOld = ("", "", "")

                    
            # The following 2 lines set how fast the Script runs.
            # Faster = better, but also more ressource heavy.
            # The Time can be set in the settigs.json under 'time'
            # by default it checks Active every second
            # and Music every 5 seconds 
            for y in range(settings['time']['musicTickRate']):                 
                time.sleep(settings['time']['baseTickRate'])    
                # This is the same thing as up there the getMusicTouple
                # but with Active this time. 
                activeTouple = getActiveTouple(musicToupleOld) 
                programPrefix = activeTouple[0]
                activeWindow = activeTouple[1]
                activeWindowTile = activeTouple[2]
                
                # This is so that if you focus the 
                # Music Exe, yone only sees the music
                # otherwise one chould see Music "twice"
                if activeWindow == musicWindowTitle:
                    activeWindow = ""

                # Prints the unbeautified Active WinTile
                print('Active updated: ' + activeWindowTile)

                # This combines all the diffrent strings into "writeme"
                writeme = musicIcon + title + musicWord + artist + musicActiveDivide + programPrefix + activeWindow

                # This opens assets/stringme_tamplate.htm 
                # and saves it's content as string
                # in fullHtmlString 
                f = open(__path + "assets/stringme_tamplate.htm", "r", encoding="utf-8") # somehow it crashes here without literal path if not run in vs code on my machine
                fullHtmlString = f.read()
                f.close()

                # This replaces the placeholder text from 
                # assets\stringme_tamplate.htm in fullHtmlString
                # This is done with a RegEx-Substitution
                fullHtmlString = re.sub(r'<p class="n", style="color: #ffffff;">this will be replaced</p>', r'<p class="n", style="color:'+ settings['colors']['base'] + ';">' + writeme + r'</p>', fullHtmlString)

                # finnlay stringme.htm is fully overwritten
                # with the correct format and content               
                f = open(__path + "stringme.htm", "w", encoding="utf-8")
                f.write(fullHtmlString)
                f.close() 

    except Exception as e:
        f = open("errorlog.txt", "a")
        f.write('\n')
        f.write(str(e))
        f.close()               

if __name__ == "__main__":
    main()



