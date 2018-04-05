from flask import Flask, jsonify, render_template, request
import json
from nsetools import Nse
import mysql.connector as mariadb
from nsepy import get_history
import datetime
from datetime import date, timedelta
from decimal import Decimal
import threading
import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing import Process
import bson
# -*- coding: utf-8 -*-
### Decalre the app
app = Flask(__name__)

#DB Connection


nse = Nse()
dayWiseDetail={}
def fnconnDB():
	mariadb_connection = mariadb.connect(user='root', password='',database='nsedb')
	# cursor = mariadb_connection.cursor()
	return mariadb_connection
def fnAllStkCode():
	allStkCodes=[]
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "SELECT stksymbol from stkname"
	cursor.execute(connString)
	for codeList in cursor:
		if codeList[0] in "\,":
			codeList[0].rplace("\,","")
		allStkCodes.append(codeList[0].strip())
	cursor.close()
	return allStkCodes
def fnAllStkNames():
	allStkNames=[]
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "SELECT stkname from stkname"
	cursor.execute(connString)
	for codeList in cursor:
		if codeList != None:
			allStkNames.append(codeList)
	cursor.close()
	return allStkNames

#Sync DB
def fnInsertStkDetails(cnvrtDate,symbol,previousClose,dayopen,dayclose,dayhigh,dayLow,volume,percntchg):
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "INSERT INTO stkhistory set sDate = '" + cnvrtDate + "', Symbol = '" + symbol + \
					"', prevclose = " + previousClose + ", dayopen = " + dayopen + ", dayclose = " + dayclose + \
					", dayhigh = " + dayhigh + ", dayLow = " + dayLow + ",volume = " + volume + \
					", percntchg = " + percntchg + ""
	cursor.execute(connString)
	mariadb_connection.commit()
	cursor.close()
	mariadb_connection.close()

#Add to Watch  list
def fnAddWatchList(addDate,stksymbol,trackprice,comment):
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	print "Inside fnAddWatchList"
	connString = "INSERT INTO stkwatchlist set addDate = '" + addDate + "', stksymbol = '" + stksymbol + \
					"', trackprice = " + trackprice + ", comment = '" + comment + "'"
	print connString
	cursor.execute(connString)
	mariadb_connection.commit()
	cursor.close()
	mariadb_connection.close()


#Add to Watch  list
def fnAddstkName(stkCode,stkName):
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "INSERT INTO stkname set stksymbol = '" + stkCode + "', stkname = '" + stkName + "'"
	print connString
	cursor.execute(connString)
	mariadb_connection.commit()
	cursor.close()
	mariadb_connection.close()


@app.route('/fortest')
def fortest():
	print test
	##### Working fine for new stock add
							# stklistFilePath = "/media/prasant/Prasanta/Python_Flask/Iinvest/all_symbols"
							# stkListFopen = open(stklistFilePath,"r")
							# for stkCode in stkListFopen:
							# 	try:
							# 		# stkQuote = nse.get_quote(str(stkCode))
							# 		stkCode = stkCode.strip()
							# 		print "Inside TRY....", stkCode, stkName
							# 		stkName = nse.get_quote(str(stkCode))['companyName']
							# 		print "Inside TRY....", stkCode, stkName
							# 	except:
							# 		stkName = stkCode
							# 	print stkCode,stkName	
							# 	fnAddstkName(stkCode,stkName.replace("'",""))
		##### Working fine for new stock add
	# dateList = []
	# fromDate = request.args['FromDate']
	# toDate = request.args['ToDate']
	# print "Date is......" + str(fromDate).replace("/","-"),toDate.replace("/","-")
	# fromDate = datetime.datetime.strptime(fromDate, '%m/%d/%Y')
	# fromDate = '{0}-{1}-{2}'.format(fromDate.year, fromDate.month, fromDate.day % 100)
	# toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	# toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	# dateList.append(fromDate)
	# dateList.append(toDate)
	# return json.dumps({"results":dateList})

@app.route("/searchStk")
def searchStk():
	allStkNames = fnAllStkNames()
	# print "2nd ............. " , allStkNames[1]
	return json.dumps(allStkNames)
	# all_stock_codes = nse.get_stock_codes()
	# return json.dumps(sorted(all_stock_codes.values()))

def fnStkNameswithStartchar(initailChars):
	allStkNames=[]
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "SELECT stkname,stksymbol from stkname where stkname like '%" +  initailChars + \
					"%' or stksymbol like '%" + initailChars + "%'"
	cursor.execute(connString)
	for codeList in cursor:
		if codeList != None:
			allStkNames.append(codeList)
	cursor.close()
	return allStkNames

@app.route("/serchstkName")
def serchstkName():
	# stkCode = fnGetStkCodefromName(request.args['stkName'])
	allStkNames = fnStkNameswithStartchar(request.args['stkName'])
	# print "2nd ............. " , allStkNames
	return json.dumps(allStkNames)


def checkmaxdata(stkcode):
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select max(sDate) from stkhistory where symbol='" + stkcode + "';"
	cursor.execute(connString)
	for i in cursor:
		maxDate = i
	cursor.close()
	return maxDate[0]

@app.route("/addWatchList")
def addWatchList():
	addStkDetails = {}
	stkCode = fnGetStkCodefromName(request.args['stkCode'])
	comment = request.args['stkComment']
	print stkCode , comment
	try:
		# reqStkList = ['previousClose','open','closePrice','dayHigh','dayLow','low52','high52',
						# 'totalTradedVolume','faceValue','companyName','symbol','basePrice','averagePrice']
		# reqStkQuote = {}
		stkQuote = nse.get_quote(str(stkCode))
		print stkQuote["lastPrice"]
		addDate = datetime.datetime.now().strftime('%Y/%m/%d')
		# addDate = datetime.datetime.now().strptime(addDate,'%m/%d/%Y')
		# addDate = str(dataDetails["Date"].split("T")[0]) 
		print addDate
		fnAddWatchList(addDate,stkCode,str(stkQuote["lastPrice"]),comment)
		result = "Success"
		print "Success..."
	except:
			result = "Failed..."
			print "Error"
	return json.dumps(result)
#Cnver  date time to make json readble
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

@app.route("/showHistory")
def showHistory():
	# maxDate = request.args['ToDate']
	# minDate = request.args['ToDate']
	stkCode = request.args['stkCode']
	# maxDate = (datetime.datetime.now()).date()
	# maxDate = datetime.datetime.now().strftime('%Y-%m-%d')
	# # maxDate = '{0}-{1}-{2}'.format(maxDate.year, maxDate.month, maxDate.day % 100)

	# minDate = datetime.datetime.strptime(minDate, '%m/%d/%Y')
	# minDate = '{0}-{1}-{2}'.format(minDate.year, minDate.month, minDate.day % 100)

	allStkInWatchList = []
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	# connString = "SELECT sDate,dayopen,dayclose,dayhigh,daylow,volume,percntchg from stkhistory where symbol = '" + stkCode + \
	# 				"' and sDate between '" + minDate + "' and '" + maxDate + "'"
	connString = "SELECT sDate,dayopen,dayclose,dayhigh,daylow,volume,percntchg from stkhistory where symbol = '" + stkCode + \
				"' order by sDate DESC limit 20 "
	print connString
	cursor.execute(connString)

	for codeList in cursor:
		if codeList != None:
			# print codeList
			allStkInWatchList.append(codeList)
	# print allStkInWatchList
	cursor.close()
	# print allStkInWatchList[0][2]
	return json.dumps(allStkInWatchList,default=to_serializable)

@app.route("/showHistoryAll")
def showHistoryAll():
	# maxDate = request.args['ToDate']
	# minDate = request.args['ToDate']
	stkCode = request.args['stkCode']
	# maxDate = (datetime.datetime.now()).date()
	# maxDate = datetime.datetime.now().strftime('%Y-%m-%d')
	# # maxDate = '{0}-{1}-{2}'.format(maxDate.year, maxDate.month, maxDate.day % 100)

	# minDate = datetime.datetime.strptime(minDate, '%m/%d/%Y')
	# minDate = '{0}-{1}-{2}'.format(minDate.year, minDate.month, minDate.day % 100)

	allStkInWatchList = []
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	# connString = "SELECT sDate,dayopen,dayclose,dayhigh,daylow,volume,percntchg from stkhistory where symbol = '" + stkCode + \
	# 				"' and sDate between '" + minDate + "' and '" + maxDate + "'"
	connString = "SELECT sDate,dayopen,dayclose,dayhigh,daylow,volume,percntchg from stkhistory where symbol = '" + stkCode + \
				"' order by sDate DESC"
	print connString
	cursor.execute(connString)

	for codeList in cursor:
		if codeList != None:
			# print codeList
			allStkInWatchList.append(codeList)
	# print allStkInWatchList
	cursor.close()
	# print allStkInWatchList[0][2]
	return json.dumps(allStkInWatchList,default=to_serializable)

def to_serializable(val):
    """Used by default."""
    return str(val)

@app.route("/listWatchList")
def listWatchList():
	allStkInWatchList=[]
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "SELECT addDate,stksymbol,trackprice,comment from stkwatchlist order by addDate"
	cursor.execute(connString)
	for codeList in cursor:
		if codeList != None:
			# print codeList
			allStkInWatchList.append(codeList)
	cursor.close()
	# print allStkInWatchList[0][2]
	return json.dumps(allStkInWatchList, default = myconverter)

@app.route("/removeWatchlist")
def removeWatchlist():
	stkCode = request.args['stkCode'] 
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "delete from stkwatchlist where stksymbol = '" + stkCode +"'"
	print connString
	try:
		cursor.execute(connString)
		mariadb_connection.commit()
		cursor.close()
		mariadb_connection.close()
		result = "Success"
	except:
		result = "Error"
	return json.dumps(result)


def syncdbtread(currentStk):
	## Check the data exist or not for stock
		if checkmaxdata(currentStk) == None :
			# If no data found then sync the date for 1 year.
			fromDate = (datetime.datetime.now() - timedelta(90)).date()
		else:
			# If data found sync the data from max available to today.
			fromDate = checkmaxdata(currentStk) + timedelta(1)
		# fromDate = (datetime.datetime.now() - timedelta(2)).date()
		toDate = (datetime.datetime.now()).date()
		# print fromDate , ".............", toDate

		print "...........Importing data for ........for" , fromDate , toDate , currentStk
		# print fromDate < toDate
		if fromDate <= toDate :
			fromDate = fromDate.strftime('%m/%d/%Y') 
			fromDate = datetime.datetime.now().strptime(fromDate,'%m/%d/%Y')
			toDate = datetime.datetime.now().strftime('%m/%d/%Y')
			toDate= datetime.datetime.now().strptime(toDate,'%m/%d/%Y')
			stkHistData = []	
			# print fromDate.year,fromDate.month,fromDate.day , ".............", toDate.year,toDate.month,toDate.day	
			nextStkcode = get_history(symbol=currentStk,\
							start=date(fromDate.year,fromDate.month,fromDate.day),\
							end=date(toDate.year,toDate.month,toDate.day))	
			pandaTableData = nextStkcode.to_json(orient="table")
			# print pandaTableData
			for dataDetails in json.loads(pandaTableData)['data']:
				cnvrtDate = str(dataDetails["Date"].split("T")[0]) 
				symbol = str(dataDetails["Symbol"]) 
				previousClose = str(dataDetails["Prev Close"])
				dayopen = str(dataDetails["Open"]) 
				dayclose = str(dataDetails["Close"]) 
				dayhigh = str(dataDetails["High"]) 
				dayLow = str(dataDetails["Low"]) 
				volume = str(dataDetails["Volume"])
				percntchg = str(round(100 * (float(dataDetails["Close"] - float(dataDetails["Prev Close"]))) / float(dataDetails["Prev Close"]),2))
				# print cnvrtDate , symbol , previousClose , dayopen , dayclose , dayhigh , dayLow , volume , percntchg
				# stkHistData = [cnvrtDate , symbol , previousClose , dayopen , dayclose , dayhigh , dayLow , volume , percntchg]
				# print stkHistData
				fnInsertStkDetails(cnvrtDate , symbol , previousClose , dayopen , dayclose , dayhigh , dayLow , volume , percntchg)
				# dayWiseDetail = {symbol + cnvrtDate  : stkHistData }
				# print dayWiseDetail

# Not working as of now...
@app.route("/showsyncstatus")
def showsyncstatus():
	stkCode = request.args['stkCode'] 
	return json.dumps(stkCode)

@app.route("/syncdb")
def syncdb():
	threads = []
	allStkCodes = fnAllStkCode()
	for currentStk in allStkCodes:
		# showsyncstatus()
		syncdbtread(currentStk)
	# processes = [mp.Process(target=syncdbtread(currentStk)) for currentStk in allStkCodes]
	# pool = Pool(8)
	# pool.map()
	# allStkCodes = ["MOHOTAMILL"]
	# for currentStk in allStkCodes:
	# 	t = Process(target=syncdbtread, args=(currentStk,))
	# 	# t = threading.Thread(target=syncdbtread, args=(currentStk,))

	# 	# t.daemon = True
	# 	threads.append(t)

	# # print "hello"
	# for i in threads:
	# 	i.start()
	# # for i in threads:
	# # 	i.join()
	# print dayWiseDetail	
	return json.dumps("Success")

def fnGetStkCodefromName(stkName):
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select stksymbol from stkname where stkname = '" + stkName + "'"
	cursor.execute(connString)
	for i in cursor:
		stkName = i[0]
	return stkName


@app.route("/showDetails")
def showDetails():
	#
	# print request.args['stkName']
	try:
		stkCode = fnGetStkCodefromName(request.args['stkName'])
		# print stkCode
	 	# Lsit of details to be required
		reqStkList = ['previousClose','open','closePrice','lastPrice','dayHigh','dayLow','low52','high52',
						'totalTradedVolume','faceValue','companyName','symbol','basePrice','averagePrice']
		reqStkQuote = {}
		# print "Hellooo............." + stkCode
		stkQuote = nse.get_quote(str(stkCode))
		# print stkQuote
		# Get the values of listed details from quote..
		for reqCode in sorted(reqStkList):
			reqStkQuote[reqCode]=stkQuote[reqCode]

		#Calacute percentage change with prev. day close
		if float(stkQuote['closePrice']) == 0:
			reqStkQuote['ChngInPercnt'] = 100 * (float(stkQuote['lastPrice'] - float(stkQuote['previousClose']))) / float(stkQuote['previousClose'])
		else:
			reqStkQuote['ChngInPercnt'] = 100 * (float(stkQuote['closePrice'] - float(stkQuote['previousClose']))) / float(stkQuote['previousClose'])
	except:
		reqStkQuote["symbol"] = stkCode
	return json.dumps(reqStkQuote)
# def updateStkName():


@app.route('/')
def index():
    return render_template('index.html')

# def candleStatus(stkCode, prevclose, openPrice, closePrice, highPrice, lowPrice ):
# 	bodySize = float(closePrice) - float(openPrice)
# 	upperShadow = float(highPrice) - float(closePrice)
# 	lowerShadow = float(openPrice) - float(lowPrice)
# 	if float(lowerShadow) >= 2 * float(bodySize) :
# 		if float(upperShadow == 0):
# 			return stkCode

# def hammerstick(stkCode, openPrice, closePrice, highPrice, lowPrice ):
# 	bodySize = float(closePrice) - float(openPrice)
# 	upperShadow = float(highPrice) - float(closePrice)
# 	lowerShadow = float(openPrice) - float(lowPrice)
# 	if float(lowerShadow) >= 2 * float(bodySize) :
# 		if float(highPrice) == float(closePrice):
# 			return stkCode
		
@app.route('/redhammer')
def redhammer():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listHammerStick = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol,dayopen,dayclose,dayhigh,daylow from stkhistory as atab where sDate= '" + toDate + "'\
						 and (atab.dayhigh >= atab.dayclose) and (atab.dayopen >= atab.dayclose) \
					 	 and ( (atab.dayhigh - atab.dayclose) >= (atab.dayopen - atab.dayclose)) \
						 and ((atab.dayopen - atab.daylow) > 3 * (atab.dayhigh - atab.dayclose))" 
					  # and ((atab.dayclose - atab.daylow) > 2 * (atab.dayopen - atab.dayclose)) and (atab.dayopen=atab.dayhigh)" 
					  # and (atab.dayclose = atab.dayhigh)
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listHammerStick.append(data[0])
	return json.dumps(listHammerStick)


@app.route('/greenhammer')
def greenhammer():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listlonghammer = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol,dayopen,dayclose,dayhigh,daylow,percntchg from stkhistory as atab where sDate= '" + toDate + "'\
					 and (atab.dayhigh >= atab.dayclose) and (atab.dayopen <= atab.dayclose) \
					 and ( (atab.dayhigh - atab.dayclose) >= (atab.dayclose - atab.dayopen)) \
					 and ((atab.dayopen - atab.daylow) > 3 * (atab.dayhigh - atab.dayclose))" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listlonghammer.append(data[0])
	return json.dumps(listlonghammer)


@app.route('/bullishmarubozu')
def bullishmarubozu():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listBullishMarubozu = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol,dayopen,dayclose,dayhigh,daylow from stkhistory as atab where sDate= '" + toDate + "'\
					  and (atab.dayopen = atab.daylow) and (atab.dayhigh = atab.dayclose) and (atab.dayopen != atab.dayclose)" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listBullishMarubozu.append(data[0])
	return json.dumps(listBullishMarubozu)


@app.route('/bearishmarubozu')
def bearishmarubozu():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listBearishMarubozu = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol,dayopen,dayclose,dayhigh,daylow from stkhistory as atab where sDate= '" + toDate + "'\
					  and (atab.dayopen = atab.dayhigh) and (atab.daylow = atab.dayclose) and (atab.dayopen != atab.dayclose)" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listBearishMarubozu.append(data[0])
	return json.dumps(listBearishMarubozu)

@app.route('/top20Gain')
def top20Gain():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listBearishMarubozu = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol from stkhistory as atab where sDate= '" + toDate + "'\
					and atab.dayclose >= 45 and atab.dayclose < 999  order by percntchg DESC limit 20" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listBearishMarubozu.append(data[0])
	return json.dumps(listBearishMarubozu)

@app.route('/top20looser')
def top20looser():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listBearishMarubozu = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol from stkhistory as atab where sDate= '" + toDate + "' \
					and atab.dayclose >= 45 and atab.dayclose < 999 order by percntchg ASC limit 20" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listBearishMarubozu.append(data[0])
	return json.dumps(listBearishMarubozu)

@app.route('/top20volume')
def top20volume():
	toDate = request.args['ToDate']
	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	print toDate
	listBearishMarubozu = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol from stkhistory as atab where sDate= '" + toDate + "'\
					and atab.dayclose >= 45 and atab.dayclose < 999 and atab.percntchg > 1 order by volume DESC limit 20" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listBearishMarubozu.append(data[0])
	return json.dumps(listBearishMarubozu)



@app.route('/bulishengulfing')
def bulishengulfing():
	allStkCodes = fnAllStkCode()
	toDate = request.args['ToDate']
	prevDate = request.args['FromDate']

	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	prevDate = datetime.datetime.strptime(prevDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	prevDate = '{0}-{1}-{2}'.format(prevDate.year, prevDate.month, prevDate.day % 100)
	print prevDate, toDate
	listBulishEngulfing = []
	bulishEngulfingSuccess = []
	cnt=0
	# for i in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol,dayopen,dayclose,dayhigh,daylow from stkhistory as atab where \
					 atab.sDate >= '" + prevDate +"' and atab.sDate <= '" + toDate + "' \
					 and atab.dayclose >= 45 and atab.dayclose < 999 order by symbol,sDate" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listBulishEngulfing.append(data)
	# print listBulishEngulfing
	while cnt < len(listBulishEngulfing):
		# print cnt
		if listBulishEngulfing[cnt][0] == listBulishEngulfing[cnt + 1][0]:
			if listBulishEngulfing[cnt][1] > listBulishEngulfing[cnt][2]:
				if listBulishEngulfing[cnt][4]  > listBulishEngulfing[cnt + 1][4] and \
					listBulishEngulfing[cnt][1] < listBulishEngulfing[cnt + 1][2] and \
					listBulishEngulfing[cnt][2] > listBulishEngulfing[cnt + 1][1] and \
					listBulishEngulfing[cnt][3] < listBulishEngulfing[cnt + 1][3] :
					# print listBulishEngulfing[cnt][0],listBulishEngulfing[cnt][1], listBulishEngulfing[cnt + 1][1]
					bulishEngulfingSuccess.append(listBulishEngulfing[cnt][0])
				cnt = cnt + 2
			else:
				cnt = cnt + 2
		else:
			cnt = cnt + 1	
	# print listBulishEngulfing[2695], listBulishEngulfing[2696]
 	return json.dumps(bulishEngulfingSuccess)




@app.route('/gapUpOpen')
def gapUpOpen():
	allStkCodes = fnAllStkCode()
	toDate = request.args['ToDate']
	prevDate = request.args['FromDate']

	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
	prevDate = datetime.datetime.strptime(prevDate, '%m/%d/%Y')
	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
	prevDate = '{0}-{1}-{2}'.format(prevDate.year, prevDate.month, prevDate.day % 100)
	# print prevDate, toDate
	listGapUpOpen = []
	GapUpOpenSuccess = []
	cnt=0
	# for i in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	connString = "select symbol,dayopen,dayclose,dayhigh,daylow,volume from stkhistory as atab where \
					 atab.sDate >= '" + prevDate +"' and atab.sDate <= '" + toDate + "' and atab.volume > 100000 \
					 and atab.dayclose >= 45 and atab.dayclose < 999 order by symbol,sDate" 
	# print connString
	cursor.execute(connString)
	for data in cursor:
		listGapUpOpen.append(data)
	# print listBulishEngulfing
	while cnt < len(listGapUpOpen) - 1:
		# print listGapUpOpen[cnt][0], listGapUpOpen[cnt + 1][0] , cnt , listGapUpOpen[cnt][5]
		if listGapUpOpen[cnt][0] == listGapUpOpen[cnt + 1][0]:
			if listGapUpOpen[cnt + 1][1] > listGapUpOpen[cnt][2]:
				if listGapUpOpen[cnt + 1][2]  > listGapUpOpen[cnt][3] and \
					listGapUpOpen[cnt][2] > listGapUpOpen[cnt][1]:

					#  and \
					# listGapUpOpen[cnt][1] < listGapUpOpen[cnt + 1][2] and \
					# listGapUpOpen[cnt][2] > listGapUpOpen[cnt + 1][1] and \
					# listGapUpOpen[cnt][3] < listGapUpOpen[cnt + 1][3] :
					# print listBulishEngulfing[cnt][0],listBulishEngulfing[cnt][1], listBulishEngulfing[cnt + 1][1]
					# print listGapUpOpen[cnt][0]
					GapUpOpenSuccess.append(listGapUpOpen[cnt][0])
				cnt = cnt + 2
			else:
				cnt = cnt + 2
		else:
			cnt = cnt + 1	
	# print listBulishEngulfing[2695], listBulishEngulfing[2696]
 	return json.dumps(GapUpOpenSuccess)


# @app.route('/threeDma')
# def threeDma():
# 	allStkCodes = fnAllStkCode()
# 	toDate = request.args['ToDate']
# 	prevDate = request.args['FromDate']

# 	toDate = datetime.datetime.strptime(toDate, '%m/%d/%Y')
# 	prevDate = datetime.datetime.strptime(prevDate, '%m/%d/%Y')
# 	toDate = '{0}-{1}-{2}'.format(toDate.year, toDate.month, toDate.day % 100)
# 	prevDate = '{0}-{1}-{2}'.format(prevDate.year, prevDate.month, prevDate.day % 100)
# 	print prevDate, toDate
# 	listBulishEngulfing = []
# 	bulishEngulfingSuccess = []
# 	cnt=0
# 	# for i in allStkCodes:
# 	mariadb_connection = fnconnDB()
# 	cursor = mariadb_connection.cursor()
# 	connString = "select symbol,dayopen,dayclose,dayhigh,daylow from stkhistory as atab where \
# 					 atab.sDate >= '" + prevDate +"' and atab.sDate <= '" + toDate + "' order by symbol,sDate" 
# 	# print connString
# 	cursor.execute(connString)
	



@app.route('/candleGraphData')
def candleGraphData():
	datalist = []
	dataToDump = []
	dataToDump1 = []
	stkCode = request.args['stkCode']
	print "Stk code is......................",request.args['stkCode']
	stkCode=request.args['stkCode']
	print stkCode
	maxDate = checkmaxdata(stkCode)
	minDate = maxDate - timedelta(3)
	maxDate = maxDate.strftime('%Y-%m-%d') 
	minDate = minDate.strftime('%Y-%m-%d') 
	print minDate, maxDate, "............................................ "
	# lsitHammerStick = []
	# allStkCodes = fnAllStkCode()
	# for stkdCode in allStkCodes:
	mariadb_connection = fnconnDB()
	cursor = mariadb_connection.cursor()
	# select * from stkhistory where symbol='ongc' order by sDate DESC limit 20
	connString = "select sDate,daylow,dayopen,dayclose,dayhigh from stkhistory where symbol = '" + stkCode + "' \
					order by sDate DESC limit 3"
	cursor.execute(connString)
	for stkdetails in cursor:
		datalist.append(stkdetails)
	for i in datalist:
		dataToDump.append("["+str(i[0])+","+ str(i[1]) + "," + str(i[2]) +"," + str(i[3]) + "," + str(i[4]) + "]")
	# dataToDump1.append("dummy")
	# dataToDump1.append(str(dataToDump).replace("\"",""))
	print dataToDump
	return json.dumps(dataToDump)


if __name__=="__main__":
    app.run(host='0.0.0.0',port=int('8000'),debug=True,threaded=True)