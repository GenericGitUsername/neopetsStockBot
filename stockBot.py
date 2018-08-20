import mechanize
import random
import datetime
import time
import math
import copy
import sys, logging
import re
import os



logFile = open('log.txt', 'a')
errorHTMLdump = open('errorHTML.txt', 'a')


##
# Main function controls browser session and logging into Neopets
##	
def main():

	logFile.write("\n")
	logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")	
	
	files = ["bankPage.txt",
			"portfolioPage.txt",
			"bargainPage.txt",
			"buyPage.txt",
			"loginPage.txt"]
	
	#for i in range(len(pages)):
	for i in range(0,len(files)):
		if os.path.exists(files[i]):
			os.remove(files[i])	
	
	br = mechanize.Browser()

	# User-Agent
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	
	login(br)
	humanizingDelay(2)
	
	#bankCollectInterest(br)
	#humanizingDelay(2)	
	
	#buyStockManager(br)
	#humanizingDelay(2)
	
	buyLotteryTickets(br)
	
	sellStockManager(br)
	humanizingDelay(2)
	
	#bankWithdrawal(br)
	#humanizingDelay(2)
	#bankDeposit(br)
	#humanizingDelay(2)
	
	
	br.open("http://www.neopets.com/logout.phtml")
	
##
# Causes the script to pause for a random time to make it appear more
# human by not always executing at the exact same time of day. maxLength
# is the maximum duration of the pause in seconds.
# minLength is optional and defaults to 0.
##
def humanizingDelay(maxLength, minLength=0.5):

	pauseDuration = random.uniform(minLength,maxLength)
	time.sleep(pauseDuration)
	
def login(browser):

	#user credentials
	userName = ""
	passWord = ""
	
	page = "http://www.neopets.com/login/index.phtml"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			pageHTML = browser.open(page)
			if(browser):
				pageHTMLString = pageHTML.read()
				with open("loginPage.txt", "w") as f:
					f.write(pageHTMLString)
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return

	browser.select_form(action="/login.phtml")
	humanizingDelay(1)
	browser.form['username'] = userName
	humanizingDelay(2)
	browser.form['password'] = passWord
	humanizingDelay(2)

	# Login
	browser.submit()

##
# Collects the daily bank interest
##	
def bankCollectInterest(browser):

	page = "http://www.neopets.com/bank.phtml"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			bankHTML = browser.open(page)	
			if(browser):						
				bankHTMLString = bankHTML.read()
				with open("bankPage.txt", "w") as f:
					f.write(bankHTMLString)
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
		
	browser.select_form(nr=3)
	if("interest" in browser.form.get_value("type")):
		collected = -1
		matchobj = re.search(r"Your current balance and interest rate allow you to gain <b>(\w*) NP<\/b>", bankHTMLString)
		if(matchobj):
			collected = matchobj.group(1)
	
		humanizingDelay(3)
		
		# collect interest
		browser.submit()
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - Collected " + collected + " NP of interest \n")
		
##
# Looks at the current neopoint value and deposits any excess
##	
def bankDeposit(browser):

	page = "http://www.neopets.com/bank.phtml"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			bankHTML = browser.open(page)		
			if(browser):					
				bankHTMLString = bankHTML.read()
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
	
	humanizingDelay(3, minLength=1)	
	currNeopoints = getNeopoints(bankHTMLString)	
	if currNeopoints > 500:
		depositValue = currNeopoints - 500
		browser.select_form(nr=1)
		browser.form['amount'] = str(depositValue)
		humanizingDelay(1)
		browser.submit()
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - " + str(depositValue) + " NP deposited to the bank.\n")
		
##
# decides if it is necessary to withdraw neopoints, and then carries out that action.
##	
def bankWithdrawal(browser):

	page = "http://www.neopets.com/bank.phtml"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			bankHTML = browser.open(page)		
			if(browser):					
				bankHTMLString = bankHTML.read()
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
	
	
	"""
	## Display all the forms and related controls
	formsList = list(browser.forms())
	for i in range(1,3):
		
		currForm = formsList[i]
		print("form " + str(i) + ": " + str(currForm))
		print("	   attrs: " + str(currForm.attrs))
		print("	   action: " + str(currForm.action))
		print("	   method: " + str(currForm.method))
		print("	   enctype: " + str(currForm.enctype))
		print("	   name: " + str(currForm.name))
		print("	   controls: " + str(currForm.controls))
		
		#selecting the controls by name doesn't work, so we get them by index
		controlsList = currForm.controls
		for j in range(len(controlsList)):
		
			currControl = controlsList[j]
			print("control " + str(j) + ": " + str(currControl))
			print("	   labels: " + str(currControl.get_labels()))
			print("	   type: " + str(currControl.type))
			print("	   name: " + str(currControl.name))
			print("	   value: " + str(currControl.value))
			print("	   disabled: " + str(currControl.disabled))
			print("	   readonly: " + str(currControl.readonly))
			print("	   id: " + str(currControl.id)) 
			
		print ""
		print ""
	"""	
	
	humanizingDelay(5, minLength=2)	
	currNeopoints = getNeopoints(bankHTMLString)	
	if currNeopoints < 17500:
		withdrawValue = 17500 - currNeopoints
		
		browser.select_form(nr=2)
		
		#For some reason these controls aren't detected as in the form, so we have to add them manually
		browser.form.new_control(type="hidden", name="type", attrs={"value": "withdraw"})
		browser.form.new_control(type="text", name="amount", attrs={"value": ""})
		browser.form.new_control(type="submit", name=None, attrs={"value": "Withdraw"})
		browser.form.fixup()
	
		browser.select_form(nr=2)
		browser.form['amount'] = str(withdrawValue) # amount
		humanizingDelay(1)
		browser.submit()
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - " + str(withdrawValue) + " NP withdrawn from the bank.\n")
	
		
##
# Takes the current page's HTML as a string and returns the neopoint value.
##	   
def getWalletNeopoints(pageHTMLString):
	npValue = -1
	
	matchobj = re.search(r"<a id=.?npanchor.? href=.*inventory.phtml.?>(\w{1,3},?\w{0,3},?\w{0,3})<.?a>", pageHTMLString)
	if(matchobj):
		npString = matchobj.group(1)
		npValue = int(npString.replace(",",""))
	
	return npValue
		
##
# Takes the bank page's HTML as a string and returns the bank neopoint value.
##	
def getBankNeopoints(bankHTMLString):
	npValue = -1
	
	matchobj = re.search(r"<td align.*center.? style.*font-weight.? bold.*>(\w{1,3},?\w{0,3},?\w{0,3}) NP<.?td>", bankHTMLString)
	if(matchobj):
		npString = matchobj.group(1)
		npValue = int(npString.replace(",",""))
	
	return npValue
	
##
# Takes the browser object and returns the combined amount of wallet and bank neopoints
##	
def getTotalNeopoints(browser):

	page = "http://www.neopets.com/bank.phtml"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			bankHTML = browser.open(page)		
			if(browser):					
				bankHTMLString = bankHTML.read()
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
	
	wallet = getWalletNeopoints(bankHTMLString)
	bank = getBankNeopoints(bankHTMLString)
	
	return (wallet+bank)
	
##
# Returns a dictonary of current stock holdings
# {"ticker":[(shares, change)], "ticker":[(shares, change), (shares, change)]}
##
def getDetailedStockHoldings(browser):
	
	page = "http://www.neopets.com/stockmarket.phtml?type=portfolio"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			portfolioHTML = browser.open(page)	
			if(browser):						
				portfolioHTMLString = portfolioHTML.read()
				with open("portfolioPage.txt", "w") as f:
					f.write(portfolioHTMLString)
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
	
	holdings = {}
	
	matchobj = re.findall(r"<tr>\s*<td align..center.>(\d?,?\d{1,3}).*\s*.*\s*.*\s*.*\s*.*\s*.*color..(\w*).><nobr>[+-]?(\d+[.]\d{2}).*\s*.*\[(\w{2,5})\]\[", portfolioHTMLString)
	if(matchobj):
		last = len(matchobj)
		for x in range(1, last):
			shares, colour, change, ticker = matchobj[x]
			shares = int(shares.replace(",",""))
			change = float(change.replace(",",""))
			
			if(colour == "red"):
				change = 0.0 - change
			if(ticker in holdings):
				holdings[ticker].append((shares, change))
			else:
				holdings[ticker] = [(shares, change)]
	
	return holdings


##
# Returns a dictonary of current stock holdings
# {"ticker":(shares, change), "ticker":(shares, change)}
##
def getSimpleStockHoldings(browser):
	
	holdings = getDetailedStockHoldings(browser) #{"ticker":[(shares, change)], "ticker":[(shares, change), (shares, change)]}
	
	#change holdings into a {ticker:shares, ticker:shares} format to easily get total shares for each ticker
	simplifiedHoldings = {}
	for k in holdings:
		if k not in simplifiedHoldings:
			simplifiedHoldings[k] = holdings[k][0][0]
		else:
			for x in range(len(holdings[k])):
				simplifiedHoldings += holdings[k][x][0]
	
	
	#for k in holdings:
	#	print(str(k) + ": " + str(holdings[k]))
	
	return simplifiedHoldings


##
# Returns a dictonary of bargain stocks with greater than 0 volume and price of 15
# {"ticker":(volume, price), "ticker":(volume, price)}
##
def getBargainStocks(browser):

	page = "http://www.neopets.com/stockmarket.phtml?type=list&search=%&bargain=true"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			bargainHTML = browser.open(page)	
			if(browser):						
				bargainHTMLString = bargainHTML.read()
				with open("portfolioPage.txt", "w") as f:
					f.write(bargainHTMLString)
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
	
	bargains = {}
	
	matchobj = re.findall(r"company_id.\d{1,3}.{5}([ABCDEFGHIJKLMNOPQRSTUVWXYZ]{2,6}).{35}[^<]*.{40}(\d*).{43}\d*.{47}(\d*)", bargainHTMLString)
	if(matchobj):
		last = len(matchobj)
		for x in range(1, last):
			ticker, volume, price = matchobj[x]
			volume = int(volume)
			price = int(price)
			
			if(volume > 0 and price == 15):
				bargains[ticker] = (volume, price)
	
	return bargains

##
# Decides what to buy and carries out that action
# Equalizes the shares bought across stocks, taking into account amount owned
# Eg: owned {"PDSS":200}
# Buy 600 "SWNC" and 400 "PDSS", for a total owned of {"PDSS":600, "SWNC":600}
##	
def buyStockManager(browser):
	
	simplifiedHoldings = getSimpleStockHoldings(browser) #{ticker:shares, ticker:shares}
	humanizingDelay(2)
	
	bargains = getBargainStocks(browser) #"ticker":(volume, price)
	humanizingDelay(2)
	if(len(bargains) == 0):
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - No stocks at 15 NP\n")
		return
		
	# Add all the shares that we potentially want to buy
	purchases = {} #{"ticker":(buyAmount, ownedAmount), "ticker":(buyAmount, ownedAmount)}	
	for k in bargains:
		if k not in simplifiedHoldings:
			purchases[k] = [0, 0]
		else:
			purchases[k] = [0, simplifiedHoldings[k]]
			
	#list of the number of shares for each stock ticker. ticker not included
	ownedStockAmounts = []		
	for k in purchases:
		if purchases[k][1] > 0:
			ownedStockAmounts.append(purchases[k][1])
			
	ownedStockAmounts.sort()
		
	shares = 1000
	loopIndex = 0
	while shares > 0 and loopIndex < (len(ownedStockAmounts)-1):		
		
		#ie. shares to buy = 1000, but the lowest owned stock amount is less than that, bring everything up to that value
		if ownedStockAmounts[loopIndex] < shares:
			minimum = ownedStockAmounts[loopIndex]
		
		#the number of stocks that need to buy up to the min number of shares
		numUnderMin = 0		
		for k in purchases:
			if((purchases[k][0] + purchases[k][1]) < minimum):
				numUnderMin += 1
								
		if numUnderMin == 0:
			loopIndex += 1
			continue
			
		if(minimum < shares):
			maxShareAllotment = minimum/numUnderMin
		else:
			maxShareAllotment = shares/numUnderMin
			
		for k in purchases:
			if((purchases[k][0] + purchases[k][1]) < minimum):
				
				if(maxShareAllotment < (minimum - purchases[k][0] - purchases[k][1])):
					buyAmount = maxShareAllotment
				else:
					buyAmount = (minimum - purchases[k][0] - purchases[k][1])
					
				purchases[k][0] += buyAmount
				shares -+ buyAmount
				
		loopIndex += 1
		
	while shares > 0:
		for k in purchases:
			purchases[k][0] += 1
			shares -= 1
			if(shares <= 0):
				break
	
	
	for k in purchases:
		if(purchases[k][0] > 0):
			#print("buy " + str(purchases[k][0]) + " shares of [" + str(k) + "]")
			buyStock(browser, k, purchases[k][0])
	
						
##
# Buys specified amount of shares of the stock ticker
# Relies on the index of the form and inputs, hopefully this doesn't change.
##	
def buyStock(browser, ticker, shares):

	page = "http://www.neopets.com/stockmarket.phtml?type=buy"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			buyStockHTML = browser.open(page)	
			if(browser):						
				buyStockHTMLString = buyStockHTML.read()
				with open("portfolioPage.txt", "w") as f:
					f.write(buyStockHTMLString)
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		return
	
	#The form we want isn't named, but it's the second one on the page
	browser.select_form(nr=1)
	#selecting the controls by name doesn't work, so we get them by index
	controls = browser.form.controls
	controls[2]._value = str(ticker) # the ticker
	controls[3]._value = str(shares) # the number of shares
	
	"""
	with open("output2.txt", "w") as f:
		currForm = browser.form
		i = 1
		print("form " + str(i) + ": " + str(currForm))
		print("	   attrs: " + str(currForm.attrs))
		print("	   action: " + str(currForm.action))
		print("	   method: " + str(currForm.method))
		print("	   enctype: " + str(currForm.enctype))
		print("	   name: " + str(currForm.name))
		print("	   controls: " + str(currForm.controls))
		
		#f.write("values: " + str(values) + "\n")
		f.write("form " + str(i) + ": " + str(currForm) + "\n")
		f.write("	   attrs: " + str(currForm.attrs) + "\n")
		f.write("	   action: " + str(currForm.action) + "\n")
		f.write("	   method: " + str(currForm.method) + "\n")
		f.write("	   enctype: " + str(currForm.enctype) + "\n")
		f.write("	   name: " + str(currForm.name) + "\n")
		f.write("	   controls: " + str(currForm.controls) + "\n")
		
		#selecting the controls by name doesn't work, so we get them by index
		controlsList = currForm.controls
		for j in range(len(controlsList)):
		
			currControl = controlsList[j]
			print("control " + str(j) + ": " + str(currControl))
			print("	   labels: " + str(currControl.get_labels()))
			print("	   type: " + str(currControl.type))
			print("	   name: " + str(currControl.name))
			print("	   value: " + str(currControl.value))
			print("	   disabled: " + str(currControl.disabled))
			print("	   readonly: " + str(currControl.readonly))
			print("	   id: " + str(currControl.id)) 
			
			f.write("control " + str(j) + ": " + str(currControl) + "\n")
			f.write("	   labels: " + str(currControl.get_labels()) + "\n")
			f.write("	   type: " + str(currControl.type) + "\n")
			f.write("	   name: " + str(currControl.name) + "\n")
			f.write("	   value: " + str(currControl.value) + "\n")
			f.write("	   disabled: " + str(currControl.disabled) + "\n")
			f.write("	   readonly: " + str(currControl.readonly) + "\n")
			f.write("	   id: " + str(currControl.id)+ "\n")
			
		print ""
		print ""
		f.write("\n")
		f.write("\n")
	"""
	humanizingDelay(5,minLength=1)
	
	response = browser.submit()
	
	#check that everything worked, return a string with the result
	if response.geturl() == "http://www.neopets.com/stockmarket.phtml?type=portfolio":
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - Success: "+str(shares)+" shares of ["+ticker+"] have been purchased.\n")
	elif response.geturl() == "http://www.neopets.com/process_stockmarket.phtml":
		responseHTML = response.read()
		startToken = "<b>Error:"
		endToken = "</div>"
		startIndex = responseHTML.index(startToken)
		endIndex = responseHTML.index(endToken,startIndex)	 
		errorString = responseHTML[startIndex:endIndex].replace("</b>","").replace("<b>","")
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - "+errorString+"\n")
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - Error: Unknown problem occured while buying stocks.\n")
	
##
# Decides what to sell and carries out that action
##	
def sellStockManager(browser):
	threshold = getSellThreshold(browser)
	print("threshold: " + str(threshold))
	
	holdings = getDetailedStockHoldings(browser) # {"ticker":[(shares, change)], "ticker":[(shares, change), (shares, change)]}
	humanizingDelay(2)
	
	sells = {"CHPS":[(1,120), (2,120), (3,120)]}
	
	for ticker in holdings:
		for j in range(len(holdings[ticker])):
			if(holdings[ticker][j][1] > threshold and ticker not in sells):
				#If any of the submembers are above threshold, sell all members of that ticker. Simplifies things.
				sells[ticker] = holdings[ticker]
				break
					
					
	if(len(sells) == 0):
		print("nothing to sell today")
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - No stocks meet sell requirements\n")
		#return
		
	
	page = "http://www.neopets.com/stockmarket.phtml?type=portfolio"
	
	# For potential issues connecting, and a URLError is raised. This sleeps for 30 seconds
	# then retries the connection up to 10 times before giving up and documenting the error.
	for attempt in range(10):
		try:
			portfolioHTML = browser.open(page)	
			if(browser):						
				portfolioHTMLString = portfolioHTML.read()
				break
		except mechanize.URLError:
			time.sleep(30)
		else:
			break
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to access " + page + " \n")
		#return
		
		
	browser.select_form(nr=1)
	currForm = browser.form
	
	#We don't know the exact names of the inputs, they have a ref number, time to search:
	controlsList = currForm.controls
	for i in range(1, (len(controlsList)-2)):
		if len(controlsList[i].name) > 10:
			controlName = controlsList[i].name[5:controlsList[i].name.find("]")]
			if controlName in sells:
				#If any of the submembers are above threshold, sell all members of that ticker. Simplifies things.
				for j in range(len(sells[controlName])):
					controlsList[(i+j)]._value = str(sells[controlName][j][0])
					logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - Sold " + str(sells[controlName][j][0]) + " of [" + str(controlName) + "] for " +  str(sells[controlName][j][1]) + "\% over buy price.\n")
					humanizingDelay(1)
				i += len(sells[controlName])
					
	values = {}
	for control in browser.form.controls:
		if control.type == "text" and control.value != "":
			values[control.name] = control.value
	
	browser.form.action = "http://www.neopets.com/process_stockmarket.phtml"
	browser.form.method = "post"
	browser.form.attrs = values
	
	humanizingDelay(5,minLength=1)
	response = browser.submit()

	#check that everything worked, return a string with the result
	if response.read().find("There were no successful transactions") == -1:
		return True
	else:
		errorHTMLdump.write("/n"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"/n"+response.read())
		return False
	"""
	with open("output1.txt", "w") as f:
		i = 2		
		print("form " + str(i) + ": " + str(currForm))
		print("	   attrs: " + str(currForm.attrs))
		print("	   action: " + str(currForm.action))
		print("	   method: " + str(currForm.method))
		print("	   enctype: " + str(currForm.enctype))
		print("	   name: " + str(currForm.name))
		print("	   controls: " + str(currForm.controls))
		
		f.write("values: " + str(values) + "\n")
		f.write("form " + str(i) + ": " + str(currForm) + "\n")
		f.write("	   attrs: " + str(currForm.attrs) + "\n")
		f.write("	   action: " + str(currForm.action) + "\n")
		f.write("	   method: " + str(currForm.method) + "\n")
		f.write("	   enctype: " + str(currForm.enctype) + "\n")
		f.write("	   name: " + str(currForm.name) + "\n")
		f.write("	   controls: " + str(currForm.controls) + "\n")
		
		#selecting the controls by name doesn't work, so we get them by index
		controlsList = currForm.controls
		for j in range(len(controlsList)):
		
			currControl = controlsList[j]
			print("control " + str(j) + ": " + str(currControl))
			print("	   labels: " + str(currControl.get_labels()))
			print("	   type: " + str(currControl.type))
			print("	   name: " + str(currControl.name))
			print("	   value: " + str(currControl.value))
			print("	   disabled: " + str(currControl.disabled))
			print("	   readonly: " + str(currControl.readonly))
			print("	   id: " + str(currControl.id)) 
			
			f.write("control " + str(j) + ": " + str(currControl) + "\n")
			f.write("	   labels: " + str(currControl.get_labels()) + "\n")
			f.write("	   type: " + str(currControl.type) + "\n")
			f.write("	   name: " + str(currControl.name) + "\n")
			f.write("	   value: " + str(currControl.value) + "\n")
			f.write("	   disabled: " + str(currControl.disabled) + "\n")
			f.write("	   readonly: " + str(currControl.readonly) + "\n")
			f.write("	   id: " + str(currControl.id)+ "\n")
			
		print ""
		print ""
		f.write("\n")
		f.write("\n")
	"""
	
	
	
##
# Determine what price to sell at based on current networth
##
def getSellThreshold(browser):

	cash = getTotalNeopoints(browser)
	thresholds = [(105000, 200),(450000,300),(1800000, 400),(5400000,600)]
	threshold = thresholds[0][1] #default, never go lower than this
	
	if(cash > thresholds[3][0]):
		threshold = thresholds[3][1]
	else:
		for i in range(1,len(thresholds)):
			if(cash < thresholds[i][0]):
				threshold = int(((float(cash-thresholds[i-1][0])/float(thresholds[i][0]-thresholds[i-1][0]))*10)+thresholds[i-1][1])
				break
				
	return threshold
	
def buyLotteryTickets(browser):

	for attempt in range(20):
		try:
			sample = random.sample([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30], 6)
			page = "http://www.neopets.com/games/process_lottery.phtml?one="+str(sample[0])+"&two="+str(sample[1])+"&three="+str(sample[2])+"&four="+str(sample[3])+"&five="+str(sample[4])+"&six="+str(sample[5])+"&"
			browser.open(page)		
			humanizingDelay(2,minLength=0.5)
			
		except mechanize.URLError:
			time.sleep(30)
		else:
			pass
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - An error occured while trying to buy lottery tickets\n")
		return
		
	

	
	
main()

































































