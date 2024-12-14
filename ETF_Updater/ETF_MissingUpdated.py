#To add the base information of ETF and Asset information
#Post update,ETF_Uploaded.py will be used to add additional details of the ETF

import pandas as PD
import pymysql
import datetime
import re
import os
 #To add the asset information to the DB
def addAsset(connection_details,data_loc):
	try:
		print("Adding asset information")
		insert_sql="INSERT INTO`etf_asset`(`asset_info`)values(%s)"
		retrieve_sql="SELECT `idetf_asset`FROM `etf_asset` WHERE `asset_info`=%s"
		cursor=connection_details.cursor()
		AssetDetails = PD.read_excel(data_loc,sheet_name = 'Asset')
		for lpcnt in AssetDetails.index:

			values =AssetDetails['Asset'][lpcnt].strip().upper()
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
				print("The  added values are",values)
#Will not write into the execl,as Asset missing information is identified during the ETF update process
		cursor.close()

		
	except Exception as e:
		raise e
def addETF(connection_details,dataloc,monthinfo):
#The 
	try:
		print("Entering Add ETF usecase")
		cursor=connection_details.cursor()
		#To debug the missing ETF  
		missingETF=PD.DataFrame(columns=['AssetInfo'])
#To retrieve the asset the information from the DB
		retrieve_etf_asset_sql = "SELECT `idetf_asset`FROM `etf_asset` WHERE `asset_info`=%s"
		retrieve_etf_symbol_sql = "SELECT `etf_symbol`FROM `etf` WHERE `etf_symbol`=%s"
		insert_sql="INSERT INTO`etf`(`etf_name`,`etf_asset_category`,`etf_symbol`,`etf_fundhouse_name`)values(%s,%s,%s,%s)"
		ETFDetails=PD.read_excel(dataloc,sheet_name= 'ETF')
		for lpcnt in ETFDetails.index:
			etfAsset=ETFDetails['Asset'][lpcnt].strip().upper()
			etfName=ETFDetails['ETFname'][lpcnt].upper()
			etfSymbol=ETFDetails['ETFSymbol'][lpcnt].upper()
			etfFundhouse=ETFDetails['ETFFundhouse'][lpcnt].upper()
#To retrieve the etf asset information from db
			cursor.execute(retrieve_etf_asset_sql,etfAsset)
			etfAssetdb=cursor.fetchone()
#To retrieve the etf symbol id information from db
			cursor.execute(retrieve_etf_symbol_sql,etfSymbol)
			etfSymboldb=cursor.fetchone()
#If the Asset information is present  in the db
			if etfAssetdb:
#etfSymbol is not present,write that information to the DB & prevent duplicate ETF being added
				if not(etfSymboldb):
					values=(etfName,etfAssetdb[0],etfSymbol,etfFundhouse)
					#cursor.execute(insert_sql,values)
				else:
					print("The duplicate values are ",etfAsset,etfSymbol,etfFundhouse)
#If the Asset information is not present,append Asset in into an list information & write into a file later
#Using loc function to update the Dataframe
			else:
				missingETF.loc[len(missingETF)]= etfAsset
				
		
#Write the missing ETF information into excel,so that Asset information can be updated
		missingETFDataFrame=PD.DataFrame(missingETF,columns=['AssetInfo'])		
		if not missingETFDataFrame.empty:
			print("The missing value",missingETFDataFrame)
			file_name ="MissingAsset_"+monthinfo+".xlsx"	
			file_path =os.path.join(r"D:\ETF_Data\ETF_Error\\", file_name)		
			missingETFDataFrame.to_excel(file_path, index=False)


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
	data_loc='D:\ETF_Data\ETF_Fund_Details\MissingInfo\missingInfo.xlsx'
	connection_details=connect_db()
	#addETF(connection_details,data_loc,monthinfo)
	#addAsset(connection_details,data_loc)
	disconnect_db(connection_details)

main()

