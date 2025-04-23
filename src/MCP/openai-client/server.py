from typing import Dict, Any, List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from mcp import types

# Initialize MCP server
mcp = FastMCP(name="Shopping Cart Calculator",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port))\
)


class ShoppingCartResponse(BaseModel):
    """Response model for shopping cart calculation."""
    subtotal: float = Field(..., description="Total before tax and discounts", ge=0)
    discount_amount: float = Field(..., description="Amount saved from discounts", ge=0)
    tax_amount: float = Field(..., description="Amount of tax applied", ge=0)
    total: float = Field(..., description="Final total after tax and discounts", ge=0)


@mcp.tool()
def calculate_shopping_cart_total(
    subtotal: float = Field(..., description="Total amount before tax and discounts", gt=0),
    tax_rate: float = Field(0.0, description="Tax rate as a decimal (e.g., 0.08 for 8%)", ge=0, le=1),
    discount_percentage: float = Field(0.0, description="Discount percentage as a decimal (e.g., 0.15 for 15%)", ge=0, le=1)
) -> ShoppingCartResponse:
    """Calculate the total cost of a shopping cart including tax and discounts.
    
    Args:
        subtotal: Total amount before tax and discounts
        tax_rate: Tax rate as a decimal (e.g., 0.08 for 8%)
        discount_percentage: Discount percentage as a decimal (e.g., 0.15 for 15%)
        
    Returns:
        ShoppingCartResponse containing:
            - subtotal: Original amount before tax and discounts
            - discount_amount: Amount saved from discounts
            - tax_amount: Amount of tax applied
            - total: Final total after tax and discounts
    """
    # Calculate discount amount
    discount_amount = subtotal * discount_percentage
    
    # Calculate amount after discount
    amount_after_discount = subtotal - discount_amount
    
    # Calculate tax amount
    tax_amount = amount_after_discount * tax_rate
    
    # Calculate final total
    total = amount_after_discount + tax_amount
    
    return ShoppingCartResponse(
        subtotal=round(subtotal, 2),
        discount_amount=round(discount_amount, 2),
        tax_amount=round(tax_amount, 2),
        total=round(total, 2)
    )

# We also add some tools that are not related to the shopping cart calculation
@mcp.tool()
def get_company_policy(policy_name: str = Field(..., description="The name of the policy to retrieve")):
    """Get a company policy by name."""
    return "Company policy: All employees must wear a mask when indoors."

@mcp.tool()
def tax_calculator(amount: float = Field(..., description="The amount to calculate tax for", ge=0),
                   tax_rate: float = Field(..., description="The tax rate to apply", ge=0, le=1)):
    """Calculate the tax amount for an amount at a given tax rate."""
    return amount * tax_rate


if __name__ == "__main__":
    mcp.run(transport="stdio")