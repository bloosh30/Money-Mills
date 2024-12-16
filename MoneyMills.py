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
    
    # get stock price
   
    optionChainPrint(ticker,contractType,strikePrice,expDate,formatDate)    

    #2021-12-23:20
#_____________________________________________________________________________________________________________________________________________________

#SearchTools makes it easier to find information
class searchTools:
  def __init__(search, strike, date, file, last):
    search.file = file
    search.strike = strike
    search.date = date
    search.last = last
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
        
        last = chainData['underlyingPrice']
        
        #SearchTools makes it easier to find information
        s = searchTools(strStrikePrice,formatDate,chainData,last)
        
        printDescription(s)    
        binomialDistribution(s)

    elif contractType == 'P':
        
        response = c.get_option_chain(ticker, contract_type=c.Options.ContractType.PUT, strike=strikePrice, from_date = expDate, to_date = expDate)
        
        text = json.dumps(response.json())
        chainData = json.loads(text)   
        
        last = chainData['underlyingPrice']

        #SearchTools makes it easier to find information
        s = searchTools(strStrikePrice,formatDate,chainData, last)  
        
        printDescription(s)   
        binomialDistribution(s)
#______________________________________________________________________________________________________________________________________________________     


def getValue(s,keyWord):
    return s.file['callExpDateMap'][s.date][s.strike][0][keyWord]
  
def printDescription(s):
    keyword = {'description','last','daysToExpiration'}
    for key in keyword:
            print(key + ':', end = ' ')
            print(s.file['callExpDateMap'][s.date][s.strike][0][key])
#______________________________________________________________________________________________________________________________________________________              
    
def binomialDistribution(s):   
        
    #VARIABLE SETUP
    
    # Number of intervals between expiriation, the more the more accurate the model
    N = 5
    
    currentPrice = float(s.last)    #Current price of stock
    strikePrice = float(s.strike)   #Strike for current Contract
    
    t = int(getValue(s,'daysToExpiration'))  #Days to expiration for contract
    t = t / 360                              #Convert to years
    
    timeChange = t / (N-1)                           #Days to expiration split into the # of levels in the model
    volatility = 0.4                                 #Volatility for current contract
    
    # Factor ratio for price increase or decrease
    factorPriceIncrease = numpy.exp(volatility * numpy.sqrt(timeChange)) 
    factorPriceDecrease = 1/factorPriceIncrease                                  
    
    # Current Interest Rate
    # Probability based on irate time change and volatility
    irate = 0.015
    prob = (numpy.exp(irate*timeChange)-factorPriceDecrease) / (factorPriceIncrease - factorPriceDecrease)
    
    #print('TEST: ')
    #print(currentPrice)
    #print(strikePrice)
    #print(timeChange)
    #print(factorPriceDecrease)
    #print(factorPriceIncrease)
    #print(irate)
    #print(prob)
    
    # Set up empty matrices
    stockPriceMatrix = numpy.zeros((N,N))
    callPriceMatrix = numpy.zeros((N,N))
    
    # Set the inital node to the current stock Price
    stockPriceMatrix[0,0] = currentPrice
    
    # Fill the remaning values into the stock price matrix
    for i in range(1, N):
        W = i + 1
        stockPriceMatrix[i, 0] = factorPriceDecrease * stockPriceMatrix[i-1, 0]
        for j in range(1, W):
            stockPriceMatrix[i, j] = factorPriceIncrease * stockPriceMatrix[i - 1, j - 1]
            
    # Calculating the stock price at expiration          
    tempMatrix = stockPriceMatrix[-1,:] - strikePrice
    
    # Return matrix shape
    tempMatrix.shape = (tempMatrix.size, )
    
    # Remove any instances of 0 because contract is worthless
    tempMatrix = numpy.where(tempMatrix >= 0, tempMatrix, 0)
    
    # Set the last row to the new value check
    callPriceMatrix[-1,:] = tempMatrix
    
    # Fill out the remaining call price Matrix
    for i in range(N - 2,-1,-1):
        for j in range(i + 1):
            callPriceMatrix[i,j] = numpy.exp(-irate * timeChange) * ((1-prob) * callPriceMatrix[i+1,j] + prob * callPriceMatrix[i+1,j+1])
   
    print('\n')   
    print("Projected Model Price Yield: ", end = ' ')         
    print(callPriceMatrix[0][0])     
    
    print('\n')  
    
    print(stockPriceMatrix)
    
    print('\n')  
    
    print(callPriceMatrix) 
    
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

