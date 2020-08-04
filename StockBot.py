import time
from bs4 import BeautifulSoup
import requests
import robin_stocks as r


#webscrapes a list of pre-filtered stocks
website = requests.get("https://www.marketwatch.com/tools/stockresearch/screener/results.asp?submit=Screen&Symbol=true&Symbol=false&ChangePct=true&ChangePct=false&FiftyTwoWeekLow=false&CompanyName=true&CompanyName=false&Volume=true&Volume=false&PERatio=false&Price=true&Price=false&LastTradeTime=false&MarketCap=false&Change=true&Change=false&FiftyTwoWeekHigh=false&MoreInfo=true&MoreInfo=false&SortyBy=Symbol&SortDirection=Ascending&ResultsPerPage=OneHundred&TradesShareEnable=true&TradesShareMin=&TradesShareMax=5&PriceDirEnable=true&PriceDir=Up&PriceDirPct=1&LastYearEnable=false&LastYearAboveHigh=&TradeVolEnable=false&TradeVolMin=&TradeVolMax=&BlockEnable=false&BlockAmt=&BlockTime=&PERatioEnable=false&PERatioMin=&PERatioMax=&MktCapEnable=false&MktCapMin=&MktCapMax=&MovAvgEnable=false&MovAvgType=Outperform&MovAvgTime=FiftyDay&MktIdxEnable=false&MktIdxType=Outperform&MktIdxPct=&MktIdxExchange=&Exchange=All&IndustryEnable=false&Industry=Accounting");
soup = BeautifulSoup(website.text, features="html.parser");

bank = 30.00; #Amount of money given to the bot
ownedStocks = []; #holds the stocks

#login = r.login('EMAIL','PASSWORD');

intro = '''
______          _____             _           
|  _  \        |_   _|           | |                    
| | | |__ _ _   _| |_ __ __ _  __| | ___ _ __           Jack Roth
| | | / _` | | | | | '__/ _` |/ _` |/ _ \ '__|          Version 1.0
| |/ / (_| | |_| | | | | (_| | (_| |  __/ |   
|___/ \__,_|\__, \_/_|  \__,_|\__,_|\___|_|   
             __/ |                            
            |___/                            
''';








print(intro);
stockLog = open("stockLog.txt", "a+");
stockLog.write(intro);





#parses ownedStocks object to return the symbol for the stock
def parseABRV(stock):
    firstSpace = stock.find(" ");
    return stock[0:firstSpace].strip();

#parses owneStocks object to return the percent increase it was bought at
def parsePERC(stock):
    if(stock.find("+") != -1):
        firstSpace = stock.find("+") + 1;
    else:
        firstSpace = stock.find("-") + 1;

    return stock[firstSpace:len(stock) - 1].strip();

   


i = 1;
#buying stocks (100 because the website pulls 100 stocks) 
while(i < 101):

    #grabbing stock info & time
    t = time.strftime("%H:%M:%S")
    stockABRV = soup.find_all(class_="results")[1].find_all("tr")[i].find_all("td")[0].get_text();
    stockPRICE = soup.find_all(class_="results")[1].find_all("tr")[i].find_all("td")[2].get_text();
    stockPercent = soup.find_all(class_="results")[1].find_all("tr")[i].find_all("td")[4].get_text();
    stockinfo = stockABRV + " " + stockPRICE + " " + stockPercent;
    i = i + 1;

    #checks stock name for possiblity "." character doesnt work for robinhood API
    if(stockABRV.find(".") != -1):
        print("Skipping stock...");
        stockLog.write("Skipping stock...\n");
        continue;
        i = i + 1;


    #buys the stocks that are less than $2.00 and makes sure it doesn't go over spending limit
    if(float(stockPRICE) < 2.00 and (bank - float(stockPRICE)) >= 0):
        #r.order_buy_market(stockABRV, 1)
        print(t + " Purchased " + stockABRV + " for $" + stockPRICE + "!");
        stockLog.write(t + " Purchased " + stockABRV + " for $" + stockPRICE + "!\n");
        bank = bank - float(stockPRICE);
        ownedStocks.append(stockinfo);



#prints out gathered information
print(); stockLog.write("\n");
print(ownedStocks); stockLog.write(str(ownedStocks)); stockLog.write("\n");
print(len(ownedStocks)); stockLog.write(str(len(ownedStocks))); stockLog.write("\n");
print('${:.2f}'.format(bank)); stockLog.write('${:.2f}'.format(bank) + "\n");
print(); stockLog.write("\n");


#checks the hour you want to stop selling
sellTime = time.strftime("%H");

#Checking to Sell (stops selling at 3pm)
while(sellTime != "15"):
    for items in ownedStocks:

        #sets up robinhood webscrape for new stock percentage increase
        sellTime = time.strftime("%H");
        t = time.strftime("%H:%M:%S");
        stockName = parseABRV(items);
        robinhood = requests.get("https://robinhood.com/stocks/" + stockName);
        rSoup = BeautifulSoup(robinhood.text, features="html.parser");

        #grabs the new percent increase an parses it into a float
        newPercent = rSoup.find(class_="app").find_all("div")[2].find(class_="main-container").find_all(class_="row")[0].find(class_="_3ZzTswmGTiUT4AhIhKZfZh").find(class_="_3KzhutxW7_10wig2fh5mA6").find(class_="_27rSsse3BjeLj7Y1bhIE_9").find_all("span")[0].get_text();
        firstIndex = newPercent.find("(");
        lastIndex = newPercent.find(")");
        posNeg = newPercent[firstIndex + 1: firstIndex + 2]; #grabs the sign in front +/-
        newPercent = newPercent[firstIndex + 2: lastIndex - 1]; #parses the percentage and gets ("##.##");

        #grabs old percent and ABRV to compare for the sell
        oldPercent = parsePERC(items);
        ABRV = parseABRV(items);


        #sells if the new percent is + and the difference of the new stock % inc and old stock % are >= 1%
        if(posNeg == "+" and (float(newPercent) - float(oldPercent)) >= 1):
            #r.order_sell_market(ABRV, 1);  
            percInc = float(newPercent) - float(oldPercent);
            print("SOLD! " + ABRV + " for a " + str(percInc) + "%" + " increase!");
            stockLog.write("SOLD! " + ABRV + " for a " + str(percInc) + "%" + " increase!\n");
            ownedStocks.remove(items);
        else:   
            print(t + " Holding " + ABRV + " until a 1%" + " increase...");
            stockLog.write(t + " Holding " + ABRV + " until a 1%" + " increase...\n");


#prints the leftover stocks
print(ownedStocks); 
stockLog.write(str(ownedStocks));
    
    





    






