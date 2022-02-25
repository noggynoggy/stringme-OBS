# stringme-OBS
**A way to show what you're actively doing + now playing in one line in OBS.**

[![Watch the video](https://i.imgur.com/24l747X.png)](https://youtu.be/4zdsZl--wLY)

(↑↑ Click me I'm a Video!)

This is windows only. As of now the script is just configured to work with [Spotify-Premium-desktop](https://www.spotify.com/de/download/windows/) as music source.

Colored output and icons are currently implemented for:
* Firefox
  - YouTube
  - Twitch 
  - Wikipedia + Wikiwand
* Discord
* Visual Studio Code
  - Saved or Unsaved
  - Icons for extensions .py, .html, .htm, .java, .ahk, .json, .ini, .txt, .js, .css, .sh
* Adobe Acrobat Reader
* Microsoft Word, Excel, Powerpoint and OneNote
* [Notepdas](https://github.com/JasonStein/Notepads) 

If something isn't listed here it will still be dispayed but not with color and or icon.

## IF YOU DONT SEE ICONS
Icons work through the font used. Currently it's `Caskaydia Cove Nerd Font`, but every font from [Nerd Fonts](https://www.nerdfonts.com/font-downloads) should work. 

## To use it in OBS (fist time):
1. Make sure you have Python3 installed on your machine. Also you will need to install some packages with pip for python. If you dont know what that means look it up or maybe watch [this video](https://youtu.be/7snh_1Hf_TI). I'll just write down all packages you'll need: 
3. Run OBS
4. Run `stringme.py`
5. Add a new source where you want it to be displayed. Choose Browser source. Check the local file checkbox. Navigate to where you saved the files from this repro and choose `stringme.htm` (Not `stringme_tamplate.htm`!). Set the dimensions to ⇅`70` and ⇄`2000`. Delete all contents from the "Custom CSS" box. Check " shutdown source when not visible". Check "Refresh browser when sceene becomes active".  Click OK.
7. Alt drag the right side of the new source so the scrollbar is hidden. 
8. If nothing is dispayed click reload on the browser scource and make sure the script is still running. 
9. Hide `python.3.##.exe` (if you want) with AHK or like [this](https://answers.microsoft.com/en-us/windows/forum/all/how-can-i-hide-a-specific-program-in-the-system/f7f09999-9397-44e8-b1d0-792a49d3721b). 

## To use it every time after the first:
1. Run OBS
2. Run `stringme.py`
3. Hide `python.3.##.exe` (if you want)

## Customization 
Python is an easy language to read just open the `stringme.py` in an editor and read the Comments what the code does you may add, edit or remove stuff. If you want to change the color or something just change the hex (`#FF0000` e.g. this is red) in the `# ENDSTRINGS Switch Statement` for the case you need. If you want to change the order of something being displayed you can change that down by the write me variable declaration. Also if you want to change something like the font being used you can change this in the `stringme_template.htm` (if you were to change something in the `stringme.htm`it would be overwritten as soon as you start the `stringme.py` again)

### Things to improove (contributions are welcome!): 
 * more programs and websides to implement 
 * Due to the large size of the font the browser source "flickes" every so often because it reloads every second and the font file has to be loaded again. A way around that would be nice. 
 * implement git branch stuff for VS Code
