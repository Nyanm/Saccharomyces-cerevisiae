# Saccharomyces-cerevisiae

An OpenCV &amp; PIL(Pillow) based sdvx@asphyxia score checker

## Introduction

Simple python application to generate game record images to help you analyze your ability.

You can download a built version directly. Also, it can run independently as python code in your IDE.

Special thanks to Achernar (with an unknown GitHub account). Amazing jobs were done by her, which helps me a lot in designing gen6.plot_summary.

## Features

### 1. System scale

   1. **Replaceable skins**  
      Skin can be simply replaced through the config.cfg. Considering that designing and coding a new skin is such a backbreaking task, there is only one default skin by now.
   

   2. **One file solution**  
      It can do all the things with only one file initially. Thanks to ifstools which can draw images from HDD game data. 


   3. **~~Interactive user interface~~**  
      Failed. As a redemption, a better interface was made to exalt the user experience.
   

   4. **Automatic upgrade (be in line with game version)**  
      Once you received your newest and hottest game, it will check the "ext" number in ea3-config and upgrade its database.

### 2. Score checker function

   1. **Best 50 Songs**   
      Generate a list that lists your best 50 scores, sorted in VOLFORCE. Also, it shows elements related to VF——score, clear mark, and grade mark.
      This is the very fundamental function of this score checker. It was partially inspired by some ARCAEA score checker. Meanwhile, it was the initial impetus for me to start this project.
   

   2. **User summary**   
      Generate an analytical summary. For each level you have chosen, It will generate pie graphs in both clear mark field and grade mark field. It will also plot a histogram to show the distribution of the score towards a specific level. In the end, a VF-Score joint graph and a score violin graph will be generated. They are comprehensive tools to help you analyze your ability.  


   3. **Recent play record**    
      Generate the music record you have just played. It follows exactly the official style, making it resemble an in-game screenshot.
   

   4. **Specific song record**   
      Generate the chosen child. You can use this function with the help of "[8] Search mid".
   

   5. **Score list**    
      Choose a level and the limits of the scores. The function will generate a list that contains the songs at this level and amid the limits. This was inspired by an IMPERIAL who needs to check her 19 S accomplishment.

### 3. Universal function

   8. **Search mid**   
      Enter anything related to the song, like the name, the author, or the memes. Besides, I raised a project to collect those SDVX song memes to contribute to this function. You can join it if you have some memes to share.  
      
      The search result also shows the level, release date, and Yomigana name at one time. This will help you to pin a song quickly when someone orders a specific song.


   9. **FAQ**   
      Well, it might be unqualified as a usable function.

## How to use

### Before using

- The software will try to extract skin ingredients from game files during the initialization. Thus, a Gen 6 game (Exceed Gear) is requisite.  

- Make sure there are no non-ASCII characters in your filepath.  

- There are 2 ways to update the software's database (a few .npy tables). If you set the "config.cfg -> Init -> is initialized" to "0" or "False", the software will update both image archive and database, and it takes a lot of time to update images. If you set the "config.cfg -> Init -> version" to a smaller number, the software will only update the database.

- Considering that the structure of .npy may change through software updates, you should give the software a soft update (through edit version number in config.cfg) each time you have downloaded the latest build. Otherwise, the software may not work as expected.

### I only use the built version

1. Run the bare .exe, it will generate a config.cfg and shut itself down.
      
2. Fill up the config.cfg under the instruction, examples are given there.
      
3. Run the software again, it will initialize some data and an image archive automatically from your HDD game.
      
4. Enter the number that corresponds to the function you want. It has no interactive interface, thus you should input your operating number and press enter.

### I want it run on my IDE

+ Set the "test_mode" to "1" in cfg_read, otherwise the program won't be able to find the correct path.

### I want to build it on my own

+ Something wrong happens between opencv-python and pyinstaller, as far as I know, the opencv runs well in version 4.5.3.

+ Set the "test_mode" to "0" in cfg_read, otherwise the exe. file won't be able to find the correct path.

## Behind the code

Finally, a makeshift (using base64 encoding to convert common byte files into UTF-8 coded python variable) was found to pack all ingredients into one .exe file. Unfortunately, the .exe build become ungodly big. Nonetheless, this helps the software avoid the issue "BEMANI will sue".

I use matplotlib and seaborn to generate graphs, which make the summary more like an academic report than a game profile. Fortunately, I can soon use them in my diploma paper. XD

Forgive my poor code ability and English. 🎵I'm just an Internet Engineering boy🎵 🎵Nobody loves me🎵

用英语写README感觉自己像个文盲

不用UTF-8都得下地狱
