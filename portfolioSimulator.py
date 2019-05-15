import datetime
import pprint
import random

import matplotlib.pyplot as plt

pp = pprint.PrettyPrinter(indent=4)


class PortfolioSimulator:
    def __init__(self,shares, portfolio_target, monthly_investment, withdrawal_years, yearly_withdrawal_amount, did_labour_win):
    #User Input
        self.shares = shares
        self.portfolio_target = portfolio_target
        self.monthly_investment = monthly_investment
        self.withdrawal_years = withdrawal_years
        self.yearly_withdrawal_amount = yearly_withdrawal_amount #The money that you are going to spend, you'll have to pay taxes on top of it
        self.did_labour_win = did_labour_win
        #End of User Input

        #Internal Variables
        self.portfolio = 0 
        self.portfolioLots = []
        self.portfolioSummary = {}

        self.date = datetime.datetime.now()

        for share in self.shares:
            self.portfolioSummary[share["ShareName"]] = 0
            
        self.dates = [] #for plotting
        self.portfolioValues = [] #for plotting

        self.checking_account = 0
        self.checking_account_history = []
        self.withdrawal_dates = []

        self.franking_credits_history = []
        self.portfolio_during_withdrawl_history = []
        self.yearly_taxable_income_history = []

        self.income_tax_history = []
        self.income_tax_history_dates = []

        self.income_from_share_sales_history = []
        self.income_from_share_sales_history_dates = []        

    def currency(self, x, pos):
        'The two args are the value and tick position'
        if x >= 1000000:
            return '${:1.1f}M'.format(x*1e-6)
        return '${:1.0f}K'.format(x*1e-3)   

    def buy_shares(self, amount)     :
        sum_of_allocations = 0 
        for share in self.shares:
            this_share_allocation = share["Allocation"]
            this_share_available_money = amount * this_share_allocation/float(100)
            buying_price = share["Price"]
            position = this_share_available_money/buying_price

            #Allocation sanity check
            sum_of_allocations += share["Allocation"]

            self.portfolioLots.append({"PurchaseDate": self.date, "ShareName": share["ShareName"], "PurchasePrice": buying_price, "Position": position, "SellingInfo":[]})
            self.portfolioSummary[share["ShareName"]] += position
        assert(sum_of_allocations == 100)

    def sell_shares(self, amount):
        self.income_from_share_sales_history.append(amount)
        self.income_from_share_sales_history_dates.append(self.date)
        #Find the most recent lot which has discount (at least 12 months old)
        for i in range(0, len(self.portfolioLots)):
            this_lot = self.portfolioLots[-i - 1] #Iterating over it in reverse order
            if(amount > 0):
                if(self.date - this_lot["PurchaseDate"] > datetime.timedelta(days = 365) and this_lot["Position"]> 0):
                    #This is the lot we want to sell
                    for share in self.shares:
                        if(share["ShareName"] == this_lot["ShareName"]):
                            share_price = share["Price"]
                            lot_value = this_lot["Position"] * share_price
                            shares_to_be_sold = 0
                            if(amount >= lot_value):
                                #sell whole lot
                                shares_to_be_sold = this_lot["Position"]
                            else:
                                #sell only part of lot
                                shares_to_be_sold = share["Price"]/float(amount)

                            money_from_sale = shares_to_be_sold * share_price
                            capital_gains = (share_price-this_lot["PurchasePrice"])*shares_to_be_sold
                            this_lot["SellingInfo"].append({"SaleDate":self.date, "SoldShares":this_lot["Position"], "SellingPrice":share_price, "CapitalGainsGenerated":capital_gains})
                            this_lot["Position"] -= shares_to_be_sold

                            self.checking_account += money_from_sale
                            # Update missing money
                            amount -= money_from_sale
                            # Update capital gains , applying 50% discount
                            if(self.date - this_lot["PurchaseDate"] > datetime.timedelta(days=365)):
                                if(self.did_labour_win):
                                    self.yearly_taxable_income += capital_gains * 75/float(100)
                                else:
                                    self.yearly_taxable_income += capital_gains/float(2)
                            else:
                                print("Should never reach here")
                                self.yearly_taxable_income = capital_gains

                            # Portfolio
                            self.portfolioSummary[share["ShareName"]] -= shares_to_be_sold        

    def work(self):
        while self.portfolio < self.portfolio_target:
            #Each iteration of this loop will add one month's investments
            self.buy_shares(self.monthly_investment) 

            #Dividend payment and reinvestment
            for share in self.shares:
                if(self.date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
                    #print"Yay!! DividendTime")
                    dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
                    reinvestment_price = share["Price"] - dividend_value_per_share
                    shares_repurchased = dividend_value_per_share * self.portfolioSummary[share["ShareName"]] / reinvestment_price
                    self.portfolioLots.append({"PurchaseDate": self.date, "ShareName": share["ShareName"], "PurchasePrice": reinvestment_price, "Position": shares_repurchased, "SellingInfo":[]})
                    share["Price"] = reinvestment_price
                    self.portfolioSummary[share["ShareName"]] += shares_repurchased

            self.portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
            for share in self.shares:
                share["Price"] += (share["Price"] * share["GrowthRate"]/float(12)/100)
                self.portfolio += share["Price"] * self.portfolioSummary[share["ShareName"]]
            # print(date, portfolio)
            self.dates.append(self.date)
            self.portfolioValues.append(self.portfolio)

            #Adding date and portfolio to arrays to be plotted later

            #Month has now passed, updating dates
            self.date += datetime.timedelta(days=35)
            self.date = datetime.datetime(self.date.year, self.date.month, 1)


        #Need to redraw money from portfolio
        for i in range(0, self.withdrawal_years):
            #we will do it get dividends whenever we get them and if we run out of cash amount we sell stocks every month to make up for the lost money
            self.yearly_taxable_income = 0
            self.franking_credits = 0

            for m in range(0, 12):
                for share in shares:
                    if(self.date.month % (12/ share["DividendsPerYear"]) == 0): #Will work for quarterly or semiannually dividends, might need to fix for other cases
                        # print("Yay!! ", share["ShareName"], " DividendTime")
                        dividend_value_per_share = share["Price"]*share["DividendYield"]/float(share["DividendsPerYear"])/100
                        ex_div_price = share["Price"] - dividend_value_per_share
                        total_dividend = dividend_value_per_share * self.portfolioSummary[share["ShareName"]] 
                        this_franking_credits = total_dividend * share["FrankingLevel"]/float(100)*3/7
                        # print(total_dividend, this_franking_credits)
                        share["Price"] = ex_div_price
                        self.checking_account += total_dividend
                        self.yearly_taxable_income += total_dividend
                        self.franking_credits += this_franking_credits

                self.date += datetime.timedelta(days=35)
                self.date = datetime.datetime(self.date.year, self.date.month, 1)

                #Time to use the money
                needed_money = self.yearly_withdrawal_amount/12
                if (self.checking_account < needed_money):
                    # print("ran out of money")
                    #Sell shares to generate the remaining money which is needed
                    missing_money = needed_money - self.checking_account

                    self.sell_shares(missing_money)
                    #Sell shares equivalent to missing money

                self.portfolio = 0 #Resetting portfolio to recalculate its value based on holdings
                for share in self.shares:
                    share["Price"] += (share["Price"] * share["GrowthRate"]/float(12)/100) # Monthly Growth
                    self.portfolio += share["Price"] * self.portfolioSummary[share["ShareName"]]
                # print(date, portfolio)
                self.dates.append(self.date)
                self.portfolio_during_withdrawl_history.append(self.portfolio)
                self.portfolioValues.append(self.portfolio)                                

                #Now we should have enough we need for this month
                self.checking_account -= needed_money #Money spent

                self.checking_account_history.append(self.checking_account)
                self.franking_credits_history.append(self.franking_credits)
                self.yearly_taxable_income_history.append(self.yearly_taxable_income)
                self.withdrawal_dates.append(self.date)            

            #Tax Time!!
            income_tax = 0

            if(self.yearly_taxable_income <= 18200):
                income_tax = 0
                income_tax -= self.franking_credits #Applying franking credits
            elif(self.yearly_taxable_income <= 37000):
                income_tax = 19* (self.yearly_taxable_income - 18200)/float(100)
                income_tax -= self.franking_credits
            elif(self.yearly_taxable_income < 80000):
                income_tax = 3572 + 32.5* (self.yearly_taxable_income - 37000)/float(100)
                income_tax -= self.franking_credits
            elif(self.yearly_taxable_income < 180000):
                income_tax = 17547+ 37* (self.yearly_taxable_income - 80000)/float(100)
                income_tax -= self.franking_credits   
            else:     
                income_tax = 54547+ 45* (self.yearly_taxable_income - 180000)/float(100)
                income_tax -= self.franking_credits   

            if(self.did_labour_win):
                if(income_tax < 0):
                    income_tax = 0

            self.income_tax_history.append(income_tax)
            self.income_tax_history_dates.append(self.date)

            if(income_tax > self.checking_account):
                self.sell_shares(income_tax - self.checking_account) #Now checking_account should have enough money to pay taxes

            self.checking_account -= income_tax

            #Due to too much income and franking credit tax returns, the checking account can become too large
            #If the amount in it incrases by more than a year's expenses, we will buy stocks from it.
            if(self.checking_account > self.yearly_withdrawal_amount):
                amount_to_be_invested = self.checking_account - self.yearly_withdrawal_amount
                self.buy_shares(amount_to_be_invested)
                self.checking_account -= amount_to_be_invested

        # plot
        plt.subplot(2,3,1)
        plt.title("Portfolio value over whole age")
        plt.plot(self.dates,self.portfolioValues)
        # beautify the x-labels
        plt.gcf().autofmt_xdate()

        # plot
        plt.subplot(2,3,2)
        plt.title("Value of Checking Account over time")
        plt.plot(self.withdrawal_dates,self.checking_account_history)
        # beautify the x-labels
        plt.gcf().autofmt_xdate()

        #plt.show()
        plt.subplot(2,3,3)
        plt.title("Taxable Income")
        plt.plot(self.withdrawal_dates,self.yearly_taxable_income_history)
        # beautify the x-labels
        plt.gcf().autofmt_xdate()

        #plt.show()
        plt.subplot(2,3,4)
        plt.title("FrankingCredits")
        plt.plot(self.withdrawal_dates,self.franking_credits_history)
        # beautify the x-labels
        plt.gcf().autofmt_xdate()

        plt.subplot(2,3,5)
        plt.title("IncomeTax")
        plt.plot(self.income_tax_history_dates ,self.income_tax_history)
        # beautify the x-labels
        plt.gcf().autofmt_xdate()

        plt.subplot(2,3,6)
        plt.title("Amount of Income Generated from Sales")
        plt.plot(self.income_from_share_sales_history_dates,self.income_from_share_sales_history)
        # formatter = plt.FuncFormatter(currency)
        # plt.yaxis.set_major_formatter(formatter)
        # beautify the x-labels
        plt.gcf().autofmt_xdate()

        # plt.show()


# shares = [{"ShareName":"VAN0003AU", "Price":2.3041, "DividendYield": 2.4, "FrankingLevel": 0, "DividendsPerYear":4, "Allocation":70, "GrowthRate":6}, #12.16
#           {"ShareName":"VAN0002AU", "Price":2.2543, "DividendYield":4.3, "FrankingLevel":70, "DividendsPerYear":4, "Allocation":30, "GrowthRate":6}] #9.69

portfolio_target = 1000000
monthly_investment = 5000
withdrawal_years = 30
yearly_withdrawal_amount = 40000 #The money that you are going to spend, you'll have to pay taxes on top of it

# thisportfolio = PortfolioSimulator(shares, portfolio_target, monthly_investment, withdrawal_years, 40000)
# thisportfolio.work()

shares = [{"ShareName":"AFI", "Price":5.88, "DividendYield": 4.05, "FrankingLevel": 100, "DividendsPerYear":4, "Allocation":50, "GrowthRate":6},  # 11.7
          {"ShareName":"ARGO", "Price":7.73, "DividendYield":4.14, "FrankingLevel":100, "DividendsPerYear":4, "Allocation":50, "GrowthRate":6}] # 7.7

thisportfolio = PortfolioSimulator(shares, portfolio_target, monthly_investment, withdrawal_years, 40000,True)
thisportfolio.work()

thisportfolio = PortfolioSimulator(shares, portfolio_target, monthly_investment, withdrawal_years, 40000,False)
thisportfolio.work()

plt.show()
