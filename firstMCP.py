from fastmcp import FastMCP
import random as r

mcp= FastMCP(name="demo")

@mcp.tool
def add_numbers(a:float, b:float) -> float:
    """Add two numbers together."""
    return a + b
@mcp.tool
def subtract_numbers(a:float, b:float) -> float:
    """Subtract two numbers."""
    return a - b

@mcp.tool
def roll_dice(n_dice:int = 1) -> list[int]:
    """Roll a number of dice with a specified number of sides."""
    return [r.randint(1, 6) for _ in range(n_dice)]

if __name__ == "__main__":
    mcp.run()