import mechanicalsoup
import random
import datetime
import time
import math
import copy
import sys
import logging
import re
import os
from boto.s3.connection import S3Connection


logFile = open('log.txt', 'a')
outputFile = open('output1.txt', 'a')
errorHTMLdump = open('errorHTML.txt', 'a')
files = [
		"loginPage.txt",
		"interestBankPage.txt",
		"withdrawalBankPage.txt",
		"portfolioPage.txt",
		"bargainPage.txt",
		"buyPage.txt",
		"depositBankPage.txt"]
response = ""


def main():
	"""Main function controls browser session and logging into Neopets"""

	logFile.write("\n")
	logFile.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"\n")

	for i in range(0, len(files)):
		if os.path.exists(files[i]):
			os.remove(files[i])

	# User-Agent
	browserString = (
					"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1)" +
					" Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.0")

	br = mechanicalsoup.StatefulBrowser(
										soup_config={'features': 'lxml'},  # Use the lxml HTML parser
										raise_on_404=True,
										user_agent=browserString)

	neopoints = login(br)
	humanizingDelay(2)
		
	
	if(neopoints != int(datetime.datetime.now().strftime("%m%d"))):
		bankCollectInterest(br)
		humanizingDelay(2)

		bankWithdrawal(br)
		humanizingDelay(2)

		buyStockManager(br)
		humanizingDelay(2)

		buyLotteryTickets(br)
		humanizingDelay(2)	
	
	sellStockManager(br)
	humanizingDelay(2)	

	bankDeposit(br)
	humanizingDelay(2)

	br.open("http://www.neopets.com/logout.phtml")


def humanizingDelay(maxLength, minLength=0.5):
	"""Causes the script to pause for a random time to make it appear more
	human by not always executing at the exact same time of day. maxLength
	is the maximum duration of the pause in seconds.
	minLength is optional and defaults to 0.
	"""

	pauseDuration = random.uniform(minLength, maxLength)
	time.sleep(pauseDuration)

	
def openPage(browser, page, filename=""):
	# For potential issues connecting, and a URLError is raised. This sleeps
	# for 30 seconds then retries the connection up to 10 times before giving
	# up and documenting the error.
	for attempt in range(10):
		try:
			pageHTML = browser.open(page)
			if(browser):
				if(filename != ""):
					with open(filename, encoding='utf-8', mode='w+') as f:
						f.write(pageHTML.text)
				return (browser, pageHTML)
		except mechanicalsoup.LinkNotFoundError:
			timer.sleep(5)
		else:
			break	
	else:
		logFile.write(
					str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
					" - An error occured while trying to access " + str(page) +
					" \n")
		return None

def login(browser):
	"""conn = boto.connect_s3()
	#s3 = S3Connection(
					os.environ['NEOPETS_USERNAME'],
					os.environ['NEOPETS_PASSWORD'])
	#print("connection: " + str(conn))
	#print("connection: " + str(s3))
	#print("username: "+ str(os.environ['neopets_username']))
	#print("password: "+ str(os.environ['neopets_password']))
	#user credentials
	#userName = str(os.environ['neopets_username'])
	#passWord = str(os.environ['neopets_password'])
	#return
	"""
	
	#userName = str(os.environ['neopets_username'])
	#passWord = str(os.environ['neopets_password'])
	credentials = []
	with open("credentials.txt", "r") as credFile:
		credentials = credFile.readlines()

	userName = str(credentials[0])
	passWord = str(credentials[1])

	page = "http://www.neopets.com/login/index.phtml"
	filename = "loginPage.txt"

	browser, pageHTML = openPage(browser, page, filename)

	browser.select_form('form[action="/login.phtml"]')
	humanizingDelay(1)
	browser['username'] = userName
	humanizingDelay(2)
	browser['password'] = passWord
	humanizingDelay(2)
	
	#browser.get_current_form().print_summary()

	# Login
	response = browser.submit_selected()
	neopoints = int(getWalletNeopoints(response.text))
	return neopoints


def bankCollectInterest(browser):
	"""Collects the daily bank interest"""

	page = "http://www.neopets.com/bank.phtml"
	filename = "interestBankPage.txt"

	browser, pageHTML = openPage(browser, page, filename)
	form_candidates = pageHTML.soup.select("form")

	# The interest form disapears when its already been collected
	if(len(form_candidates) < 7):
		return

	# Fragile: if they add more forms, this might break
	browser.select_form(form_candidates[3])

	# browser.get_current_form().print_summary()
	collected = ""
	submits = browser.get_current_page().find_all(type="submit")
	for value in submits:
		matchobj = re.search(r"(\d*) NP", str(value))
		if(matchobj):
			collected = matchobj.group(1)
			break

	humanizingDelay(3)

	# collect interest
	browser.submit_selected()
	logFile.write(
				str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
				" - Collected " + str(collected) + " NP of interest \n")
	return


def bankWithdrawal(browser):
	"""decides if it is necessary to withdraw neopoints,
	and then carries out that action.
	"""

	page = "http://www.neopets.com/bank.phtml"
	filename = "interestBankPage.txt"

	browser, pageHTML = openPage(browser, page, filename)
	form_candidates = pageHTML.soup.select("form")

	humanizingDelay(1)
	response = browser.refresh()
	currNeopoints = int(getWalletNeopoints(response.text))

	# 15000 for stocks, 100 for selling, 2000 for lottery, up to 1231 for date
	withdrawThreshold = (17500 + int(datetime.datetime.now().strftime("%m%d")))

	if currNeopoints < withdrawThreshold:
		humanizingDelay(5, minLength=2)
		withdrawValue = withdrawThreshold - currNeopoints

		# Fragile: if they add more forms, this might break
		browser.select_form(form_candidates[2])

		# For some reason these controls aren't detected as in the form, so we
		# have to add them manually
		browser.new_control(type="hidden", name="type", value="withdraw")
		browser.new_control(type="text", name="amount", value="")
		browser.new_control(type="submit", name=None, value="Withdraw")

		# Fragile: if they add more forms, this might break
		browser.select_form(form_candidates[2])

		humanizingDelay(1)
		browser['amount'] = str(withdrawValue)
		humanizingDelay(1)
		browser.submit_selected()
		logFile.write(
					str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
					" - " + str(withdrawValue) + " NP withdrawn from the bank.\n")


def bankDeposit(browser):
	"""Looks at the current neopoint value and deposits any excess
	after successfully buying stocks. Leave the days date as the active
	amount of neopoints. that way its easy to see if today has made
	purchases already. mm/dd
	"""

	page = "http://www.neopets.com/bank.phtml"
	filename = "interestBankPage.txt"

	browser, pageHTML = openPage(browser, page, filename)
	form_candidates = pageHTML.soup.select("form")

	humanizingDelay(1)
	response = browser.refresh()
	currNeopoints = int(getWalletNeopoints(response.text))

	humanizingDelay(3, minLength=1)

	todayDate = int(datetime.datetime.now().strftime("%m%d"))
	if currNeopoints > todayDate:
		depositValue = currNeopoints - todayDate

		# Fragile: if they add more forms, this might break
		browser.select_form(form_candidates[1])

		browser['amount'] = str(depositValue)
		humanizingDelay(1)
		
		response = browser.submit_selected()
		neopoints = int(getWalletNeopoints(response.text))
		
		print("neopoints: " + str(neopoints))
		
		logFile.write(
					str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +
					" - " + str(depositValue) + " NP deposited to the bank.\n")
	elif currNeopoints < todayDate:
		bankWithdrawal(browser)
		bankDeposit(browser)

  
def getWalletNeopoints(pageHTMLString):
	""" Takes the current page's HTML as a string and returns the neopoint
	value.
	"""

	npValue = -1

	matchobj = re.search(r"<a id=.?npanchor.? href=.*inventory.phtml.?>(\w{1,3},?\w{0,3},?\w{0,3})<.?a>", pageHTMLString)
	if(matchobj):
		npString = matchobj.group(1)
		npValue = int(npString.replace(",",""))

	return npValue


def getBankNeopoints(pageHTMLString):
	""" Takes the bank page's HTML as a string and returns the bank neopoint
	value.
	"""

	npValue = -1

	matchobj = re.search(r"<td align.*center.? style.*font-weight.? bold.*>(\w{1,3},?\w{0,3},?\w{0,3}) NP<.?td>", pageHTMLString)
	if(matchobj):
		npString = matchobj.group(1)
		npValue = int(npString.replace(",",""))

	return npValue


def getTotalNeopoints(browser):
	""" Takes the browser object and returns the combined amount of wallet and
	bank neopoints
	"""

	page = "http://www.neopets.com/bank.phtml"

	browser, pageHTML = openPage(browser, page)
	form_candidates = pageHTML.soup.select("form")

	humanizingDelay(1)
	response = browser.refresh()

	wallet = int(getWalletNeopoints(response.text))
	bank = int(getBankNeopoints(response.text))

	return (wallet+bank)


def getDetailedStockHoldings(browser):
	""" Returns a dictonary of current stock holdings
	{"ticker":[(shares, change)], "ticker":[(shares, change), (shares, change)]}
	"""

	page = "http://www.neopets.com/stockmarket.phtml?type=portfolio"

	browser, pageHTML = openPage(browser, page)
	form_candidates = pageHTML.soup.select("form")

	humanizingDelay(1)
	response = browser.refresh()

	holdings = {}

	matchobj = re.findall(r"<tr>\s*<td align..center.>(\d?,?\d{1,3}).*\s*.*\s*.*\s*.*\s*.*\s*.*color..(\w*).><nobr>[+-]?(\d+[.]\d{2}).*\s*.*\[(\w{2,5})\]\[", response.text)
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

	"""
	print("detailedHoldings: ")
	for k in holdings:
		print(str(k) + ": " + str(holdings[k]))
	"""
	return holdings


def getSimpleStockHoldings(browser):
	"""Returns a dictonary of current stock holdings
	{"ticker":(shares, change), "ticker":(shares, change)}
	"""

	# { "ticker":[(shares, change)],
	#   "ticker":[(shares, change), (shares, change)]}
	holdings = getDetailedStockHoldings(browser)

	# change holdings into a {ticker:shares, ticker:shares} format to easily
	# get total shares for each ticker
	simplifiedHoldings = {}
	for k in holdings:
		if k not in simplifiedHoldings:
			simplifiedHoldings[k] = 0
			for x in range(len(holdings[k])):
				simplifiedHoldings[k] = (simplifiedHoldings[k]
										+ holdings[k][x][0])			

	"""
	print("simpleHoldings: ")
	for k in simplifiedHoldings:
		print(str(k) + ": " + str(simplifiedHoldings[k]))
	"""
	return simplifiedHoldings


def getBargainStocks(browser):
	""" Returns a dictonary of bargain stocks with greater than 0 volume and 
	price of 15.
	{"ticker":(volume, price), "ticker":(volume, price)}
	"""

	page = "http://www.neopets.com/stockmarket.phtml?type=list&search=%&bargain=true"

	browser, pageHTML = openPage(browser, page)
	form_candidates = pageHTML.soup.select("form")

	humanizingDelay(1)
	response = browser.refresh()

	bargains = {}

	matchobj = re.findall(r"company_id.\d{1,3}.{5}([ABCDEFGHIJKLMNOPQRSTUVWXYZ]{2,6}).{35}[^<]*.{40}(\d*).{43}\d*.{47}(\d*)", response.text)
	if(matchobj):
		last = len(matchobj)
		for x in range(1, last):
			ticker, volume, price = matchobj[x]
			volume = int(volume)
			price = int(price)

			if(volume > 0 and price == 15):
				bargains[ticker] = (volume, price)

	return bargains


def buyStockManager(browser):
	""" Decides what to buy and carries out that action. Equalizes the shares
	bought across stocks, taking into account amount owned.

	Eg: owned {"PDSS":200}
	Buy 600 "SWNC" and 400 "PDSS", for a total owned of
	{"PDSS":600, "SWNC":600}
	"""

	# {ticker:shares, ticker:shares}
	simplifiedHoldings = getSimpleStockHoldings(browser)
	humanizingDelay(2)

	# "ticker":(volume, price)
	bargains = getBargainStocks(browser)
	humanizingDelay(2)
	if(len(bargains) == 0):
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - No stocks at 15 NP\n")
		return

	# Add all the shares that we potentially want to buy
	# {"ticker":(buyAmount, ownedAmount), "ticker":(buyAmount, ownedAmount)}
	purchases = {}
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

		#ie. shares to buy = 1000, but the lowest owned stock amount is
		#less than that, bring everything up to that value
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


def buyStock(browser, ticker, shares):
	"""Buys specified amount of shares of the stock ticker. Relies on the
	index of the form and inputs, hopefully this doesn't change.
	"""

	page = "http://www.neopets.com/stockmarket.phtml?type=buy"

	browser, pageHTML = openPage(browser, page)
	form_candidates = pageHTML.soup.select("form")
	"""
	print("attepted to purchase " + str(shares) + " of [" + str(ticker) + "]")
	return
	"""

	humanizingDelay(1)

	# Fragile: if they add more forms, this might break
	browser.select_form(form_candidates[1])

	browser["ticker_symbol"] = str(ticker)
	browser["amount_shares"] = str(shares)

	humanizingDelay(3,minLength=1)

	response = browser.submit_selected()

	#check that everything worked, return a string with the result
	if response.url == "http://www.neopets.com/stockmarket.phtml?type=portfolio":
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - Success: "+str(shares)+" shares of ["+ticker+"] have been purchased.\n")
	else:
		logFile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" - Error: Unknown problem occured while buying stocks.\n")


def sellStockManager(browser):
	""" Decides what to sell and carries out that action """

	# threshold is the required amount of profit before selling a
	# particular stock
	threshold = getSellThreshold(browser)

	# {"ticker":[(shares, change)],
	#  "ticker":[(shares, change), (shares, change)]}
	holdings = getDetailedStockHoldings(browser)
	humanizingDelay(2)

	tickersToSell = {}
	#tickersToSell = {"CHPS": [(1, 0), (2, 0), (3,0)]}

	for ticker in filter(lambda x: x not in tickersToSell, holdings):
		for subHolding in holdings[ticker]:
			profit = subHolding[1]

			if(profit > threshold):
				# If any of the submembers are above threshold, sell all
				# members of that ticker. Simplifies things.
				tickersToSell[ticker] = holdings[ticker]
				break

	if(len(tickersToSell) == 0):
		print("nothing to sell today")
		logFile.write(
				datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				+ " - No stocks meet sell requirements\n")
		return

	page = "http://www.neopets.com/stockmarket.phtml?type=portfolio"

	browser, pageHTML = openPage(browser, page)	
	form_candidates = pageHTML.soup.select("form")
	
	# Each control name has a unique identifier, this will get them though
	ownedDetailedStockNames = browser.get_current_page().find_all(
															"input",
															maxlength="8",
															size="7",
															type="text")
	"""
	indexMatch = -1
	values = {}
	i = 0
	for ticker in tickersToSell:
		j = 0
		# get the index of the first matching name
		for detailedStockName in ownedDetailedStockNames:
			thisName = detailedStockName["name"][5:-11]
			if(str(ticker) == str(thisName)):
				indexMatch = j
				break
			j += 1
		
		for x in range(len(tickersToSell[ticker])):
			ownedDetailedStockNames[(indexMatch+x)]["value"] = tickersToSell[ticker][x][0]
			
			values[ownedDetailedStockNames[(indexMatch+x)]["name"]] = tickersToSell[ticker][x][0]
		
		i += 1
		indexMatch = -1
	"""
		
	
	values = {}
	# {"CHPS": [(1, 0), (2, 0), (3,0)]}
	# ["sell[CHPS][87009291]":0, 
	# "sell[CHPS][87015942]":0,
	# "sell[CHPS][87205936]":0]
	for ticker in tickersToSell:
		# get the index of the first matching name
		j = 0
		indexMatch = -1
		for stockName in ownedDetailedStockNames:
			thisName = stockName["name"][5:-11]
			if(str(ticker) == str(thisName)):
				indexMatch = j
				break
			j += 1		
		
		for x in range(len(tickersToSell[ticker])):
			# Set in the form
			ownedDetailedStockNames[(indexMatch+x)]["value"] = tickersToSell[ticker][x][0]
			
			# Set for post submit
			values[ownedDetailedStockNames[(indexMatch+x)]["name"]] = tickersToSell[ticker][x][0]
			
			# write to logfile
			logFile.write(
						datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
						" - Sold " +
						str(tickersToSell[ticker][x][0]) +
						" of [" + str(ticker) +
						"] for " +
						str(tickersToSell[ticker][x][1]) +
						"\% over buy price.\n")
	
	browser.select_form(form_candidates[1])
	# browser.get_current_form().print_summary()	
	
	form_candidates[1]["action"] = "http://www.neopets.com/process_stockmarket.phtml"		
	form_candidates[1]["type"] = "post"
	form_candidates[1]["method"] = "post"
	form_candidates[1]["value"] = values
		
		
	humanizingDelay(5,minLength=1)
	
	response = browser.submit_selected()
	
	return
	
	#check that everything worked, return a string with the result
	if response.read().find("There were no successful transactions") == -1:
		return True
	else:
		errorHTMLdump.write("/n"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"/n"+response.read())
		return False


def getSellThreshold(browser):
	""" Determine what price to sell at based on current networth """

	cash = getTotalNeopoints(browser)
	thresholds = [(105000, 200),(450000,300),(1800000, 400),(5400000,600)]

	#default, never go lower than this
	threshold = thresholds[0][1]

	if(cash > thresholds[3][0]):
		threshold = thresholds[3][1]
	else:
		for i in range(1,len(thresholds)):
			if(cash < thresholds[i][0]):
				threshold = int(((float(cash-thresholds[i-1][0])/float(thresholds[i][0]-thresholds[i-1][0]))*10)+thresholds[i-1][1])
				break

	return threshold


def buyLotteryTickets(browser):

	for ticket in range(20):
		sample = random.sample([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30], 6)
		page = (
			"http://www.neopets.com/games/process_lottery.phtml?one=" +
			str(sample[0]) +
			"&two=" +
			str(sample[1]) +
			"&three=" +
			str(sample[2]) +
			"&four=" +
			str(sample[3]) +
			"&five=" +
			str(sample[4]) +
			"&six=" +
			str(sample[5]) +
			"&")

		browser, lotteryHTML = openPage(browser, page)


main()

































































