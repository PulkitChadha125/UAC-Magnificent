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
                'NiftyQtyMultiplier': row['NiftyQtyMultiplier'],
                'Bankniftyultiplier': row['Bankniftyultiplier'],
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
                'Initial_Sell_Pe': None,
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

def stockdev_multiclient_orderplacement_buy(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            if basesymbol=="NIFTY":
                Orderqty=qty*daram['NiftyQtyMultiplier']
            if basesymbol=="BANKNIFTY":
                Orderqty=qty*daram['Bankniftyultiplier']


            Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="MARKET", productType='INTRADAY', qty=Orderqty,
                                         price=price)
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
            if basesymbol=="NIFTY":
                Orderqty=qty*daram['NiftyQtyMultiplier']
            if basesymbol=="BANKNIFTY":
                Orderqty=qty*daram['Bankniftyultiplier']
            Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="MARKET", productType='INTRADAY', qty=Orderqty,
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
def main_strategy():
    global result_dict,strikeListCe,strikeListPe,callltp ,putltp,CallStrikeListBuy ,CallStrikeListSell ,PutStrikeListBuy ,PutStrikeListSell
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                EntryDate=params['EntryDate']
                EntryTime=params['EntryTime']
                EntryTime = datetime.strptime(EntryTime, "%H:%M").time()
                ExitDate=params['ExitDate']
                ExitTime=params['ExitTime']
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
                                             token=get_token(params['Initial_Buy_Ce']))
                    buypeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Buy_Pe'],
                                                        token=get_token(params['Initial_Buy_Pe']))
                    sellpeltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Pe'],
                                                        token=get_token(params['Initial_Sell_Pe']))
                    sellceltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Initial_Sell_Ce'],
                                                        token=get_token(params['Initial_Sell_Ce']))

                    OrderLog = f"{timestamp} Buy order executed @ Call {params['Initial_Buy_Ce']} @ TradePrice: {buyceltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    OrderLog = f"{timestamp} Buy order executed @ Put {params['Initial_Buy_Pe']} @ TradePrice: {buypeltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    OrderLog = f"{timestamp} Sell order executed @ Call {params['Initial_Sell_Ce']} @ TradePrice: {sellpeltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)
                    OrderLog = f"{timestamp} Sell order executed @ Put {params['Initial_Sell_Pe']} @ TradePrice: {sellceltp}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


while True:
    main_strategy()
    time.sleep(2)
