# Viper V765 RGB Software
UNOFFICIAL Software for changing RGB color of the Viper V765 keyboard. Works on Linux and should work on Windows too though I never tested it on there.
I only made it for ISO-DE layout but I am sure it works with other ISO layouts too. I don't know about ANSII, so you might have to figure it out with trial and error.
Can't guarantee functionality since my keyboard broke and I don't use the software myself anymore. But I hope it can come in handy for others.

I also tried to seperate the packet sending stuff in it's own file so if someone wants they can write there own software around it (i hope it is clear enough how to use it). 
Especially since my own UI is very basic and focused on functionality.

Finally, I am sure there is a lot of room for improvement (like not hardcoding the relative venv path in there) but I don't really have any reason to work on this anymore
and don't have the hardware anymore to test if it would still work. But if you want you are more than welcome to change the code to your liking.

**IMPORTANT: I can no longer guarantee that this software works fine since I don't have this keyboard anymore! Use it at your own risk!**

## Installation (Linux)
- Assuming you already have python installed, create a virtual environment called "venv": 
    - `python3 -m venv venv`
- Activate the environment: 
    - `source venv/bin/activate`
- Install the requirements: 
    - `pip install -r requirements.txt`
## Usage
- Run: `python3 index.py`
- This will present you with two options:
    - **Using existing preset:** Here are the presets you would find in the normal Windows software as well as the five custom ones you can save. *(e.g. spectrum, rain, breath)*
    - **Create custom preset:** This will open a GUI showing a keyboard. **You can...**
        - modify single keys with right click. 
        - select multiple keys with left click and modify them with the "Set Color" button at the bottom.
        - export presets to files *(since I thought the 5 built-in slots aren't enough)*
        - import presets from files *(you can find a few examples in the example-presets folder)*
        - **Don't forget to apply and click "Ok" on the alert/popup.**
- Now you might have to enter your sudo password so the changes can be applied.
- Once all the kernel drivers are reattached your keyboard should have changed color.

## Motivation
When I switched to Linux, I couldn't change the color of my keyboard anymore, since the software is Windows only. I already didn't really like the official software, 
so I decided to frankenstein my own software for it. This was my first time working with Python and my first time reverse engineering anything, so the code might suck a lot.
But it worked well for me. It also was a lot of fun to try and find out what the packets do and how to modify them.
