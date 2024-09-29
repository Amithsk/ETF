#This is the backup process of updating the ETF details daily.
#The code update the ETF details,generated using the NSE and AMI website for a specific peroid.
#Currently the ETF details generation is manual,need to auotmate it
from numpy import empty
import pandas as PD
import pymysql
import datetime
import glob
import os
if __name__ == '__main__':
#To debug the missing ETF  
    missingETF=[]    

#Read the data file
    # Prompt the user for the folder containing the CSV files
    input_folder = input("Please enter the path of the folder containing the CSV files: ")
    dataDetails=PD.read_csv(input_folder)
    

    
#DB connection setup
    connection = pymysql.connect(host='localhost',user='root',password='',db='ETF')
    cursor = connection.cursor()
    retrieveetf_sql="SELECT `idetf` FROM `etf` where `etf_symbol` = %s"
    insert_sql="INSERT `etf_daily_transaction`(`etf_id`,`etf_trade_date`,`etf_daily_traded_volume`,`etf_daily_traded_value`,`etf_last_traded_price`,`etf_prevclose_price`,`etf_trade_date`,`etf_traded_high`,`etf_traded_low`,`etf_day_open`,`etf_daily_nooftrade`,`etf_52wh`,`etf_52wl`,`etf_daily_deliverableqty`,`etf_daily_deliverablepercentageqty`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    #Get the data from the file
    for rwCnt in dataDetails.index:
#Iterate the rows in 'csv' is bit different 
#In the case of 'xls',[] would work but in the case of 'csv' we need to use 'iloc' to iterate through rows
        
        etfTradeDate=dataDetails.iloc[rwCnt,0]
        etfNav = dataDetails.iloc[rwCnt,2]
        etfDateOpen=dataDetails.iloc[rwCnt,3]
        etfHigh=dataDetails.iloc[rwCnt,4]
        etfLow=dataDetails.iloc[rwCnt,5]
        etfLTP=dataDetails.iloc[rwCnt,6]
        etfPrevclose=dataDetails.iloc[rwCnt,7]
        etfNav = dataDetails.iloc[rwCnt,2]
        etfVwap=dataDetails.iloc[rwCnt,8]
        etf52WH= dataDetails.iloc[rwCnt,9]
        etf52WL= dataDetails.iloc[rwCnt,10]
        etfVolume=dataDetails.iloc[rwCnt,11]
        etfValue=dataDetails.iloc[rwCnt,12]
        etfDayTrade=dataDetails.iloc[rwCnt,13]
        etfsymboldetail=dataDetails.iloc[rwCnt,14]
        etfDeliverableQty= dataDetails.iloc[rwCnt,15]
        etfDeliverableQtyPercentage =dataDetails.iloc[rwCnt,16]
        
#Retrieve the ETF details from the DB,based on the Symbol information
        cursor.execute(retrieveetf_sql,etfsymboldetail)
        etfInfo=cursor.fetchone()
#checking if the ETF informaton is present in the DB
        if (etfInfo):
            etfID=etfInfo[0]
            Values=(etfID,etfVolume,etfValue,etfLTP,etfPrevclose,etfTradeDate,etfHigh,etfLow,etfDateOpen,etfDayTrade,etf52WH,etf52WL,etfDeliverableQty,etfDeliverableQtyPercentage)
            print("The values of ETF",Values)
            #cursor.execute(insert_sql,Values)
        else:
            print("Am i called here")
            missingETF.append(etfsymboldetail)
    cursor.close()
#Write the missing ETF information to excel
    dateInfo=((datetime.date.today()).strftime("%d-%b-%Y"))
    missingETFDataFrame=PD.DataFrame(missingETF,columns=['ETF_Name'])
    if not missingETFDataFrame.empty:
        missingETFDataFrame.to_excel(r'/Volumes/Project/ETFAnalyser/ETF/ETF_Data/Error/'+dateInfo+'.xlsx')

    
    #Generate the Date information dynamically 
#Disconnect the connection
    connection.commit()
    connection.close()
