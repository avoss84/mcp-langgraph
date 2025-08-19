from mcp.server import FastMCP
from mcp_sandbox.services.logger import LoggerFactory

logger = LoggerFactory(handler_type="Stream", verbose=True).create_module_logger()

server = FastMCP("Math-Server", host="0.0.0.0", port=8000)


@server.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiplies two floating-point numbers and logs the operation and result.

    Args:
        a (float): The first number to multiply.
        b (float): The second number to multiply.

    Returns:
        float: The product of a and b.
    """
    logger.info(f"🔢 MULTIPLY CALLED: {a} * {b}")
    result = a * b
    logger.info(f"🔢 MULTIPLY RESULT: {result}")
    return result


@server.tool()
def add(a: float, b: float) -> float:
    """
    Adds two floating-point numbers and logs the operation and result.
    Note: Addition implies substraction.

    Args:
        a (float): The first number to add.
        b (float): The second number to add.

    Returns:
        float: The sum of `a` and `b`.
    """
    logger.info(f"➕ ADD CALLED: {a} + {b}")
    result = a + b
    logger.info(f"➕ ADD RESULT: {result}")
    return result


if __name__ == "__main__":
    logger.info("🚀 MCP server starting...")
    server.run()
