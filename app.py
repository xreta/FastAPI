import datetime as dt
import enum
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, Form, Query
from starlette.responses import RedirectResponse
import uvicorn

app = FastAPI()

# Model
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")

    price: float = Field(description="The price of the Trade.")

    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")

    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")

    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")

    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")

    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")

    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")

    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")

    trader: str = Field(description="The name of the Trader")

# Hard Coded Database
trades = [
    {
    "assetClass": "Bond",
    "counterparty": "Google",
    "instrumentId": "ABCD",
    "instrumentName": "Meta",
    "tradeDateTime": "2022-04-04T14:14:01.000Z",
    "tradeDetails": {
        "buySellIndicator": "BUY",
        "price": 10.11,
        "quantity": 23
    },
    "tradeId": "123",
    "trader": "Shadan"
    },
    {
        "assetClass": "Bond",
        "counterparty": "EY",
        "instrumentId": "TSWQ",
        "instrumentName": "Smn",
        "tradeDateTime": "2022-02-09T11:13:01.000Z",
        "tradeDetails": {
            "buySellIndicator": "SELL",
            "price": 99.00,
            "quantity": 54
        },
        "tradeId": "111",
        "trader": "Isabelle"
    },
    {
        "assetClass": "Equity",
        "counterparty": "JP Morgan",
        "instrumentId": "TSEW",
        "instrumentName": "Shares",
        "tradeDateTime": "2022-01-05T12:11:01.000Z",
        "tradeDetails": {
            "buySellIndicator": "BUY",
            "price": 12.12,
            "quantity": 17
        },
        "tradeId": "100",
        "trader": "Messi"
    },
    {
        "assetClass": "Equity",
        "counterparty": "KPMG",
        "instrumentId": "DAM",
        "instrumentName": "Mutual Funds",
        "tradeDateTime": "2022-06-06T18:31:01.000Z",
        "tradeDetails": {
            "buySellIndicator": "SELL",
            "price": 12.43,
            "quantity": 56
        },
        "tradeId": "007",
        "trader": "Ronaldo"
    }
]

class sortChoice(str, enum.Enum):
    asc = "asc"
    desc = "desc"

# 1 Fetch a list of trades
@app.get("/trades/", status_code=200)
async def fetch_all_trades():
    return trades

# 2 Fetch a trade by ID
@app.get("/trades/{trade_id}", status_code=200)
async def fetch_trade_by(trade_id: str) -> dict:

    result = [trade for trade in trades if trade["trade_id"] == trade_id]
    if result:
        return result[0]    
    else:
        return {"error": f"Trade with id {trade_id} not found"}

# 3 Searching trades
@app.get("/trades", status_code=200)
def search_trade(
    counterparty: Optional[str] = None,
    instrument_id: Optional[str] = None,
    instrument_name: Optional[str] = None,
    trader: Optional[str] = None,
):
    results = []
    for trade in trades:
        if (
            (counterparty is None or trade["counterparty"] == counterparty)
            and (instrument_id is None or trade["instrument_id"] == instrument_id)
            and (instrument_name is None or trade["instrument_name"] == instrument_name)
            and (trader is None or trade["trader"] == trader)
        ):
            results.append(trade)
    return results

# 4 Advanced filtering 
@app.get("/trades", status_code=200)
def advance_search_trade(
    assetClass: Optional[str] = None,
    end: Optional[dt.datetime] = None,
    maxPrice: Optional[float] = None,
    minPrice: Optional[float] = None,
    start: Optional[dt.datetime] = None,
    tradeType: Optional[str] = None,
):
    results = []
    for trade in trades:
        if (
            (assetClass is None or trade["asset_class"] == assetClass)
            and (end is None or trade["trade_date_time"] <= end)
            and (maxPrice is None or trade["trade_details"]["price"] <= maxPrice)
            and (minPrice is None or trade["trade_details"]["price"] >= minPrice)
            and (start is None or trade["trade_date_time"] >= start)
            and (tradeType is None or trade["trade_details"]["buySellIndicator"] == tradeType)
        ):
            results.append(trade)
    return results


if __name__ == "__main__":
    uvicorn.run("app:app", port=9000, reload=True)
    