from  PIL import Image, ImageFile, ImageFilter, ImageEnhance, ImagePath, ImageDraw, ImageOps, ImageTk
# from scipy.spatial import ConvexHull, convex_hull_plot_2d
import matplotlib.pyplot as plt
from pathlib import Path

from tkinter import filedialog, Tk, Button, Canvas, Label, IntVar, Checkbutton
#from tkinter import *
#import tkinter as tk


def paste_over_white(pix, x, y):
    whiteim = Image.new("RGBA", pix.size, "WHITE")
    whiteim.paste(pix, (x, y), pix)
    return whiteim


def CleanEdgeBW(pix):
    pix = pix.convert("L").point(lambda x: 0 if x < 254 else 255, '1')
    width, height = pix.size
    px = pix.load()
    for x in range(width):
        for y in range(height):
            neighbors = 0
            actual = int(px[x, y] & 1)
            if x > 0 and x < width-1:
                neighbors += int(px[x-1, y] & 1)
                neighbors += int(px[x+1, y] & 1)
            if y > 0 and y < height-1:
                neighbors += (px[x, y+1] & 1)
                neighbors += (px[x, y-1] & 1)
            if (actual == 1 and neighbors < 2) or (actual == 0 and neighbors > 2):
                px[x, y] ^= 0xff
    return pix


def CrawlPath(pix, start: tuple, path):
    to_location = (-1, -1)
    path.append(to_location)
    path.append(start)
    point = len(path)
    width, height = pix.size
    px = pix.load()
    direction = 1
    while to_location != start:
        right = left = up = down = direction = 0
        x, y = path[point-1]
        # print(point, x, y)
        if y < height-1:
            down = px[x, y+1]
        if y > 0:
            up = px[x, y-1]
        if x < width-1:
            right = px[x+1, y]
        if x > 0:
            left = px[x-1, y]
        print(left, right, up, down)
        if down and (x, y+1) != path[point-2]:
            y += 1
        elif up and (x, y-1) != path[point-2]:
            y -= 1
        elif left and (x-1, y) != path[point-2]:
            x -= 1
        elif right and (x+1, y) != path[point-2]:
            x += 1
        to_location = (x, y)
        px[x, y] = 0
        path.append(to_location)
        point += 1
        direction = right + left + up + down
        if not direction:
            break
#        print(direction)
    return path


def FindPath(pix):
    path = []
    width, height = pix.size
    path_count = 0
    px = pix.load()
    for x in range(width):
        for y in range(height):
            if px[x, y] > 0:
                in_path = False
                for i in path:
                    if i == (x, y):
                        in_path = True
                        break
                if not in_path:
                    path = CrawlPath(pix, (x, y), path)
                    path_count += 1
                    print("path count:"+str(path_count))

    return path


def AddWhiteBorder(pix, thickness):
    width, height = pix.size
    size = (width+2*thickness, height+2*thickness)
    newim = Image.new("RGBA", size, "WHITE")
    newim.paste(pix, (thickness, thickness), pix)
    return newim


def RasterPrint(pix, gfile, PASSESPERXMM, PASSESPERYMM, LASERMAX, LASERMIN, MINSPEED, MAXSPEED):
    px = pix.load()
    width, height = pix.size
    old_lpower = 0
    old_feed = 2000
    print(width, height)
    print(PASSESPERXMM, PASSESPERYMM)
    print(width/PASSESPERXMM, height/PASSESPERYMM)
    printrow = 0
    start = 0
    end = height
    for x in range(width):
        old_power = 0
        blank_row = 1
        start = 0
        end = height
        for y in range(height):
            if px[x, y] != 255:
                blank_row = 0
                if start == 0:
                    if y > 1:
                        start = y-1
            if px[x, height-y-1] != 255:
                if end == height:
                    if y < height-3:
                        end = height-y
            if start > 0 and end < height:
                break
        if blank_row == 0:
            printrow += 1
        if printrow % 2 == 0:
            oldy = 0
            gfile.write("M68 E0 Q0\nG00 X[#100+"+str(round(x/PASSESPERXMM, 2)
                                                     )+"] Y"+str(round(start/PASSESPERYMM, 2))+"\n")
        else:
            oldy = height-1
            gfile.write("M68 E0 Q0\nG00 X[#100+"+str(round(x/PASSESPERXMM, 2)
                                                     )+"] Y"+str(round(end/PASSESPERYMM, 2))+"\n")
        for y in range(height):
            if blank_row:
                break
            if printrow % 2 == 0:
                yy = y
            else:
                yy = height-y-1
            pxval = 255-px[x, yy]
            laser_power = round((LASERMAX-LASERMIN)*(pxval)/255+LASERMIN, 1)
            lpower = laser_power
            if(laser_power == LASERMIN):
                feed = MAXSPEED
                laser_power = LASERMIN
            else:
                feed = MINSPEED*100/laser_power
                laser_power = 100

            #print(str(x)+","+str(yy)+" "+str(y)+"laserpower:" +str(laser_power))
            if(old_lpower != lpower or height-1 == yy or yy == 0):
                if printrow % 2 == 0:
                    if height-1 == yy:
                        gfile.write("o100 call ["+str(round(end/PASSESPERYMM, 1)) + "] [" + str(
                            round(old_power, 1))+"] ["+str(old_feed)+"]\n")
                    elif yy == 0:
                        gfile.write("o100 call ["+str(round(start/PASSESPERYMM, 1)) + "] [" + str(
                            round(old_power, 1))+"] ["+str(old_feed)+"]\n")
                    elif start != oldy:
                        gfile.write("o100 call ["+str(round(oldy/PASSESPERYMM, 1)) + "] [" + str(
                            round(old_power, 1))+"] ["+str(old_feed)+"]\n")
                else:
                    if height-1 == yy:
                        gfile.write("o100 call ["+str(round(end/PASSESPERYMM, 1)) + "] [" + str(
                            round(old_power, 1))+"] ["+str(old_feed)+"]\n")
                    elif yy == 0:
                        gfile.write("o100 call ["+str(round(start/PASSESPERYMM, 1)) + "] [" + str(
                            round(old_power, 1))+"] ["+str(old_feed)+"]\n")
                    elif end != oldy:
                        gfile.write("o100 call ["+str(round(oldy/PASSESPERYMM, 1)) + "] [" + str(
                            round(old_power, 1))+"] ["+str(old_feed)+"]\n")
                old_lpower = lpower
                old_power = laser_power
                old_feed = round(feed)
            oldy = yy


def PlotContour(pix, box, file, CONTOURSPEED, PASSESPERXMM, PASSESPERYMM):
    im_bw = CleanEdgeBW(pix)
#   im_bw.show()
    im_contour_edges = im_bw.filter(ImageFilter.FIND_EDGES).crop(box)
    im_contour_edges.show()
    ipath = FindPath(im_contour_edges)
#    print(ipath)
    PathPlot(ipath, file, CONTOURSPEED, PASSESPERXMM, PASSESPERYMM)


global CONTOURSPEED


def PathPlot(contour_path, gfile, CONTOURSPEED, PASSESPERXMM, PASSESPERYMM):
    path_count = 0
    gfile.write("\n;--------\n;CONTOUR\n\n")
    gfile.write("G01 F"+str(CONTOURSPEED)+" \n\n")
    pastg = 00
    pastx, pasty = 0, 0
    g = ""
    for i in contour_path:
        if g == "G00 ":
            x, y = i
            g += "X"+str(round(x/PASSESPERXMM, 2)) + " Y" + \
                str(round(y/PASSESPERYMM, 2))+" \n"
            gfile.write("\n;path "+str(path_count)+"\n\nM68 E0 Q3.75\n")
            gfile.write(g)
            g = ""
            pastg = "G00"
        elif i == (-1, -1):
            g = "G00 "
            path_count += 1
        else:
            x, y = i
            g = ""
            if pastg == "G00":
                gfile.write("G04 P0.1\nM67 E0 Q100\n")
            g += "G01"
            if x != pastx:
                g += " X"+str(round(x/PASSESPERXMM, 2))
            if y != pasty:
                g += " Y" + str(round(y/PASSESPERYMM, 2))
            g += " \n"
            pastg = "G01"
            gfile.write(g)
            pastx, pasty = i
    gfile.write(g)


def FilePreambule(file, PASSESPERXMM, Xoffset, Yoffset):
    g = "G90\nG21\n\n\n"
    g += "#100="+str(Xoffset)+"\n"
    g += "o100 sub\n"
    g += "    M67 E0 Q[#2]\n"
    g += "    G1 Y[#1+"+str(Yoffset)+"] F[#3]\n"
    g += "o100 endsub\nG64 P"+str((0.01+1/PASSESPERXMM)/2)+"\n\n"
    file.write(g)


def FileEnd(file):
    file.write("\nM68 E0 Q0\nG00 X0 Y0\nM02")
    file.close()


def OutputRaster(im, OutputFile, LASERMIN, LASERMAX, MAXSPEED, MINSPEED, CONTOURSPEED, IMAGEWIDTHMM, IMAGEHEIGHTMM, PASSESPERXMM, PASSESPERYMM, Xoffset, Yoffset):
    #    width, height = im.size
    WHITEBORDER = 6
#    box = (WHITEBORDER-1, WHITEBORDER-1, width -
#           WHITEBORDER+1, height-WHITEBORDER+1)
    im = ImageOps.expand(im, WHITEBORDER, fill=255)
    im = im.transpose(Image.FLIP_LEFT_RIGHT).rotate(180)
    f = open(OutputFile, "w")
    FilePreambule(f, PASSESPERXMM, Xoffset, Yoffset)
    RasterPrint(im, f, PASSESPERXMM, PASSESPERYMM,
                LASERMAX, LASERMIN, MINSPEED, MAXSPEED)
    FileEnd(f)
