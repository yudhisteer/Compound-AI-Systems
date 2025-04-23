from mcp.server.fastmcp import FastMCP
from accounts import Account

mcp = FastMCP(name="accounts_server",
            host="0.0.0.0",  # only used for SSE transport (localhost)
            port=8050,  # only used for SSE transport (set this to any port)
    )

#------------------------------------------
# Tools
#------------------------------------------

@mcp.tool(name="get_balance", description="Get the cash balance of the given account name.")
async def get_balance(name: str) -> float:
    """Get the cash balance of the given account name.

    Args:
        name: The name of the account holder
    """
    return Account.get(name).balance

@mcp.tool(name="get_holdings", description="Get the holdings of the given account name.")
async def get_holdings(name: str) -> dict[str, int]:
    """Get the holdings of the given account name.

    Args:
        name: The name of the account holder
    """
    return Account.get(name).holdings

@mcp.tool(name="buy_shares", description="Buy shares of a stock.")
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Buy shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to buy
        rationale: The rationale for the purchase and fit with the account's strategy
    """
    return Account.get(name).buy_shares(symbol, quantity, rationale)


@mcp.tool(name="sell_shares", description="Sell shares of a stock.")
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Sell shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to sell
        rationale: The rationale for the sale and fit with the account's strategy
    """
    return Account.get(name).sell_shares(symbol, quantity, rationale)

@mcp.tool(name="change_strategy", description="At your discretion, if you choose to, call this to change your investment strategy for the future.")
async def change_strategy(name: str, strategy: str) -> str:
    """At your discretion, if you choose to, call this to change your investment strategy for the future.

    Args:
        name: The name of the account holder
        strategy: The new strategy for the account
    """
    return Account.get(name).change_strategy(strategy)





#------------------------------------------
# Resources
#------------------------------------------

@mcp.resource(uri="accounts://accounts_server/{name}", description="Get the report of the given account name.")
async def read_account_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.report()

@mcp.resource(uri="accounts://strategy/{name}", description="Get the strategy of the given account name.")
async def read_strategy_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.get_strategy()

if __name__ == "__main__":
    mcp.run(transport='stdio')