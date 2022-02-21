# stringme-OBS
A Script providing a way to show the currently active window and playing music live on screen. Using the windows window title and OBS' local-file browser scource.



This is windows only. As of now the script is just configured to work with [Spotify-Premium-desktop](https://www.spotify.com/de/download/windows/) as music source. And even that is kinda janky as of now since to obtain th window handle of Spotify.exe you will need to have it as activated window (4) seconds after starting `stringme.py`. Also the "fancy" features as like Program highlighting is only implemented for

* Firefox
* Discord
* Visual Studio Code
* Adobe Acrobat Reader
* Microsoft Word, Excel, Powerpoint and OneNote
* [Notepdas](https://github.com/JasonStein/Notepads) 

And Websides currently implementented:
* YouTube
* Twitch
* Wikipedia (+Wikiwand)

If something isn't listed here it will still be dispayed but not with color and or icon.

##To use it in OBS (fist time):
1. Make sure you have Python3 installed on your machine. Also you will need to install some packages with pip for python. If you dont know what that means look it up or maybe watch [this video](https://youtu.be/7snh_1Hf_TI). I'll just write down all packages you'll need: 
3. Run `stringme.py`
4. Have Spotify.exe window activated (click on the window or on the taskbar icon) within `4` seconds of Step 3
5. Add a new source where you want it to be displayed. Choose Browser source. Check the local file checkbox. Navigate to where you saved the files from this repro and choose `stringme.htm` (Not `stringme_tamplate.htm`!). Delete all contents from the "Custom CSS" box. Check Reload by scene switch. Set the dimensions to ⇅`45` and ⇄`2000`. Click finish.
7. Alt drag the right side of the new source so the scrollbar is hidden. 
8. If nothing is dispayed click reload on the browser scource and make sure the script is still running. 
9. I like to hide the script window from the taskbar with AHK or like [this](https://answers.microsoft.com/en-us/windows/forum/all/how-can-i-hide-a-specific-program-in-the-system/f7f09999-9397-44e8-b1d0-792a49d3721b). 

To use it every time after the first:
1. Run `stringme.py`
3. Have Spotify.exe window activated (click on the window or on the taskbar icon) within ´`4` seconds of Step 1
4. hide the scipt so that if doesnt take up space on the taksbar

 Things to improove (contributions are welcome!): 
 * more programs and websides to implement 
 * Due to the large size of the font the browser source "flickes" every so often because it reloads every second and the font file has to be loaded again. A way around that would be nice. 
 * Not having to activate spotify on every start (maybe with PID and enumerate windows but I dont know)
