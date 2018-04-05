for currentstk in allStkCodes:
	try:
		stkdetails =  nse.get_quote(str(currentstk))
		stkname = stkdetails["companyName"]
             	print stkname
            	cursor = mariadb_connection.cursor()
            	cursor.execute("update stkname set stkname = '" + stkname + "' where stksymbol = '" + currentstk + "'")
             	mariadb_connection.commit()
     	except:
             	Print "............... Failed ................."

