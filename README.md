# Saccharomyces-cerevisiae

A OpenCV &amp; PIL based sdvx@asphyxia score checker

## Introduction

Simple python application to draw data from  Asphyxia  Core database, plot images to help you analyze your scores. It can be built into an exe, theoretically, and I will release it in group now and then. 

Codes here are only for exhibiting case, however you can still pull request.

## Function

1. ### System scale

   1. Replaceable skins: Skin can be simply replaced through the config.txt. It's regretful that designing and coding a new skin is such a backbreaking task, so there is only one default skin by now.
   2. ~~Interactive user interface~~

2. ### Score checker function

   1. Best 50 Songs and VF analysis: Plots a list which contains your B50 scores, sorted in VOLFORCE. Also, it shows elements related to VF——score, clear mark, grade mark.
      This is the very function of this score checker. This was partially inspired by some ARCAEA score checker, meanwhile it was the initial impetus for me to started this application.
   2. Recent play record: Plots the music record you just played. 
   3. Specific song record: Plots the chosen child. You can use this function with the help of "8 Search mid".
   4. User summary: Plots an analytical summary. For each level you have chosen, It will plots pie graph in both clear mark field and grade mark field. It will also plots a histogram to show the distribution of a specific level. In the end, a VF-Score joint graph and Score violin graph will be ploted. They are comprehensive tools to help you analyze your ability.

3. ### Universal function

   1. Search mid: Enter anything related to the song, like the name, the author or the memes. Besides I raised a project to collect those SDVX song memes to contribute this function. You can join it if you have some memes to share.
   2. Show available skin list: Ambitious goal, humble reality.

## How to use

1. Download the full exe version of this application. The codes won't work alone.
2. Fill up the config.exe, examples are given there.
3. Run exe.
4. If you have updated your game version recently, delete the "is_initialized" line to restart the initialization, otherwise new songs won't appear. 

## Still going to say…

Considering the sake of "BEMANI will sue", I simply omitted the image archive. Thus, codes here can not be built. Please contact me personally for more information.

Plot is a verb.

I use matplotlib and seaborn to generate graphs, which make the summary more like an academical report than a game profile. Fortunately, I can soon use them in my diploma paper. XD

用英语写README感觉自己像个文盲，麻了。

用SHIFT-JIS的人有难了，死后会下编码地狱，满目所见都是乱码。

QQ居然不能发送长度超过10000px的图片，脏话。

