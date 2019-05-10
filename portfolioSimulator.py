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

        portfolioLots.append({"PurchaseDate": date, "ShareName": share["ShareName"], "BuyingPrice": buying_price, "Position": position, "SellingInfo":[]})
        portfolioSummary[share["ShareName"]] += position
    assert(sum_of_allocations == 100)

    #Dividend payment and reinvestment
    for share in shares:
        if(date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
            print("Yay!! DividendTime")
            dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
            reinvestment_price = share["Price"] - dividend_value_per_share
            shares_repurchased = dividend_value_per_share * portfolioSummary[share["ShareName"]] / reinvestment_price
            portfolioLots.append({"PurchaseDate": date, "ShareName": share["ShareName"], "BuyingPrice": reinvestment_price, "Position": shares_repurchased, "SellingInfo":[]})
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

yearly_withdrawal_amount = 20000 #After tax
monthly_withdrawal_amount = yearly_withdrawal_amount/float(12)
withdrawal_years = 3 #100 years
#withdrawal_percent = 4

checking_account = 0
checking_account_history = []
withdrawal_dates = []

franking_credits = 0
franking_credits_history = []
overdue_capital_gains_tax = 0

portfolio_during_withdrawl_history = []

for i in range(0, withdrawal_years):
    #we will do it get dividends whenever we get them and if we run out of cash amount we sell stocks every month to make up for the lost money

    for m in range(0, 12):
        #Dividend payment and reinvestment
        for share in shares:
            if(date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
                print("Yay!! ", share["ShareName"], " DividendTime")
                dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
                ex_div_price = share["Price"] - dividend_value_per_share
                total_dividend = dividend_value_per_share * portfolioSummary[share["ShareName"]] 
                this_franking_credits = total_dividend * share["FrankingLevel"]/float(100)*3/7
                print(total_dividend, this_franking_credits)
                share["Price"] = ex_div_price
                checking_account += total_dividend
                franking_credits += this_franking_credits

        date += datetime.timedelta(days=35)
        date = datetime.datetime(date.year, date.month, 1)

        portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
        for share in shares:
            share["Price"] += (share["Price"] * growthRate/float(12)/100) # Monthly Growth
            portfolio += share["Price"] * portfolioSummary[share["ShareName"]]
        print(date, portfolio)
        dates.append(date)
        portfolio_during_withdrawl_history.append(portfolio)
        portfolioValues.append(portfolio)

        #Time to use the money
        needed_money = yearly_withdrawal_amount/12
        if (checking_account >= needed_money):
            checking_account -= needed_money #Money spent
        else:
            print("ran out of money")
            #Sell shares to generate the remaining money which is needed
            missing_money = needed_money - checking_account
            #Find the most recent lot which has discount (at least 12 months old)
            for i in range(0, len(portfolioLots)):
                this_lot = portfolioLots[-i - 1] #Iterating over it in reverse order
                if(date - this_lot["PurchaseDate"] > datetime.timedelta(days = 365) and this_lot["Position"]> 0):
                    #This is the lot we want to sell
                    for share in shares:
                        if(share["ShareName"] == this_lot["ShareName"]):
                            share_price = share["Price"]
                            lot_value = this_lot["Position"] * share_price
                            if(missing_money > lot_value):
                                #sell whole lot
                                #spend money
                                #update missing money
                                #update capital gains
                                pass
                            else:
                                #sell only part of lot
                                pass


            checking_account -= needed_money #Money spent

        checking_account_history.append(checking_account)
        franking_credits_history.append(franking_credits)
        withdrawal_dates.append(date)            


    #Tax Time!!


print(checking_account)

# plot
plt.figure(1)
plt.title("Portfolio value over whole age")
plt.plot(dates,portfolioValues)
# beautify the x-labels
plt.gcf().autofmt_xdate()

# plot
plt.figure(2)
plt.title("Value of Checking And Franking Credit Account over time")
plt.plot(withdrawal_dates,checking_account_history)
plt.plot(withdrawal_dates,franking_credits_history)
# plt.plot(withdrawal_dates,portfolio_during_withdrawl_history)
# beautify the x-labels
plt.gcf().autofmt_xdate()

#plt.show()
plt.figure(3)
plt.title("Value of Portfolio over time")
plt.plot(withdrawal_dates,portfolio_during_withdrawl_history)
# beautify the x-labels
plt.gcf().autofmt_xdate()

plt.show()