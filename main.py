import AngelIntegration
from datetime import datetime, timedelta
import time
import traceback
import pandas as pd
import Stockdeveloper
import TelegramIntegration as tele

print(f"Strategy developed by Programetix visit link for more development requirements : {'https://programetix.com/'} ")

client_dict={}

def get_client_detail():
    global client_dict
    try:
        csv_path = 'clientdetails.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()


        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Title': row['Title'],
                'Value': row['Value'],
                'QtyMultiplier': row['QtyMultiplier'],
                'autotrader': None,
            }
            client_dict[row['Title']] = symbol_dict
        # print("client_dict: ", client_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_client_detail()
def round_to_nearest(number, nearest):
    return round(number / nearest) * nearest

def get_user_settings():
    global result_dict
    # Symbol,lotsize,Stoploss,Target1,Target2,Target3,Target4,Target1Lotsize,Target2Lotsize,Target3Lotsize,Target4Lotsize,BreakEven,ReEntry
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            # StepNumberBUYCE	StepNumberSELLCE	StepNumberBUYPE	StepNumberSELLPE	SellPremium_CE	SellPremium_PE	BuyPremium_PE	BuyPremium_CE
            symbol_dict = {
                'Symbol': row['Symbol'],"Quantity":row['Quantity'],"StepSize":row['StepSize'],"StepNumberBUYCE":row['StepNumberBUYCE'],
                "StepNumberSELLCE": row['StepNumberSELLCE'],"StepNumberBUYPE": row['StepNumberBUYPE'],"StepNumberSELLPE": row['StepNumberSELLPE'],
                "SellPremium_CE": row['SellPremium_CE'],"SellPremium_PE": row['SellPremium_PE'],"BuyPremium_PE": row['BuyPremium_PE'],"BuyPremium_CE": row['BuyPremium_CE'],
                'EntryDate': row['EntryDate'],'EntryTime': row['EntryTime'],'TradeExpiery':row['TradeExpiery'],'BaseSymbol':row['BaseSymbol'],
                'ExitDate': row['ExitDate'],'ExitTime': row['ExitTime'],'InitialTrade':None,'BuyPercentage':row['BuyPercentage'],'SellPercentage':row['SellPercentage'],
                'BuyrangeValue':None,'SellrangeVale':None,'Initial_Buy_Ce':None,'Initial_Buy_Pe':None,'Initial_Sell_Ce':None,
                'Initial_Sell_Pe': None,"CALLBUY_STOCKDEV":None,"CALLSELL_STOCKDEV":None,"PUTBUY_STOCKDEV":None,"PUTSELL_STOCKDEV":None,'LimitSubValue':float(row['LimitSubValue'])
                ,'TakeExitBuyCE':row['TakeExitBuyCE'], 'TakeExitBuyPE':row['TakeExitBuyPE'], 'TakeExitSellCE':row['TakeExitSellCE'], 'TakeExitSellPE':row['TakeExitSellPE'],
                'InstantSQOFF':row['InstantSQOFF'],'INSTRUMENTSAVED':None
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
result_dict={}

def get_api_credentials():
    credentials = {}
    delete_file_contents("OrderLog.txt")
    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials
get_user_settings()
credentials_dict = get_api_credentials()
stockdevaccount=credentials_dict.get('stockdevaccount')
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)
AngelIntegration.symbolmpping()



def stock_dev_login_multiclient(client_dict):

    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            daram['autotrader']=Stockdeveloper.login(daram['Value'])
    print("client_dict: ",client_dict)

stock_dev_login_multiclient(client_dict)

def stockdev_multiclient_orderplacement_sell(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):

            Orderqty=qty*daram['QtyMultiplier']
            res=Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="LIMIT", productType='DELIVERY', qty=Orderqty,
                                         price=price)
            print(res)
            orderlog = (
                f"{timestamp} Sell Order executed {side} side {symbol} @  {price},stoploss= {Stoploss}, "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)
def stockdev_multiclient_orderplacement_buy(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            Orderqty=qty*daram['QtyMultiplier']
            res=Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="LIMIT", productType='DELIVERY', qty=Orderqty,
                                         price=price)
            print(res)
            orderlog = (
                f"{timestamp} Buy Order executed {side} side {symbol} @  {price},stoploss= {Stoploss}, "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)

CallStrikeListBuy={}
CallStrikeListSell={}
PutStrikeListBuy={}
PutStrikeListSell={}


def genertaepricedictpe_sell(price, step, distance,BaseSymbol,formatted_date):
    start_price = price
    end_price =  price + (step * distance)
    price_list = [start_price + i * distance for i in range((end_price - start_price) // distance + 1)]
    price_dict = {price: {"PESymbol": f"{BaseSymbol}{formatted_date}{price}PE", "PEPREMIUM": "PRE"} for price in
                  price_list}
    for price in price_dict:
        pe_symbol = price_dict[price]["PESymbol"]
        params = {'Symbol': BaseSymbol,  'PESymbol': pe_symbol,"Strike":price}
        price_dict[price]["PEPREMIUM"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['PESymbol'],
                                                                  token=get_token(params['PESymbol']))

    return price_dict


def genertaepricedictpe_buy(price, step, distance,BaseSymbol,formatted_date):
    start_price = price - (step * distance)
    end_price = price
    price_list = [start_price + i * distance for i in range((end_price - start_price) // distance + 1)]
    price_dict = {price: {"PESymbol": f"{BaseSymbol}{formatted_date}{price}PE", "PEPREMIUM": "PRE"} for price in
                  price_list}
    for price in price_dict:
        pe_symbol = price_dict[price]["PESymbol"]
        params = {'Symbol': BaseSymbol,  'PESymbol': pe_symbol,"Strike":price}
        price_dict[price]["PEPREMIUM"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['PESymbol'],
                                                                  token=get_token(params['PESymbol']))

    return price_dict

def generatepricedictce_buy(price, step, distance,BaseSymbol,formatted_date):
    start_price = price
    end_price = price + (step * distance)
    price_list = [start_price + i * distance for i in range((end_price - start_price) // distance + 1)]
    print("price_list: ",price_list)
    price_dict = {price: {"CESymbol": f"{BaseSymbol}{formatted_date}{price}CE", "CEPREMIUM": "PRE"} for price in price_list}
    for price in price_dict:
        ce_symbol = price_dict[price]["CESymbol"]
        params = {'Symbol': BaseSymbol, 'CESymbol': ce_symbol,"Strike":price}
        price_dict[price]["CEPREMIUM"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['CESymbol'],
                                                                  token=get_token(params['CESymbol']))
    return price_dict

def generatepricedictce_sell(price, step, distance,BaseSymbol,formatted_date):
    start_price = price - (step * distance)
    end_price = price
    price_list = [start_price + i * distance for i in range((end_price - start_price) // distance + 1)]
    price_dict = {price: {"CESymbol": f"{BaseSymbol}{formatted_date}{price}CE", "CEPREMIUM": "PRE"} for price in price_list}
    for price in price_dict:
        ce_symbol = price_dict[price]["CESymbol"]
        params = {'Symbol': BaseSymbol, 'CESymbol': ce_symbol,"Strike":price}
        price_dict[price]["CEPREMIUM"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['CESymbol'],
                                                                  token=get_token(params['CESymbol']))
    return price_dict

# exit
def stockdev_multiclient_orderplacement_exit(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price,log):
    Orderqty = None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            Orderqty=qty*daram['QtyMultiplier']
            Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="MARKET", productType='DELIVERY', qty=Orderqty,
                                         price=price)
            orderlog = (
                f"{timestamp} {log} {symbol} @  {price} "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)

def finc_closest_Pe(price_dict, target_premium):
    closest_pe_symbol = None
    closest_pe_premium = float('-inf')
    for price in price_dict:
        pe_premium = price_dict[price]["PEPREMIUM"]
        if pe_premium < target_premium and pe_premium > closest_pe_premium:
            closest_pe_premium = pe_premium
            closest_pe_symbol = price_dict[price]["PESymbol"]

            print("closest_pe_premium: ",closest_pe_premium)
            print("closest_pe_symbol: ",closest_pe_symbol)
            print("price: ", price)

    return  closest_pe_symbol

def finc_closest_Ce(price_dict, target_premium):
    closest_ce_symbol = None
    closest_ce_premium = float('-inf')
    for price in price_dict:
        ce_premium = price_dict[price]["CEPREMIUM"]
        if ce_premium < target_premium and ce_premium > closest_ce_premium:
            closest_ce_premium = ce_premium
            closest_ce_symbol = price_dict[price]["CESymbol"]

    return closest_ce_symbol
def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token



def callstrike(price_dict, target_premium):
    closest_ce_symbol = None
    closest_ce_premium = float('-inf')
    for price in price_dict:
        ce_premium = price_dict[price]["CEPREMIUM"]
        if ce_premium < target_premium and ce_premium > closest_ce_premium:
            closest_ce_premium = ce_premium
            closest_ce_symbol = price_dict[price]["CESymbol"]
            reqprice = price

    return reqprice

def putstrike(price_dict, target_premium):
    closest_pe_symbol = None
    closest_pe_premium = float('-inf')
    for price in price_dict:
        pe_premium = price_dict[price]["PEPREMIUM"]
        if pe_premium < target_premium and pe_premium > closest_pe_premium:
            closest_pe_premium = pe_premium
            closest_pe_symbol = price_dict[price]["PESymbol"]
            reqprice = price

    return reqprice
once=False
def main_strategy():
    global once,result_dict,strikeListCe,strikeListPe,callltp ,putltp,CallStrikeListBuy ,CallStrikeListSell ,PutStrikeListBuy ,PutStrikeListSell
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                EntryTime=params['EntryTime']
                EntryTime = datetime.strptime(EntryTime, "%H:%M").time()
                EntryDate = params['EntryDate']
                EntryDate = datetime.strptime(EntryDate, "%d-%b-%y")

                current_date = datetime.now().date()
                current_time = datetime.now().time()
                if current_date == EntryDate.date() and current_time.strftime("%H:%M") == EntryTime.strftime("%H:%M") \
                    and params['InitialTrade']is None:
                    params['InitialTrade']="TRADE_TAKEN"
                    SpotLtp=AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                                      token=get_token(params['Symbol']))
                    print(SpotLtp)
                    params['BuyrangeValue'] =SpotLtp*params['BuyPercentage']*0.01
                    params['BuyrangeValue']= SpotLtp+params['BuyrangeValue']
                    params['SellrangeVale']=SpotLtp*params['SellPercentage']*0.01
                    params['SellrangeVale']=SpotLtp-params['SellrangeVale']
                    print("BuyrangeValue: ",params['BuyrangeValue'])
                    print("SellrangeVale: ", params['SellrangeVale'])
                    OrderLog = f"{timestamp} BuyrangeValue : {params['BuyrangeValue']} @ SellrangeVale: {params['SellrangeVale']}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    date_obj = datetime.strptime(params["TradeExpiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%d%b%y").upper()
                    targetbuystrike= round_to_nearest(number=params['BuyrangeValue'], nearest=params['StepSize'])
                    targetsellstrike = round_to_nearest(number=params['SellrangeVale'], nearest=params['StepSize'])
                    CallStrikeListBuy=generatepricedictce_buy(price=targetbuystrike, step=params['StepNumberBUYCE'],
                                                              distance=params['StepSize'],BaseSymbol=params['BaseSymbol'],
                                                              formatted_date=formatted_date)
                    CallStrikeListSell=generatepricedictce_sell(price=targetbuystrike, step=params['StepNumberSELLCE'],
                                                              distance=params['StepSize'],BaseSymbol=params['BaseSymbol'],
                                                              formatted_date=formatted_date)

                    PutStrikeListBuy=genertaepricedictpe_buy(price=targetsellstrike, step=params['StepNumberBUYPE'],
                                                             distance=params['StepSize'],BaseSymbol=params['BaseSymbol'],formatted_date=formatted_date)
                    PutStrikeListSell=genertaepricedictpe_sell(price=targetsellstrike, step=params['StepNumberSELLPE'],
                                                             distance=params['StepSize'],BaseSymbol=params['BaseSymbol'],formatted_date=formatted_date)

                    params['Initial_Buy_Ce']= finc_closest_Ce(CallStrikeListBuy, target_premium=params['BuyPremium_CE'])
                    params['Initial_Buy_Pe']= finc_closest_Pe( PutStrikeListBuy , target_premium=params['BuyPremium_PE'])
                    params['Initial_Sell_Ce']= finc_closest_Ce(CallStrikeListSell, target_premium=params['SellPremium_CE'])
                    params['Initial_Sell_Pe']= finc_closest_Pe(PutStrikeListSell, target_premium=params['SellPremium_PE'])


                    print("targetbuystrike: ",targetbuystrike)
                    print("targetsellstrike: ",targetsellstrike)
                    print("CallStrikeListBuy: ", CallStrikeListBuy)
                    print("CallStrikeListSell: ", CallStrikeListSell)
                    print("PutStrikeListBuy: ", PutStrikeListBuy)
                    print("PutStrikeListSell: ", PutStrikeListSell)

                    print("Initial_Buy_Ce: ", params['Initial_Buy_Ce'])
                    print("Initial_Buy_Pe: ", params['Initial_Buy_Pe'])
                    print("Initial_Sell_Ce: ", params['Initial_Sell_Ce'])
                    print("Initial_Sell_Pe: ", params['Initial_Sell_Pe'])
                    buyceltp=AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Ce'],
                                             token=get_token(params['Initial_Buy_Ce']))-params['LimitSubValue']
                    buypeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Pe'],
                                                        token=get_token(params['Initial_Buy_Pe']))-params['LimitSubValue']
                    sellpeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Pe'],
                                                        token=get_token(params['Initial_Sell_Pe']))-params['LimitSubValue']
                    sellceltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Ce'],
                                                        token=get_token(params['Initial_Sell_Ce']))-params['LimitSubValue']

                    OrderLog = f"{timestamp} Buy order executed @ Call {params['Initial_Buy_Ce']} @ TradePrice: {buyceltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    params["CALLBUY_STOCKDEV"]= f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_CE_{callstrike(CallStrikeListBuy,target_premium=params['BuyPremium_CE'])}"
                    params["CALLSELL_STOCKDEV"]= f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_CE_{callstrike(CallStrikeListSell,target_premium=params['SellPremium_CE'])}"
                    params["PUTBUY_STOCKDEV"]=  f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_PE_{putstrike(PutStrikeListBuy,target_premium=params['BuyPremium_PE'])}"
                    params["PUTSELL_STOCKDEV"]=   f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_PE_{putstrike(PutStrikeListSell,target_premium=params['SellPremium_PE'])}"

                    stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'], client_dict=client_dict, timestamp=timestamp,
                                                             symbol=params["CALLBUY_STOCKDEV"], direction="BUY",
                                                             Stoploss=0, Target=0, qty=params['Quantity'], price=buyceltp, side="CALL")
                    OrderLog = f"{timestamp} Buy order executed @ Put {params['Initial_Buy_Pe']} @ TradePrice: {buypeltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'], client_dict=client_dict,
                                                            timestamp=timestamp,
                                                            symbol=params["PUTBUY_STOCKDEV"], direction="BUY",
                                                            Stoploss=0, Target=0, qty=params['Quantity'],
                                                            price=buyceltp, side="PUT")
                    OrderLog = f"{timestamp} Sell order executed @ Call {params['Initial_Sell_Ce']} @ TradePrice: {sellpeltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    stockdev_multiclient_orderplacement_sell(basesymbol=params['BaseSymbol'], client_dict=client_dict,
                                                            timestamp=timestamp,
                                                            symbol=params["CALLSELL_STOCKDEV"], direction="SELL",
                                                            Stoploss=0, Target=0, qty=params['Quantity'],
                                                            price=buyceltp, side="CALL")
                    OrderLog = f"{timestamp} Sell order executed @ Put {params['Initial_Sell_Pe']} @ TradePrice: {sellceltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    stockdev_multiclient_orderplacement_sell(basesymbol=params['BaseSymbol'], client_dict=client_dict,
                                                             timestamp=timestamp,
                                                             symbol=params["PUTSELL_STOCKDEV"], direction="SELL",
                                                             Stoploss=0, Target=0, qty=params['Quantity'],
                                                             price=buyceltp, side="PUT")

                if current_date == EntryDate.date() and current_time.strftime("%H:%M") == EntryTime.strftime("%H:%M") \
                    and params['InitialTrade']=="TRADE_TAKEN" and params['INSTRUMENTSAVED'] is None:
                    params['INSTRUMENTSAVED']="Done"
                    df = pd.DataFrame.from_dict(result_dict, orient='index')
                    df.reset_index(inplace=True)
                    df.rename(columns={'index': 'symbol'}, inplace=True)
                    csv_file = 'result.csv'
                    df.to_csv(csv_file, index=False)

                timebasedexit()
                instantsqoff()

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


timeexit=False
def timebasedexit():
    global timeexit,result_dict, strikeListCe, strikeListPe, callltp, putltp, CallStrikeListBuy, CallStrikeListSell, PutStrikeListBuy, PutStrikeListSell
    try:
        df = pd.read_csv("result.csv")
        timedict = df.set_index('symbol').T.to_dict()
        for symbol, params in timedict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                ExitDate = params['ExitDate']
                ExitTime = params['ExitTime']
                ExitTime = datetime.strptime(ExitTime, "%H:%M").time()
                ExitDate = datetime.strptime(ExitDate, "%d-%b-%y").date()
                current_date = datetime.now().date()
                current_time = datetime.now().time()

                if current_date == ExitDate and current_time.strftime("%H:%M") == ExitTime.strftime("%H:%M") \
                        and params['InitialTrade'] == "TRADE_TAKEN" :
                    print(params['InitialTrade'])
                    print("time based exit : initiated")
                    params['InitialTrade'] = "TimeExitHappened"
                    print(params['InitialTrade'])
                    if params['TakeExitBuyCE']==True:
                        buyceltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Ce'],
                                                            token=get_token(params['Initial_Buy_Ce']))
                        OrderLog = f"{timestamp} Buy trade exited @ Call {params['Initial_Buy_Ce']} exitery date exit  @ TradePrice: {buyceltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                 client_dict=client_dict, timestamp=timestamp,
                                                                 symbol=params["CALLBUY_STOCKDEV"], direction="SELL",
                                                                 Stoploss=0, Target=0, qty=params['Quantity'],
                                                                 price=buyceltp, log="Buy trade exited ce @ ")

                    if params['TakeExitBuyPE']==True:
                        buypeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Pe'],
                                                            token=get_token(params['Initial_Buy_Pe']))
                        OrderLog = f"{timestamp} Buy trade exited @ Put {params['Initial_Buy_Pe']}  exitery date exit @ TradePrice: {buypeltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                 client_dict=client_dict,
                                                                 timestamp=timestamp,
                                                                 symbol=params["PUTBUY_STOCKDEV"], direction="SELL",
                                                                 Stoploss=0, Target=0, qty=params['Quantity'],
                                                                 price=buypeltp, log="Buy trade exited pe@ ")

                    if params['TakeExitSellCE']==True:
                        sellpeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Pe'],
                                                             token=get_token(params['Initial_Sell_Pe']))
                        OrderLog = f"{timestamp} Sell trade exited @ Call {params['Initial_Sell_Ce']} exitery date exit  @ TradePrice: {sellpeltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                 client_dict=client_dict,
                                                                 timestamp=timestamp,
                                                                 symbol=params["CALLSELL_STOCKDEV"], direction="BUY",
                                                                 Stoploss=0, Target=0, qty=params['Quantity'],
                                                                 price=sellpeltp, log="sell trade exited ce@ ")
                    if params['TakeExitSellPE']==True:
                        sellceltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Ce'],
                                                             token=get_token(params['Initial_Sell_Ce']))
                        OrderLog = f"{timestamp} Sell trade exited @ Put {params['Initial_Sell_Pe']} exitery date exit  @ TradePrice: {sellceltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                 client_dict=client_dict,
                                                                 timestamp=timestamp,
                                                                 symbol=params["PUTSELL_STOCKDEV"], direction="BUY",
                                                                 Stoploss=0, Target=0, qty=params['Quantity'],
                                                                 price=sellceltp, log="sell trade exited PE@ ")

                if params['InitialTrade'] == "TimeExitHappened":
                    params['InitialTrade']="NOMORETRADES"
                    df = pd.DataFrame.from_dict(timedict, orient='index')
                    df.reset_index(inplace=True)
                    df.rename(columns={'index': 'symbol'}, inplace=True)
                    csv_file = 'result.csv'
                    df.to_csv(csv_file, index=False)

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()

def instantsqoff():
    global result_dict, strikeListCe, strikeListPe, callltp, putltp, CallStrikeListBuy, CallStrikeListSell, PutStrikeListBuy, PutStrikeListSell
    try:
        df = pd.read_csv("result.csv")
        instantsqoff_dict = df.set_index('symbol').T.to_dict()

        for symbol, params in instantsqoff_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                print("InstantSQOFF: ",params['InstantSQOFF'])
                print("InitialTrade: ", params['InitialTrade'])
                print("symbol_value: ", symbol_value)
                if params['InstantSQOFF'] == True :
                    if params['InitialTrade'] == "TRADE_TAKEN" :
                        print("Manual Sq off initiated")
                        params['InitialTrade']=False
                        buyceltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Ce'],
                                                                token=get_token(params['Initial_Buy_Ce']))
                        OrderLog = f"{timestamp} Buy trade exited @ Call {params['Initial_Buy_Ce']} sqareoff exit  @ TradePrice: {buyceltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                     client_dict=client_dict, timestamp=timestamp,
                                                                     symbol=params["CALLBUY_STOCKDEV"],
                                                                     direction="SELL",
                                                                     Stoploss=0, Target=0, qty=params['Quantity'],
                                                                     price=buyceltp, log="Buy trade exited ce @ ")

                        buypeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Pe'],
                                                                token=get_token(params['Initial_Buy_Pe']))
                        OrderLog = f"{timestamp} Buy trade exited @ Put {params['Initial_Buy_Pe']}  sqareoff exit @ TradePrice: {buypeltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                     client_dict=client_dict,
                                                                     timestamp=timestamp,
                                                                     symbol=params["PUTBUY_STOCKDEV"], direction="SELL",
                                                                     Stoploss=0, Target=0, qty=params['Quantity'],
                                                                     price=buypeltp, log="Buy trade exited pe@ ")

                        sellpeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Pe'],
                                                                 token=get_token(params['Initial_Sell_Pe']))
                        OrderLog = f"{timestamp} Sell trade exited @ Call {params['Initial_Sell_Ce']} sqareoff exit  @ TradePrice: {sellpeltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                     client_dict=client_dict,
                                                                     timestamp=timestamp,
                                                                     symbol=params["CALLSELL_STOCKDEV"],
                                                                     direction="BUY",
                                                                     Stoploss=0, Target=0, qty=params['Quantity'],
                                                                     price=sellpeltp, log="sell trade exited ce@ ")
                        sellceltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Ce'],
                                                                 token=get_token(params['Initial_Sell_Ce']))
                        OrderLog = f"{timestamp} Sell trade exited @ Put {params['Initial_Sell_Pe']} sqareoff exit  @ TradePrice: {sellceltp}"
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        stockdev_multiclient_orderplacement_exit(basesymbol=params['BaseSymbol'],
                                                                     client_dict=client_dict,
                                                                     timestamp=timestamp,
                                                                     symbol=params["PUTSELL_STOCKDEV"], direction="BUY",
                                                                     Stoploss=0, Target=0, qty=params['Quantity'],
                                                                     price=sellceltp, log="sell trade exited PE@ ")
                if params['InitialTrade']==False:
                    params['InitialTrade'] = "NOMORETRADES"
                    params['InstantSQOFF'] =False
                    df = pd.DataFrame.from_dict(instantsqoff_dict, orient='index')
                    df.reset_index(inplace=True)
                    df.rename(columns={'index': 'symbol'}, inplace=True)
                    csv_file = 'result.csv'
                    df.to_csv(csv_file, index=False)

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


while True:
    main_strategy()
    time.sleep(2)
