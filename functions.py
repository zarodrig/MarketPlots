####################################################
#  FileName:functions.py
#  Author: Zorondras Rodriguez
#  Creation Date: December 5, 2020
#  Version:  0.12
#  Revision Date: December 9, 2020
#  Course: ENSF 310
#  Assignment: Final Project
#
#  Description: module for functions for final project
####################################################

## container for required data to pass to the grabber for each commodity type
class commoData:
    ''' Class to hold commodity file and folder data for grabber'''
    def __init__(self,folderName:str,fileName:str):
        self.folderName = folderName
        self.fileName = fileName

    def __repr__(self):
        print("Folder: " +self.folderName, "FileName: "+ self.fileName )

class timeInterval:
    '''
    Class / Data structure to hold two dates either as decimal dates or strings
    '''
    def __init__(self,T1:int,T2:int):
        self.T1 =T1
        self.T2 =T2

    def __repr__(self):
        print("Lower Time: "+ self.T1 +" Upper Time: "+self.T2)


def getDateRange():
    ''' 
        Ask for user input for a time range / date range of data to plot,
        return a timeInterval Object based on user specifications
    '''
    userResponse=input("Would you like to change the data range to plot? Y(y)/N(n):\n")

    if (userResponse == 'Y' or userResponse == 'y'):    
        T1str = input ("Enter the start date: YYYY-MM-DD:\n")
        T2str = input ("Enter the end date: YYYY-MM-DD:\n")
    
        # now we are going to convert the strings to decimal date
        # and then load them into a timeInterval object and return it
        # we assume that the user entered a string in the proper format with year month day
        strSplit1=T1str.split('-',-1)
        strSplit2=T2str.split('-',-1)

        T1=int(strSplit1[0])+(int(strSplit1[1])-1)/12+int(strSplit1[2])/365
        T2=int(strSplit2[0])+(int(strSplit2[1])-1)/12+int(strSplit2[2])/365

        tRange=timeInterval(T1,T2)
        return tRange  

    elif (userResponse == 'N' or userResponse == 'n'):
        return False  
    else:
        print("Input was not Y,y,N or n, no action taken.")
        return False


def applyDateRange(data):
    ''' Apply a date range to the input data set , return an output data set
        filters the input pandas dataframe and returns the filtered data
    '''
    dateRange = getDateRange()  # get a date range from user input returns a timeScale object or boolean 

    ## if user answered no then return the original data unfiltered
    if (dateRange == False):
        return data
    else:  # otherwise filter the data
        dataOut = data[data['decimal_date'] >= dateRange.T1]  # clip from the left range
        dataOut = dataOut[dataOut['decimal_date'] <= dateRange.T2]      # clip from the right range 
        return dataOut


def grabData( commodity: commoData, source:str):
    ''' 
    Grab the dataset requested from the internet
    Input commodity is a string specific to the website datahub.io, or stock ticker symbol
    from the websites quandl.com,finance.yahoo.com, or marketstack.com 
    '''
    import urllib.request, urllib.parse, urllib.error
    import requests
    import pandas as pd
    
    # These are seconds after 1970, used to index yahoo finance historical dataset (just go from 1970-2025)
    T1=0 #  1970 
    T2=(2025-1970)*(3600*24*(365)) # approximate number of seconds to 2021 excluding leap years etc close enough to full range

    quandlAPICode='BkxodE_kpxbAszq7rpPn'  # My API code for quandl data
    marketStackAPICode='b0d09a6b303b8533e9f1b0091078fcfb' # My API code for marketstack data
    interval='15min'  # 15min, 30min, 1h (Default), 3h, 6h,
    #interval='1h' # marketstack data interval
    ## setup the data link
    if (source == 'datahub'):
        resourceURL= 'https://datahub.io/core/'+ commodity.folderName + '/r/' + commodity.fileName +'.csv'
        hostname = 'datahub.io'
    elif (source =='quandl'):
        resourceURL = 'https://www.quandl.com/api/v3/datasets/' + commodity.folderName+'/'+commodity.fileName+'.csv?api_key='+quandlAPICode
        hostname = 'www.quandl.com'
    elif (source =='marketstack'):
        resourceURL ='http://api.marketstack.com/v1/'+commodity.folderName+'?access_key='+marketStackAPICode+'&symbols='+commodity.fileName+'&interval='+ interval
        hostname = 'api.marketstack.com'
    elif (source == 'yahoo'):
        resourceURL = "https://query1.finance.yahoo.com/v7/finance/download/"+commodity.fileName+"?period1="+str(T1)+"&period2="+str(T2)+"&interval=1d&events=history&includeAdjustedClose=true"

    if (source == 'datahub' or source =='quandl' or source == 'yahoo' ):
        #https://docs.python.org/3/howto/urllib2.html
        #https://docs.python.org/3/library/urllib.request.html
        try:    
            # Original strategy (based on the course notes)
            #fhand = urllib.request.urlopen(resourceURL)  # open the resource and return a handle
            #read the data into a pandas dataframe
            #data = pd.read_csv(fhand)  # read the data into a pandas file
            #save this as a text file csv in the directory for recall
            #data.to_csv(commodity.folderName+"_"+commodity.fileName +".csv")  # This also writes the header to line 0
            #fhand.close()  # close the connection
            
            ### Alternative strategy 
            #https://docs.python.org/3/library/urllib.request.html
            local_filename, headers = urllib.request.urlretrieve(resourceURL)
            html = open(local_filename)
            data = pd.read_csv(html)
            data.to_csv(commodity.folderName+"_"+commodity.fileName +".csv")  # This also writes the header to line 0
            html.close()

            return data  # return the pandas dataset data
        except urllib.error.HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except urllib.error.URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        
    elif (source == 'marketstack'):
        #https: // marketstack.com/documentation
        api_result = requests.get(resourceURL) # , params)
        api_response = api_result.json()  # convert from json into dict
        ## convert from json to pandas format
        data = pd.DataFrame(api_response['data'])
        #save this as a text file csv in the directory for recall
        data.to_csv(commodity.folderName+"_"+ commodity.fileName +".csv")  # This also writes the header to line 0
        api_result.close()  # close the connection
        #api_response.close() # close the response ( is this even required?)

        ### Alternative strategy   (BROKEN)
        #https://docs.python.org/3/library/urllib.request.html
        #local_filename, headers = urllib.request.urlretrieve(resourceURL)
        #html = open(local_filename)
        #dataIn = html.json()
        ##dataIn = pd.read_json(html)
        #data = pd.DataFame(dataIn['data'])
        #data.to_csv(commodity.folderName+"_"+commodity.fileName +".csv")  # This also writes the header to line 0
        #html.close()
        
        return data  # return the pandas dataset data


def playIntroMenu():
    ''' Play a partial menu to populate the data and ticker on first use'''
    print("Welcome to the Commodity and Stock Market Data Plotter:")
    print("1) Get data from online.")
    print("2) Open Data from file.")
    print("q) Quit Program\n")
    userSelection=input("Please select an Option:\n")
    return userSelection

def playMenu():
    ''' Play the full menu for the user loop in main'''
    print("Welcome to the Commodity and Stock Market Data Plotter:")
    print("1) Get data from online.")
    print("2) Open Data from file.")
    print("3) Plot Data")
    print("4) Show head rows of loaded data")
    print("5) Show tail rows of loaded data")
    print("6) Crop Data")
    print("7) Save Current Data to Disk File")
    print("q) Quit Program\n")
    userSelection=input("Please select an Option:\n")
    return userSelection

def generateMarkStackHourLabels(startDay, endDay, data):
    import numpy as np

    # generate day ticks from startDay to endDay by 1
    hourTicksNP = np.arange(startDay, endDay, 1/24)  # Ticks on the hour
    hourTicks = hourTicksNP.tolist()  # convert the numpy array to a List
    labelList = list()  # make a list for the tick labels

    numTicks = len(hourTicks)  # get the number of ticks

    monthLabels = ["Jan", "Feb", "Mar", "Apr", "May",
                   "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # assume your not in a leap year # we can test for this and fix it if necessary
    daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    startYear = data['Year'].iloc[0]
    # Decide if it is a leap year
    # divisible by 4 (except for years evenly divisible by 100, which are not leap years unless evenly divisible by 400
    if (startYear % 4 == 0 and startYear % 100 != 0 or startYear % 400 == 0):  # if year is leap year
        daysInMonth[1] = 29  # fix the days in february to 29

    oldDay = data['Day'].iloc[0]
    oldMonth = data['Month'].iloc[0]
    # construct the days list

    tickMonth = oldMonth
    tickDay = oldDay

    ## For loop to construct the labelList with month dates
    label = ""
    ### data independent solution purley math based (don't even need to check the data past the first element)
    for k in range(0, numTicks):
        rem = k % 24

        if (k == 0):
            tickMonth = oldMonth
            tickDay = oldDay

        if (k > 0 and rem == 0):  # new day so update the days
            tickDay = (oldDay+1) % daysInMonth[oldMonth-1]
            if(tickDay == 0):
                # markup for non zero index of days
                tickDay = daysInMonth[oldMonth-1]
            if(tickDay == 1):  # you must have rolled over to the next month
                # increment the month and wrap around if necessary
                tickMonth = (oldMonth+1) % 12
                if(tickMonth == 0):  # if it mods to 0 change the month to 12
                    tickMonth = 12  # markup for non zero indexing of months

        ## update the day and month number
        oldDay = tickDay
        oldMonth = tickMonth

        if (rem == 0):
            label = monthLabels[tickMonth - 1] + " " + str(tickDay)+"  /"+ "0"+str(rem)+":00"
        else:
            if(rem < 10):
                label = str(tickDay)+" /"+"0"+str(rem)+":00"
            else:
                label = str(tickDay)+" /"+str(rem)+":00"
        # add the string label for the tick to the list
        labelList.append(label)

    return hourTicks, labelList

def generateMarkStackDayLabels(startDay, endDay, data):
    '''
    Helper function to generate x-axis day labels for dataPlotterPlus if the time scale range is < 1 month
    returns a list of tickmarks and x-axis labels based on the day data category in data which is a pandas dataframe
    '''
    import numpy as np

    # generate day ticks from startDay to endDay by 1
    dayTicksNP = np.arange(startDay, endDay, 1)
    dayTicks = dayTicksNP.tolist()  # convert the numpy array to a List
    labelList = list()  # make a list for the tick labels

    numTicks = len(dayTicks)  # get the number of ticks

    monthLabels = ["Jan", "Feb", "Mar", "Apr", "May",
                   "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # assume your not in a leap year # we can test for this and fix it if necessary
    daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    startYear = data['Year'].iloc[0]
    # Decide if it is a leap year
    # divisible by 4 (except for years evenly divisible by 100, which are not leap years unless evenly divisible by 400
    if (startYear % 4 == 0 and startYear % 100 != 0 or startYear % 400 == 0):  # if year is leap year
        daysInMonth[1] = 29  # fix the days in february to 29

    oldDay = data['Day'].iloc[0]
    oldMonth = data['Month'].iloc[0]
    tickDay = oldDay
    tickMonth = oldMonth
    ## For loop to construct the labelList with month dates
    ### MATH BASED SOLUTION
    label = ""
    for k in range(0, numTicks):
        ### if there is no data in the next tick period the tick day will stay constant
        ### This is an attempt at a bug fix for this problem
        if (k > 0):
            tickDay = (oldDay+1) % daysInMonth[oldMonth-1]
            if(tickDay == 0):
                # markup for non zero index of days
                tickDay = daysInMonth[oldMonth-1]
            if(tickDay == 1):  # you must have rolled over to the next month
                # increment the month and wrap around if necessary
                tickMonth = (oldMonth+1) % 12
                if(tickMonth == 0):  # if it mods to 0 change the month to 12
                    tickMonth = 12  # markup for non zero indexing of months

        # store the oldDay and oldMonth as the new ones calculated
        oldDay = tickDay
        oldMonth = tickMonth
        ## construct the label as Month + day
        label = monthLabels[tickMonth - 1] + " " + str(tickDay)
        #Add the string label for the tick to the list
        labelList.append(label)

    return dayTicks, labelList

def generateDayAxisLabels(data):
    '''
    Helper function to generate x-axis day labels for dataPlotterPlus if the time scale range is < 4 months
    returns a list of tickmarks and x-axis labels based on the day data category in data which is a pandas dataframe
    '''
    labelList=list()  # make a list for the labels
    tickLocations=data['decimal_date'].tolist()  # make ticks at the location of the data
    monthLabels = ["Jan", "Feb", "Mar", "Apr", "May",
                   "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    numTicks=len(tickLocations)

    ## For loop to construct the labelList with days as labels
    label=""
    oldMonth=0
    for k in range(0,numTicks):
        dayNum=data['Day'].iloc[k] # get the day of the year
        monthNum= data['Month'].iloc[k]  # get the month number 
        if ( dayNum==1 or k==0 or monthNum!=oldMonth):  # for the first of the month label the month and the day
            year = data['Year'].iloc[k]
            label = str(dayNum)+"\n\n"+str(year)+" "+monthLabels[monthNum-1]
        else:
            label = str(dayNum)  # otherwise the label is the day 
        oldMonth=monthNum # update to the new month
        labelList.append(label)  # add the string label for the tick to the list
    return tickLocations, labelList

def generateMonthAxisLabels(yearStart,yearEnd):
    '''
    Helper function to generate month axis labels to plot in dataPloterPlus 
    if the time range is shorter than 3 years. returns a list of tickmarks and ticklabels 
    '''
    import numpy as np
    #https: // numpy.org/doc/stable/reference/generated/numpy.arange.html  # numpy.arange
    monthTicksNP=np.arange(yearStart,yearEnd,1/12)   # generate ticks here
    monthTicks=monthTicksNP.tolist()  # convert to a List
    labelList=list()  # make a list for the tick labels

    numTicks = len(monthTicks) #get the number of ticks 
    monthLabels = ["Jan", "Feb", "Mar", "Apr", "May",
                       "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ## For loop to construct the labelList with month dates
    label=""
    for k in range(0,numTicks):
        rem=k%12
        year = yearStart+int(k/12)
        if (rem ==0):
            label=monthLabels[rem]+"\n\n"+str(year)
        else:
            label = monthLabels[rem]

        labelList.append(label)  # add the string label for the tick to the list
    return monthTicks, labelList

def dataPlotterPlus(data, xCol: str, yCol: str, xLab: str, yLab: str, newTicker: commoData, smaDays: int, smaBool: bool, logBool:bool):
    '''Plot the completed dataset as inputed, this version allows for direct selection of the 
       variables and their xlabel and ylabel strings.
    '''
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter

    fig1 = plt.figure(figsize=(16, 10))
    plt.title(newTicker.folderName+'/'+newTicker.fileName,fontsize=18, fontweight='bold')
    plt.xlabel(xLab, fontsize=14, fontweight='bold')  # xlabel
    plt.ylabel(yLab, fontsize=14, fontweight='bold')  # ylabel
    plt.grid('both')  # grid on

    nRows = int(len(data.index))  # get the number of data rows
    ax = plt.gca()  # get the axis of the current plot

    #https://stackoverflow.com/questions/773814/plot-logarithmic-axes-with-matplotlib-in-python
    # set y-axis to logarithmic scale if user requests
    if(logBool):
        ax.set_yscale('log')


    #https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
    yearStart = int(data['decimal_date'].iloc[0])
    yearEnd = int(data['decimal_date'].iloc[nRows-1]) + 1 # make data up to the next year
    # width in years of the data
    maxYears = int(data['decimal_date'].iloc[nRows-1]-data['decimal_date'].iloc[0])

    if (maxYears > 3):
        #### format the x axis with this many digits (Just plot years)
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))   
        plt.plot(data[xCol], data[yCol], '-k')  # plot the data
        if (smaBool):
            # plot the data with 30 day SMA
            plt.plot(data[xCol], data[yCol].rolling(smaDays).mean(), '-r')
            plt.legend([newTicker.fileName, str(smaDays)+" day SMA"], fontsize=16)
        else:
            plt.legend([newTicker.fileName], fontsize=16)

    elif (maxYears < 3 and maxYears>1):
        monthTicks,labelList=generateMonthAxisLabels(yearStart, yearEnd)
        ## SET XTICK LABELS
        ax.set_xticks(monthTicks, minor=False)
        ax.set_xticklabels(labelList, rotation=40)

        plt.plot(data[xCol], data[yCol], '-k')  # plot the data
        if (smaBool):
            plt.plot(data[xCol], data[yCol].rolling(smaDays).mean(),'-r')  # plot the data with 30 day SMA
            plt.legend([newTicker.fileName, str(smaDays)+" day SMA"], fontsize=16)
        else:
            plt.legend([newTicker.fileName], fontsize=16)
    else:  
        # if less than a year of data is to be plotted
        # compute dMonths
        dMonths = data['Month'].iloc[nRows-1]-data['Month'].iloc[0]
        #print("Dmonths =",dMonths)
        if(dMonths>3):
            monthTicks, labelList = generateMonthAxisLabels(yearStart, yearEnd)
            ## SET XTICK LABELS
            ax.set_xticks(monthTicks, minor=False)
            ax.set_xticklabels(labelList, rotation=40)
            plt.plot(data[xCol], data[yCol], '-k')  # plot the data
            if (smaBool):
                plt.plot(data[xCol], data[yCol].rolling(smaDays).mean(),'-r')  # plot the data with 30 day SMA
                plt.legend([newTicker.fileName, str(smaDays)+" day SMA"], fontsize=16)
            else:
                plt.legend([newTicker.fileName], fontsize=16)
        else:
            # overide and plot by decimal_date but make labels by day and month
            tickLocations, labelList = generateDayAxisLabels(data)
            ## SET XTICK LABELS
            ax.set_xticks(tickLocations, minor=False)
            ax.set_xticklabels(labelList, rotation=40)
            plt.plot(data[xCol], data[yCol], '-k')  # plot the data
            if (smaBool):
                # plot the data with 30 day SMA
                plt.plot(data[xCol], data[yCol].rolling(smaDays).mean(), '-r')
                plt.legend([newTicker.fileName, str(
                    smaDays)+" day SMA"], fontsize=16)
            else:
                plt.legend([newTicker.fileName], fontsize=16)

    ### work on something similar if dMonths is small
    ### if years > 5 only plot the year
    ### if years < 5 and years >1  plot months with yearly Jan 2000 Feb, ....Jan 2001 Feb Mar....
    ### if dMonths < 4 , print the days with Month index
    
    ### Set the plot limits
    # Set this to be the decimal degree limits
    ### you could use this to zoom / scale the data ranges for zooms
    xL_lim = data[xCol].iloc[0]  # First data point for decimal date
    # Last data point for decimal date
    xU_lim = data[xCol].iloc[nRows-1]
    ax.set_xlim(xL_lim, xU_lim)  # set to the full data range
    #ax.set_ylim(yL_lim,yU_lim)  # let the y value follow the data (let the plot take care of this)

    plt.show()
    return

def dataPlotterMarketStack(data, xCol: str, yCol: str, xLab: str, yLab: str, newTicker: commoData, smaDays: int, smaBool: bool, logBool:bool):
    ''' Specialize plot utility for short time scale data from market stack (2 weeks - 1 day)
       plots the x-axis with the month and day labels if time range is between 1-month to 4 days
       plots the day and the hour on the x-axis if the time range is < 4 days.  
    '''
    import matplotlib.pyplot as plt

    fig1 = plt.figure(figsize=(16,10))
    #plt.title(newTicker.folderName+'/'+newTicker.fileName, fontsize=18, fontweight='bold')
    plt.xlabel(xLab,fontsize=14,fontweight='bold') # xlabel
    plt.ylabel(yLab,fontsize=14,fontweight='bold')  # ylabel
    plt.grid('both')  # grid on 
    ax = plt.gca()  # get the axis of the current plot

    #https://stackoverflow.com/questions/773814/plot-logarithmic-axes-with-matplotlib-in-python
    # set y-axis to logarithmic scale if user requests
    if(logBool):
        ax.set_yscale('log')

    ## I have made new columns decimal_day and decimal_date
    ## the data is usually 5-14 days long  so if it's greater than 5 days, only label the day at the start of the day
    #  If the data is < 3 days long label the hours 

    nRows = int(len(data.index)) # get the number of data rows

    startDay= int(data['decimal_day'].iloc[0]) # the lowest whole number decimal day
    endDay =  int(data['decimal_day'].iloc[nRows-1]) +1 # the largest whole number decimal day
    numDays = int(data['decimal_day'].iloc[nRows-1]-data['decimal_day'].iloc[0])  # the approximate amount of days in the data

    if (numDays > 4):
        tickLocations, labelList=generateMarkStackDayLabels(startDay, endDay, data)
        ## SET XTICK LABELS
        ax.set_xticks(tickLocations, minor=False)
        ax.set_xticklabels(labelList, rotation=40)
        ##### PERFORM DATA PLOTS
        plt.plot(data[xCol], data[yCol], '-k') # plot the data 
        if (smaBool):
            plt.plot(data[xCol], data[yCol].rolling(smaDays).mean(), '-r')  # plot the data with 30 day SMA
            plt.legend([newTicker.fileName,str(smaDays)+" day SMA"],fontsize=16)
        else:
            plt.legend([newTicker.fileName], fontsize=16)
    else:
        tickLocations, labelList = generateMarkStackHourLabels(startDay, endDay, data)
        ## SET XTICK LABELS
        ax.set_xticks(tickLocations, minor=False)
        ax.set_xticklabels(labelList, rotation=40)
        ##### PERFORM DATA PLOTS
        plt.plot(data[xCol], data[yCol], '-k')  # plot the data
        if (smaBool):
            # plot the data with 30 day SMA
            plt.plot(data[xCol], data[yCol].rolling(smaDays).mean(), '-r')
            plt.legend([newTicker.fileName, str(
                smaDays)+" day SMA"], fontsize=16)
        else:
            plt.legend([newTicker.fileName], fontsize=16)

    ### Set the plot limits/ Restore the plot limits to the data ranges
    # Set this to be the decimal degree limits
    ### you could use this to zoom / scale the data ranges for zooms
    xL_lim = data[xCol].iloc[0]  # First data point for decimal day
    # Last data point for decimal day
    xU_lim = data[xCol].iloc[nRows-1]
    ax.set_xlim(xL_lim, xU_lim)  # set to the full data range
    #ax.set_ylim(yL_lim,yU_lim)  # let the y value follow the data (let the plot take care of t

    ## Placed Here to add the Year back into the title
    plt.title(newTicker.folderName+'/'+newTicker.fileName + " Year: "+ str(data['Year'].iloc[0]),
              fontsize=18, fontweight='bold')

    plt.show()
    return


def dataPlotter(data, newTicker:commoData, smaDays:int, smaBool:bool, logBool:bool):
    '''Plot the completed dataset as inputed
    dataPlotter(data,newTicker:commoData, kday:int, smaBool:bool)
    '''
    import matplotlib.pyplot as plt

    fig1 = plt.figure(figsize=(16,10))
    plt.title(newTicker.folderName+'/'+newTicker.fileName, fontsize=18, fontweight='bold')
    plt.xlabel('Date',fontsize=14,fontweight='bold') # xlabel
    plt.ylabel('Price [$]',fontsize=14,fontweight='bold')  # ylabel
    plt.grid('both')  # grid on 

    ax=plt.gca()
    #https://stackoverflow.com/questions/773814/plot-logarithmic-axes-with-matplotlib-in-python
    # set y-axis to logarithmic scale if user requests
    if(logBool):
        ax.set_yscale('log')

    plt.plot(data['decimal_date'], data['Price'], '-k') # plot the data 
    if (smaBool):
        plt.plot(data['decimal_date'], data['Price'].rolling(smaDays).mean(), '-r')  # plot the data with 30 day SMA
        plt.legend([newTicker.fileName,str(smaDays)+" day SMA"],fontsize=16)
    else:
        plt.legend([newTicker.fileName], fontsize=16)

    plt.show()
    return

def createTicker():
    '''Interactively ask the user to create a commoData object
       consisting of the folder where the data comes from
       and the ticker symbol
       newTicker=commoData(folderName,tickerName)
       newTicker=createTicker() 
    '''
    source=input("Enter Data Source (quandl,datahub,marketstack,yahoo):\n")
    tickerSymbol=input("Enter Stock Ticker (e.g. MSFT):\n")
    sourceFolder=input("Enter Data Source Folder(eg. EOD,eod,intraday):\n")
    commodity=commoData(sourceFolder,tickerSymbol)
    return commodity,source

def getPlotOptions():  # get some plotting options
    ''' Asks the user if they want to plot a SMA on the data plot
        if so, asks the user for the length in days of the SMA
        if not returns (1,false)
        if so return (SMAdays,True)
        also prompts for y-log scale 
        SMAdays,SMAbool,logBool=getPlotOptions()
        '''      

    userResponse=input("Would you like the Y-axis to be in logarimic scale?:Y/N\n")
    if (userResponse == 'Y' or userResponse == 'y' or userResponse.lower() == 'yes'):
        logBool=True
    else:
        logBool=False

    userResponse=input("Would you like to plot a Simple Moving Average (SMA):Y/N\n")
    if (userResponse=='Y' or userResponse=='y' or userResponse.lower()=='yes'):
        SMAbool=True
        SMAdays = input("How many days are in the rolling SMA?:\n")
        if (int(SMAdays)>=1):
            return int(SMAdays),SMAbool,logBool
        else:
            SMAdays=7 # 7 day moving average
            return  SMAdays,SMAbool,logBool
    else: 
        SMAbool=False
        return 1,SMAbool,logBool
    
def openFileFromDisk():
    ''' Prompts the User for a File Name, 
        opens the csv file and returns it as a pandas data frame
        data = openFileFromDisk()
    '''

    import pandas as pd
    fileName=input("Enter the filename:\n")
    try:
        fhand = open(fileName,'r') #open the file for reading
        data = pd.read_csv(fhand) # use pandas to import the csv file from disk
        return data 
    except:
        print("The file "+fileName+" could not be openned for reading.")
        return None   

def reformatQuandlInputData(data):
    ''' Take the data with string dates and turn them into numbers
    and return a pandas dataframe with the new columns inserted 
    make a smaller data frame with integer dates, float decimal date and 
    a subset of the original data values (loads and plots faster)
    '''
    import pandas as pd
    import numpy as np
    
    dateList1 = data['Date'].values  # these are all datetime64 objects of the date
    integerDates = list()  # make a new list to hold the integer vector of the date
    floatDates = list()  # make a list to store the floating point date
    yearList = list()  # make a list for the year column
    monthList = list()  # make a list for the month column 
    dayList = list() # make a list for the day column

    for item in dateList1:
        # split the date string
        date2string= np.datetime_as_string(item, unit='D')
        strSplit = date2string.split('-', -1)
        ## convert the date into integers for year month and day, then add to their own lists
        strSplit[0] = int(strSplit[0])
        yearList.append(strSplit[0])
        strSplit[1] = int(strSplit[1])
        monthList.append(strSplit[1])
        strSplit[2] = int(strSplit[2])
        dayList.append(strSplit[2])
        integerDates.append(strSplit)
        decimalDate = strSplit[0]+(strSplit[1]-1)/12 + strSplit[2]/365  # sloppy but will get the job done
        floatDates.append(decimalDate)  # add the decimal
    
    dataNew = pd.DataFrame({'Year': yearList, 'Month': monthList,'Day': dayList, 'decimal_date': floatDates,\
        'Open': data['Open'].values, 'High': data['High'], 'Low': data['Low'], 'Close':data['Close'],'Volume':data['Volume'] })
    return dataNew

def reformatGrabberInputData(data,source:str):
    ''' Take the data with string dates and turn them into numbers
    and return a pandas dataframe with the new columns inserted 
    make a smaller data frame with integer dates, float decimal date and 
    a subset of the original data values (loads and plots faster)
    '''
    import pandas as pd
    import numpy as np
    from datetime import datetime

    dateList1 = data['Date'].values  # these are all strings of the date
    integerDates = list()  # make a new list to hold the integer vector of the date
    floatDates = list()  # make a list to store the floating point date
    yearList = list()  # make a list for the year column
    monthList = list()  # make a list for the month column
    dayList = list()  # make a list for the day column

    for item in dateList1:
        # split the date string
        #date2string = item  # is already in string format
        strSplit = item.split('-', -1)
        ## convert the date into integers for year month and day, then add to their own lists
        strSplit[0] = int(strSplit[0])
        yearList.append(strSplit[0])
        strSplit[1] = int(strSplit[1])
        monthList.append(strSplit[1])
        strSplit[2] = int(strSplit[2])
        dayList.append(strSplit[2])
        integerDates.append(strSplit)
        decimalDate = strSplit[0]+(strSplit[1]-1)/12 + strSplit[2]/365  # sloppy but will get the job done
        floatDates.append(decimalDate)  # add the decimal

    if (source=='quandl'):
        dataNew = pd.DataFrame({'Year': yearList, 'Month': monthList, 'Day': dayList, 'decimal_date': floatDates,
                            'Open': data['Open'], 'High': data['High'], 'Low': data['Low'], 'Close': data['Close'], 'Volume': data['Volume']})
        return dataNew
    elif(source=='datahub'):
        dataNew = pd.DataFrame({'Year': yearList, 'Month': monthList, 'Day': dayList, 'decimal_date': floatDates,'Price': data['Price']})
        return dataNew
    elif (source=='yahoo'):
        dataNew = pd.DataFrame({'Year': yearList, 'Month': monthList, 'Day': dayList, 'decimal_date': floatDates,
                            'Open': data['Open'], 'High': data['High'], 'Low': data['Low'], 'Close': data['Close'],'Adj_Close': data['Adj Close'], 'Volume': data['Volume']})
        return dataNew

## for market stack data 
def reformatMarketStackInputData(data, folder:str):
    ''' Take the data with string dates and turn them into numbers
    and return a pandas dataframe with the new columns inserted 
    make a smaller data frame with integer dates, float decimal date and 
    a subset of the original data values (loads and plots faster)
    '''
    import pandas as pd
    import numpy as np
    from datetime import datetime

    dateList1 = data['date'].values  # these are all strings of the date
    integerDates = list()  # make a new list to hold the integer vector of the date
    floatDates = list()  # make a list to store the floating point date
    yearList = list()  # make a list for the year column
    monthList = list()  # make a list for the month column
    dayList = list()  # make a list for the day column
    hourList = list() # make a list column for the hour of the ticker
    minuteList = list() # make a column for the minute of the ticker 
    decimalDayList = list() # make a column for day hour
    for item in dateList1:
        # split the date string
        #date2string = item  # is already in string format
        strSplit = item.split('-', -1)
        ## convert the date into integers for year month and day, then add to their own lists
        strSplit[0] = int(strSplit[0])
        yearList.append(strSplit[0])
        strSplit[1] = int(strSplit[1])
        monthList.append(strSplit[1])
        timeSplit=strSplit[2].split('T',-1)[1].split(':',-1) # split off the time
        strSplit[2] = int(strSplit[2].split('T', -1)[0])  # day
        dayList.append(int(strSplit[2]))
        hourList.append(int(timeSplit[0]))
        minuteList.append(int(timeSplit[1]))
        # add hour minute second to dataOut frame , then calculate decDate as
        decimalDate = int(strSplit[0])+int(strSplit[1]-1)/12 + int(strSplit[2])/(365)+int(timeSplit[0])/(24*365)\
            + int(timeSplit[1])/(60*24*365)  # should work down to the minute rework for seconds and miliseconds if necessary
        integerDates.append(strSplit)
        floatDates.append(decimalDate)  # add the decimal
        ## add decimal day for short time windows of data
        decimalDay = 365*int(strSplit[1]-1)/12+int(strSplit[2])+int(timeSplit[0])/24+int(timeSplit[1])/(24*60)
        decimalDayList.append(decimalDay)

    if (folder == "intraday"):    
        dataNew = pd.DataFrame({'Year': yearList, 'Month': monthList, 'Day': dayList, 'Hour':hourList,'Minute':minuteList,'decimal_date': floatDates, 'decimal_day':decimalDayList,\
                                'Last': data['last'].values,'Open': data['open'].values, 'High': data['high'], 'Low': data['low'], 'Close': data['close'], 'Volume': data['volume']})
        return dataNew.sort_values(by='decimal_date', ascending=True)
    elif(folder == "eod"):
        dataNew = pd.DataFrame({'Year': yearList, 'Month': monthList, 'Day': dayList, 'Hour': hourList, 'Minute': minuteList, 'decimal_date': floatDates, 'decimal_day': decimalDayList,
                                'Open': data['open'].values, 'High': data['high'], 'Low': data['low'], 'Close': data['close'], 'Volume': data['volume']})
        return dataNew.sort_values(by='decimal_date', ascending=True)

def clearScreen():
    import os
    if (os.name == 'nt'): # for Windows NT systems
        os.system('cls')
    else:  # for unix/linux systems
        os.system('clear')


############################## MAIN PROGRAM FILE ############################################################
def main_program():
    import pandas as pd
    source = 'quandl'  # this can be modified to another data vendor like datahub
    data=pd.DataFrame([]) # point to Null
    newTicker=commoData("NULL","NULL")

    clearScreen()# clear the terminal on restart 
    ### play the menu
    response=playIntroMenu()
    ### first run has no data handle this and get data or quit
    if (response == '1'):
        newTicker,source = createTicker()  # Ask the user for the ticker info
        # download the data set selected by the user
        try:
            dataIn = grabData(newTicker, source)
            if (source == 'quandl' or source == 'datahub' or source=='yahoo'):
                data = reformatGrabberInputData(dataIn, source).sort_values(by='decimal_date', ascending=True)  # fix up the data for plotting
            elif(source == 'marketstack'):    
                data = reformatMarketStackInputData(dataIn,newTicker.folderName).sort_values(by='decimal_date',ascending=True)
        except:
            print("Data could not be retrieved. Try again")
            pass
    elif (response == '2'):
        try:
            dataIn = openFileFromDisk()  # open the data file from disk
            newTicker,source = createTicker()  # Ask the user for the ticker info
            if (source == 'quandl' or source == 'datahub' or source == 'yahoo'):
                data = reformatGrabberInputData(dataIn, source).sort_values(by='decimal_date', ascending=True)   # fix up the data for plotting
            elif(source == 'marketstack'):
                data = reformatMarketStackInputData(dataIn,newTicker.folderName).sort_values(by='decimal_date',ascending=True)  
        except:
            print("Data could not be Loaded. Try again")
            pass  # return to loop start
   
    elif (response == 'q' or response == 'Q'):
        print("Thanks for playing, see you later!\n")
        quit()  # exit the program
    else:
        print("Bad selection. Try again.\n")

    response='Y' # set this to enter the loop  
   #### Menu Loop to open/grab/plot data
    while (response != 'q' and response != 'Q'): # changed from while True, could not seem to break the loop (bug)
        ### play the menu
        response=playMenu()
        if (response == '1'):
            clearScreen()  # clear the terminal on each return to the Menu from plotting   
            newTicker, source = createTicker()  # Ask the user for the ticker info
            try:
                dataIn=grabData(newTicker,source) # download the data set selected by the user
                if (source == 'quandl' or source == 'datahub' or 'yahoo'):
                    data = reformatGrabberInputData(dataIn, source).sort_values(by='decimal_date', ascending=True)  # fix up the data for plotting
                elif(source == 'marketstack'):    
                    data = reformatMarketStackInputData(dataIn,newTicker.folderName).sort_values(by='decimal_date',ascending=True)
            except:
                print("Data could not be retrieved. Try again.")
                print(newTicker.fileName,newTicker.folderName,source)
            continue
        elif (response == '2'):
            try:
                dataIn=openFileFromDisk()  # open the data file from disk
                newTicker,source = createTicker()  # Ask the user for the ticker info 
                if (source == 'quandl' or source == 'datahub' or source == 'yahoo' ):
                    data = reformatGrabberInputData(dataIn, source).sort_values(by='decimal_date', ascending=True)  # fix up the data for plotting
                elif(source == 'marketstack'):    
                    data = reformatMarketStackInputData(dataIn,newTicker.folderName).sort_values(by='decimal_date',ascending=True)
            except:
                print("Data could not be loaded.Try again")
                print(newTicker.fileName, newTicker.folderName, source)
                continue
   
        elif (response == '3'):
            ## we assume that the data already exists from step 1 or 2 above 
            SMAdays,SMABool,logBool = getPlotOptions()  # get some plotting options 
            dataOut = applyDateRange(data) # Ask user if they want to plot a range of data
            #clearScreen()  # clear the terminal on each return to the Menu from plotting 

            if (source == 'quandl' or source == 'yahoo'):      
                try:
                    dataPlotterPlus(dataOut,'decimal_date','Close','Date', 'Price [$]', newTicker, SMAdays, SMABool,logBool)
                except:
                    print("Some Plotting Parameter is Wrong. Investigate and Try again.")
                    continue
            elif(source == 'datahub'):
                try:
                    # dataPlotter(dataOut, newTicker, SMAdays, SMABool) # deprecated
                    dataPlotterPlus(dataOut,'decimal_date','Price','Date','Price [$]',newTicker,SMAdays,SMABool,logBool)
                except:
                    print("Some Plotting Parameter is Wrong. Investigate and Try again.")
                    continue
            elif (source =='marketstack' and newTicker.folderName == 'intraday'):
                try:
                    dataPlotterMarketStack(dataOut,'decimal_day','Last','Date','Price [$]',newTicker,SMAdays,SMABool,logBool)
                except:
                    print("Some Plotting Parameter is Wrong. Investigate and Try again.")
                    continue
            elif (source =='marketstack' and newTicker.folderName == 'eod'):
                try:
                    dataPlotterPlus(dataOut,'decimal_date','Close','Date','Price [$]',newTicker,SMAdays,SMABool,logBool)
                except:
                    print("Some Plotting Parameter is Wrong. Investigate and Try again.")
                    continue
        elif (response == '4'):
            ## we assume that the data already exists from step 1 or 2 above
            clearScreen()
            print(data.head())  # This has stopped working
            #print("There should be data rows from head here!")
        elif (response == '5'):
            ## we assume that the data already exists from step 1 or 2 above
            clearScreen()
            print(data.tail())  # This has stopped working....
            #print("There should be data rows from tail here!")
        elif(response == '6'):
            clearScreen()  # clear the terminal on each return to the Menu from plotting 
            print("Data clipping will overwrite the current dataset!!") 
            print("This will return a crop of the original data for plotting or saving to disk")
            # Ask user if they want to plot a range of data
            data = applyDateRange(data)      
        elif(response == '7'):
            ### save the dataFrame to a csv file (usefull after data crop)
            clearScreen()
            fileOutName = input("Enter a filename to save:\n")     
            data.to_csv(fileOutName)
            print(fileOutName + " was saved to disk.")
        elif (response == 'q' or response == 'Q'):
            break
        else:
            print("Bad selection. Try again.\n")

    print("Out of the Loop...Exiting Program")  # This works now
    print("Thanks for playing, see you later!\n")
    return True
################################  END OF MAIN PROGRAM #####################################



############################## DEPRECATED #############################################################

## This is now handled in main
def handleIntroUserSelection(response):  
    if (response == '1'):
        commodity,source=dataOptions()#  show the options     
        data =grabData(commodity,source) # download the data set selected by the user
        return data,commodity
    elif (response == '2'):
        data=openFileFromDisk()  # open the data file from disk
        return data
    elif (response == 'q' or response == 'Q'):
        print("Thanks for playing, see you later!\n")
        quit() # exit the program
    else:
        print("Bad selection. Try again.\n")

### This is now handled in main
def handleUserSelection(response, data):  
    if (response == '1'):
        commodity=dataOptions()#  show the options     
        data=grabData(commodity) # download the data set selected by the user
        return data
    elif (response == '2'):
        data=openFileFromDisk()  # open the data file from disk
        return data
    elif (response == '3'): 
        kday,smaBool=getPlotOptions()       
        dataPlotter(data)
        return data
    elif (response == 'q' or response == 'Q'):
        print("Thanks for playing, see you later!\n")
        quit() # exit the program
    else:
        print("Bad selection. Try again.\n")

### No longer required (project switched to Quandl data)
def dataOptions():
    print("The following data sources are available:\n")
    print("0) Stock Ticker")
    print("1) Natural Gas.")
    print("2) West Texas Intermediate (WTI).")
    print("3) Brent Crude")
    print("4) Gold ")
    print("5) 10 Year T-bill")
    print("6) S&P 500")
    userSelection = input("Please select an Option:\n")
    if (userSelection == "0"):
        tickerSymbol = input("Enter Stock Ticker:\n")
        sourceFolder = input("Enter Quandl Data Source Folder:\n")
        commodity = commoData(sourceFolder, tickerSymbol)
        return commodity, "quandl"
    if (userSelection == "1"):
        commodity = commoData("natural-gas", "daily")
        return commodity, "datahub"
    elif (userSelection == "2"):
        commodity = commoData("oil-prices", "wti-daily")
        return commodity, "datahub"
    elif (userSelection == "3"):
        commodity = commoData("oil-prices", "brent-daily")
        return commodity, "datahub"
    elif (userSelection == "4"):
        commodity = commoData("gold-prices", "monthly")
        return commodity, "datahub"
    elif (userSelection == "5"):
        commodity = commoData("bond-yields-us-10y", "monthly")
        return commodity, "datahub"
    elif (userSelection == "6"):
        commodity = commoData("s-and-p-500", "data")
        return commodity, "datahub"
    else:
        print("Bad selection, please try again!\n")
        return

############################################ END OF FILE #################################################
