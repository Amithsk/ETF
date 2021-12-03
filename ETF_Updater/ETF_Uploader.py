#To upload the ETF data into the DB for reporting purpose
#To upload the ETF's NAV,AUM,Tracking error,Expense ratio
#To upload the Asset's Tracking error,Expense ratio
import pandas as PD
import pymysql

#Asset():
#updateAsset():
#createAsset():
#createAssetdetails():
#ETF():
#createETF():
#updateETF():
#createETFdetails():


#def updateAsset(connection_details):

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

#def createAssetdetails(connection_details):

#def createETF(connection_details):

#def addETF(connection_details):

#def createETFdetails(connection_details):

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
	data_loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/ETFdetail.xlsx'
	connection_details=connect_db()
	addAsset(connection_details,data_loc)
	disconnect_db(connection_details)
main()

