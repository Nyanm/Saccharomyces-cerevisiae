# Saccharomyces-cerevisiae

A OpenCV &amp; PIL(Pillow) based sdvx@asphyxia score checker

---

## Introduction

Simple python application to generate game record images in order to help you analyze your ability.

You can download a built version directly. Also, it can run independently as python code in your IDE.

Special thanks to Achernar (with no GitHub account XD). Amazing jobs was done by her which helps me a lot in designing gen6.plot_summary.

---

## Features

### 1. System scale

   1. **Replaceable skins**  
      Skin can be simply replaced through the config.txt. Considering that designing and coding a new skin is such a backbreaking task, there is only one default skin by now.
   

   2. **One file solution**  
      The application can do all the things with only one file initially. Thanks to ifstools, it can draw images from HDD game data. 


   3. **~~Interactive user interface~~**  
      Failed. As a redemption, a better interface was made to exalt user experience.
   

   4. **Automatic upgrade (be in line with game version)**  
      Once you received your newest and hottest game, application will check "ext" number in ea3-config and upgrade itself.

### 2. Score checker function

   1. **Best 50 Songs**   
      Generate a list which lists your B50 scores, sorted in VOLFORCE. Also, it shows elements related to VF——score, clear mark, grade mark.
      This is the very function of this score checker. This was partially inspired by some ARCAEA score checker, meanwhile it was the initial impetus for me to start this project.
   

   2. **User summary**   
      Generate an analytical summary. For each level you have chosen, It will generate pie graphs in both clear mark field and grade mark field. It will also plot a histogram to show the distribution of the score towards to a specific level. In the end, a VF-Score joint graph and Score violin graph will be generated. They are comprehensive tools to help you analyze your ability.


   3. **Recent play record**    
      Generate the music record you have just played. It follows exactly the official style, makes it like a screenshot in game.
   

   4. **Specific song record**   
      Generate the chosen child. You can use this function with the help of "8 Search mid".
   

   5. **Score list**    
      Choose a level and a score threshold, then the program will generate a list which contains all songs above this score at this level. This was inspired by a IMPERIAL who needs to check her 19 S accomplishment.

### 3. Universal function

   8. **Search mid**   
      Enter anything related to the song, like the name, the author or the memes. Besides, I raised a project to collect those SDVX song memes to contribute this function. You can join it if you have some memes to share.
   

   9. **FAQ**   
      Well it might be unqualified as a usable function.

---

## How to use

### I only use built version

1. Run the bare .exe, it will generate a config.cfg and shut itself down.
      
2. Fill up the config.cfg under the instruction, examples are giving there.
      
3. Run the application again, it will initialize some data, and an image archive automatically from your HDD game.
      
4. Enter the number correspond to the function you want. It has no interactive interface, thus you should input your operate number and press enter.

### I want it run on my IDE

+ Set the "test_mode" to "1" in cfg_read, otherwise the program won't be able to find the correct path.

### I want to build it on my own

+ Something wrong happens between opencv-python and pyinstaller, as far as I know the opencv runs well in version 4.5.3.

+ Set the "test_mode" to "0" in cfg_read, otherwise the exe. file won't be able to find the correct path.

---

## Behind the code

Finally, a makeshift was found to pack all ingredients into one .exe file. Unfortunately, the application become ungodly big. Nonetheless, this helps it avoid the issue "BEMANI will sue"

Plot maybe a verb.

I use matplotlib and seaborn to generate graphs, which make the summary more like an academical report than a game profile. Fortunately, I can soon use them in my diploma paper. XD

Forgive my poor code ability and English. 🎵I'm just an Internet Engineering boy🎵 🎵Nobody loves me🎵

用英语写README感觉自己像个文盲

不用UTF-8都得下地狱
