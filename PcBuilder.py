from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
import requests
from lxml.html import fromstring
from itertools import cycle
import time
import random
from selenium import webdriver

'''
This program uses PcPartPicker build guides, completed builds and parts lists to assemble a full computer system
along with peripherals. A very usefull program for people looking for a pc which meets thier needes without much thought
'''

def get_html(url): #gets the html for any url
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    time.sleep(random.randint(1,5)/10)
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


def money_convertion(money): #converts a a price from a string to useable format
    money = float(money.replace(" ", "").replace("\n", "").replace("+", "").replace("£", ""))
    return money


def completed_builds(money1, money2): #finds the best community pc
    money = float((money1+money2)/200)
    money = round(money)
    money = int(money*100)
    url = "https://uk.pcpartpicker.com/builds/#sort=recent&X="
    url = url + str((money-200)*100) + "," + str((money+200)*100)
    if minipc == "no":
        url += "&E=4,3,1"
    url += "&page=" #the url will look something like this - https://uk.pcpartpicker.com/builds/#sort=recent&X=90000,130000&E=4,3,1&page=
    closePrices = []
    closeLinks = []
    browser = webdriver.Firefox()
    browser.minimize_window() #creates and minimizes the browser
    type(browser)
    for i in range(5): #how many pages, 5 is perfect mix between time and choice
        time.sleep(1)
        page = i + 1
        browser.implicitly_wait(6) #used so that the page has time to load
        browser.get(url+str(page)) #open the url plus the page number 
        browser.implicitly_wait(6)
        time.sleep(2)
        prices = browser.find_elements_by_class_name("log__price")
        browser.implicitly_wait(6)
        links = browser.find_elements_by_class_name("logGroup__target")
        browser.implicitly_wait(6)
        for g in range(20): #how many pcs to check(there are 20 on a page, so 20 max)
            browser.implicitly_wait(3)
            price = prices[g].text
            browser.implicitly_wait(3)
            link = links[g].get_attribute('href')
            if "+" not in price: #it appears that prices with a + means they are modified lists. This means we cant use them, eg a person may list the gpu as
                                # costing £300, because they bought it on ebay, even though it cost £500 new
                price = price.replace("£", "")
                difference = (int(money))-(round(float(price)))
                if difference < 0:
                    difference = difference * -1
                if difference < 200: #if the price of the pc is close to what we want, sometimes the seach doesnt always show prices specifed by the X= modifer
                    closePrices.append(price)
                    closeLinks.append(link)
    validLinks = []
    validPrices = []
    for i in range(len(closePrices)): #does further checks on the collected builds, normally about 10 get to this point.
        disq = False
        price = closePrices[i]
        link = closeLinks[i]
        browser.get(link)
        partList = browser.find_element_by_link_text("View full price breakdown").get_attribute("href")
        browser.find_element_by_link_text("View full price breakdown").click() #opens the part list
        browser.implicitly_wait(3)
        partPrice = browser.find_elements_by_class_name("td__price")
        where = browser.find_elements_by_class_name("td__where")
        components = browser.find_elements_by_class_name("td__component")
        for j in range(len(where)):
            place = where[j].text
            if str(place) == "Purchased" or partPrice[j].text == "No Prices" or partPrice[j].text == "No Prices\n Available" or "No Prices" in partPrice[j].text or "$" in partPrice[j].text:
                #double checks to make sure that the part is still avaliable to buy and a price wasnt set manually.
                disq = True
        for component in components:
            component = component.text
            if component == "Monitor" or component == "Keyboard" or component == "Mouse" or component == "Headphones" or component == "Speakers" or component == "UPS" or component == "Custom":
                #makes sure that the part list doesnt have any peripherals, this influences the price of the build
                disq = True
        if partList in validLinks:
            #makes sure theres no duplicates
            disq = True
        if disq == False:
            #if it passed all tests
            validLinks.append(partList)
            validPrices.append(price)
    closest1difference = 2000
    closest2difference = 2000
    closest1number = 0
    closest2number = 1
    for i in range(len(validPrices)): #goes through all the passed pc's and finds the closest 2 pcs to the desired price
        difference = float(validPrices[i]) - money
        if difference < 0:
            difference = difference * -1
        if difference < closest1difference:
            closest2difference = closest1difference
            closest2number = closest1number
            closest1difference = difference
            closest1number = i
        elif difference < closest2difference:
            closest2difference = difference
            closest2number = i

    #all the relevent data is found about the builds, and the data is printed out and appended to a list called info and info2
            
    browser.get(validLinks[closest1number])
    browser.implicitly_wait(3)
    parts = browser.find_elements_by_class_name("tr__product")
    closest1cpu = parts[0].find_element_by_class_name("td__name").text
    closest1gpu = browser.find_elements_by_partial_link_text("Video Card")[1].text
    browser.implicitly_wait(3)
    browser.get(validLinks[closest2number])
    browser.implicitly_wait(3)
    parts = browser.find_elements_by_class_name("tr__product")
    closest2cpu = parts[0].find_element_by_class_name("td__name").text
    closest2gpu = browser.find_elements_by_partial_link_text("Video Card")[1].text
    print("\nCommunity Recomended Pc: £" + validPrices[closest1number] + " - " + closest1cpu + " - " + closest1gpu + " - " + validLinks[closest1number])
    info.append("Community Recomended Pc: £" + validPrices[closest1number] + " - " + closest1cpu + " - " + closest1gpu + " - " + validLinks[closest1number] + "\n")
    print("Other Community Recomended Pc: £" + validPrices[closest2number] + " - " + closest2cpu + " - " + closest2gpu + " - " + validLinks[closest2number] + "\n")
    info2.append("Other Community Recomended Pc: £" + validPrices[closest2number] + " - " + closest2cpu + " - " + closest2gpu + " - " + validLinks[closest2number] + "\n")
    browser.close()
    browser.quit()


def pc_guide(money1, money2): #used to find the Builds made by the devs of the site, these are usually high quality, but there is little choice.
                              #here we use requests and bs4 instead of selenium as all the info we need is stored in the source code
    url = "https://uk.pcpartpicker.com/guide/"
    pcGuideSoup = get_html(url)
    block = pcGuideSoup.find_all(class_="guideGroup guideGroup__card")
    closestPc = 0
    closestDifference = 1000
    secondClosestPc = 0
    secondClosestDifference = 1000
    money = (money1+money2)/2
    for pc in block:
        name = pc.find(class_="guideGroup__content--wrapper1").find(class_="guide__title").get_text()
        if name != "Portable LAN Build": #this pc is disqualified as it isnt optimal for price, but space
            price = money_convertion(pc.find(class_="guideGroup__content--wrapper2").find(class_="guide__numbers").find(class_="guide__price").get_text())
            difference = price - money
            if difference < 0: #finds the closest priced pc on the page
                difference = difference * -1
            if price > money:
                difference = difference * 2
            if difference < closestDifference:
                secondClosestPc = closestPc
                secondClosestDifference = closestDifference
                closestDifference = difference
                closestPc = pc
            elif difference < secondClosestDifference:
                secondClosestDifference = difference
                secondClosestPc = pc

    #and follows the same procees to display it and save it
    
    closestPrice = money_convertion(closestPc.find(class_="guideGroup__content--wrapper2").find(class_="guide__numbers").find(class_="guide__price").get_text())
    secondClosestPrice = money_convertion(secondClosestPc.find(class_="guideGroup__content--wrapper2").find(class_="guide__numbers").find(class_="guide__price").get_text())
    closestCpu = closestPc.find(class_="guideGroup__content--wrapper1").find(class_="guide__keyProducts list-unstyled").find("li").get_text()
    closestGpu = (closestPc.find(class_="guideGroup__content--wrapper1").find(class_="guide__keyProducts list-unstyled").find("li").find_next("li").get_text().replace("Parametric Video Card (Chipset: ", "").split(";", 1)[0].replace(")", ""))
    secondClosestCpu = secondClosestPc.find(class_="guideGroup__content--wrapper1").find(class_="guide__keyProducts list-unstyled").find("li").get_text()
    secondClosestGpu = (secondClosestPc.find(class_="guideGroup__content--wrapper1").find(class_="guide__keyProducts list-unstyled").find("li").find_next("li").get_text().replace("Parametric Video Card (Chipset: ", "").split(";", 1)[0].replace(")", ""))
    closestname = closestPc.find(class_="guideGroup__content--wrapper1").find(class_="guide__title").get_text()
    secondClosestname = secondClosestPc.find(class_="guideGroup__content--wrapper1").find(class_="guide__title").get_text()
    link = closestPc.find(class_="guideGroup__target")
    secondLink = secondClosestPc.find(class_="guideGroup__target")
    print("\nRecomended PC: " + closestname + " - £" + str(closestPrice) + " - " + str(closestCpu) + " - " + str(closestGpu) + " - https://uk.pcpartpicker.com" + link["href"])
    info.append("Recomended PC: " + closestname + " - £" + str(closestPrice) + " - " + str(closestCpu) + " - " + str(closestGpu) + " - https://uk.pcpartpicker.com" + link["href"] + "\n")
    print("Other Recomended PC: " + secondClosestname + " - £" + str(secondClosestPrice) + " - " + str(secondClosestCpu) + " - " + str(secondClosestGpu) + " - https://uk.pcpartpicker.com" + secondLink["href"] + "\n\nThe process is not over, please wait")
    info2.append("Other Recomended PC: " + secondClosestname + " - £" + str(secondClosestPrice) + " - " + str(secondClosestCpu) + " - " + str(secondClosestGpu) + " - https://uk.pcpartpicker.com" + secondLink["href"])
    money1 = money - closestPrice
    money2 = money - secondClosestPrice

  
def FindPeripherals(url, suggestedPrice): #used to find the peripherals
    count = 1
    page = 1
    browser = webdriver.Firefox()
    type(browser)
    part2Name = "None"
    while True: #keeps going untill perameters are met
        browser.get(url + "&page=" + str(page)) #opens up the part list
        browser.minimize_window() 
        browser.implicitly_wait(5)
        components = len(browser.find_elements_by_class_name("td__price"))
        for i in range(components): #for all of the parts on the page, around 100 normally

            try:
                price = int(float(browser.find_elements_by_class_name("td__price")[i].text.replace("Add", "").replace("£", ""))) #finds the price of the part
            except:
                price = 0 #some parts dont have listed prices, because they arent being sold anywhere, in this case we make it cost 0
            try:
                name = (str(browser.find_elements_by_class_name("td__nameWrapper")[i].text)).lower() #the same of the name
            except:
                name = "0"
            if ((price > int(suggestedPrice)*0.85 and price < int(suggestedPrice)*1.3 and price != 0) or (int(suggestedPrice) == 0)) and "keypad" not in name: #if the price is close to what we want
                if count == 1: #find 2 of each part
                    part1Name = browser.find_elements_by_class_name("td__nameWrapper")[i].text
                    part1Link = browser.find_elements_by_class_name("td__name")[i].find_element_by_tag_name("a").get_attribute('href')
                    part1Price = price
                    count += 1
                if count == 2 and browser.find_elements_by_class_name("td__nameWrapper")[i].text != part1Name:
                    part2Link = browser.find_elements_by_class_name("td__name")[i].find_element_by_tag_name("a").get_attribute('href')
                    part2Name = browser.find_elements_by_class_name("td__nameWrapper")[i].text
                    part2Price = price
                    count += 1
                    
        if count < 2: #if we wont have 2 parts yet do next page
            page += 1
        if count >= 2 and part2Name != "None": #if we have 2 parts break from loop
            break
        if (count < 2 and page == 4): #if we are on page 4 and still havent got a part we change the desired price to find a less well suited part
            print("No Matches Found, widening search")
            page = 1
            suggestedPrice += random.randint(-10, 15)
            if suggestedPrice < 0:
                suggestedPrice = 10
    browser.close()
    browser.quit()
    return part1Name, part2Name, part1Link, part2Link, part1Price, part2Price #return the parts we found


def OS(money): #if they want an os we give them standard windows 10 home
    info.append("Recomended Operating System - " + str("Microsoft Windows 10 Home OEM 64-bit") + " - £" + str(90) + " - " + str("https://uk.pcpartpicker.com/product/96RFf7/microsoft-os-kw900139") + "\n")
    info2.append("Other recomended Operating System - " + str("Microsoft Windows 10 Home OEM 64-bit") + " - £" + str(90) + " - " + str("https://uk.pcpartpicker.com/product/96RFf7/microsoft-os-kw900139") + "\n")
    money -= 90 #we aproximate price to be 90
    return money


def monitor(money): #the function for getting an monitor, first we collect all the relevent info
    while True: #all inputs are encased with try and except blocks and while loops, so that inputed data is correct
        try:
            monNumber = int(input("How many monitors do you want: "))
            if monNumber >= 0:
                break
            else:
                print("Minimum is 1")
        except:
            print("Invalid Input, Integers Only")
    totalCost = 0
    money1 = money
    money2 = money
    for i  in range(monNumber):
        print("Resolution (from this list - 1920x1080, 2560x1080, 2560x1440, 3440x1440, 3840x2160)")
        while True:
            try:
                resolutionx = int(input("X: "))
                resolutiony = int(input("Y: "))
                if resolutionx == 1920 or resolutionx == 2560 or resolutionx == 3440 or resolutionx == 3840:
                    if resolutiony == 1080 or resolutiony == 1440 or resolutiony == 2160:
                        break
                    else:
                        print(resolutiony + " was not an option")
                else:
                    print(resolutionx + " was not an option")
            except:
                print("Invalid Input")
        while True:
            try:
                print("Minium refresh rate (from this list - 60, 70, 75, 85, 95, 100, 120, 144, 155, 166, 180, 200, 240")
                refresh = int(input("Refresh rate: "))
                if refresh == 60 or refresh == 70 or refresh == 75 or refresh == 85 or refresh == 95 or refresh == 100 or refresh == 144 or refresh == 155 or refresh == 166 or refresh == 180 or refresh == 200 or refresh == 240:
                    print("Maxium response time in ms, eg 1, 2, 3, 4 ect, max 20")
                    response = int(input("Response time: "))
                    if response > 0 and response <= 20:
                        print("How much would you like it to cost roughly, type 0 for as cheap as possible")
                        suggestedPrice = int(input("Cost: "))
                        if suggestedPrice >= 0:
                            break
                        else:
                            print("Must be 0 or more")
                    else:
                        print("Must be between 1 and 20 including")
                else:
                    print(refresh + " is not a valid Input")
            except:
                print("Invalid Input")
        print("\nPlease wait")
        url = "https://uk.pcpartpicker.com/products/monitor/#T="
        
        for g in range(response): #all the parameters we just collected are added to the url
            if g == 0:   
                url = url + str(g+1)
            else:
                url = url + "," + str(g+1)
        url = url + "&D=" + str(refresh*1000) + ",240000&r=" + str(resolutionx*10) + str(resolutiony) + "&sort=price"

        part1Name, part2Name, part1Link, part2Link, part1Price, part2Price = FindPeripherals(url, int(suggestedPrice)) #we use the FindPeripherals function to scrape
        #the data collected is then printed out and appended to info and info2
        print("\nRecomended monitor - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link))
        info.append("Recomended monitor - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link) + "\n")
        print("Other recomended monitor - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        info2.append("Other recomended monitor - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        money1 = money - part1Price
        money2 = money - part2Price
    return money1, money2


def keyboard(money1, money2): #the same process is repeated for all peripherals
    while True:
        needed = str(input("Do you need a keyboard: ")).lower()
        if needed == "yes" or needed == "no":
            break
        else:
            print("Must be yes or no")
    if needed == "yes" or needed == "y":
        while True:
            machanical = str(input("Machanical, yes or no: ")).lower()
            if machanical == "yes" or machanical == "no":
                break
            else:
                print("Must be yes or no")
        while True:
            rgb = str(input("RGB, yes or no: ")).lower()
            if rgb == "yes" or rgb == "no":
                break
            else:
                print("Must be yes or no")
        while True:
            small = str(input("Include Mini Keyboards, yes or no: ")).lower()
            if small == "yes" or small == "no":
                break
            else:
                print("Must be yes or no") 
        if autoPrice == "yes" or autoPrice == "y":
            suggestedPrice = startingMoney/15
        else:
            while True:
                try:
                    suggestedPrice = int(input("Roughly, how much should it cost: "))
                    if suggestedPrice >= 0:
                        break
                    else:
                        print("Must be 0 or more")
                except:
                    print("Invalid Input, Integers Only")
            
        print("\nPlease wait")
        url = "https://uk.pcpartpicker.com/products/keyboard/#"
        if machanical == "yes" or machanical == "y":
            url += "k=1"
        if rgb == "yes" or rgb == "y":
            url += "&b=46"
        if small == "yes" or small == "y":
            url += "&d=5,2,3,4"
        else:
            url += "&d=5,4"
        url += "&sort=price"
        part1Name, part2Name, part1Link, part2Link, part1Price, part2Price = FindPeripherals(url, int(suggestedPrice))
        print("\nRecomended keyboard - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link))
        info.append("Recomended keyboard - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link) + "\n")
        print("Other recomended keyboard - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        info2.append("Other recomended keyboard - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        money1 -= part1Price
        money2 -= part2Price
    return money1, money2


def mouse(money1, money2):
    while True:
        needed = str(input("Do you need a mouse: ")).lower()
        if needed == "yes" or needed == "no":
            break
        else:
            print("Invalid Input, yes or no question")
    if needed == "yes" or needed == "y":
        while True:
            try:
                connection = int(input("Wired(0) or Wireless(1): "))
                if connection == 0 or connection == 1:
                    break
                else:
                    print("Only 0 or 1")
            except:
                print("Invalid Input, 0 or 1")
        if autoPrice == "yes" or autoPrice == "y":
            suggestedPrice = startingMoney/33
        else:
            while True:
                try:
                    suggestedPrice = int(input("Roughly, how much should it cost: "))
                    if suggestedPrice >= 0:
                        break
                    else:
                        print("Must be 0 or more")
                except:
                    print("Invalid Input, Integer Only")
        print("\nPlease wait")
        url = "https://uk.pcpartpicker.com/products/mouse/#"
        if connection == 0:
            url += "k=1"
        elif connection == 1:
            url += "k=2,3"
        url += "&m=8,11,14,18,454,162,453,230,242"
        url += "&t=2,1&sort=price"
        part1Name, part2Name, part1Link, part2Link, part1Price, part2Price = FindPeripherals(url, int(suggestedPrice))
        print("\nRecomended mouse - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link))
        info.append("Recomended mouse - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link) + "\n")
        print("Other recomended mouse - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        info2.append("Other recomended mouse - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        money1 -= part1Price
        money2 -= part2Price
    return money1, money2


def headphones(money1, money2):
    while True:
        needed = str(input("Do you need headphones: ")).lower()
        if needed == "yes" or needed == "no":
            break
        else:
            print("Invalid Input, yes or no question")
    if needed == "yes" or needed == "y":
        while True:
            try:
                mic = int(input("With microphone(0) or without(1): "))
                connection = int(input("Wireless(0) or wired(1): "))
                if (mic == 0 or mic == 1) and (connection == 0 or connection == 1):
                    break
                else:
                    print("Only 0 or 1")
            except:
                print("Invalid Input, 0 or 1")
        if autoPrice == "yes" or autoPrice == "y":
            suggestedPrice = startingMoney/18
        else:
            while True:
                try:
                    suggestedPrice = int(input("Roughly, how much should it cost: "))
                    if suggestedPrice >= 0:
                        break
                    else:
                        print("Must be 0 or more")
                except:
                    print("Invalid Input, Integer Only")
        print("\nPlease wait")
        url = "https://uk.pcpartpicker.com/products/headphones/#"
        if mic == 0:
            url += "v=1"
        else:
            url += "v=0"
        if connection == 0:
            url += "&w=1"
        else:
            url += "&w=0"
        url += "&sort=price"
        part1Name, part2Name, part1Link, part2Link, part1Price, part2Price = FindPeripherals(url, int(suggestedPrice))
        print("\nRecomended headphones - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link))
        info.append("Recomended headphones - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link) + "\n")
        print("Other recomended headphones - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        info2.append("Other recomended headphones - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        money1 -= part1Price
        money2 -= part2Price
    return money1, money2


def speakers(money1, money2):
    while True:
        needed = str(input("Do you need speakers: ")).lower()
        if needed == "yes" or needed == "no":
            break
        else:
            print("Invalid Input, yes or no question")
    if needed == "yes" or needed == "y":
        if autoPrice == "yes" or autoPrice == "y":
            suggestedPrice = startingMoney/28
        else:
            while True:
                try:
                    suggestedPrice = int(input("Roughly, how much should it cost: "))
                    if suggestedPrice >= 0:
                        break
                    else:
                        print("Must be 0 or more")
                except:
                    print("Invalid Input, Integer Only")
        print("\nPlease wait")
        url = "https://uk.pcpartpicker.com/products/speakers/#sort=price"
        part1Name, part2Name, part1Link, part2Link, part1Price, part2Price = FindPeripherals(url, int(suggestedPrice))
        print("\nRecomended speakers - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link))
        info.append("Recomended speakers - " + str(part1Name) + " - £" + str(part1Price) + " - " + str(part1Link) + "\n")
        print("Other recomended speakers - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        info2.append("Other recomended speakers - " + str(part2Name) + " - £" + str(part2Price) + " - " + str(part2Link) + "\n")
        money1 -= part1Price
        money2 -= part2Price
    return money1, money2


def create_list(): #this is used to take the info and info lists and add all the parts onto an PcPartPicker part list
    global listLinks, finalCosts, official1, official2
    listLinks = []
    finalCosts = []
    if community == 1 or community == 2: #depending on what options they chose we change the list
        community1 = info[len(info)-1]
        community2 = info2[len(info2)-1]
        del info[len(info)-1]
        del info2[len(info2)-1]
    if community == 0 or community == 2:
        official1 = info[len(info)-1]
        official2 = info2[len(info2)-1]
        for i in range(2): #gets the urls for the parts
            urls = []
            if i == 0:
                for component in info:
                    part = ("https" + (component.split("https", 1)[1]))
                    urls.append(part)
            else:
                for component in info2:
                    part = ("https" + (component.split("https", 1)[1]))
                    urls.append(part)
            browser = webdriver.Firefox()
            type(browser)
            pc = urls[len(urls)-1] #the pc builds part list
            browser.get(pc)
            browser.minimize_window() 
            browser.implicitly_wait(3)
            browser.execute_script("window.scrollTo(0, 2000)")
            browser.implicitly_wait(5)
            browser.execute_script("window.scrollTo(0, 2500)")
            try:
                browser.implicitly_wait(2)
                time.sleep(2)
                browser.find_element_by_link_text("Decline").click() #sometime the cookies decline blocks the button so we click decline
            except:
                #print("Error pressing decline, non critical")
                browser.execute_script("window.scrollTo(0, 2500)")
            browser.implicitly_wait(4)
            time.sleep(1)
            while True:
                try:
                    browser.implicitly_wait(4)
                    browser.find_element_by_link_text("Customize This Part List").click() #allows us to edit the pc's part list
                    break
                except:
                    browser.execute_script("window.scrollTo(0, 2400)")
                    print("Error clicking customize, retrying")
            #we then add all the extra parts to the build, by opening the part url and clicking add
            if len(urls) > 1:
                for url in urls:
                    if url != pc:
                        while True:
                            try:
                                browser.implicitly_wait(6)
                                browser.get(url)
                                browser.implicitly_wait(6)
                                browser.find_element_by_link_text("Add").click()
                                time.sleep(1)
                                break
                            except:
                                print("Error Retrying, couldnt click add")
                        browser.implicitly_wait(6)

            #we then collect data about the final build
            
            listLink = browser.find_element_by_class_name("text-input").get_attribute("value")
            listLinks.append(listLink)
            finalCost = browser.find_elements_by_class_name("td__price")
            finalCost = finalCost[len(finalCost)-1].text.replace("£", "")
            finalCosts.append(finalCost)
            browser.implicitly_wait(3)
            browser.find_element_by_class_name("actionBox__options--new").click()
            browser.implicitly_wait(3)
            browser.close()
            browser.quit()

    #if they also wanted comunity builds we repeat the process with minor changes
            
    if community == 1 or community == 2:
        if community == 2:
            del info[len(info)-1]
            del info2[len(info2)-1]
        info.append(community1)
        info2.append(community2)
        for i in range(2):
            urls = []
            if i == 0:
                for component in info:
                    part = ("https" + (component.split("https", 1)[1]))
                    urls.append(part)
            else:
                for component in info2:
                    part = ("https" + (component.split("https", 1)[1]))
                    urls.append(part)
            browser = webdriver.Firefox()
            type(browser)
            pc = urls[len(urls)-1]
            browser.get(pc)
            browser.minimize_window()
            while True:
                try:
                    browser.implicitly_wait(10)
                    browser.find_element_by_class_name("actionBox__options--edit").click()
                    break
                except:
                    print("Error editing build, retrying")
                    print(urls)
                    print(urls[len(urls)-1])
            if len(urls) > 1:
                for url in urls:
                    if url != pc:
                        while True:
                            try:
                                browser.implicitly_wait(6)
                                browser.get(url)
                                browser.implicitly_wait(6)
                                browser.find_element_by_link_text("Add").click()
                                time.sleep(1)
                                break
                            except:
                                print("Error Retrying, coudnt click add")
                        browser.implicitly_wait(6)
            listLink = browser.find_element_by_class_name("text-input").get_attribute("value")
            listLinks.append(listLink)
            finalCost = browser.find_elements_by_class_name("td__price")
            finalCost = finalCost[len(finalCost)-1].text.replace("£", "")
            finalCosts.append(finalCost)
            browser.implicitly_wait(3)
            browser.find_element_by_class_name("actionBox__options--new").click()
            browser.implicitly_wait(3)
            browser.close()
            browser.quit()   

   
def ending(): #prints out all the data and links onto the console
    if community == 0 or community == 2:
        print("\nSystem 1 Price - £" + str(round(float(finalCosts[0]))) + ", PcPP Link - " + listLinks[0])
        print("System 2 Price - £" + str(round(float(finalCosts[1]))) + ", PcPP Link - " + listLinks[1])
    if community == 1:
        print("Community System 1 Price - £" + str(round(float(finalCosts[0]))) + ", PcPP Link - " + str(listLinks[0]))
        print("Community System 2 Price - £" + str(round(float(finalCosts[1]))) + ", PcPP Link - " + str(listLinks[1]))
    if community == 2:
        print("\nCommunity System 1 Price - £" + str(round(float(finalCosts[2]))) + ", PcPP Link - " + str(listLinks[2]))
        print("Community System 2 Price - £" + str(round(float(finalCosts[3]))) + ", PcPP Link - " + str(listLinks[3]))

    #open a text file and writes all the data to there aswell for later
    name = "mypc-" + str(startingMoney) + "-" + str(random.randint(100, 999)) + ".txt"
    f = open(name, "w+")

    if community == 0:
        for recomendation in info:
            f.write(recomendation)
        f.write("\nSYSTEM 1 COST: £" + str(round(float(finalCosts[0]))) + ", PcPP Link - " + listLinks[0] + "\n\n")
        for recomendation2 in info2:
            f.write(recomendation2)
        f.write("\n\nSYSTEM 2 COST: £" + str(round(float(finalCosts[1]))) + ", PcPP Link - " + listLinks[1])
        f.close()
    else:
        for recomendation in info:
            f.write(recomendation)
        f.write("\nCOMMUNITY SYSTEM 1 COST: £" + str(round(float(finalCosts[2]))) + ", PcPP Link - " + listLinks[2] + "\n\n")
        for recomendation2 in info2:
            f.write(recomendation2)
        f.write("\nCOMMUNITY SYSTEM 2 COST: £" + str(round(float(finalCosts[3]))) + ", PcPP Link - " + listLinks[3] + "\n\n")
        del info[len(info)-1]
        del info2[len(info2)-1]
        if community == 2:
            info.append(official1)
            info2.append(official2)
            for recomendation in info:
                f.write(recomendation)
            f.write("\nOFFICIAL SYSTEM 1 COST: £" + str(round(float(finalCosts[0]))) + ", PcPP Link - " + listLinks[0] + "\n\n")
            for recomendation2 in info2:
                f.write(recomendation2)
            f.write("\n\nOFFICIAL SYSTEM 2 COST: £" + str(round(float(finalCosts[1]))) + ", PcPP Link - " + listLinks[1] + "\n\n")
        f.close()
    print("Pc components saved at " + name)
    ending = input("\nPress enter to exit")


def login(): #a semi secure login system
    status = True
    while status:
        f = open("key.key", "r")
        key = f.read()
        f.close()
        Iusername = input("Please input your username: ")
        Ipassword = str(input("Please input your password: "))
        
        passwordPaste = "https://pastebin.com/raw/Mi3GkAQ3" #where the encrytped password and usernames are stored
        
        r = requests.get(passwordPaste)
        lines = r.text
        lines = lines.split("\n")
        f = Fernet(key)
        for line in lines: #checks each combo in the pastebin to see if it matches with the input data when decrypted with the key
                            #this means you can revoke someones access if you remove thier username or password from the pastebin
            line = line.split(" ", 1)
            username = line[0]
            password = line[1].replace("\r", "").replace("b'", "").replace("'", "")
            password = bytes(password, encoding="ascii")
            password = f.decrypt(password)
            password = str(password)[2: -1]
            if username == Iusername and Ipassword == password:
                print("\nWelcome\n")
                status = False
        if status == True:
            print("Incorrect or Invalid username or password")
            print("Retry\n")
            

login()     
info = []
info2 = []

#asks a bunch of questions at the start of the program after login to customise thier experience
while True:
    try:
        global startingMoney
        startingMoney = int(input("How much money do you want to spend: "))
        break
    except:
        print("Invalid Input, Integers only")
print("\nWould you like defult pricing ratios to be applied to peripherals(excluding monitors). Eg for a £2500 setup, headphones will be 5.5% of that, aka £140")
global autoPrice
while True:
    autoPrice = str(input("\nAuto Pricing, yes or no: ")).lower()
    if autoPrice == "yes" or autoPrice == "no":
        break
    else:
        print("Invalid Input, only enter yes or no")
print("\nWould you like to include community builds in our search, this increases time of the search and community builds arent always optimal.\nHowever it will make the overall build closer to your budget")
while True:
    try:
        global community
        community = int(input("\nJust official builds (0), just community builds (1) or both (2): "))
        if community == 0 or community == 1 or community == 2:
            break
        else:
            print("Invalid Input")
    except:
        print("Invalid Input, only enter yes or no")
if community == 1 or community == 2:
    global minipc
    while True:
        minipc = str(input("\nInclude mini Pc's, yes or no: ")).lower()
        if minipc == "yes" or minipc == "no":
            break
        else:
            print("Invalid Input, only enter yes or no")
while True:
    os = str(input("\nDo you need a copy of windows 10?, yes or no: ")).lower()
    if os == "yes" or os == "no":
        break
    else:
        print("Invalid Input, only enter yes or no")
print("\nPlease Do Not Close FireFox Anytime!!\nPlease Read HOW-TO-USE.txt before using\n")

#Main Stack#
money = startingMoney
if os == "yes":
    money = OS(money)
money1, money2 = monitor(money)
money1, money2 = keyboard(money1, money2)
money1, money2 = mouse(money1, money2)
money1, money2 = headphones(money1, money2)
money1, money2 = speakers(money1, money2)
if community == 0:
    pc_guide(money1, money2)
elif community == 1:
    completed_builds(money1, money2)
else:
    pc_guide(money1, money2)
    completed_builds(money1, money2)
create_list()
ending()
