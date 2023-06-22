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
  
# @CODE : AN ENDPOINT THAT TAKES A STRING AND CONFIRMS IT HAS
# AT LEAST ONE UPPERCASE, LOWERCASE, NUMBER AND INCLUDES 8 OR MORE CHARACTERS
@app.get("/check_password_strength")
async def check_password_strength(password: str) -> bool:
    """
    Coded By: <name>  
    This function checks whether a given password is strong enough, i.e., it contains at least one digit, one lowercase letter,
    one uppercase letter, and includes at least 8 characters.
    """
    import re
    regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$'
    # The above regex pattern requires:
    # - (?=.*\d): At least one digit
    # - (?=.*[a-z]): At least one lowercase letter
    # - (?=.*[A-Z]): At least one uppercase letter
    # - .{8,}: At least 8 characters
    match = re.search(regex, password)
    return bool(match)


# @CODE : ADD ENDPOINT TO LIST ALL AVAILABLE CURRENCIES  
# NOTE : FastAPI enforces that the return type of the function matches the function signature!  
#        This is a common error!
@app.get("/available_currencies")
async def available_currencies(from_currency: str) -> dict:
    """
    Coded by: <name>  
    This endpoint returns a list of available fiat currencies that can be paired with the @from_currency parameter.  
    @from_currency : str - you must specify a currency to see what currencies it can be compared against  
    """
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}")
    if response.status_code == 200:
        data = response.json()
        print(data['rates'].keys())
        return {"currencies":list(data["rates"].keys())}
    else:
        raise HTTPException(status_code=400, detail="From currency not supported")

# @CODE : ADD ENDPOINT TO GET LIST OF CRYPTO CURRENCIES
# You can use this API https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-currencies
# and search for the endpoint that returns all the crypto currencies  
@app.get("/available_crypto")
async def available_crypto() -> dict:
    """
    Coded by: <name>  
    This endpoint allows you to see what crypto-currencies are available  
    """
    response = requests.get('https://api.coinbase.com/v2/currencies/crypto')
    if response.status_code == 200:
        return response.json()
    
# @CODE : ADD ENDPOINT TO GET Price of crypto  
# Use the coinbase API from above
@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str) -> dict:
    """
    Coded by: <name>  
    This endpoint allows you to get a quote for a crypto in any supported currency  
    @from_crypto - chose a crypto currency (eg. BTC, or ETH)  
    @to_currency - chose a currency to obtain the price in (eg. USD, or CAD)  
    """
    response = requests.get(f'https://api.coinbase.com/v2/prices/{from_crypto.upper()}-{to_currency.upper()}/spot')
    if response.status_code == 200:
        return response.json()

# @CODE : ADD ENPOINT TO UPDATE PRICE OF ASSET IN ORDERBOOK DB
# The code below starts you off using SQLAlchemy ORM
# Dependencies should already be installed from your requirements.txt file
# Using the ORM instead of raw SQL is safer and less coupled, it is best practice!
@app.get("/update_orderbookdb_asset_price")
async def update_orderbookdb_asset_price(symbol: str, new_price: float) -> dict:
    """
    Coded by: <name>  
    This endpoint allows us to update the price of our apps assets  
    @symbol - pick a symbol to update the price of in the orderbook app  
    @new_price - The new price of the symbol  
    """
    
    # import sqlalchemy
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, update, MetaData
    from sqlalchemy.orm import sessionmaker
    
    # create a engine for building sessions
    engine = create_engine('mysql+pymysql://wiley:wiley123@orderbookdb/orderbook')

    # create an ORM object that maps to our Product table
    metadata = MetaData()
    product_table = Table('Product', metadata,
        Column('symbol', String(16), primary_key=True),
        Column('price', Numeric(precision=15, scale=2)),
        Column('productType', String(12)),
        Column('name', String(128)),
        Column('lastUpdate', DateTime)
    )
    metadata.create_all(engine)

    # create a database session maker
    Session = sessionmaker(bind=engine)

    try:
        # Instantiate the session
        session = Session()
        # create the statement to udpate
        stmt = update(product_table).where(product_table.c.symbol == symbol).values(price=new_price)
        # execute commit and flush the statement
        session.execute(stmt)
        session.commit()
        session.flush()
        return {"update_report": "success", "symbol": symbol, "new_price": new_price}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred, make sure symbol exists and price is numeric")
    finally:
        session.close()

    
# @CODE : ADD ENDPOINT FOR INSERTING A CRYPTO CURRENCY INTO THE ORDERBOOK APP
@app.get("/add_crypto_to_orderbook")
async def add_crypto_to_orderbook(symbol: str) -> dict:
    """
     Coded by: <name>  
     This endpoint uses the `convert_crypto` function above to get the price of a crypto-currency  
     and inserts that currency and price into the orderbook database 
    """
    # import sqlalchemy
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, update, MetaData
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('mysql+pymysql://wiley:wiley123@orderbookdb/orderbook')
    metadata = MetaData()
    product_table = Table('Product', metadata,
        Column('symbol', String(16), primary_key=True),
        Column('price', Numeric(precision=15, scale=2)),
        Column('productType', String(12)),
        Column('name', String(128)),
        Column('lastUpdate', DateTime)
    )

    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    crypto_data = await convert_crypto(symbol, "USD")
    
    price = crypto_data["data"]["amount"]

    try:
        session = Session()
        new_product = product_table.insert().values(symbol=symbol, price=price, productType="crypto", name=symbol)
        session.execute(new_product)
        session.commit()
        session.flush()
        return {"insert_report": "success", "symbol": symbol, "price": price, "productType": 'crypto', "name": symbol}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred while inserting the product data")
    finally:
        session.close()
   
