#To upload the ETF data into the DB for reporting purpose
#To upload the ETF's NAV,AUM,Tracking error,Expense ratio
#To upload the Asset's Tracking error,Expense ratio
import pandas as PD
import pymysql
import datetime
import re
#Facing problem with etfExpesnseRatio,etfTracking values after division
#'0.0014000000000000002' huge numbers were returned,to avoid that Decimal was used
#https://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points
from decimal import Decimal as D


#For some ETF the AUM,ExpenseRatio,TrackingError values might not be present,so need to convert into numerical value('0')
#Expenseratio,TrackingError is returned in '0.20%' percentage format,need to convert into decimal format and remove '%'
def formatdata(etfAUM,etfExpenseRatio,etfTrackingError):
	if(etfAUM == '—'):
		etfAUM = 0
	else:
		etfAUM=re.sub('[₹,cr]','',str(etfAUM))
	if (etfExpenseRatio == '—'):
		etfExpenseRatio = 0
	else:
		#Decimal is used to avoid the issue faced while using float
		etfExpenseRatio=(D(re.sub('%','',str(etfExpenseRatio)))/100)
	if(etfTrackingError=='—'):
		etfTrackingError=0
	else:
		#Decimal is used to avoid the issue faced while using float
	
		etfTrackingError=(D(re.sub('%','',str(etfTrackingError)))/100)
	

	return etfAUM,etfExpenseRatio,etfTrackingError

#To add the asset information to the DB
def addAsset(connection_details,data_loc):
	try:
		print("Adding asset information")
		insert_sql="INSERT INTO`etf_asset`(`asset_info`)values(%s)"
		cursor=connection_details.cursor()
		AssetDetails = PD.read_excel(data_loc,sheet_name = 'Asset')
		for lpcnt in AssetDetails.index:
			values =AssetDetails['Asset'][lpcnt]
			cursor.execute(insert_sql,values)
		cursor.close()
		
	except Exception as e:
		raise e
#To add the asset related information(TrackingError,ExpenseRatio) to the DB
def addAssetdetails(connection_details,dataloc,monthinfo):
	try:
		print("Adding asset related information")
		insert_sql="INSERT INTO`etf_asset_details`(`asset_id`,`asset_trackingerror`,`asset_expenseratio`,`asset_month`)values(%s,%s,%s,%s)"
		retrieve_sql ="SELECT `idetf_asset` FROM `etf_asset` WHERE `asset_info`=%s"
		cursor=connection_details.cursor()
		AssetDetails= PD.read_excel(dataloc,sheet_name = 'Data')
		for lpcnt in AssetDetails.index:
			assetCode = AssetDetails['Sector'][lpcnt]
			assetTrackingError = AssetDetails['Asset_Tracking_Error'][lpcnt]
			assetExpenseRatio=AssetDetails['Sctr_Expense_Ratio'][lpcnt]
			#To retrieve the Asset code information from the DB
			cursor.execute(retrieve_sql,assetCode)
			assetCode_db = cursor.fetchone()
			#To update the Asset detail information in the DB
			values=(assetCode_db[0],assetTrackingError,assetExpenseRatio,monthinfo)
			cursor.execute(insert_sql,values)
	except Exception as e:
		raise e


def addETF(connection_details,dataloc):
	try:
		print("Entering Add ETF usecase")
		cursor=connection_details.cursor()
		retrieve_sql = "SELECT `idetf_asset`FROM `etf_asset` WHERE `asset_info`=%s"
		insert_sql="INSERT INTO`etf`(`etf_name`,`etf_asset_category`,`etf_symbol`)values(%s,%s,%s)"
		ETFDetails=PD.read_excel(dataloc,sheet_name='Data')
		for lpcnt in ETFDetails.index:
			etfAsset=ETFDetails['Sector'][lpcnt]
			etfName=ETFDetails['ETFname'][lpcnt]
			etfSymbol=ETFDetails['ETFSymbol'][lpcnt]
			cursor.execute(retrieve_sql,etfAsset)
			etfAssetdb=cursor.fetchone()
			values=(etfName,etfAssetdb[0],etfSymbol)
			#print("The values are ",values)
			cursor.execute(insert_sql,values)
	except Exception as e:
		raise e

def addETFdetails(connection_details,dataloc,monthinfo):
	try:
		print("Entering Add ETF details usecase")
		cursor=connection_details.cursor()
		ETFDetails=PD.read_excel(dataloc,sheet_name='Data')
		for lpcnt in ETFDetails.index:
			etfTrackingError =ETFDetails['Tracking_Error'][lpcnt]
			etfExpenseRatio=ETFDetails['Expense_Ratio'][lpcnt]
			etfAUM=ETFDetails['AUM'][lpcnt]
			etfFundhouse=ETFDetails['ETF Fund house'][lpcnt]
			#To get the ETF id information,we can also use ETF name
			etfSymbol =ETFDetails['ETFSymbol'][lpcnt]
			etfAUM,etfExpenseRatio,etfTrackingError=formatdata(etfAUM,etfExpenseRatio,etfTrackingError)
			values=(etfAUM,etfTrackingError,etfExpenseRatio,monthinfo,etfFundhouse)
			print("The values are ",values)

	except Exception as e:
		raise e


def connect_db():
	try:
		connection = pymysql.connect(host='localhost',user='root',password='',db='ETF')
		#To check if the connection is successful
		#Source:https://stackoverflow.com/questions/45800460/how-to-use-mysqldb-is-connected-to-check-an-active-mysql-connection-using-pyth
		if connection.open:
			print("Success")
			return connection
	except Exception as whaterror:
		print(whaterror)

def disconnect_db(connection_details):
	try:
		connection_details.commit()
		connection_details.close()
		if connection_details.open:
			print("Something went wrong")
		else:
			print("Everything is success")
	except Exception as whaterror:
		print(whaterror)

def main():
	monthinfo = (datetime.datetime.now()).strftime("%b")
	data_loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/ETFdetail_'+monthinfo+'_Combined.xlsx'
	connection_details=connect_db()
	#addAsset(connection_details,data_loc)
	#addAssetdetails(connection_details,data_loc,monthinfo)
	#addETF(connection_details,data_loc)
	addETFdetails(connection_details,data_loc,monthinfo)
	disconnect_db(connection_details)

main()

