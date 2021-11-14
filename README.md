# Saccharomyces-cerevisiae

A OpenCV &amp; PIL based sdvx@asphyxia score checker

### !!! RECONSTRUCTION WOULD BE DONE SOON !!!

## Introduction

Simple python application to draw data from  Asphyxia  Core database, plot images to help you analyze your scores. It can be built into an exe, theoretically, and I will release it in group now and then. 

Codes here are only for exhibiting case, however you can still pull request.

## Function

1. ### System scale

   1. Replaceable skins: Skin can be simply replaced through the config.txt. It's regretful that designing and coding a new skin is such a backbreaking task, so there is only one default skin by now.
   
   2. One file solution: The application can do all the things with only one file initially. Thanks to ifstools, it can draw images from HDD game data. 

   3. ~~Interactive user interface~~: Failed. As a redemption, a better interface was made to exalt user experience.

2. ### Score checker function

   1. Best 50 Songs: Generate a list which lists your B50 scores, sorted in VOLFORCE. Also, it shows elements related to VF——score, clear mark, grade mark.
      This is the very function of this score checker. This was partially inspired by some ARCAEA score checker, meanwhile it was the initial impetus for me to start this project.
   
   2. User summary: Generate an analytical summary. For each level you have chosen, It will generate pie graphs in both clear mark field and grade mark field. It will also plot a histogram to show the distribution of the score towards to a specific level. In the end, a VF-Score joint graph and Score violin graph will be generated. They are comprehensive tools to help you analyze your ability.

   3. Recent play record: Generate the music record you have just played. 
   
   4. Specific song record: Generate the chosen child. You can use this function with the help of "8 Search mid".

3. ### Universal function

   1. Search mid: Enter anything related to the song, like the name, the author or the memes. Besides, I raised a project to collect those SDVX song memes to contribute this function. You can join it if you have some memes to share.
   
   2. Show available skin list: Ambitious goal, humble reality.

## How to use

1. Run the bare .exe, it will generate a config.txt and shut itself down.
   
2. Fill up the config.exe under the instruction, examples are giving there.
   
3. Run the application again, it will initialize some data, and an image archive automatically from your HDD game.
   
4. Enter the number correspond to the function you want, meanwhile a user interface would be illustrated.
   
5. If you have updated your game version recently, delete the "is_initialized" line to restart the initialization, otherwise new songs won't appear. 

## Still going to say…

Finally, a makeshift was found to pack all ingredients into one .exe file. Unfortunately, the application become ungodly big. Anyway, this helps it avoid the issue "BEMANI will sue". 

Plot is a verb.

I use matplotlib and seaborn to generate graphs, which make the summary more like an academical report than a game profile. Fortunately, I can soon use them in my diploma paper. XD

用英语写README感觉自己像个文盲，麻了。

~~用SHIFT-JIS的人有难了，死后会下编码地狱，满目所见都是乱码。~~不用UTF-8都得下地狱

