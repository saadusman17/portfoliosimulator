import datetime
import pprint
import datetime
import random
import matplotlib.pyplot as plt

pp = pprint.PrettyPrinter(indent=4)

shares = [{"ShareName":"VAS", "Price":10, "DividendYield": 2, "FrankingLevel": 70, "DividendsPerYear":4, "Allocation":50}, 
{"ShareName":"AFI", "Price":25, "DividendYield":4, "FrankingLevel":100, "DividendsPerYear":4, "Allocation":50}]

portfolioTarget = 1000000
MonthlyInvestment = 3000
growthRate = 6 #Including dividends

portfolioLots = []
portfolioSummary = {}

portfolio = 0
date = datetime.datetime.now()

for share in shares:
    portfolioSummary[share["ShareName"]] = 0
    
iteration_counter = 0

dates = [] #for plotting
portfolioValues = [] #for plotting

while portfolio < portfolioTarget:
    
    #Each iteration of this loop will add one month's investments
    sum_of_allocations = 0 
    for share in shares:
        this_share_allocation = share["Allocation"]
        this_share_available_money = MonthlyInvestment * this_share_allocation/float(100)
        buying_price = share["Price"]
        position = this_share_available_money/buying_price

        #Allocation sanity check
        sum_of_allocations += share["Allocation"]

        portfolioLots.append({"Date": date, "ShareName": share["ShareName"], "BuyingPrice": buying_price, "Position": position})
        portfolioSummary[share["ShareName"]] += position
    assert(sum_of_allocations == 100)

    #Dividend payment and reinvestment
    for share in shares:
        if(date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
            print("Yay!! DividendTime")
            dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
            reinvestment_price = share["Price"] - dividend_value_per_share
            shares_repurchased = dividend_value_per_share * portfolioSummary[share["ShareName"]] / reinvestment_price
            portfolioLots.append({"Date": date, "ShareName": share["ShareName"], "BuyingPrice": reinvestment_price, "Position": shares_repurchased})
            share["Price"] = reinvestment_price
            portfolioSummary[share["ShareName"]] += shares_repurchased

    portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
    for share in shares:
        share["Price"] += (share["Price"] * growthRate/float(12)/100)
        portfolio += share["Price"] * portfolioSummary[share["ShareName"]]
    print(date, portfolio)
    dates.append(date)
    portfolioValues.append(portfolio)

    #Adding date and portfolio to arrays to be plotted later

    #Month has now passed, updating dates
    date += datetime.timedelta(days=35)
    date = datetime.datetime(date.year, date.month, 1)

    iteration_counter += 1

# plot
plt.plot(dates,portfolioValues)
# beautify the x-labels
plt.gcf().autofmt_xdate()

plt.show()

# exit()
# pp.pprint("Lots:")    
# pp.pprint(portfolioLots)
# pp.pprint("PortfolioValue:")    
# pp.pprint(portfolio)
# pp.pprint("PortfolioSummary:")    
# pp.pprint(portfolioSummary)
# pp.pprint("Shares Situation:")    
# pp.pprint(shares)

#Need to redraw money from portfolio

yearly_withdrawal_amount = 60000
monthly_withdrawal_amount = yearly_withdrawal_amount/float(12)
withdrawal_months = 12*100 #100 years
withdrawal_percent = 4

for i in range(0, withdrawal_months):
    pass #to be done