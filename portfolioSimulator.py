import datetime
import pprint
import datetime
import random
import matplotlib.pyplot as plt

pp = pprint.PrettyPrinter(indent=4)

#User Input
shares = [{"ShareName":"VAN0003AU", "Price":2.3041, "DividendYield": 2.4, "FrankingLevel": 0, "DividendsPerYear":4, "Allocation":60, "GrowthRate":6.33}, 
          {"ShareName":"VAN0002AU", "Price":2.2543, "DividendYield":4.3, "FrankingLevel":70, "DividendsPerYear":4, "Allocation":40, "GrowthRate":8.11}]

portfolioTarget = 2000000
MonthlyInvestment = 5000
withdrawal_years = 30
yearly_withdrawal_amount = 80000 #The money that you are going to spend, you'll have to pay taxes on top of it
#End of User Input

portfolio = 0 
portfolioLots = []
portfolioSummary = {}

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

        portfolioLots.append({"PurchaseDate": date, "ShareName": share["ShareName"], "PurchasePrice": buying_price, "Position": position, "SellingInfo":[]})
        portfolioSummary[share["ShareName"]] += position
    assert(sum_of_allocations == 100)

    #Dividend payment and reinvestment
    for share in shares:
        if(date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
            #print"Yay!! DividendTime")
            dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
            reinvestment_price = share["Price"] - dividend_value_per_share
            shares_repurchased = dividend_value_per_share * portfolioSummary[share["ShareName"]] / reinvestment_price
            portfolioLots.append({"PurchaseDate": date, "ShareName": share["ShareName"], "PurchasePrice": reinvestment_price, "Position": shares_repurchased, "SellingInfo":[]})
            share["Price"] = reinvestment_price
            portfolioSummary[share["ShareName"]] += shares_repurchased

    portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
    for share in shares:
        share["Price"] += (share["Price"] * share["GrowthRate"]/float(12)/100)
        portfolio += share["Price"] * portfolioSummary[share["ShareName"]]
    # print(date, portfolio)
    dates.append(date)
    portfolioValues.append(portfolio)

    #Adding date and portfolio to arrays to be plotted later

    #Month has now passed, updating dates
    date += datetime.timedelta(days=35)
    date = datetime.datetime(date.year, date.month, 1)

    iteration_counter += 1

#Need to redraw money from portfolio

monthly_withdrawal_amount = yearly_withdrawal_amount/float(12)

checking_account = 0
checking_account_history = []
withdrawal_dates = []

franking_credits_history = []
overdue_capital_gains_tax = 0

portfolio_during_withdrawl_history = []
yearly_taxable_income_history = []

income_tax_history = []
income_tax_history_dates = []

income_from_share_sales_history = []
income_from_share_sales_history_dates = []

for i in range(0, withdrawal_years):
    #we will do it get dividends whenever we get them and if we run out of cash amount we sell stocks every month to make up for the lost money
    yearly_taxable_income = 0
    franking_credits = 0

    for m in range(0, 12):
        #Dividend payment and reinvestment
        for share in shares:
            if(date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
                # print("Yay!! ", share["ShareName"], " DividendTime")
                dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
                ex_div_price = share["Price"] - dividend_value_per_share
                total_dividend = dividend_value_per_share * portfolioSummary[share["ShareName"]] 
                this_franking_credits = total_dividend * share["FrankingLevel"]/float(100)*3/7
                # print(total_dividend, this_franking_credits)
                share["Price"] = ex_div_price
                checking_account += total_dividend
                yearly_taxable_income += total_dividend
                franking_credits += this_franking_credits

        date += datetime.timedelta(days=35)
        date = datetime.datetime(date.year, date.month, 1)

        #Time to use the money
        needed_money = yearly_withdrawal_amount/12
        if (checking_account < needed_money):
            print("ran out of money")
            #Sell shares to generate the remaining money which is needed
            missing_money = needed_money - checking_account
            income_from_share_sales_history.append(missing_money)
            income_from_share_sales_history_dates.append(date)
            #Find the most recent lot which has discount (at least 12 months old)
            for i in range(0, len(portfolioLots)):
                this_lot = portfolioLots[-i - 1] #Iterating over it in reverse order
                if(missing_money > 0):
                    if(date - this_lot["PurchaseDate"] > datetime.timedelta(days = 365) and this_lot["Position"]> 0):
                        #This is the lot we want to sell
                        for share in shares:
                            if(share["ShareName"] == this_lot["ShareName"]):
                                share_price = share["Price"]
                                lot_value = this_lot["Position"] * share_price
                                shares_to_be_sold = 0
                                if(missing_money >= lot_value):
                                    #sell whole lot
                                    shares_to_be_sold = this_lot["Position"]
                                else:
                                    #sell only part of lot
                                    shares_to_be_sold = share["Price"]/float(missing_money)

                                money_from_sale = shares_to_be_sold * share_price
                                capital_gains = (share_price-this_lot["PurchasePrice"])*shares_to_be_sold
                                this_lot["SellingInfo"].append({"SaleDate":date, "SoldShares":this_lot["Position"], "SellingPrice":share_price, "CapitalGainsGenerated":capital_gains})
                                this_lot["Position"] -= shares_to_be_sold

                                checking_account += money_from_sale
                                # Update missing money
                                missing_money -= money_from_sale
                                # Update capital gains , applying 50% discount
                                if(date - this_lot["PurchaseDate"] > datetime.timedelta(days=365)):
                                    yearly_taxable_income += capital_gains/2
                                else:
                                    print("Should never reach here")
                                    yearly_taxable_income = capital_gains

                                # Portfolio
                                portfolioSummary[share["ShareName"]] -= shares_to_be_sold

        portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
        for share in shares:
            share["Price"] += (share["Price"] * share["GrowthRate"]/float(12)/100) # Monthly Growth
            portfolio += share["Price"] * portfolioSummary[share["ShareName"]]
        # print(date, portfolio)
        dates.append(date)
        portfolio_during_withdrawl_history.append(portfolio)
        portfolioValues.append(portfolio)                                

        #Now we should have enough we need for this month
        checking_account -= needed_money #Money spent

        checking_account_history.append(checking_account)
        franking_credits_history.append(franking_credits)
        yearly_taxable_income_history.append(yearly_taxable_income)
        withdrawal_dates.append(date)            

    #Tax Time!!
    income_tax = 0

    if(yearly_taxable_income <= 18200):
        income_tax = 0
        income_tax -= franking_credits #Applying franking credits
    elif(yearly_taxable_income <= 37000):
        income_tax = 19* (yearly_taxable_income - 18200)/float(100)
        income_tax -= franking_credits
    elif(yearly_taxable_income < 80000):
        income_tax = 3572 + 32.5* (yearly_taxable_income - 37000)/float(100)
        income_tax -= franking_credits
    elif(yearly_taxable_income < 180000):
        income_tax = 17547+ 37* (yearly_taxable_income - 80000)/float(100)
        income_tax -= franking_credits   
    else:     
        income_tax = 54547+ 45* (yearly_taxable_income - 180000)/float(100)
        income_tax -= franking_credits   

    income_tax_history.append(income_tax)
    income_tax_history_dates.append(date)
    checking_account -= income_tax

print(checking_account)

# plot
plt.figure(1)
plt.title("Portfolio value over whole age")
plt.plot(dates,portfolioValues)
# beautify the x-labels
plt.gcf().autofmt_xdate()

# plot
plt.figure(2)
plt.title("Value of Checking Account over time")
plt.plot(withdrawal_dates,checking_account_history)
# beautify the x-labels
plt.gcf().autofmt_xdate()

#plt.show()
plt.figure(3)
plt.title("Taxable Income, FrankingCredits")
plt.plot(withdrawal_dates,yearly_taxable_income_history)
plt.plot(withdrawal_dates,franking_credits_history)
# beautify the x-labels
plt.gcf().autofmt_xdate()

plt.figure(4)
plt.title("IncomeTax")
plt.plot(income_tax_history_dates ,income_tax_history)
# beautify the x-labels
plt.gcf().autofmt_xdate()

plt.figure(5)
plt.title("Amount of Income Generated from Sales")
plt.plot(income_from_share_sales_history_dates,income_from_share_sales_history)
# beautify the x-labels
plt.gcf().autofmt_xdate()

plt.show()