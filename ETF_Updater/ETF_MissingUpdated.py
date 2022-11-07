#To upload the missing ETF & Asset information
#Pending
#1.Make the code OOP ,currently method driven
import pandas as PD
import pymysql
import datetime
import re

#To debug the missing ETF  
missingETF=[]  

#To add the asset information to the DB
def addAsset(connection_details,data_loc):
	try:
		print("Adding asset information")
		insert_sql="INSERT INTO`etf_asset`(`asset_info`)values(%s)"
		retrieve_sql="SELECT `idetf_asset`FROM `etf_asset` WHERE `asset_info`=%s"
		cursor=connection_details.cursor()
		AssetDetails = PD.read_excel(data_loc,sheet_name = 'Asset')
		for lpcnt in AssetDetails.index:
			values =AssetDetails['Asset'][lpcnt]
#To check if the value already exist in the DB
			cursor.execute(retrieve_sql,values)
			etfAsset=cursor.fetchone()
#Check if the value exist in the DB
			if  etfAsset:
#If the value exist,just ignore so that duplicate entries are not there
				print("The value already present",etfAsset[0])
			else:
#If the value don't exist,add the values
				cursor.execute(insert_sql,values)
				print("The values are",values)
#Will not write into the execl,as Asset missing information is identified during the ETF update process
		cursor.close()

		
	except Exception as e:
		raise e
def addETF(connection_details,dataloc,monthinfo):
	try:
		print("Entering Add ETF usecase")
		cursor=connection_details.cursor()
#To retrieve the asset the information from the DB
		retrieve_sql = "SELECT `idetf_asset`FROM `etf_asset` WHERE `asset_info`=%s"
		insert_sql="INSERT INTO`etf`(`etf_name`,`etf_asset_category`,`etf_symbol`)values(%s,%s,%s)"
		ETFDetails=PD.read_excel(dataloc,sheet_name= 'ETF')
		for lpcnt in ETFDetails.index:
			etfAsset=ETFDetails['Sector'][lpcnt]
			etfName=ETFDetails['ETFname'][lpcnt]
			etfSymbol=ETFDetails['ETFSymbol'][lpcnt]
			cursor.execute(retrieve_sql,etfAsset)
			etfAssetdb=cursor.fetchone()
#If the Asset information is present,write that information to the DB
			if etfAssetdb:
				values=(etfName,etfAssetdb[0],etfSymbol)
				cursor.execute(insert_sql,values)
			else:
#If the Asset information is not prt,append Asset in into an list information & write into a file later
				missingETF.append(etfAsset)
#Write the missing ETF information into excel,so that Asset information can be updated
		missingETFDataFrame=PD.DataFrame(missingETF,columns=['AssetInfo'])
		if not missingETFDataFrame.empty:
			missingETFDataFrame.to_excel(r'/Volumes/Project/ETFAnalyser/ETF/ETF_Data/Error/'+'MissingAsset_'+monthinfo+'.xlsx')


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
	data_loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/ETF_fund_details/MissingInfo/missingInfo.xlsx'
	connection_details=connect_db()
	#addETF(connection_details,data_loc,monthinfo)
	#addAsset(connection_details,data_loc)
	disconnect_db(connection_details)

main()

