import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()
logger.remove()
logger.add(sys.stderr, level="DEBUG", colorize=True)
logger.add("app-logs/app.log", level="DEBUG", rotation="10 MB", retention="10 days", serialize=True)

logger.info("Logging setup done for API MICROSERVICE!")
