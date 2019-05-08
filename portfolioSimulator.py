import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)

shares = [{"ShareName":"VAS", "Price":10, "DividendYield": 2, "FrankingLevel": 70, "DividendsPerYear":4, "Allocation":50}, 
{"ShareName":"AFI", "Price":25, "DividendYield":4, "FrankingLevel":100, "DividendsPerYear":4, "Allocation":50}]

portfolioTarget = 100000
MonthlyInvestment = 1000
growthRate = 6

portfolioLots = []
portfolioSummary = {}

portfolio = 0
date = datetime.datetime.now()

for share in shares:
    portfolioSummary[share["ShareName"]] = 0
    

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

    #Month has now passed, calculating updated values
    date += datetime.timedelta(days=35)
    date = datetime.datetime(date.year, date.month, 1)

    portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
    for share in shares:
        share["Price"] += (share["Price"] * growthRate/float(12)/100)
        portfolio += share["Price"] * portfolioSummary[share["ShareName"]]
    print(date, portfolio)

    #Need to pay dividends and repurchase that stuff

#Need to redraw money from portfolio

pp.pprint("Lots:")    
pp.pprint(portfolioLots)
pp.pprint("PortfolioValue:")    
pp.pprint(portfolio)
pp.pprint("PortfolioSummary:")    
pp.pprint(portfolioSummary)
pp.pprint("Shares Situation:")    
pp.pprint(shares)