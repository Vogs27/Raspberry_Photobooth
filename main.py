from gpiozero import Button, LED
import time
from picamera import PiCamera
from datetime import datetime
from signal import pause
import cups
import PIL.Image
import pygame
import shutil
from PIL import Image, ImageDraw
from threading import Thread
from pygame.locals import *
import os

camera = PiCamera()

#INPUT pins
redButton = Button(4)
greenButton = Button(3)
whiteButton = Button(2)

#OUTPUT pins
redLed = LED(23)
greenLed = LED(22)
whiteLed = LED(27)
flashLed = LED(17)

#Global var
printedPhotos = 0 #foto stampate fino ad adesso (per stimare la carta rimasta)
maxSheets = 20 #max fogli di carta nella stampante per volta
IMAGE_WIDTH = 550
IMAGE_HEIGHT = 360
size = 550,360
savedFolder = 'saved'
printedFolder = 'printed'
refusedFolder = 'refused'
rawFolder = 'raw'
tempFolder = 'temp'
frameFolder = 'frames'
filePath = ''
templatePath = 'templates/template.jpg'
bgimage = PIL.Image.open(templatePath)

#initialization
pygame.init()  # Initialise pygame
pygame.mouse.set_visible(False) #hide the mouse cursor
infoObject = pygame.display.Info() #get display info
#screen = pygame.display.set_mode((800, 600))
screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen
if not os.path.isdir(savedFolder):
    os.makedirs(savedFolder)
if not os.path.isdir(printedFolder):
    os.makedirs(printedFolder)
if not os.path.isdir(refusedFolder):
    os.makedirs(refusedFolder)
if not os.path.isdir(rawFolder):
    os.makedirs(rawFolder)
if not os.path.isdir(tempFolder):
    os.makedirs(tempFolder)
if not os.path.isdir(frameFolder):
    os.makedirs(frameFolder)

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying

camera.resolution = (infoObject.current_w, infoObject.current_h)
camera.rotation              = 0
camera.hflip                 = True
camera.vflip                 = False
camera.brightness            = 50
camera.preview_alpha = 120
camera.preview_fullscreen = True


# set variables to properly display the image on screen at right ratio
def set_demensions(img_w, img_h):
	# Note this only works when in booting in desktop mode.
	# When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (infoObject.current_w * img_h) / img_w

    if (ratio_h < infoObject.current_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = infoObject.current_w
        offset_y = (infoObject.current_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > infoObject.current_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (infoObject.current_h * img_w) / img_h
        transform_y = infoObject.current_h
        offset_x = (infoObject.current_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = infoObject.current_w
        transform_y = infoObject.current_h
        offset_y = offset_x = 0

def takeSinglePhoto():
    #disconnecting callback function from buttons
    global greenButton
    global redButton
    global whiteButton
    global tempFolder
    global screen
    global background
    global pygame
    global filePath

    greenLed.off()
    whiteLed.off()
    greenButton.when_pressed = None
    whiteButton.when_pressed = None
    #preparing to take pictures
    screen.fill((255, 255, 255))
    pygame.display.flip()
    pygame.time.delay(1000)
    #time.sleep(1)
    flashLed.on()
    camera.start_preview()
    for x in range(3, -1, -1):
        if x == 0:
            font = pygame.font.Font(None, 100)
            text = font.render("Sorridi ;)", 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = screen.get_rect().centery
        else:
            font = pygame.font.Font(None, 100)
            text = font.render(str(x), 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = screen.get_rect().centery
        screen.blit(text, textpos)
        pygame.display.flip()
        pygame.time.delay(1000)
        screen.fill((255, 255, 255))
        pygame.display.flip()
    ts = time.time()
    #ts = datetime.now().isoformat()
    filename = os.path.join(tempFolder, 'single' + str(ts) + '.jpg')
    camera.capture(filename)
    camera.stop_preview()
    flashLed.off()
    #photo preview:
    show_image(filename)
    filePath=filename
    pygame.time.delay(3000)
    show_image('templates/end.jpg')
    #preparing for next menu
    greenLed.on()
    whiteLed.on()
    redLed.on()
    whiteButton.when_pressed = printPhoto
    redButton.when_pressed = refusePhoto
    greenButton.when_pressed = saveOnlyPhoto

def CapturePicture(count):
    global frameFolder
    global screen
    global background
    global pygame
    pygame.time.delay(2000)
    screen.fill((255, 255, 255))
    pygame.display.flip()
    flashLed.on()
    camera.start_preview()
    for x in range(3, -1, -1):
        if x == 0:
            font = pygame.font.Font(None, 100)
            text = font.render("Sorridi ;)", 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = screen.get_rect().centery
        else:
            font = pygame.font.Font(None, 100)
            text = font.render(str(x), 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = screen.get_rect().centery
        screen.blit(text, textpos)
        pygame.display.flip()
        pygame.time.delay(1000)
        screen.fill((255, 255, 255))
        pygame.display.flip()
    #ts = time.time() str(ts)
    ts = datetime.now().isoformat()
    filename = os.path.join(frameFolder, 'frame'+str(count)+'_'+ ts + '.jpg')
    camera.capture(filename)
    camera.stop_preview()
    flashLed.off()
    #photo preview:
    show_image(filename)
    pygame.time.delay(3000)
    return filename

def takeCollage():
    global greenButton
    global redButton
    global whiteButton
    global tempFolder
    global frameFolder
    global screen
    global background
    global pygame
    global filePath
    global size
    #disconnecting callback function from buttons
    greenLed.off()
    whiteLed.off()
    greenButton.when_pressed = None
    whiteButton.when_pressed = None

    CountDownPhoto = "1/3"
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 500)
    text = font.render(CountDownPhoto, 1, (227, 157, 200))
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = screen.get_rect().centery
    screen.blit(text, textpos)
    pygame.display.flip()
    filename1 = CapturePicture(1)
    CountDownPhoto = "2/3"
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 500)
    text = font.render(CountDownPhoto, 1, (227, 157, 200))
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = screen.get_rect().centery
    screen.blit(text, textpos)
    pygame.display.flip()
    filename2 = CapturePicture(2)
    CountDownPhoto = "3/3"
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 500)
    text = font.render(CountDownPhoto, 1, (227, 157, 200))
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = screen.get_rect().centery
    screen.blit(text, textpos)
    pygame.display.flip()
    filename3 = CapturePicture(3)

    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 100)
    text = font.render('Attendi...', 1, (227, 157, 200))
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = screen.get_rect().centery
    screen.blit(text, textpos)
    pygame.display.flip()

    image1 = PIL.Image.open(filename1)
    image2 = PIL.Image.open(filename2)
    image3 = PIL.Image.open(filename3)
    image1.thumbnail(size, Image.ANTIALIAS)
    image2.thumbnail(size, Image.ANTIALIAS)
    image3.thumbnail(size, Image.ANTIALIAS)
    bgimage.paste(image1, (625, 30))
    bgimage.paste(image2, (625, 410))
    bgimage.paste(image3, (55, 410))
    # Create the final filename
    ts = time.time()
    Final_Image_Name = os.path.join(tempFolder, "Final_" + "4"+"_"+str(ts) + ".jpg")
    bgimage.save(Final_Image_Name)
    show_image(Final_Image_Name)
    filePath = Final_Image_Name
    pygame.time.delay(3000)
    #preparing for next menu
    show_image('templates/end.jpg')
    greenLed.on()
    whiteLed.on()
    redLed.on()
    whiteButton.when_pressed = printPhoto
    redButton.when_pressed = refusePhoto
    greenButton.when_pressed = saveOnlyPhoto

def printPhoto():
    global greenButton
    global redButton
    global whiteButton
    global printedPhotos
    global maxSheets
    global background
    global pygame
    global filePath
    #here we print photos
    #deactivating callback function
    greenLed.off()
    whiteLed.off()
    redLed.off()
    whiteButton.when_pressed = None
    redButton.when_pressed = None
    greenButton.when_pressed = None
    basename = os.path.basename(filePath)
    newFilePath = os.path.join(printedFolder, basename)
    shutil.move(filePath, newFilePath)
    ##bgimage2 = .rotate(90)
    ##bgimage2.save('/home/pi/Desktop/tempprint.jpg')
    if(printedPhotos<maxSheets):
        if os.path.isfile(newFilePath):
            conn = cups.Connection()
            printers = conn.getPrinters()
            printer_name = printers.keys()[0]
            screen.fill((255, 255, 255))
            font = pygame.font.Font(None, 50)
            text = font.render('Stampa in corso, 1 minuto', 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = screen.get_rect().centerx
            textpos.centery = screen.get_rect().centery
            screen.blit(text, textpos)
            pygame.display.flip()
            pygame.time.delay(1000)
            printqueuelength = len(conn.getJobs())
            if printqueuelength > 1:
                screen.fill((255, 255, 255))
                font = pygame.font.Font(None, 60)
                text = font.render('Stampante occupata', 1, (227, 157, 200))
                textpos = text.get_rect()
                textpos.centerx = screen.get_rect().centerx
                textpos.centery = screen.get_rect().centery
                screen.blit(text, textpos)
                pygame.display.flip()
            else:
                conn.printFile(printer_name, newFilePath, "PhotoBooth", {})
                pygame.time.delay(60000)
    else:
        background.fill(pygame.Color("white"))
        font = pygame.font.Font(None, 50)
        text = font.render('Carta esaurita, chiama Edo', 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = screen.get_rect().centerx
        textpos.centery = screen.get_rect().centery
        screen.blit(text, textpos)
        pygame.display.flip()
        printedPhotos = 0
        pygame.time.delay(200000)
    print('restart')
    restart()

def refusePhoto():
    global filePath
    global greenButton
    global redButton
    global whiteButton
    #here we save photo under refused folder
    #deactivating callback function
    greenLed.off()
    whiteLed.off()
    redLed.off()
    whiteButton.when_pressed = None
    redButton.when_pressed = None
    greenButton.when_pressed = None
    basename = os.path.basename(filePath)
    newFilePath = os.path.join(refusedFolder, basename)
    shutil.move(filePath, newFilePath)
    print('restart')
    restart()

def saveOnlyPhoto():
    global filePath
    global greenButton
    global redButton
    global whiteButton
    print('dentro a saveonly \n')
    #here we save the photo without printing
    #deactivating callback function
    greenLed.off()
    whiteLed.off()
    redLed.off()
    whiteButton.when_pressed = None
    redButton.when_pressed = None
    greenButton.when_pressed = None
    print('calcolo path\n')
    basename = os.path.basename(filePath)
    newFilePath = os.path.join(savedFolder, basename)
    print('muovo')
    shutil.move(filePath, newFilePath)
    print('restart')
    restart()
    print('esco')

# display one image on screen
def show_image(image_path):
    screen.fill(pygame.Color("black")) # clear the screen
    img = pygame.image.load(image_path) # load the image
    img = img.convert()
    set_demensions(img.get_width(), img.get_height()) # set pixel dimensions based on image
    x = (infoObject.current_w / 2) - (img.get_width() / 2)
    y = (infoObject.current_h / 2) - (img.get_height() / 2)
    screen.blit(img,(x,y))
    pygame.display.flip()

def restart():
    show_image('templates/Intro.jpg')
    greenLed.on()
    whiteLed.on()
    greenButton.when_pressed = takeCollage
    whiteButton.when_pressed = takeSinglePhoto

#MAIN MAIN MAIN MAIN MAIN
show_image('templates/Intro.jpg')
greenLed.on()
whiteLed.on()
greenButton.when_pressed = takeCollage
whiteButton.when_pressed = takeSinglePhoto
pause()


#def main(threadName, *args):
#    show_image('templates/Intro.jpg')
#    greenLed.on()
#    whiteLed.on()
#    greenButton.when_pressed = takeCollage
#    whiteButton.when_pressed = takeSinglePhoto
#try:
#    Thread(target=main, args=('Main', 1)).start()
#except KeyboardInterrupt:
#    pygame.quit()
