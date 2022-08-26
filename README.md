# stringme-OBS
**A way to show what you're actively doing + now playing in one line in OBS.**

[![Watch the video](https://i.imgur.com/24l747X.png)](https://youtu.be/4zdsZl--wLY)

(↑↑ Click me I'm a Video!)

This is windows only. 

## Currently implemented are:
* Firefox
  - Google.com, YouTube.com, Twitch.tv , Wikipedia.org + Wikiwand.com, IMDb.com, hs-mittweida.de, Netflix.com, StackOverflow.com
* Discord
* Visual Studio Code
  - Saved or Unsaved
  - Icons for extensions `.py`, `.html`, `.htm`, `.java`, `.ahk`, `.json`, `.ini`, `.txt`, `.js`, `.css`, `.sh`
* Adobe Acrobat Reader
* Microsoft Word, Excel, Powerpoint and OneNote
* [Notepdas](https://github.com/JasonStein/Notepads) 
* Joplin
* Obsidian
* Mozilla Thunderbird
* Powershell Core
* Python 3 Shell
* Spotify (Premium)
* GIMP
* Paint

> These are everything I use. Contributions for more Programs/Websites are welcome!
If something isn't listed here it will still be dispayed but not with color and or icon.

## To use it in OBS (fist time):
1. Make sure you have Python3.10 or greater installed on your machine. Also you will need to install all packages in reqirements.txt with pip for python. If you want do do it manually and don't know what that means look it up or maybe watch [this video](https://youtu.be/7snh_1Hf_TI). Or just run ↓ whilest in the `/StringMe-OBS` fodler.

```shell
python -m pip install pywin32
pip install -r requirements.txt
``` 
> Make sure the `python` command also corresponds with `Python 3.10.xx`. You can check with zhe command `python --version`.
> If it errors, you might have not set up pip corretctly. Read: [help](https://pip.pypa.io/en/stable/installation/).

2. Run OBS
3. Run `stringme.py` with Python3
   In Powershell with `python3 .\StringMe-OBS.py` 
   In File Explorer by right clicking it, open with, Pyhton 3.*Version*.
4. Add a new source where you want it to be displayed. Choose Browser source. Check the local file checkbox. Navigate to where you saved the files from this repro and choose `stringme.htm` (Not `stringme_tamplate.htm`!). Set the dimensions (⇅`70`, ⇄`2000` worked for me). Delete all contents from the "Custom CSS" box. Check " shutdown source when not visible". Check "Refresh browser when screen becomes active".  Click OK.
5. If necessary alt-drag the right side of the new source so the scrollbar is hidden. 
6. If nothing is dispayed click reload on the browser scource and make sure the script is still running. 
7. Hide `python.3.##.exe` from the Taskbar (if you want) with AHK or like [this](https://answers.microsoft.com/en-us/windows/forum/all/how-can-i-hide-a-specific-program-in-the-system/f7f09999-9397-44e8-b1d0-792a49d3721b). There is usefull console output, but your viewers won't gain much from it. 


## To use it every time after the first:
1. Run OBS
2. Run `stringme.py`
3. Hide `python.3.##.exe` (if you want)

## Behaviour Tips
* It will only display Spotify info if Spotify.exe was already running when the Script started. *This is done to minimize Ressorce requirements*  
* If for some reason after some time nothing is displayed in OBS, reload the browser source. (This means there was a bug in the code for a usecase I have not tested yet. You may file a bug report.)
* If the program crashes file a bug report and include the content of errorlog.txt and what to do to recreate the bug.
---
## Customization
There are a lot of things to set up in settings.json. You will need to restart the Program to see things change. 
The following will elaborate on what the lines each do:

- **"showMusicByDefault"**: set false to never display music info (Also saves ressorces)
- **"colors"**: Explains itself. Please only use 6 character long hex codes. (Things like `#000` or `blue` break the code!)
- **"on"**: Customize "Firefox`on`Website"
- **"musicWord"**, **"musicIcon"**, **"musicActiveDivider"**: Customize Format of "whats around" the Song name and Artist name
- **"musicSource"**: I only tested Spotify Premium, but maybe there are other programs that have their Info in the window title. You can set the exe name here and try.
- **"musicIdle"**: When nothign is playing, this is what the exe's window title is. 
- **"VSCodeUnsaved"**: is what will be displayed after everything, when the file you're working on is unsaved
- **"googleSearchInYourLanguage"**: Google.com changes it's window title depending your language. You can account for that here.
- **"HotKey"**: Sets the Hot Key for Selective Modes (Read extra Features ↓) 
- **"baseTickRate"**: time in seconds the program "reloads". Less means faster response time, but more ressource intensive.  
- **"musicTickRate"**: Sets how often it'll "reload" the music info (So, e.g. baseTickRate:1 and MusicTickRate:5 means every 5 seconds).
- **"cutMusicTitle"**: If the title is longer than "musicTitle" cut it short?
- **"musicTitle"**: Sets Max Length for a music Title
- **"cutActive"**: If the The active title should be cut if its too long
- **"totalLengthFixed"**: Sets Max Length for everything displayed combined
- **"useDynamicMaxLengthFile"**: If true the dynamic cuuting will be done (Read extra Features ↓) 
---
## Extra Feastures
### Selective Modes
- Cycle between [Music and Active], [Music only], [Active only] and [Both disabled] with a hotkey 
- You can set the Hotkey in the settings.json file
- [Here](https://css-tricks.com/snippets/javascript/javascript-keycodes/) you can find a guide for key-codes 

### Shorten Music and Active
there are options in settings.json to "cut short" too long strings, including the song title and active
![](https://i.imgur.com/8WJTJZS.png)

#### Dynamic Cutting
If "useDynamicMaxLengthFile" is enabled in settings.json, the "totalLengthFixed" will be ignored and the total length will instead be read from the assets\dynamicMaxLength.txt at every base step. *(For example, every time you change your scene with a hotkey, the hothey could also change the content of the file)*
