import os
from win32gui import GetWindowText, GetForegroundWindow
from datetime import datetime
from pynput.keyboard import Key, Controller
from pynput import keyboard
import psutil, win32process, win32gui, re, time, json, multiprocessing

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

# https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
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
    # the comments to the side stering with #.. are an example what happens to a string at each step.
    musicWindowTitle = GetWindowText(musicHwnd)                                             #.. Amy Lee - Speak to Me (From "Voice from the Stone" Original Motion Picture Soundtrack)

    # Since we work with HTLM later on, "<" have to be protcted
    # We also count for knowing "where to cut" later
    lessThansReplacedMusic = 0
    lessThansReplacedMusic = musicWindowTitle.count('<')
    if lessThansReplacedMusic != 0:
        musicWindowTitle = re.sub(r'([^\\])<', r'\1&lt;', musicWindowTitle)

    if musicWindowTitle == settings['strings']['musicIdle'] or musicWindowTitle == "":
        return "", "", ""
    else:   
        artist = re.sub(r'^(.*?) - .*', r'\1', musicWindowTitle)                            #.. Amy Lee
        title = re.sub(artist + " - ", '', musicWindowTitle)                                #.. Speak to Me (From "Voice from the Stone" Original Motion Picture Soundtrack) 
        
        # This removes brackets and content from brackets 
        # This is not neccessary, you may comment that out
        # if you want to keep the brackets
        # it often gets realy long with them (see example)
        title = re.sub(r'(.*)\(.*\)(.*)', r'\1\2', title)                                   #.. Speak to Me
        title = re.sub(r'(.*)\[.*\](.*)', r'\1\2', title)                                   # same idea with [] Brackets

            
        # Cut title further if its longer than the set maxLength.
        # Try cuting everything after  " - " or " | ", if its still too long
        # just cut after the in settings.json set length
        if settings['maxLengths']['cutMusicTitle']:
            if len(title) > int(settings['maxLengths']['musicTitle']):
                if " - " in title or " | " in title:
                    title = title[:title.index(" - ")]
                if len(title) > int(settings['maxLengths']['musicTitle']):
                    title = title[:int(settings['maxLengths']['musicTitle'])] + "…"


        # The next 2 lines "inject" HTML/CSS in the string. 
        # later it will be written to a htm file,
        # so the colors (set in settings.json) will be displayed. 
        artist = '<span style="color:' + settings['colors']['musicArtist'] + '">' + artist + '</span>' 
        title = '<span style="color:' + settings['colors']['musicTitle'] + '">' + title + '</span>'
             
        # returns touple
        return title, artist, musicWindowTitle, lessThansReplacedMusic

def getActiveTouple(musicToupleOld, doMusicRightNow, hotkeyStatus, lessThansReplacedMusic):
    # This function is to return stuff related to the currently activated window.
    # (The Active window is the one "marked" on the taskbar)
    # It also reorders and "beautifies" by "injecting" HTML/CSS and icons in the strings.
    # Colors just work with normal hexcodes (settings.json)

    # Icons work with using some obscure UniCode symbols with a font that changes these to symbols.
    # I here use assets/casnf.woff2. Its from Nerdfonts.com.
    # You don't have to use woff2s. otfs or ttfs should also work. 
    # The font you set in settings.json will not change the icons. 
    # The Icons allways use assets\casnf.woff2.  

    # Comments staring with #.. are examples what happens at each line

    # Sets active to the active window Title (String)
    active = GetWindowText(GetForegroundWindow()) 
    activeWindowTextUntouched = active                    

    # Since we work with HTLM later on, "<" have to be protcted
    # We also count for knowing "where to cut" later
    lessThansReplaced = 0
    lessThansReplaced = active.count('<')
    if lessThansReplaced != 0:
        active = re.sub(r'([^\\])<', r'\1&lt;', active)

    # Now to the reordering and beautifying.
    # First there are some general things that I just "cut short" 
    # All of these steps are done with RegEx Substitution.
    # There is also in the same step HTML/CSS injected, for colors.

    # This removes a wierd rtm mark https://www.compart.com/de/unicode/U+200E
    # that casued problems (occurs with notepads) 
    active = re.sub('‎', '', active)

    # removes unesserary complication with UNICODE
    active = re.sub('–', '-', active) 

    # Removes path from No-Name programs
    # (Programs with no defined Window-Title have the full Path as Title) 
    active = re.sub(r'^([A-Z]:)(.*\\)+(.*)', r'\3', active)  

    # removes notification-brackets like (1) or (58) 
    # For example Reddit has these in the title
    active = re.sub(r'(.*)\([0-9]{1,3}\) (.*)', r'\1\2', active)   

    # changes PowerPoint-Bildschirmpräsentation and PowerPoint-Referentenansicht to just "Powerpoint"
    # also swaps the order becuse pwpnt has it backwards for some reason
    if re.search("PowerPoint-Bildschirmpräsentation", active):
        active = re.sub(r'PowerPoint-Bildschirmpräsentation  -  (.*)', r'\1 - PowerPoint', active)
    active = re.sub(r'(PowerPoint-Referentenansicht)',r'PowerPoint', active)
    
    # Also jsut to initite some strings, what they do will be explained later
    isActiveCutString = program = extensionSuffix = website = unsavedMark = ""

    # The following stuff is to seperate the Program out of the window title.
    # Many programs have their name at the end of the Window-Title. For example
    # qna - Discord
    # (= Discord in a channel called qna)
    # So I define a string "endstring" as the chars behind the hyphen.
    # (not every Program has a normal  Ascii 45 as dash, so the regex is a bit more complicated)

    endString = re.sub(r'(.*)( [—-] )(.*)$', r'\3', active, re.UNICODE)  #.. Mozilla Firefox

    # this function is used below to beautify websites 
    # (for multiple browsers (thats why it's a function)) 
    def websites(active, program, website):
        match active:
            # when you are on a Startpage, the title often just says the name of the website.
            # Here we beautify those.
            case "YouTube": 
                active = ''                                                                           
                program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)          # These here for the "Startpages"
                website = '<span style="color:' + settings['colors']['YouTube'] + '"> YouTube</span>'                # they have only the Site name and nothing more
            case "Twitch": 
                active = ""
                program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                website = '<span style="color:' + settings['colors']['Twitch'] + '"> Twitch</span>'
            case "Wikipedia": 
                active = ""
                program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                website = '<span style="color:' + settings['colors']['Wikipedia'] + '"> Wikipedia</span>'
            case "Wikiwand": 
                active = ""
                program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                website = '<span style="color:' + settings['colors']['Wikiwand'] + '"> Wikiwand</span>'
            case "Netflix": 
                active = ""
                program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                website = '<span style="color:' + settings['colors']['Netflix'] + '">ﱄ Netflix</span>'
            case "Google": 
                active = ""
                program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                website = '<span style="color:' + settings['colors']['Google'] + '"> Google</span>'
            # the _ case is for every non startpage
            case _:
                # Google changes Titles in diffrent languages
                # This is to accompany this.                    
                if website == settings['strings']['googleSearchInYourLanguage']:
                    website = "Google Search"

                match website:  
                    # these are for "subpages", like a specific Video on YT, not just youtube.com
                    # we have to 1. 
                    case "Google Search": 
                        active = re.sub(r'(.*)??- ' + settings['strings']['googleSearchInYourLanguage'], r'\1', active)
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['Google'] + '"> Google: </span>'      
                    case "YouTube":
                        active = re.sub(r'(.*)??( - )+?YouTube', r'\1', active)                                         #.. The Video Title 
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)    #.. <span style="color:#ff5405"> Firefox on</span> 
                        website = '<span style="color:' + settings['colors']['YouTube'] + '"> YouTube: </span>'        #.. <span style="color:#ff2e2e"> YouTube:</span>
                    case "Wikipedia":
                        active = re.sub(r'(.*)??( - )+?Wikipedia', r'\1', active)
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['Wikipedia'] + '"> Wikipedia: </span>'
                    case "Wikiwand":
                        active = re.sub(r'(.*)??( - )+?Wikiwand', r'\1', active)
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['Wikiwand'] + '"> Wikiwand: </span>'
                    case "Twitch":
                        active = re.sub(r'(.*)??( - )+?Twitch', r'\1', active)   
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['Twitch'] + '"> Twitch: </span>'   
                    case "IMDb":
                        active = re.sub(r'(.*)??( - )+?IMDb', r'\1', active) 
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['IMDb'] + '"> IMDb: </span>' 
                    case "Netflix":
                        active = re.sub(r'(.*)??( - )+?Netflix', r'\1', active)
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['Netflix'] + '">ﱄ Netflix: </span>'
                    case "HS Mittweida":
                        active = re.sub(r'(.*)??( \| )+?', r'\1', active) 
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['HSMW'] + '"> HSMW: </span>' 
                    case "Stack Overflow":
                        active = re.sub(r'(.*)??( - )+?Stack Overflow', r'\1', active)  
                        program = re.sub(r'(.*): </span>', r'\1' + settings['strings']['on'] + r' </span>', program)
                        website = '<span style="color:' + settings['colors']['StackOverflow'] + '">  Stack Overflow: </span>'  
                    case _: 
                        website = ""
        return active, program, website          

    # Now a fat match (switch) case. 
    # This does all the programs reordering (splitting into program)and HTML/CSS injecting 
    # For Browsers it has a nested machcase for websides
    # For IDEs/Editors it has a nested machcase for filetypes  
    match endString:   
        case "Mozilla Firefox":
            # taking the "Mozilla Firefox" out of active
            active = re.sub(r'(.*) [—-] Mozilla Firefox', r'\1', active)                                #.. The Video Title - YouTube

            # setting program. With HTML                                                                
            program = '<span style="color:' + settings['colors']['Firefox'] + '"> Firefox: </span>'    #.. <span style="color:#hexfromsettings"> Firefox:</span> 

            # setting website. WithOUT HTML                                                                
            website = re.sub(r'(.*)( [-\|] )(.*)$', r'\3', active)                                      #.. Youtube

            # this calls the function and then saves the variables "back" from the 
            # touple, the funtion returns, to the 3 variables                                                                                                                                                     
            websitesTouple = websites(active, program, website) 
            active = websitesTouple[0]                                                                             
            program = websitesTouple[1]  
            website = websitesTouple[2]
        case "Google Chrome":
            active = re.sub(r'(.*) [—-] Google Chrome', r'\1', active)                                  
            program = '<span style="color:' + settings['colors']['Chrome'] + '"> Chrome: </span>'        
            website = re.sub(r'(.*)( [-\|] )(.*)$', r'\3', active)                                                                                                          
            websitesTouple = websites(active, program, website)
            active = websitesTouple[0]                                                                             
            program = websitesTouple[1]  
            website = websitesTouple[2]
        case "Microsoft​ Edge": # ← wierd unicode stuff in there
            # active = re.sub(r'(.*)( and [0-9] more pages?)? - (Personal)?(\[Guest\])? - Microsoft​ Edge', r'\1', active) 
            # For some reason this ↑ line doesn't cut the "and more pages" stuff.
            # Therefore I botched this double re.sub() with an if re.match() together
            active = re.sub(r'(.*) - (Personal)?(\[Guest\])? - Microsoft​ Edge', r'\1', active) 
            if re.match(r'.* and [0-9]+ more pages?', active):
                active = re.sub(r'(.*)( and [0-9] more pages?)', r'\1', active)
            program = '<span style="color:' + settings['colors']['Edge'] + '"> Edge: </span>'        
            website = re.sub(r'(.*)( [-\|] )(.*)$', r'\3', active)                                                                                                          
            websitesTouple = websites(active, program, website)
            active = websitesTouple[0]                                                                             
            program = websitesTouple[1]  
            website = websitesTouple[2]
        case "Adobe Acrobat Reader DC (64-bit)":
            program = re.sub(r'(.*) - Adobe Acrobat Reader DC \(64-bit\)', r'<span style="color:' + settings['colors']['AdobeAcrobatReaderDC'] + r'"> Acrobat:</span> ', active)
            active = re.sub(r'(.*) - Adobe Acrobat Reader DC \(64-bit\)', r'\1', active)
        case "Discord":
            program = re.sub(r'(.*) - Discord', r'<span style="color:' + settings['colors']['Discord'] + r'">ﭮ Discord:</span> ', active)
            active = re.sub(r'(.*) - Discord', r'\1', active)
        case "Visual Studio Code":
            # symbols for certain extensions (if you set the font to a nerdfont in your editor to can see them here too)
            extensionSuffix = re.sub(r'(.*)\.([a-z]*) - (.*)',r'\2', active) #.. py
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
            program = re.sub(r'(.*) - Visual Studio Code', r'<span style="color:' + settings['colors']['VSCode'] + r'"> VS Code:</span> ', active)
            if "●" in active:
                unsavedMark = settings['strings']['VSCodeUnsaved']
            else:
                unsavedMark = ""
            active = re.sub(r'(●)? ?(.*) - Visual Studio Code', r'\2' + extensionSuffix, active)
        case "OneNote":
            program = re.sub(r'(.*) - OneNote', r'<span style="color:' + settings['colors']['MSOneNote'] + r'">ﱅ OneNote:</span> ', active)
            active = re.sub(r'(.*) - OneNote', r'\1', active)
        case "Word":
            program = re.sub(r'(.*) - Word', r'<span style="color:' + settings['colors']['MSWord'] + r'"> Word:</span> ', active)
            active = re.sub(r'(.*) - Word', r'\1', active)
        case "Excel":
            program = re.sub(r'(.*) - Excel', r'<span style="color:' + settings['colors']['MSExcel'] + r'"> Excel:</span> ', active)
            active = re.sub(r'(.*) - Excel', r'\1', active)
        case "PowerPoint":
            program = re.sub(r'(.*) - PowerPoint', r'<span style="color:' + settings['colors']['MSPowerPoint'] + r'"> PowerPoint:</span> ', active)
            active = re.sub(r'(.*) - PowerPoint', r'\1', active)
        case "Notepads":
            program = re.sub(r'(.*) - Notepads', r'<span style="color:' + settings['colors']['Notepads'] + r'"> Notepads:</span> ', active)
            active = re.sub(r'(.*) - Notepads', r'\1', active)
        case "Mozilla Thunderbird":
            program = re.sub(r'(.*) - Mozilla Thunderbird', r'<span style="color:' + settings['colors']['Thunderbird'] + r'"> Thunderbird:</span> ', active)
            active = re.sub(r'(.*) - Mozilla Thunderbird', r'\1', active)
        case "GIMP":
            program = re.sub(r'(.*) - GIMP', r'<span style="color:' + settings['colors']['GIMP'] + r'"> GIMP:</span> ', active)
            active = re.sub(r'\[(.+?)\].+? ([0-9]+x[0-9]+) - GIMP', r'\1 \2', active)   
        case "Paint":
            program = re.sub(r'(.*) - Paint', r'<span style="color:' + settings['colors']['Paint'] + r'"> Paint:</span> ', active)
            active = re.sub(r'(.*) - Paint', r'\1', active)
        case _: pass
    
    # Sets variables to "" 
    # for programs that dont say what they 
    # are in the window title 
    # or programs not yet implented in the swich case
    if active == musicToupleOld:
        active = ""
    # Cut lenghts futher. If settings are set.
    if settings['maxLengths']['cutActive']:
        if doMusicRightNow and hotkeyStatus.value < 3: # hotkeyStatus 3 and 4 have both no music
            if program == "":
                # cut enabled, Music, no Program  
                stuffBeforeActiveLenght = len(settings['strings']['musicIcon']) + len(musicToupleOld[0])-35 + len(settings['strings']['musicWord']) + len(musicToupleOld[1])-35 + len(settings['strings']['musicActiveDivider']) + lessThansReplaced*3 + lessThansReplacedMusic*3
            else:
                if website == "":
                    # cut enabled, Music, Program, no Website  
                    stuffBeforeActiveLenght = len(settings['strings']['musicIcon']) + len(musicToupleOld[0])-35 + len(settings['strings']['musicWord']) + len(musicToupleOld[1])-35 + len(settings['strings']['musicActiveDivider']) + len(program)-35 + lessThansReplaced*3 + lessThansReplacedMusic*3
                else: 
                    # cut enabled, Music, Program, Website  
                    stuffBeforeActiveLenght = len(settings['strings']['musicIcon']) + len(musicToupleOld[0])-35 + len(settings['strings']['musicWord']) + len(musicToupleOld[1])-35 + len(settings['strings']['musicActiveDivider']) + len(program)-35 + len(website)-35 + lessThansReplaced*3 + lessThansReplacedMusic*3 
        else:
            if program == "":
                # cut enabled, no Music, no Program 
                stuffBeforeActiveLenght = 0
            else:
                if website == "":
                    # cut enabled, no Music, Program, no Website
                    stuffBeforeActiveLenght = len(program)-35 + lessThansReplaced*3 + lessThansReplacedMusic*3
                else:
                    # cut enabled, no Music, Program, Website
                    stuffBeforeActiveLenght = len(program)-35 + len(website)-35 + lessThansReplaced*3 + lessThansReplacedMusic*3


        # This does the Dynamic Max Length File "getting" 
        # If its disabled, it just gets the Fixed Max Length from the settings.json
        if settings['maxLengths']['useDynamicMaxLengthFile']:
            maxlf = open(__path + "assets/dynamicMaxLength.txt", "r", encoding="utf-8")
            maxLength = int(maxlf.read().strip())
            maxlf.close()
        else: maxLength = int(settings['maxLengths']['totalLengthFixed'])

        # This actually does the cutting, if its to long 
        # It also sets a string which we can print in the Console later
        if maxLength < (stuffBeforeActiveLenght + len(active)):
            isActiveCutString = "Yes"
            cutAt = maxLength - (stuffBeforeActiveLenght + len(active))
            active = active[:cutAt] + "…"
        else:
            isActiveCutString = "No"
        

    # Some Programs only have the Program name in the Title 
    # So they are beautifyed here 
    active = re.sub(r'^(OBS ).*', r'<span style="color:' + settings['colors']['OBS'] + r'"> OBS</span>', active)
    active = re.sub('Joplin', '<span style="color:' + settings['colors']['Joplin'] + '"> Joplin</span>', active)
    active = re.sub('Discord', '<span style="color:' + settings['colors']['Discord'] + '">ﭮ Discord</span>', active)
    active = re.sub('Mozilla Firefox', '<span style="color:' + settings['colors']['Firefox'] + '"> Firefox</span>', active) # start page
    active = re.sub('PowerShell Core', '<span style="color:' + settings['colors']['PowerShellCore'] + '"> PowerShell Core</span>', active) 
    active = re.sub(r'(Select )?Python 3.[0-9][0-9]? \(64-bit\)', r'<span style="color:' + settings['colors']['Python3'] + r'"> Python 3</span>', active) 
    active = re.sub('GNU Image Manipulation Program', '<span style="color:' + settings['colors']['GIMP'] + '"> GIMP</span>', active)
    active = re.sub('python3\.10\.exe', '<span style="color:' + settings['colors']['Python3'] + '"> Python 3</span>', active)
    active = re.sub('Spotify Premium', '<span style="color:' + settings['colors']['musicIconColor'] + '">' + settings['strings']['musicIcon'] + settings['strings']['musicSource'][:-4] + '</span>', active)
    active = re.sub(r'.* - Obsidian v[0-9]+\.[0-9]+\.[0-9]+', '<span style="color:' + settings['colors']['Obsidian'] + '"> Obsidian</span>', active)
    
    # this step is by default completely uneccesary 
    # it just "swaps" active and program,
    # when active starts with html stuff. 
    # But when the order of things is changes by the user in some wierd way, this might be neccesary.
    if active[:18] == '<span style="color':
        program = active 
        active = ""

    # returns touple 
    return program, active, website, unsavedMark, activeWindowTextUntouched, isActiveCutString

# https://pynput.readthedocs.io/en/latest/keyboard.html
def hotkey(hotkeyStatus):
    def on_activate(): 
        print("\nHotkey detected.")
        hotkeyStatus_Lock = multiprocessing.Lock() 
        with hotkeyStatus_Lock:  
            hotkeyStatus.value = hotkeyStatus.value + 1
            if hotkeyStatus.value == 5:
                hotkeyStatus.value = 1

    def for_canonical(f):
        return lambda k: f(l.canonical(k))

    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse(settings['strings']['hotKey']),
        on_activate)
    with keyboard.Listener(
            on_press=for_canonical(hotkey.press), 
            on_release=for_canonical(hotkey.release)) as l:
        l.join()

def main(hotkeyStatus): 
    # Set unused Strings empty to initialize
    musicIcon = title = musicWord = artist = musicToupleOld  = musicActiveDivide = program = active = website = musicWindowTitle = isActiveCutString = ""
    
    # Set unused Booleans
    doMusicRightNow = True

    # This makes a keyboard for key emulation 
    # This will be used later to tell OBS that something happened through the use of Hotkeys
    KeyboardTyper = Controller() 

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
            doMusicRightNow = True
        else:
            musicStatus = f"{settings['strings']['musicSource']} was not detected."
            doMusic = False
            musicToupleOld = musicWord = musicIcon = musicActiveDivide = "" 
    else:
        musicStatus = "Music displaying is disabled in Settings.json."
        doMusic = False
        musicToupleOld = musicWord = musicIcon = musicActiveDivide = "" 

    tick = 1
    musicStatus = ""
    # This is the loop that runns all the time.
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
                    pass
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
                    lessThansReplacedMusic = musicTouple[3]
                    
                    # if the music is idle, make all music related strings empty
                    if artist == "" and title == "":
                        musicStatus = "Music is idle. (Nothing is playing)" 
                        doMusicRightNow = False
                        musicIcon = ""
                        musicWord = "" 
                        musicActiveDivide = ""
                    else: 
                        musicStatus = "Detected" 
                        doMusicRightNow = True
                        # "reset" the the variables
                        musicWord = '<span style="color:'+ settings['colors']['musicWordColor'] + '">' + settings['strings']['musicWord'] + '</span>'
                        musicIcon = '<span style="color:'+ settings['colors']['musicIconColor'] + '">' + settings['strings']['musicIcon'] + '</span>'
                        musicActiveDivide = settings['strings']['musicActiveDivider']
                    # This is for telling OBS when musicWindowTitle changed.
                    # You may do with that what youw want.
                    # I use it to display the cover image of the song with an OBS plugin called Tuna.
                    # It presses RAlt+F15
                    KeyboardTyper.press(Key.alt)   
                    time.sleep(0.05)            
                    KeyboardTyper.press(Key.f15)     
                    time.sleep(0.05)            
                    KeyboardTyper.release(Key.f15)   
                    time.sleep(0.05)            
                    KeyboardTyper.release(Key.alt) 
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
                if hotkeyStatus.value % 2 == 1: # 1 and 3 are with active
                    activeTouple = getActiveTouple(musicToupleOld, doMusicRightNow, hotkeyStatus, lessThansReplacedMusic)
                    program = activeTouple[0]
                    active = activeTouple[1]
                    website = activeTouple[2]
                    unsavedMark = activeTouple[3]
                    activeWindowTile = activeTouple[4]
                    isActiveCutString = activeTouple[5]
                else:
                    program = active = website = unsavedMark = activeWindowTile = isActiveCutString = ""
                    activeWindowTile = "Active deactivated"

                # This is so that if you focus the 
                # Music Exe, yone only sees the music
                # otherwise one chould see Music "twice"
                if active == musicWindowTitle:
                    active = ""

                # This combines all the diffrent strings into "writeme"
                # depending on the Hotkey status
                match hotkeyStatus.value:
                    case 1: writeme = musicIcon + title + musicWord + artist + musicActiveDivide + program + website + active + unsavedMark
                    case 2: writeme = musicIcon + title + musicWord + artist + musicActiveDivide 
                    case 3: writeme = program + website + active + unsavedMark
                    case _: writeme = ""

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


                # clears the screen
                os.system('cls')
                #prints new info to the console
                print("StringMe-OBS - - - Tick: " + str(tick))
                print("-----------")
                print("Music Status: " + musicStatus)
                print("Music: " + musicWindowTitle)
                print("-----------")
                print("Active: " + activeWindowTile)
                print("Is Cut: " + isActiveCutString)
                print("-----------")
                match hotkeyStatus.value:
                    case 1: print("Hotkey: Music & Active")
                    case 2: print("Hotkey: Music Only")
                    case 3: print("Hotkey: Active Only")
                    case 4: print("Hotkey: Both Disabled")
                print("\n\n")
                print("prg: " + program)
                print("web: " + website)
                print("act: " + active)
                print("usm: " + unsavedMark)
                tick += 1

    except Exception as e:
        f = open(__path + "assets/errorlog.txt", "a")
        f.write(str(datetime.now()) + "\n" + str(e))
        f.write('\n\n')
        f.close()               

# Global variable initiation
# somehow it didnt work in the if __name__ statement 
# thats why its commented out
# hotkeyStatus = multiprocessing.Value('i', 1)
# print(type(hotkeyStatus))

if __name__ == "__main__":
    with multiprocessing.Manager() as karen: 

        hotkeyStatus = karen.Value('i', 1)

        pServer = multiprocessing.Process(target=main, args=[hotkeyStatus])
        pHotKey = multiprocessing.Process(target=hotkey, args=[hotkeyStatus])

        pServer.start()
        pHotKey.start()

        pServer.join()
        pHotKey.join()
    



