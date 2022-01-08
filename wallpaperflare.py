#!/usr/bin/env python3

import subprocess,os

query=input("Query: ")
screen_size=input("Screen(FHD): ")
thumbs="/tmp/thumbs"
walls="~/wallpapers"
cleaned=False

if not screen_size:
    screen_size="1920x1080"

if not query:
    #list with redirection and preview links,some redirection maybe broken need to remove them
    #unecessary links have 56 chars max currently so this works
    data='curl -sL "https://www.wallpaperflare.com/" | grep -Eo "(http|https)://[a-zA-Z0-9./?=_%:-]*" | uniq -u | sed -r "/.{57}/!d"' 
else:
    data='curl -sL "https://www.wallpaperflare.com/search?wallpaper="' + query + ' | grep -Eo "(http|https)://[a-zA-Z0-9./?=_%:-]*" | uniq -u | sed -r "/.{57}/!d"| sed 1,12d ' #first 12 lines are useless here 

links_list=subprocess.check_output(data, shell=True,text=True).split() #even index: redirection url of image,odd index: image preview

def cleanup(): #remove redirection without image links
    global cleaned
    for i,x in enumerate(links_list):
        if i%2==0:
            if ".jpg" in x:
                del links_list[i-2] #since was checking at even places
                break #breaks the loop everytime finds a redirection without image link
        cleaned = True #runs when '.jpg' case failed means no redirection without image left
    if cleaned:
        return
    else:
        cleanup()
        cleaned = True

if len(links_list)==0:
    print("Sorry no results found !")
else:
    os.system(f'rm -rf {thumbs}')
    if ".jpg" in links_list[0]: #in some cases redirection link at start is missing , removes if its the 1st
        del links_list[0]
    cleanup()
    os.system(f'mkdir -p {thumbs} {walls}')
    for x in links_list[1::2]:
        if ".jpg" in x: #some queries still has redirection links skipping those
            os.system(f'wget -q -P {thumbs} {x} &')
    os.system('sleep 2') #without sleep, This shows data of last search !
    wall_names=subprocess.check_output(f'sxiv -o -t {thumbs}|cut -d"/" -f4',shell=True,text=True).split() #list of selected wallpapers 
   
    if len(wall_names) !=0:
        walls_index=[]

        for x in wall_names:
            for i,y in enumerate(links_list):
                if not (y.find(x) == -1):
                    walls_index.append(i-1) #since redirection link is 1 above
                    break

        for x in walls_index:
            links_list[x]=links_list[x]+"/download"
            image_url=subprocess.check_output(f'curl -sL {links_list[x]}|'+'pup "img#show_img attr{src}"',shell=True,text=True).strip()
            image_name=subprocess.check_output("basename "+image_url,shell=True,text=True).strip()
            os.system(f'wget -q {image_url} -P {walls}') #getting wall
            os.system(f'convert {walls}/{image_name} -resize {screen_size} {walls}/{image_name}') #resize

os.system(f'sxiv {walls}')
os.system(f'rm -rf {thumbs}') #cleanup thumbnails

