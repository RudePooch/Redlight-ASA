#IMPORTED LIBRARIES
import configparser
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
from win32gui import FindWindow
from loguru import logger
import sys
import time
import os
from diffimg import diff
from discord_webhook import DiscordWebhook
from datetime import datetime
import pytesseract
from win32api import GetSystemMetrics


#TESSERACT INSTALL DIRECTORY
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#SETTING A VARIABLE FOR FILE EXTENSION
who = os.path.splitext(os.path.basename(__file__))[0]

#SETTING/GETTING SCREEN RESOLUTION
windll.user32.SetProcessDPIAware()
gsX = GetSystemMetrics(0) #WIDTH
gsY = GetSystemMetrics(1) #HEIGHT
srX = 2560
srY = 1440

#SETTING UP FLASHY CONSOLE TEXT
LOG_LEVEL = "DEBUG"
logger.remove()
logger.add(sys.stderr,
           format="<g>{time:HH:mm:ss}</g> <lvl>{message}</lvl>",
           level=LOG_LEVEL)
logger.level(who, no=35, color="<y>", icon="👀")

#GETTING DISCORD HOOKS/ROLES
read_config = configparser.ConfigParser()
read_config.read("Redlight.ini")
log_urls = read_config.get("Log_Alert", "log_urls")
alert_urls = read_config.get("Log_Alert", "alert_urls")
ocr_urls = read_config.get("Log_Alert", "ocr_urls")
roles = read_config.get("Role", "roles")
svrole = read_config.get("Role", "svrole")

#TODO: Alert configuration may be cleaner if parsed as a dict. Perhaps look into vyperconfig in the future.
kill_alert_enabled = read_config.get("Alerts", "kills")
death_and_destruction_alert_enabled = read_config.get("Alerts", "death_and_destruction")
teksensor_alert_enabled = read_config.get("Alerts", "teksensor")
parasaur_ping_alert_enabled = read_config.get("Alerts", "parasaur_ping")
starvation_alert_enabled = read_config.get("Alerts", "starvation")
demolition_alert_enabled = read_config.get("Alerts", "demolition")
enemy_structure_destroyed_alert_enabled = read_config.get("Alerts", "enemy_structure_destroyed")
log_positioning_alert_enabled = read_config.get("Alerts", "log_positioning")

#DECORATOR FOR CONSOLE
def endoffunc():
    try:
        #DECORATOR FOR CONSOLE
        print("*")
    except Exception as e:
        logger.error(f"End Of Func Failed: ", e)

#IS ARK RUNNING, EXIT IF NOT
def checkRunning():
    try:
        #CHECKS FOR ARK
        ark_running = FindWindow(None, "ArkAscended")
        #ARK NOT RUNNING = EXIT
        if ark_running == 0:
            logger.error(f"ARK is not running, please start the game")
            exit()
        #ARK IS RUNNING = TRUE
        return True
    except Exception as e:
        logger.error(f"Check Running Failed")

#ARE TRIBE LOGS OPEN
def arelogs():
    try:
        windll.user32.SetProcessDPIAware()

        #OPENS TARGET IMAGE, CONVERT COLOUR
        img = Image.open('Tribe Log.png').convert('L')

        #SAVES CONVERTED IMAGE/VARIABLE
        img.save('Tribe Log.png')
        file = "Tribe Log.png"

        #CONVERTS IMAGE TO TEXT
        rawText = pytesseract.image_to_string(file)
        parsedText = rawText.replace('\n', '')

        #IF "LOG" FOUND IN IMAGE, RETURN TRUE
        if "LOG" in parsedText:
            tribe = True
            return tribe

        #"TRIBE" NOT FOUND
    except Exception as e:
        logger.error(f"Are Logs Failed")

#GETS THE FIRST IMAGE FOR COMPARISON
def findcompare(im):
    try:
        #UPDATED TO ASA
        #CHECK TO SEE IF IMAGE EXISTS, IF FALSE, CREATE ONE
        logger.info("Getting Compare")
        CL2 = os.path.exists("Compare Old.png")
        if CL2 == False:
            im.crop((round(gsX * 1035 / srX), round(gsX * 285 / srX), round(gsX * 1515 / srX),
                     round(gsX * 340 / srX))).save('Compare Old.png')
    except Exception as e:
        logger.error(f"Find Compare Failed: ", e)

#COMPARES THE OLD IMAGE WITH THE NEW
def compare(im, roles):
    try:
        #SAVES A NEW IMAGE FOR COMPARE
        logger.info("Comparing results")
        im.crop((round(gsX * 1035 / srX), round(gsX * 285 / srX), round(gsX * 1515 / srX),
                 round(gsX * 340 / srX))).save('Compare New.png')

        #COMPARES NEW(1) VS OLD(2)
        diff_results = diff("Compare New.png", "Compare Old.png", delete_diff_file=True)

        #IF THE RESULTS ARE GREATER THAN >=, GATHER IMAGES FOR THE REPORT
        if diff_results >= 0.07:
            logger.error("New log entry detected")

            #REPLACES THE OLD COMPARE IMAGE
            im.crop((round(gsX * 1035 / srX), round(gsX * 285 / srX), round(gsX * 1515 / srX),
                     round(gsX * 340 / srX))).save('Compare Old.png')

            #GATHERS IMAGE FOR THE SCANTEST ()
            im.crop((round(gsX * 1230 / srX), round(gsX * 295 / srX), round(gsX * 1310 / srX),
                     round(gsX * 300 / srX))).save('Log Scan.png')

            #CREATES AN IMAGE TO PASTE THE OTHER IMAGES TO
            img = Image.new('RGBA', (round(gsX * 480 / srX), round(gsX * 200 / srX)), (0, 0, 0, 0))
            img.save("Log Report.png")

            #MAKES THE IMAGE BACKGROUND TRANSPARENT
            trans = Image.open("Log Report.png")
            back_trans = trans.copy()

            #GATHERS ADDITIONAL IMAGES FO THE UPDATE
            im = Image.open("ARK.png")

            #GATHERS IN GAME "DAY" AND PASTES TO THE TRANSPARENT IMAGE
            region = im.crop((round(gsX * 35 / srX), round(gsX * 55 / srX), round(gsX * 195 / srX),
                              round(gsX * 85 / srX))) # DAY
            back_trans.paste(region, (0, 0))

            #GATHERS IN GAME "TIME" AND PASTES TO THE TRANSPARENT IMAGE
            region = im.crop((round(gsX * 35 / srX), round(gsX * 120 / srX), round(gsX * 135 / srX),
                              round(gsX * 150 / srX))) # TIME
            back_trans.paste(region, (round(gsX * 155 / srX), 0))

            #GATHERS TOP SECTION OF LOGS AND PASTES TO THE TRANSPARENT IMAGE
            region = im.crop((round(gsX * 1035 / srX), round(gsX * 285 / srX), round(gsX * 1515 / srX),
                              round(gsX * 460 / srX))) # SNIP OF LOGS
            back_trans.paste(region, (0, round(gsX * 29 / srX)))

            #SAVES THE IMAGE
            back_trans.save("Log Report.png")

            #READY TO DETECT THE ALERT IN LOGS
            return AlertDetection(roles)
        logger.info("Checking Parasaur")

        #SAVES IMAGE TO CHECK IF PARASAUR IS GOING OFF SAVES/OPENS IMAGE
        im.crop((round(gsX * 210 / srX), round(gsX * 32 / srX), round(gsX * 410 / srX),
                 round(gsX * 42 / srX))).save('Parasaur Scan.png')
        openscantest2 = Image.open("Parasaur Scan.png")

        #GETS PIXEL DATA FROM THE IMAGE
        sop2 = openscantest2.getdata()
        lop2 = list(sop2)

        #SCANS FOR PARASAUR PING (CYAN) ALERT = 7
        if (255, 255, 255) in lop2:
            logger.error("Alert Found: Parasaur Ping Detected")
            #SETS UP MESSAGE FOR DISCORD WEBHOOK IF ALERT FOUND
            content = (f"{roles} - **Parasaur, Simply Too Close** - {who}")
            #TODO: Fix config such that true/false are parsed as boolean rather than strings
            if parasaur_ping_alert_enabled == 'true':
                #To avoid issues just hard code the webhook here to upload an image of
                im.crop((round(gsX * 190 / srX), round(gsX * 10 / srX), round(gsX * 900 / srX),
                 round(gsX * 80 / srX))).save('Parasaur Scan.png')
                webhook = DiscordWebhook(url=alert_urls, content=content)
                with open("Parasaur Scan.png", "rb") as f:
                    webhook.add_file(file=f.read(), filename='Parasaur Scan.png')
                    webhook.execute()


        #ALERT NOT DETECTED
        logger.debug("Nothing new to report")
        time.sleep(0.1)
        endoffunc()
    except Exception as e:
        logger.error(f"Compare Failed: ", e)

#DETECTS WHAT ALERT IS IN LOGS
def AlertDetection(roles):
    try:
        windll.user32.SetProcessDPIAware()

        #OPENS IMAGE
        openscantest = Image.open("Log Scan.png")

        #GETS PIXEL DATA FROM THE IMAGE
        sop = openscantest.getdata()
        list_of_pixels = list(sop)

        #SCANS FOR STARVE (GREY) ALERT = 1
        if (184, 184, 184) in list_of_pixels:

            #CONVERT IMAGE TO TEXT
            froze = processImage()

            #IF "FROZE" NOT IN IMAGE
            if not froze:
                #SETS UP MESSAGE FOR DISCORD WEBHOOK IF ALERT FOUND
                content = (f"Something Starved - {who}")
                if starvation_alert_enabled == 'true':
                    return LiveHook(content)

            #"FROZE" IN IMAGE, IGNORE ALERT
            else:
                return
        #SCANS FOR DEMOLISH (YELLOW) ALERT = 2
        elif (255, 255, 0) in list_of_pixels:
            logger.success("Internal Demolish")
            endoffunc()
            return

        #SCANS FOR CLAIMED/TAME (GREEN) ALERT = 8
        elif (0, 255, 0) in list_of_pixels:
            logger.success("Maewing Claim/Tame")
            endoffunc()
            return

        #SCANS FOR KILLED (PINK) ALERT = 3
        elif (255, 0, 255) in list_of_pixels:

            #CONVERT IMAGE TO TEXT
            claimed = processImage()

            #IF "CLAIMED" NOT IN IMAGE
            if not claimed:
                #SETS UP MESSAGE FOR DISCORD WEBHOOK IF ALERT FOUND
                content = (f"{roles} - **Killed Something, Take a Look** - {who}")
                logger.error("Alert Found: Your tribe killed something")
                if kill_alert_enabled == 'true':
                    return LiveHook(content)
            #"CLAIMED" IN IMAGE, IGNORE ALERT
            else:
                return

        #SCANS FOR SENSOR (PLUM) ALERT = 4
        elif (158, 76, 76) in list_of_pixels:
            #SETS UP MESSAGE FOR DISCORD WEBHOOK IF ALERT FOUND
            content = (f"{svrole} - **Tek Sensor, Someone's Looking** - {who}")
            logger.error("Alert Found: Tek Sensor Triggered")
            if teksensor_alert_enabled == 'true':
                return LiveHook(content)

        #SCANS FOR DEATH/DESTRUCTION (RED) ALERT = 5
        elif (255, 0, 0) in list_of_pixels:
            # SETS UP MESSAGE FOR DISCORD WEBHOOK IF ALERT FOUND
            logger.error("Alert Found: Death/Destruction Detected")
            content = (f"{roles} - **Death/Destruction, Wake up Buddy** - {who}")
            if death_and_destruction_alert_enabled == 'true':
                return LiveHook(content)

        #ENEMY STRUCTURE DESTROYED (SAND) ALERT = 6
        elif (255, 191, 76) in list_of_pixels:
            logger.error("Alert Found: You destroyed enemy structure")
            content = (f"{roles} - **You destroyed enemy structure, Intended?**")
            if enemy_structure_destroyed_alert_enabled == 'true':
                return LiveHook(content)

        #POTENTIALLY ADD SOMETHING TO DETECT TURRET SOUNDS

        #UNDEFINED COLOURS/LOGS ARE NOT AT THE TOP
        else:
            content = (f"{roles} - **Log positioning skewed?** - {who}")
            logger.error("Alert Found: Log positioning Skewed")
            if log_positioning_alert_enabled == 'true':
                return LiveHook(content)    
    except Exception as e:
        logger.error(f"Something failed in AlertDetection: ", e)

#(LIVE ALERTS) DISCORD WEBHOOK
def LiveHook(content):
    try:
        #SENDS THE REPORT TO DISCORD WEBOOK
        webhook = DiscordWebhook(url=alert_urls, content=content)
        with open("log Report.png", "rb") as f:
            webhook.add_file(file=f.read(), filename='Log Report.png')
            webhook.execute()
            logger.debug("Alerts Updated")
        endoffunc()
    except Exception as e:
        logger.error(f"Live Hook Failed", e)

#IMAGE TO TEXT SENDS OCR TO HOOK IF SET
def processImage():
    try:
        windll.user32.SetProcessDPIAware()

        #IMAGE TO TEXT
        file = "Compare New.png"
        rawText = pytesseract.image_to_string(file)
        parsedText = rawText.replace('\n', '')

        #SAVES TEXT FROM IMAGE TO TEXT FILE
        with open('Saved Logs.txt', 'a') as f:
            f.write(f"\n {parsedText}")

            #SENDS THE OCR TEXT TO DISCORD WEBHOOK IF SET
            if "https" in ocr_urls:
                content = (f"{parsedText}")
                webhook = DiscordWebhook(url=ocr_urls, content=content)
                webhook.execute()

            #IF "FROZE" IN IMAGE RETURN TRUE
            if "froze" in parsedText:
                logger.success(parsedText)
                endoffunc()
                froze = True
                f.close()
                return froze

            # IF "CLAIMED" IN IMAGE RETURN TRUE
            elif "claimed" in parsedText:
                logger.success(parsedText)
                endoffunc()
                claimed = True
                return claimed
    except Exception as e:
        logger.error(f"Process Image Failed", e)

#GATHERS IMAGES FOR LOG OVERVIEW
def ScreenGrab():
    try:
        logger.info("Getting Screen Grab")
        windll.user32.SetProcessDPIAware()

        #CREATES AN IMAGE TO PASTE THE OTHER IMAGES TO
        Image.new('RGBA', (round(gsX * 1095 / srX), round(gsX * 930 / srX)), (0, 0, 0, 0)).save("Log Update.png")

        #MAKES THE IMAGE BACKGROUND TRANSPARENT
        trans = Image.open("Log Update.png")
        back_trans = trans.copy()
        im = Image.open("ARK.png")

        #GATHERS LOGS AND PASTES TO THE TRANSPARENT IMAGE
        region = im.crop((round(gsX * 1012 / srX), round(gsX * 160 / srX), round(gsX * 1545 / srX),
                          round(gsX * 1095 / srX)))
        back_trans.paste(region, (0, 0))

        #GATHERS IN GAME "DAY" AND PASTES TO THE TRANSPARENT IMAGE
        region = im.crop((round(gsX * 35 / srX), round(gsX * 55 / srX), round(gsX * 195 / srX),
                              round(gsX * 85 / srX))) # DAY
        back_trans.paste(region, (23, round(gsX * 73 / srX)))

        #GATHERS IN GAME "TIME" AND PASTES TO THE TRANSPARENT IMAGE
        region = im.crop((round(gsX * 35 / srX), round(gsX * 120 / srX), round(gsX * 135 / srX),
                              round(gsX * 150 / srX))) # TIME
        back_trans.paste(region, (round(gsX * 183 / srX), round(gsX * 73 / srX)))

        #GATHERS GLOBAL CHAT
        region = im.crop((round(gsX * 40 / srX), round(gsX * 1070 / srX), round(gsX * 690 / srX),
                 round(gsX * 1335 / srX)))
        region.save("Global New.png")

        #CHECK TO SEE IF IMAGE EXISTS, IF FALSE, CREATE ONE
        Glbl2c = os.path.exists("Global Old.png")
        if Glbl2c == False:
            region.save("Global Old.png")

        #COMPARES NEW(1) VS OLD(2)
        diff_results = diff("Global New.png", "Global Old.png", delete_diff_file=True)

        #IF THE RESULTS ARE GREATER THAN >=, GATHER IMAGES FOR THE REPORT
        if diff_results >= 0.02:
            #REPLACES THE OLD COMPARE IMAGE
            region.save("Global Old.png")
            back_trans.paste(region, (round(gsX * 533 / srX), 0))
            GlblPost = 1

        #NO CHANGE IN GLOBAL
        else:
            GlblPost = 0
        back_trans.save("Log Update.png")

        #PREP MORE IMAGES FOR LOG OVERVIEW
        PrepPlayerCount()

        #OPEN IMAGES TO PREPARE FOR FINAL PROCESSING
        im = Image.open("Log Update.png")
        im2 = Image.open("Player Count.png")
        back_im = im.copy()

        #IF GLOBAL IS DIFFERENT, POST IN THE UPDATES
        if GlblPost == 1:
            back_im.paste(im2, (round(gsX * 533 / srX), round(gsX * 253 / srX)))
            back_im.save("Log Update.png")

        #GLOBAL IS NOT DIFFERENT, CARRY ON
        else:
            back_im.paste(im2, (round(gsX * 533 / srX), 0))
            back_im.save("Log Update.png")
        LogHook()
    except Exception as e:
        logger.error(f"Screen Grab Failed", e)

#GATHERS IMAGES FOR ONLINE PLAYERS (X/6) - (MORE FOR SMALLTRIBES)
def PrepPlayerCount():
    windll.user32.SetProcessDPIAware()

    #CREATES AN IMAGE TO PASTE THE OTHER IMAGES TO
    img = Image.new('RGBA', (round(gsX * 270 / srX), round(gsX * 370 / srX)), (0, 0, 0, 0))
    img.save("Player Count.png")

    #MAKES THE IMAGE BACKGROUND TRANSPARENT
    round(gsX * 1645 / srX), round(gsX * 300 / srX)
    trans = Image.open("Player Count.png")
    back_trans = trans.copy()

    #OPENS IMAGE
    im = Image.open("ARK.png")

    #GATHERS ONLINE MEMBERS - (X/6)
    region = im.crop((round(gsX * 850 / srX), round(gsX * 380 / srX), round(gsX * 935 / srX), round(gsX * 415 / srX)))  # (region=(1184, 264, 461, 36))
    back_trans.paste(region, (0, 0))
    im.load()

    #SCANS TRIBE SLOT REGIONS FOR PIXEL IN "OFFLINE"
    OnOff1 = x, y = round(gsX * 863 / srX), round(gsX * 478 / srX)
    OnOff2 = x, y = round(gsX * 863 / srX), round(gsX * 538 / srX)
    OnOff3 = x, y = round(gsX * 863 / srX), round(gsX * 599 / srX)
    OnOff4 = x, y = round(gsX * 863 / srX), round(gsX * 658 / srX)
    OnOff5 = x, y = round(gsX * 863 / srX), round(gsX * 718 / srX)
    OnOff6 = x, y = round(gsX * 863 / srX), round(gsX * 778 / srX)
    Slot1 = im.getpixel(OnOff1)
    Slot2 = im.getpixel(OnOff2)
    Slot3 = im.getpixel(OnOff3)
    Slot4 = im.getpixel(OnOff4)
    Slot5 = im.getpixel(OnOff5)
    Slot6 = im.getpixel(OnOff6)
    #print(Slot1, Slot2, Slot3, Slot4, Slot5, Slot6)

    #IF OFFLINE SET SLOT TO 0 (NO IMAGE THERE)
    if Slot1 == (121, 184, 195):  # If Offline
        #SLOT 1
        Slot1 = 0
        S1 = "Slot 1 Offline"
        logger.error("Slot 1 Offline")
    #IF ONLINE SET SLOT TO 1 (IMAGE GOES HERE)
    else:
        #SLOT 1
        Slot1 = 1
        S1 = "Slot 1 Online"
        logger.success("Slot 1 Online")

    #IF OFFLINE SET SLOT TO 0 (NO IMAGE THERE)
    if Slot2 == (121, 184, 195):
        #SLOT 2
        Slot2 = 0
        S2 = "Slot 2 Offline"
        logger.error("Slot 2 Offline")
    #IF ONLINE SET SLOT TO 1 (IMAGE GOES HERE)
    else:
        #SLOT 2
        Slot2 = 1
        S2 = "Slot 2 Online"
        logger.success("Slot 2 Online")

    #IF OFFLINE SET SLOT TO 0 (NO IMAGE THERE)
    if Slot3 == (121, 183, 195):
        #SLOT 3
        Slot3 = 0
        S3 = "Slot 3 Offline"
        logger.error("Slot 3 Offline")
    #IF ONLINE SET SLOT TO 1 (IMAGE GOES HERE)
    else:
        #SLOT 3
        Slot3 = 1
        S3 = "Slot 3 Online"
        logger.success("Slot 3 Online")

    #IF OFFLINE SET SLOT TO 0 (IMAGE GOES HERE)
    if Slot4 == (121, 184, 195):
        #SLOT 4
        Slot4 = 0
        S4 = "Slot 4 Offline"
        logger.error("Slot 4 Offline")
    #IF ONLINE SET SLOT TO 1 (NO IMAGE THERE)
    else:
        #SLOT 4
        Slot4 = 1
        S4 = "Slot 4 Online"
        logger.success("Slot 4 Online")

    #IF OFFLINE SET SLOT TO 0 (NO IMAGE THERE)
    if Slot5 == (121, 184, 195):
        #SLOT 5
        Slot5 = 0
        S5 = "Slot 5 Offline"
        logger.error("Slot 5 Offline")
    #IF ONLINE SET SLOT TO 1 (IMAGE GOES HERE)
    else:
        #SLOT 5
        Slot5 = 1
        S5 = "Slot 5 Online"
        logger.success("Slot 5 Online")

    #IF OFFLINE SET SLOT TO 0 (NO IMAGE THERE)
    if Slot6 == (121, 184, 195):
        #SLOT 6
        Slot6 = 0
        S6 = "Slot 6 Offline"
        logger.error("Slot 6 Offline")
    #IF ONLINE SET SLOT TO 1 (IMAGE GOES HERE)
    else:
        #SLOT 6
        Slot6 = 1
        S6 = "Slot 6 Online"
        logger.success("Slot 6 Online")

    #GATHERS IMAGES FOR TRIBE MEMBER, ONLINE/OFFLINE AND PASTES TO THE TRANSPARENT IMAGE
    #DETERMINES WHERE TO PLACE EACH IMAGE IN ACCORDANCE WITH TRIBE SLOT/WHO IS ON
    if Slot1 == 1:
        #SLOT 1
        #TRIBE MEMBER
        region = im.crop((round(gsX * 500 / srX), round(gsX * 450 / srX), round(gsX * 690 / srX),
                          round(gsX * 507 / srX)))

        #ONLINE/OFFLINE
        region2 = im.crop((round(gsX * 855 / srX), round(gsX * 450 / srX), round(gsX * 938 / srX),
                          round(gsX * 507 / srX)))

        back_trans.paste(region, (0, round(gsX * 35 / srX))) #27
        back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 35 / srX)))

    if Slot2 == 1:
        #SLOT 2
        #TRIBE MEMBER
        region = im.crop((round(gsX * 500 / srX), round(gsX * 510 / srX), round(gsX * 690 / srX),
                          round(gsX * 567 / srX)))

        #ONLINE/OFFLINE
        region2 = im.crop((round(gsX * 855 / srX), round(gsX * 510 / srX), round(gsX * 938 / srX),
                          round(gsX * 567 / srX)))
        if Slot1 == 0:
            back_trans.paste(region, (0, round(gsX * 35 / srX))) #27
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 35 / srX)))
            Slot1 = 1
            Slot2 = 0
        else:
            back_trans.paste(region, (0, round(gsX * 91 / srX))) #77
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 91 / srX)))
            Slot2 = 1

    if Slot3 == 1:
        #SLOT 3
        #TRIBE MEMBER
        region = im.crop((round(gsX * 500 / srX), round(gsX * 570 / srX), round(gsX * 690 / srX),
                          round(gsX * 627 / srX)))

        #ONLINE/OFFLINE
        region2 = im.crop((round(gsX * 855 / srX), round(gsX * 570 / srX), round(gsX * 938 / srX),
                          round(gsX * 627 / srX)))
        if Slot1 == 0:
            back_trans.paste(region, (0, round(gsX * 35 / srX))) #27
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 35 / srX)))
            Slot1 = 1
            Slot3 = 0
        elif Slot2 == 0:
            back_trans.paste(region, (0, round(gsX * 91 / srX))) #77
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 91 / srX)))
            Slot2 = 1
            Slot3 = 0
        else:
            back_trans.paste(region, (0, round(gsX * 147 / srX))) #127
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 147 / srX)))
            Slot3 = 1

    if Slot4 == 1:
        #SLOT 4
        #TRIBE MEMBER
        region = im.crop((round(gsX * 500 / srX), round(gsX * 630 / srX), round(gsX * 690 / srX),
                          round(gsX * 687 / srX)))

        #ONLINE/OFFLINE
        region2 = im.crop((round(gsX * 855 / srX), round(gsX * 630 / srX), round(gsX * 938 / srX),
                          round(gsX * 687 / srX)))
        if Slot1 == 0:
            back_trans.paste(region, (0, round(gsX * 35 / srX))) #27
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 35 / srX)))
            Slot1 = 1
            Slot4 = 0
        elif Slot2 == 0:
            back_trans.paste(region, (0, round(gsX * 91 / srX))) #77
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 91 / srX)))
            Slot2 = 1
            Slot4 = 0
        elif Slot3 == 0:
            back_trans.paste(region, (0, round(gsX * 147 / srX))) #127
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 147 / srX)))
            Slot3 = 1
            Slot4 = 0
        else:
            back_trans.paste(region, (0, round(gsX * 203 / srX))) #177
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 203 / srX)))
            Slot4 = 1

    if Slot5 == 1:
        #SLOT 5
        #TRIBE MEMBER
        region = im.crop((round(gsX * 500 / srX), round(gsX * 690 / srX), round(gsX * 690 / srX),
                          round(gsX * 747 / srX)))

        #ONLINE/OFFLINE
        region2 = im.crop((round(gsX * 855 / srX), round(gsX * 690 / srX), round(gsX * 938 / srX),
                          round(gsX * 747 / srX)))
        if Slot1 == 0:
            back_trans.paste(region, (0, round(gsX * 35 / srX))) #27
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 35 / srX)))
            Slot1 = 1
            Slot5 = 0
        elif Slot2 == 0:
            back_trans.paste(region, (0, round(gsX * 91 / srX))) #77
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 91 / srX)))
            Slot2 = 1
            Slot5 = 0
        elif Slot3 == 0:
            back_trans.paste(region, (0, round(gsX * 147 / srX))) #127
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 147 / srX)))
            Slot3 = 1
            Slot5 = 0
        elif Slot4 == 0:
            back_trans.paste(region, (0, round(gsX * 203 / srX))) #177
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 203 / srX)))
            Slot4 = 1
            Slot5 = 0
        else:
            back_trans.paste(region, (0, round(gsX * 259 / srX))) #227
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 259 / srX)))
            Slot5 = 1

    if Slot6 == 1:
        #SLOT 6
        #TRIBE MEMBER
        region = im.crop((round(gsX * 500 / srX), round(gsX * 750 / srX), round(gsX * 690 / srX),
                          round(gsX * 807 / srX)))

        #ONLINE/OFFLINE
        region2 = im.crop((round(gsX * 855 / srX), round(gsX * 750 / srX), round(gsX * 938 / srX),
                          round(gsX * 807 / srX)))
        if Slot1 == 0:
            back_trans.paste(region, (0, round(gsX * 35 / srX))) #27
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 35 / srX)))
            Slot1 = 1
            Slot6 = 0
        elif Slot2 == 0:
            back_trans.paste(region, (0, round(gsX * 91 / srX))) #77
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 91 / srX)))
            Slot2 = 1
            Slot6 = 0
        elif Slot3 == 0:
            back_trans.paste(region, (0, round(gsX * 147 / srX))) #127
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 147 / srX)))
            Slot3 = 1
            Slot6 = 0
        elif Slot4 == 0:
            back_trans.paste(region, (0, round(gsX * 203 / srX))) #177
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 203 / srX)))
            Slot4 = 1
            Slot6 = 0
        elif Slot5 == 0:
            back_trans.paste(region, (0, round(gsX * 259 / srX))) #227
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 259 / srX)))
            Slot5 = 1
            Slot6 = 0
        else:
            back_trans.paste(region, (0, round(gsX * 315 / srX))) #277
            back_trans.paste(region2, (round(gsX * 190 / srX), round(gsX * 315 / srX)))
            Slot6 = 1
    back_trans.save("Player Count.png")

#LOG OVERVIEW DISCORD WEBHOOK IF SET
def LogHook():
    if "https" in log_urls:
        try:
            #SETS THE WEBHOOK/MESSAGE
            content = (f"**Quick Update** - {who}")

            #SENDS THE REPORT TO DISCORD WEBHOOK
            webhook = DiscordWebhook(url=log_urls, content=content)
            with open("Log Update.png", "rb") as f:
                webhook.add_file(file=f.read(), filename='Log Update.jpg')
                webhook.execute()
            logger.debug("Overview Updated")
            endoffunc()
        except Exception as e:
            logger.error(f"Log Overview Failed", e)

#MAIN LOOP OF REDLIGHT
def startup():
    checkRunning()

    #GETS SYSTEM TIME FOR USE IN LOG OVERVIEW
    timestamp = time.time()
    date_time = datetime.fromtimestamp(timestamp)
    str_time = date_time.strftime("%M%S")

    #TAKES SCREENSHOT OF ARK (REGARDLESS OF IF THE WINDOW IS ACTIVE OR NOT)
    try:
            logger.info("Taking SS")
            hwnd = win32gui.FindWindow(None, "ArkAscended")  # Finds targeted window
            windll.user32.SetProcessDPIAware()
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bot - top
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
            saveDC.SelectObject(saveBitMap)
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)  # 0/1 Come back Black image, 2 Returns an image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            inactivebuffer = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            if result == 1:
                inactivebuffer.save("ARK.png")
                im = Image.open("ARK.png")
    except Exception as e:
        logger.error(f"Issue with background image: ", e)

    #SAVES IMAGE FOR CHECKING IF LOGS ARE OPEN
    im.crop((round(gsX * 990 / srX), round(gsX * 155 / srX), round(gsX * 1090 / srX),
             round(gsX * 227 / srX))).save('Tribe Log.png')
    tribe = arelogs()

    #IF LOGS ARE OPEN CHECK SYSTEM TIME, IF SYSTIME = THESE TIMES PERFORM LOG OVERVIEW
    if tribe:
        #EG 950 = 9m:50s
        if str(950) in str_time or str(951) in str_time\
                or str(952) in str_time or str(953) in str_time\
                or str(954) in str_time:
            ScreenGrab()
        #CAN ADD A PRECHECK TO DETERMINE WHERE WE ARE ON THE ARK MENU (RECONNECT)
        findcompare(im)
        compare(im, roles)

        #DELAY BETWEEN SCANS
        time.sleep(1.9)
        return

    #IF LOGS NOT OPEN, COUNTDOWN 60s OR 1m
    logger.error("Logs closed, 60s cooldown")

    #WRITES TO CONSOLE THE TIME REMAINING (60 CONTROLS THE COOLDOWN)
    for remaining in range(60, 0, -1):
        time.sleep(0.2)
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining".format(remaining))
        sys.stdout.flush()
        time.sleep(0.8)
    sys.stdout.write("\r")
    endoffunc()
    return

#STARTS REDLIGHT UP
if __name__ == '__main__':
    windll.user32.SetProcessDPIAware()
    logger.log(who, "Starting LogBot")
    ark_running = checkRunning()
    startup()
    #ScreenGrab()

#IF "ark_running" = TRUE, CONTINUE RUNNING
while True:
    startup()

#Alert:=
    # =0 ;No Change
    # =1 ;Cryo/Starve (Grey) - Cryo ignored, Starve sent as general update
    # =2 ;Demolish (Yellow) - Demolish ignored
    # =3 ;Killed/Claimed (Pink) - Pings "roles" for killed, ignores Claimed
    # =4 ;Sensor (Plum) - Pings "svrole"
    # =5 ;Death/Destruction (Red) - Pings "roles"
    # =6 ;Enemy structure destroyed (Sand) - Pings "roles"
    # =7 ;Parasaur Ping (Cyan) - Pings "roles"
    # =8 ;Claimed/Tamed (Green) Ingores
    # =9 ;Tek Turret (Audio)? - Not defined
    # =X ;Undefined Colour - Pings "roles"
