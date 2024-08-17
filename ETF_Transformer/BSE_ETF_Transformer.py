from typing import final
from numpy import subtract
import pandas as PD
import datetime
if __name__ == '__main__':
    try:

        dateInfo =  datetime.date.today()
        tempDataFrame = PD.DataFrame()
        finalDataFrame = PD.DataFrame()
        #loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/BSE_daily_data/'+str(dateInfo)+'.xlsx'
        loc='/Volumes/Project/ETFAnalyser/ETF/ETF_Data/BSE_daily_data/2022-02-06.xlsx'

        df = PD.read_excel(loc,sheet_name = 'Sheet1')
#Facing issue with the special character in column name 'Day's High / Low',so replaced ' with space now 'Days High / Low'
        df.columns = df.columns.str.replace('\'', '')
#Why two '[[]]' because an error was thrown "Expected a 1D array, got an array with shape (35, 2)"
#So need to supply two dimensional array 
        tempDataFrame[['PrevClose','PrevOpen']]=df['Prev. Close / Open'].str.split('/',expand=True)
        tempDataFrame=tempDataFrame.to_numeric(tempDataFrame,downcast="float")
        #df["A"] = pd.to_numeric(df["A"], downcast="float")

        #tempDataFrame['CHNG%']=tempDataFrame.apply(lambda x:tempDataFrame['PrevOpen']-tempDataFrame['PrevClose'],axis = 1)
        #float(df['Change'])/float(tempDataFrame['PrevClose'])
        #df['d - a'] = df.apply(lambda x: x['d'] - x['a'], axis = 1)
        print(tempDataFrame)
        print(tempDataFrame.dtypes)
 
        
        finalDataFrame['ETFSymbol']=df['ETF Name']
        finalDataFrame['ETFAsset']=df['Underlying Asset']
        finalDataFrame[['DailyHigh','DailyLow']]=df['Days High / Low'].str.split('/',expand=True)
        finalDataFrame['PrevClose']= tempDataFrame['PrevClose']
        finalDataFrame['LTP']=df['LTP/Close']
        finalDataFrame['CHNG']=df['Change']
        finalDataFrame['Volume']=df['Total Volume']
        finalDataFrame['Value']=df['Turnover (Lacs)']
#Split the column data into different columns by delimiter
#https://datascienceparichay.com/article/pandas-split-column-by-delimiter/
#Get the 52 week high/low information

        finalDataFrame[['52WeekHigh','52WeekLow']] = df['52Week High / Low'].str.split('/',expand=True)

#Write the data into the xlsx file
        #finalDataFrame.to_excel(r'/Volumes/Project/ETFAnalyser/ETF/ETF_Data/BSE_daily_data/'+str(dateInfo)+'_transformed.xlsx',index=False)
        
    except :
        print("Some error thrown")