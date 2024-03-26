from numpy import empty
import pandas as PD
import pymysql
import datetime
if __name__ == '__main__':
#To debug the missing ETF  
    missingETF=[]    

#Read the data file
    dateInfo=((datetime.date.today()).strftime("%d-%b-%Y"))
    #dateInfo=''

    #finalloc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/NSE_daily_data/'+'MW-ETF-'+dateInfo+'.csv'
    finalloc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/NSE_daily_data/Feb_24/MW-ETF-01-Feb-2024.csv'
    dataDetails=PD.read_csv(finalloc)
    index='NSE'

    
#DB connection setup
    connection = pymysql.connect(host='localhost',user='root',password='',db='ETF')
    cursor = connection.cursor()
    retrieveetf_sql="SELECT `idetf` FROM `etf` where `etf_symbol` = %s"
    insert_sql="INSERT `etf_daily_transaction`(`etf_id`,`etf_daily_traded_volume`,`etf_daily_traded_value`,`etf_last_traded_price`,`etf_prevclose_price`,`etf_trade_date`,`etf_index`,`etf_traded_high`,`etf_traded_low`,`etf_changepercentage`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    #Get the data from the file
    for rwCnt in dataDetails.index:
#Iterate the rows in 'csv' is bit different 
#In the case of 'xls',[] would work but in the case of 'csv' we need to use 'iloc' to iterate through rows
        etfsymboldetail=dataDetails.iloc[rwCnt,0]
        etfHigh=dataDetails.iloc[rwCnt,3]
        etfLow=dataDetails.iloc[rwCnt,4]
        etfprevclose=dataDetails.iloc[rwCnt,5]
        etfLTP=dataDetails.iloc[rwCnt,6]
        etfChangePercentage=str(dataDetails.iloc[rwCnt,8])
        etfVolume=dataDetails.iloc[rwCnt,9]
        etfValue=dataDetails.iloc[rwCnt,10]
#To replace the '-' symbol with '0' so that calculation can be performed
#Need to replace this method with better one
        if etfHigh == '-':
            etfHigh=0
        if etfLow == '-':
            etfLow=0
        if etfprevclose == '-':
            etfprevclose=0
        if etfLTP =='-':
            etfLTP=0
        if etfChangePercentage =='-':
            etfChangePercentage=0
        if etfVolume == '-':
            etfVolume =0
        if etfValue == '-':
            etfValue=0
        
#Retrieve the ETF details from the DB,based on the Symbol information
        cursor.execute(retrieveetf_sql,etfsymboldetail)
        etfInfo=cursor.fetchone()
#checking if the ETF informaton is present in the DB
        if (etfInfo):
            etfID=etfInfo[0]
            Values=(etfID,etfVolume,etfValue,etfLTP,etfprevclose,dateInfo,index,etfHigh,etfLow,etfChangePercentage)
            print("The values of ETF",Values)
            #cursor.execute(insert_sql,Values)
        else:
            print("Am i called here")
            missingETF.append(etfsymboldetail)
    cursor.close()
#Write the missing ETF information to excel
    missingETFDataFrame=PD.DataFrame(missingETF,columns=['ETF_Name'])
    if not missingETFDataFrame.empty:
        missingETFDataFrame.to_excel(r'/Volumes/Project/ETFAnalyser/ETF/ETF_Data/Error/'+dateInfo+'.xlsx')

    
    #Generate the Date information dynamically 
#Disconnect the connection
    connection.commit()
    connection.close()
