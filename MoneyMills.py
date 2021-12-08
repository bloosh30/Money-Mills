from os import EX_CANTCREAT
from tda import auth, client
#from tda.orders import EquityOrderBuilder, Duration, Session
import config
import datetime
import json

import numpy
#import matplotlib.pyplot as plt
from scipy.sparse import csc_matrix


def requestOptionChain():       
 
    # Ticker Symbol
    print("\n")
    ticker = input("Enter Ticker: ")
    
    # Call Put
    while True:
        contractType = input("Enter the Contract Type (C/P): ")          
        if contractType == 'C':
            break
        if contractType == 'P':
            break
        print("Incorrect Entry \n")


    # Strike Price
    strikePrice = input("Enter The Strike Price: ")
    
    # Expiration Date 
    while True:   
        contractexpDate = input("Enter The Expiration contract expiration Date (MM-DD-YY): ")
        if len(contractexpDate) == 8:
            break
        print("Incorrect Entry \n")  
    
    mm = contractexpDate[0] + contractexpDate[1]
    dd = contractexpDate[3] + contractexpDate[4]
    yy = contractexpDate[6] + contractexpDate[7]
    
    expDate = datetime.date(year = int(yy)+2000, month = int(mm), day = int(dd)) 

    #Calculate days reminainig for expiration date
    daysRemaining = expDate.day - datetime.datetime.now().day

    formatDate = str(expDate.year) + "-" + str(expDate.month) + "-" + str(expDate.day) + ":" + str(daysRemaining)
   
    optionChainPrint(ticker,contractType,strikePrice,expDate,formatDate)    

    #2021-12-23:20
#_____________________________________________________________________________________________________________________________________________________

#SearchTools makes it easier to find information
class searchTools:
  def __init__(search, strike, date, file):
    search.file = file
    search.strike = strike
    search.date = date
#_____________________________________________________________________________________________________________________________________________________

# PRINT OPTION CHAIN FUNCTION 
def optionChainPrint(ticker,contractType,strikePrice,expDate,formatDate):

    print('\n')

    #Set up Formats to insert into function
    strikePrice = float(strikePrice)
    strStrikePrice = str(strikePrice)

    # FOR SAMPLE RUN
    if contractType == 'C' :

        response = c.get_option_chain(ticker, contract_type=c.Options.ContractType.CALL, strike=strikePrice, from_date = expDate, to_date = expDate)   
        
        text = json.dumps(response.json())
        chainData = json.loads(text)

        #SearchTools makes it easier to find information
        s = searchTools(strStrikePrice,formatDate,chainData)    

        getValue(s,'description')
        getValue(s,'bid')
        getValue(s,'ask')
        getValue(s,'totalVolume')
        getValue(s,'daysToExpiration')
        
        binomialDistribution(getValue(s,'daysToExpiration'), 160 ,getValue(s,'bid'), strikePrice)

    elif contractType == 'P':
        
        response = c.get_option_chain(ticker, contract_type=c.Options.ContractType.PUT, strike=strikePrice, from_date = expDate, to_date = expDate)
        
        text = json.dumps(response.json())
        chainData = json.loads(text)   

        s = searchTools(strStrikePrice,formatDate,chainData)  

        getValue(s,'description')
        getValue(s,'bid')
        getValue(s,'ask')
        getValue(s,'totalVolume')
        getValue(s,'daysToExpiration')
#______________________________________________________________________________________________________________________________________________________     


#def setVariableValues(chainData,strStrikePrice,formatDate):

        # SET ALL VARIABLES NEEDE DFOR EQUAITON HERE

def getValue(s,keyWord):
    if keyWord != 'description':
        print(keyWord + ':', end = ' ')
    print(s.file['callExpDateMap'][s.date][s.strike][0][keyWord])
  
    
def binomialDistribution(daysToExpiration, stockPrice, bid, strikePrice ):   
    
    #VARIABLE SETUP
    
    S0 = stockPrice
    t = daysToExpiration
    u = 1.05
    d = 1/u
    p = 0.6
    
    K = strikePrice
    
    sxu = S0 * u
    sxd = S0 * d
    
    print (sxu, sxd)
    
    
#______________________________________________________________________________________________________________________________________________________

try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path = config.chromedriver_path)as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)

requestOptionChain()

print('\n')

#stockPriceMatrix = csc_matrix( (N,N) )

