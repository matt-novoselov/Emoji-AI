from os import getenv
import dotenv

# Load secrets from environment
dotenv.load_dotenv()

# Load Telegram bot API token
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
# Load public domain for webhooks
WEBHOOK_DOMAIN = getenv("WEBHOOK_DOMAIN")

# Load Replicate API token
REPLICATE_API_TOKEN = getenv("REPLICATE_API_TOKEN")

# MySQL database credits
DB_NAME = getenv("DB_NAME")
DB_USERNAME = getenv("DB_USERNAME")
DB_HOST = getenv("DB_HOST")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_PORT = getenv("DB_PORT")
