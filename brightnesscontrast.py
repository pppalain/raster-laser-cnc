
import laserengrave
from PIL import Image, ImageFile, ImageFilter, ImageEnhance, ImagePath, ImageDraw, ImageOps, ImageTk, ImageChops
from subprocess import Popen, PIPE
import sys
from tkinter import filedialog, Tk, Button, Canvas, Label, IntVar, StringVar, DoubleVar, Checkbutton, Entry
import tkinter
# import gmic

#
# an image viewer
LASERMIN = 6
LASERMAX = 100
MAXSPEED = 4000
MINSPEED = 1300
CONTOURSPEED = 1000
IMAGEWIDTHMM = 150
IMAGEHEIGHTMM = 0
PASSESPERXMM = 8
PASSESPERYMM = 8
PLOTCONTOUR = 0
PAINTING = 0
PRINTRASTER = 1
EQUALIZE = 0
AUTOCONTRAST = 0
EDGEENHANCE = 0
EDGEENHANCEMORE = 0
FINDEDGES = 0
OBJECTWIDTH = 200
OBJECTHEIGHT = 200
XOFFSET = 0.0
CHKXCENTER = 0
YOFFSET = 0.0
CHKYCENTER = 0


class UI(tkinter.Frame):
    def __init__(self, master, brightness=1, contrast=1, sharpness=1):
        tkinter.Frame.__init__(self, master)

        self.brightness_var = DoubleVar()
        self.contrast_var = DoubleVar()
        self.sharpness_var = DoubleVar()
        self.painting_var = IntVar()
        self.unsharp_var = IntVar()
        self.edgeenhance_var = IntVar()
        self.edgeenhancemore_var = IntVar()
        self.findedges_var = IntVar()
        self.show_dithered_var = IntVar()
        self.plot_contour_var = IntVar()
        self.x_center_var = IntVar()
        self.y_center_var = IntVar()
        self.print_raster_var = IntVar()
        self.equalize_var = IntVar()
        self.autocontrast_var = IntVar()
        self.imagewidthmm_var = StringVar()
        self.imageheightmm_var = StringVar()
        self.objectwidthmm_var = StringVar()
        self.objectheightmm_var = StringVar()
        self.passperxmm_var = StringVar()
        self.passperymm_var = StringVar()
        self.minspeed_var = StringVar()
        self.maxspeed_var = StringVar()
        self.posx = 1500/2
        self.posy = 900/2
        self.scan_markx = 0
        self.scan_marky = 0
        self.scan_dx = 0
        self.scan_dy = 0
        global IMAGEHEIGHTMM
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        self.Frame1 = tkinter.Frame(
            width=250, height=900, bg="", colormap="new")
        self.Frame1.place(relx=0.005, rely=0.01, relheight=0.95)
        self.filename = tkinter.filedialog.askopenfilename(
            initialdir="./", title="Select file", filetypes=(("image files", "*.jpg *.png"), ("all files", "*.*")))
        self.image = Image.open(self.filename).convert("L")
#        self.image = self.image.Image.crop(self.image.Image.getbox())
#         painting_cmd = ["gmic", self.filename, "fx_painting",
#                         "8,0.4,0,0,0,0", "output", "painting.jpg"]
#         p = Popen(painting_cmd)
#         p.communicate()
        self.painting = Image.open("painting.jpg").convert("L")
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(background="#d9d9d9")
        self.Frame1.pack(side=tkinter.LEFT)
        self.canvas = tkinter.Canvas(
            self, width=1500, height=900)
        self.backdrop = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(
            1500/2, 900/2, image=self.backdrop, anchor=tkinter.CENTER)
        self.canvas.pack(side=tkinter.LEFT)
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<ButtonRelease-1>", self.scroll_end)
  #      self.canvas.place(x=205, y=1,width=1500, height=900)

        scale_brightness = tkinter.Scale(self.Frame1, orient=tkinter.HORIZONTAL, from_=0, to=3,
                                         resolution=0.01, command=self.redraw,
                                         length=256, variable=self.brightness_var)
        scale_brightness.set(brightness)
        scale_brightness.bind("<ButtonRelease-1>", self.redraw)
        scale_contrast = tkinter.Scale(self.Frame1, orient=tkinter.HORIZONTAL, from_=0, to=2,
                                       resolution=0.01, command=self.redraw,
                                       length=256, variable=self.contrast_var)
        scale_contrast.set(contrast)
        scale_contrast.bind("<ButtonRelease-1>", self.redraw)

        scale_sharpness = tkinter.Scale(self.Frame1, orient=tkinter.HORIZONTAL, from_=0, to=3,
                                        resolution=0.05, command=self.redraw,
                                        length=256, variable=self.sharpness_var)
        scale_sharpness.set(1)
        scale_sharpness.bind("<ButtonRelease-1>", self.redraw)

        chk_plot_contour = Checkbutton(
            self.Frame1, text='Plot Contour', variable=self.plot_contour_var, command=self.test_plot_contour)
        chk_print_raster = Checkbutton(
            self.Frame1, text='Raster Print', variable=self.print_raster_var, command=self.test_print_raster)
        chk_painting = Checkbutton(
            self.Frame1, text='Painting effect', variable=self.painting_var, command=self.redraw)
        chk_autocontrast = Checkbutton(
            self.Frame1, text='Autocontrast', variable=self.autocontrast_var, command=self.redraw)
        chk_equalize = Checkbutton(
            self.Frame1, text='Equalize', variable=self.equalize_var, command=self.redraw)
        chk_unsharp = Checkbutton(
            self.Frame1, text='Unsharp Mask', variable=self.unsharp_var, command=self.redraw)
        chk_findedges = Checkbutton(
            self.Frame1, text='Find Edges', variable=self.findedges_var, command=self.redraw)
        chk_edgeenhance = Checkbutton(
            self.Frame1, text='Edge Enhance', variable=self.edgeenhance_var, command=self.redraw)
        chk_edgeenhancemore = Checkbutton(
            self.Frame1, text='Enhance More', variable=self.edgeenhancemore_var, command=self.redraw)
        chk_show_dithered = Checkbutton(
            self.Frame1, text='Show dithered', variable=self.show_dithered_var, command=self.redraw, anchor="w")
        chk_center_x = Checkbutton(
            self.Frame1, text='Center image on X', variable=self.x_center_var, command=self.test_center)
        chk_center_y = Checkbutton(
            self.Frame1, text='Center image on Y', variable=self.y_center_var, command=self.test_center)
        loadImage = Button(
            self.Frame1, text="Load Image", command=self.loadImage)
        exportGcode = Button(
            self.Frame1, text="Export Gcode", command=self.gcode)
        r = 0
        scale_contrast.grid(row=r, columnspan=2)
        r += 1
        scale_brightness.grid(row=r, columnspan=2)
        r += 1
        scale_sharpness.grid(row=r, columnspan=2)
        r += 1
        chk_autocontrast.grid(row=r, column=0, sticky=tkinter.W)
        chk_equalize.grid(row=r, column=1, sticky=tkinter.W)
        r += 1
        chk_unsharp.grid(row=r, column=0, sticky=tkinter.W)
        chk_painting.grid(row=r, column=1, sticky=tkinter.W)
        r += 1
        chk_edgeenhance.grid(row=r, column=0, sticky=tkinter.W)
        chk_edgeenhancemore.grid(row=r, column=1, sticky=tkinter.W)
        r += 1
        chk_findedges.grid(row=r, column=0, sticky=tkinter.W)
        chk_show_dithered.grid(row=r, column=1, sticky=tkinter.W)
        r += 1
        chk_plot_contour.grid(row=r, column=0, sticky=tkinter.W)
        chk_print_raster.grid(row=r, column=1, sticky=tkinter.W)
        r += 1
        chk_center_x.grid(row=r, column=0, sticky=tkinter.W)
        chk_center_y.grid(row=r, column=1, sticky=tkinter.W)
        r += 1
        self.width_entry = Entry(
            self.Frame1, textvariable=self.imagewidthmm_var, state=tkinter.NORMAL)
        self.maxspeed_entry = Entry(
            self.Frame1, textvariable=self.maxspeed_var, state=tkinter.NORMAL)
        self.minspeed_entry = Entry(
            self.Frame1, textvariable=self.minspeed_var, state=tkinter.NORMAL)
        self.height_entry = Entry(
            self.Frame1, textvariable=self.imageheightmm_var)
        self.objheight_entry = Entry(
            self.Frame1, textvariable=self.objectheightmm_var)
        self.objwidth_entry = Entry(
            self.Frame1, textvariable=self.objectwidthmm_var, state=tkinter.NORMAL)
        self.passperx_entry = Entry(
            self.Frame1, textvariable=self.passperxmm_var)
        self.passpery_entry = Entry(
            self.Frame1, textvariable=self.passperymm_var)
        self.maxspeed_entry.insert(0, MAXSPEED)
        self.minspeed_entry.insert(0, MINSPEED)
        self.passperx_entry.insert(0, PASSESPERXMM)
        self.passpery_entry.insert(0, PASSESPERYMM)
        self.objwidth_entry.insert(0, OBJECTWIDTH)
        self.objheight_entry.insert(0, OBJECTHEIGHT)
        self.objheight_entry.bind("<Return>", self.test_obj)
        self.objheight_entry.bind("<FocusOut>", self.test_obj)
        self.objwidth_entry.bind("<Return>", self.test_obj)
        self.objheight_entry.bind("<FocusOut>", self.test_obj)
        self.minspeed_entry.bind("<Return>", self.test_speed)
        self.minspeed_entry.bind("<FocusOut>", self.test_speed)
        self.maxspeed_entry.bind("<Return>", self.test_speed)
        self.maxspeed_entry.bind("<FocusOut>", self.test_speed)
        self.passperx_entry.bind("<Return>", self.redraw)
        self.passperx_entry.bind("<FocusOut>", self.redraw)
        self.passpery_entry.bind("<Return>", self.redraw)
        self.passpery_entry.bind("<FocusOut>", self.redraw)
        self.height_entry.bind("<Return>", self.redraw)
        self.height_entry.bind("<FocusOut>", self.redraw)
        self.width_entry.insert(0, str(IMAGEWIDTHMM))
        IMAGEHEIGHTMM = int(IMAGEWIDTHMM*self.image.size[1]/self.image.size[0])
        self.height_entry.insert(0, str(IMAGEHEIGHTMM))
        self.width_entry.bind("<Return>", self.redraw)
        self.width_entry.bind("<FocusOut>", self.redraw)
        Label(self.Frame1, text="Width(mm)").grid(row=r, sticky=tkinter.E)
        self.width_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="Height(mm)").grid(row=r, sticky=tkinter.E)
        self.height_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="X pass/mm").grid(row=r, sticky=tkinter.E)
        self.passperx_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="Y pass/mm").grid(row=r, sticky=tkinter.E)
        self.passpery_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="Maximum Speed (mm/s)").grid(row=r, sticky=tkinter.E)
        self.maxspeed_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="Minimum Speed (mm/s) ").grid(row=r, sticky=tkinter.E)
        self.minspeed_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="Object width (mm)").grid(
            row=r, sticky=tkinter.E)
        self.objwidth_entry.grid(row=r, column=1)
        r += 1
        Label(self.Frame1, text="Object height (mm)").grid(
            row=r, sticky=tkinter.E)
        self.objheight_entry.grid(row=r, column=1)
        r += 1
        loadImage.grid(row=r, columnspan=2, sticky=tkinter.E)
        r += 1
        exportGcode.grid(row=r, columnspan=2, sticky=tkinter.E)

    def scroll_start(self, event):
        self.scan_markx = int(event.x)
        self.scan_marky = int(event.y)

    def scroll_end(self, event):
        self.scan_dx = int(event.x)-self.scan_markx
        self.scan_dy = int(event.y)-self.scan_marky
        self.redraw()
        self.scan_dy = 0
        self.scan_dx = 0

    def test_plot_contour(self):
        global PLOTCONTOUR
        PLOTCONTOUR = self.plot_contour_var.get()

    def test_print_raster(self):
        global PRINTRASTER
        PRINTRASTER = self.print_raster_var.get()

    def test_center(self):
        global CHKXCENTER
        global CHKYCENTER
        CHKXCENTER = self.x_center_var.get()
        CHKYCENTER = self.y_center_var.get()
        print("center horizontal:"+str(CHKXCENTER))
        print("center vertical:"+str(CHKYCENTER))

    def test_obj(self, event):
        global OBJECTHEIGHT
        global OBJECTWIDTH
        OBJECTWIDTH = int(self.objectwidthmm_var.get())
        OBJECTHEIGHT = int(self.objectheightmm_var.get())
        print("Object size set to "+str(OBJECTWIDTH)+"x"+str(OBJECTHEIGHT)+" mm")

    def test_speed(self, event):
        global MAXSPEED
        global MINSPEED
        MAXSPEED = int(self.maxspeed_var.get())
        MINSPEED = int(self.minspeed_var.get())
        print("minspeed set to "+str(MINSPEED)+" mm/s")
        print("maxspeed set to "+str(MAXSPEED)+" mm/s")

    def gcode(self):
        saveas = tkinter.filedialog.asksaveasfilename(initialdir="w:/",
                                                      filetypes=[("LinuxCNC", "*.ngc")])
        print("exporting Gcode")
        XOFFSET = float(CHKXCENTER*(OBJECTWIDTH-IMAGEWIDTHMM))/2
        print("xoffset="+str(XOFFSET))
        laserengrave.OutputRaster(im2, saveas, LASERMIN, LASERMAX, MAXSPEED, MINSPEED,
                                  CONTOURSPEED, IMAGEWIDTHMM, IMAGEHEIGHTMM, PASSESPERXMM, PASSESPERYMM, XOFFSET, 0.0)
        print("finished Gcode export")

    def redraw(self, event=None):
        global im2
        global IMAGEWIDTHMM
        global IMAGEHEIGHTMM
        global PASSESPERYMM
        global PASSESPERXMM
        self.posx += self.scan_dx
        self.posy += self.scan_dy
        new_width = int(self.imagewidthmm_var.get())
        new_height = int(self.imageheightmm_var.get())
        PASSESPERXMM = float(self.passperxmm_var.get())
        PASSESPERYMM = float(self.passperymm_var.get())
        im2 = self.image
        if self.painting_var.get():
            im2 = self.painting
        if new_width != IMAGEWIDTHMM:
            IMAGEWIDTHMM = new_width
            IMAGEHEIGHTMM = int(
                IMAGEWIDTHMM*im2.size[1]/im2.size[0])
            self.height_entry.delete(0, 'end')
            self.height_entry.insert(0, str(IMAGEHEIGHTMM))
        elif new_height != IMAGEHEIGHTMM:
            IMAGEHEIGHTMM = new_height
            IMAGEWIDTHMM = int(
                IMAGEHEIGHTMM*im2.size[0]/im2.size[1])
            self.width_entry.delete(0, 'end')
            self.width_entry.insert(0, str(IMAGEWIDTHMM))
        im2 = ImageEnhance.Brightness(im2)
        im2 = im2.enhance(self.brightness_var.get())
        im2 = ImageEnhance.Contrast(im2)
        im2 = im2.enhance(self.contrast_var.get())

        im2 = ImageEnhance.Sharpness(im2)
        im2 = im2.enhance(self.sharpness_var.get())
        if self.equalize_var.get():
            im2 = ImageOps.equalize(im2)
        if self.autocontrast_var.get():
            im2 = ImageOps.autocontrast(im2)
        if self.unsharp_var.get():
            im2 = im2.filter(ImageFilter.UnsharpMask(
                radius=2, percent=350, threshold=3))

        if self.edgeenhancemore_var.get():
            im2 = im2.filter(ImageFilter.EDGE_ENHANCE_MORE)
        elif self.edgeenhance_var.get():
            im2 = im2.filter(ImageFilter.EDGE_ENHANCE)
        new_size = (int(IMAGEWIDTHMM*PASSESPERXMM),
                    int(im2.size[1]*IMAGEWIDTHMM*PASSESPERYMM/im2.size[0]))
        im2 = im2.resize(new_size)
        new_size2 = (int(new_size[0]*PASSESPERYMM /
                         PASSESPERXMM), int(new_size[1]))
        if self.findedges_var.get():
            im3 = im2
            im2 = im2.filter(ImageFilter.FIND_EDGES)
            im2 = ImageOps.invert(im2)
#            im2 = ImageChops.darker(im2, im3)
#            im2 = Image.blend(im2, im3, 0.5)
            im2 = ImageChops.add_modulo(im2, im3)
        if self.show_dithered_var.get():
            im2 = im2.convert("1")
        show_im2 = im2.resize(new_size2)
        self.overlay = ImageTk.PhotoImage(show_im2)
        txt = self.filename
        txt += "\nSize: "+str(im2.size[0])+" x "+str(im2.size[1])+"\n"
        txt += "Width: "+str(IMAGEWIDTHMM)+" mm\n"
        txt += "Height: "+str(IMAGEHEIGHTMM)+" mm\n"
        # update canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            self.posx, self.posy, image=self.overlay, anchor=tkinter.CENTER)
        self.canvas.create_text(
            25, 20, justify=tkinter.LEFT, anchor=tkinter.NW, text=txt, fill="#F2F")

    def loadImage(self):
        self.filename = tkinter.filedialog.askopenfilename(
            initialdir="./", title="Select file", filetypes=(("image files", "*.jpg *.png"), ("all files", "*.*")))
        self.image = Image.open(self.filename).convert("L")
        # painting_cmd = ["gmic", self.filename, "fx_painting",
        #                 "8,0.4,0,0,0,0", "output", "painting.jpg"]
        # p = Popen(painting_cmd)
        # p.communicate()
        self.painting = Image.open("painting.jpg").convert("L")
        self.redraw(self)
# ---------------------------------------------------------------------

# --------------------------------------------------------------------
# main


root = tkinter.Tk()
root.title("LinuxCNC Laser")

UI(root).pack()
root.mainloop()
print(PLOTCONTOUR, PRINTRASTER)
print(PASSESPERXMM, PASSESPERYMM)
