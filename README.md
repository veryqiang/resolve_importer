# Davinci Resolve Footage Importer

Tool for importing a folder containing sub-folders and footages to Davinci Resolve.

Created with Davinci Resolve scripting API.

GUI made with PySimpleGUI, which is easier GUI solution for new programmers.

## Goal

The main goal of this importer, beside my learning to program, is to help keep a Resolve project tidy and maybe save some boring labor,
by providing:

* tagging/timestamp for folder names
* clip color
* marker labels

There is also an option to create timeline from imported clips, useful for VFX review sessions.

## How to run:
Make sure you have Python 3.6 or newer installed. 

Then install PySimpleGUI:
    
    pip install pysimplegui
or

    pip3 install pysimplegui

Run the script:
 
    python3 ./resolve_importer.py
    
Optionally you can config Python Launcher 3.6+ as default method for .py files then you can click and run the script directly.

Tested on macOS Catalina. 


Note: 
I am a colorist new to programming, this is my learning project. 
Though the tool should not be destructive, please test in your non-production environment.