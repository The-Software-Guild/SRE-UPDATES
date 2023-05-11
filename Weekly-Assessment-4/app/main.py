from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"


async def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}")
    if response.status_code == 200:
        data = response.json()
        if to_currency.upper() in data["rates"]:
            return data["rates"][to_currency.upper()]
        else:
            raise HTTPException(status_code=400, detail="To currency not supported")
    else:
        raise HTTPException(status_code=400, detail="From currency not supported")


@app.get("/exchange_rate")
async def exchange_rate(from_currency: str, to_currency: str) -> dict:
    rate = await get_exchange_rate(from_currency, to_currency)
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "exchange_rate": rate,
    }


@app.get("/convert_amount")
async def convert_amount(from_currency: str, to_currency: str, amount: float) -> dict:
    rate = await get_exchange_rate(from_currency, to_currency)
    converted_amount = amount * rate
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "amount": amount,
        "converted_amount": converted_amount,
    }

# @CODE : ADD ENDPOINT TO LIST ALL AVAILABLE CURRENCIES
@app.get("/available_currencies")
async def available_currencies(from_currency: str, to_currency: str) -> list:
    """
    Coded by: <name>
    This endpoint returns a list of available fiat currenices.
    """
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}")
    if response.status_code == 200:
        data = response.json()
        return data["rates"].keys():

# @CODE : ADD ENDPOINT TO GET LIST OF CRYPTO CURRENCIES
# You can use https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-currencies
@app.get("/available_crypto")
async def available_crypto() -> list[dict]:
    """
    Coded by: <name>
    This endpoint allows you to see what crypto-currencies are available
    """
    response = requests.get('https://api.coinbase.com/v2/currencies')
    if response.status_code == 200:
        return response.json()
    
# @CODE : ADD ENDPOINT TO GET Price of crypto
@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str) -> list[dict]:
    """
    Coded by: <name>
    This endpoint allows you to get a quote in for crypto in any supported currency
    """
    response = requests.get(f'GET https://api.coinbase.com/v2/prices/{from_crypto}-{to_currency}/spot')
    if response.status_code == 200:
        return response.json()

# @CODE : ADD ENPOINT TO UPDATE PRICE OF ASSET IN ORDERBOOK DB
# HINT - You will need to refer to the Orderbook-API on how it connects to the database!
# HINT - You may need to modify the requirments.txt to add libraries
# NOTE - Make sure code is not vulnerable to SQL injection! 
# NOTE - If you want to use the ORM you will need to add and import SQLClasses.py or just use query
@app.get("/update_orderbookdb_asset_price")
async def update_orderbookdb_asset_price(symbol: str, new_price: int) -> dict:
    """
    Coded by: <name>
    This endpoint allows us to update the price of our apps assets
    """
    from sqlalchemy import create_engine
    
    engine = create_engine('postgresql://user:password@localhost/mydatabase')
    
    try: new_price = float(new_price) except: raise HTTPException(status_code=400, detail="new_price must be numeric")
    
    with engine.connect() as conn:
        update_statement = "UPDATE Product SET price = :new_price WHERE symbol = :symbol;"
        try:
            conn.execute(update_statement, new_price=new_price, symbol=symbol)
            return {"update_report":"sucess", "symbol":symbol, "new_price":new_price}
        except:
            raise HTTPException(status_code=400, detail="An error occoured, make sure symbol exists")

    
# @CODE : ADD ENDPOINT FOR INSERTING A NEW Product (eg. ability to trade crypto)
@app.get("/new_orderbookdb_asset")
async def new_orderbookdb_asset(symbol: str, 
                                price: int,
                               productType: str,
                               name: str) -> dict:
    """
    Coded by: <name>
    This endpoint allows the insertion of a new finacial asset for trading within our orderbook application
    The idea is that we can use our new API to obtain prices for assets (like bitcoin) and use this endpoint to add them to our app
    """
    from sqlalchemy import create_engine
    
    engine = create_engine('postgresql://user:password@localhost/mydatabase')
    
    try: price = float(price) except: raise HTTPException(status_code=400, detail="new_price must be numeric")
    
    with engine.connect() as conn:
        update_statement = """INSERT INTO `orderbook`.`Product`
                            (`symbol`,
                            `price`,
                            `productType`,
                            `name`)
                            VALUES
                            (:symbol,
                            :price,
                            :productType,
                            :name);"""
        try:
            conn.execute(update_statement, price=price, symbol=symbol, productType=productType, name=name)
            return {"insert_report":"sucess", "symbol":symbol, "price":price}
        except:
            raise HTTPException(status_code=400, detail="Make sure asset exists")
    
