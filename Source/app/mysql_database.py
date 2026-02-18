from app.config import DB_HOST, DB_PORT, DB_USERNAME, DB_NAME, DB_PASSWORD
import asyncio
import aiomysql
from aiomysql import Error
from app.Username_Generator import generator


mydb = None
connection_lock = asyncio.Lock()


def validate_db_settings():
    missing_settings = []

    if not DB_HOST:
        missing_settings.append("DB_HOST")
    if not DB_PORT:
        missing_settings.append("DB_PORT")
    if not DB_USERNAME:
        missing_settings.append("DB_USERNAME")
    if not DB_NAME:
        missing_settings.append("DB_NAME")
    if DB_PASSWORD is None:
        missing_settings.append("DB_PASSWORD")

    if missing_settings:
        missing_list = ", ".join(missing_settings)
        raise RuntimeError(f"Missing database settings: {missing_list}")


# Function to connect to the database with credentials
async def connect_db():
    validate_db_settings()
    try:
        connection = await aiomysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USERNAME,
            password=DB_PASSWORD,
            db=DB_NAME,
        )
        return connection

    except Error as e:
        raise RuntimeError(f"There was an error in connecting to MySQL Server: {e}") from e


async def get_connection():
    global mydb
    if mydb is not None and not mydb.closed:
        try:
            await mydb.ping(reconnect=True)
            return mydb
        except Error:
            mydb = None

    async with connection_lock:
        if mydb is None or mydb.closed:
            mydb = await connect_db()
        else:
            try:
                await mydb.ping(reconnect=True)
            except Error:
                mydb = await connect_db()
    return mydb


# Function to get database cursor
async def get_cursor():
    connection = await get_connection()
    return connection.cursor()


# Function to get username and status by Telegram user id
async def return_pack_username_and_activated_status(user_id):
    async with await get_cursor() as cur:
        try:
            # Check if user exists
            data_query = (user_id,)
            query = "select if( exists(select* from EmojiAI where TelegramUserID=%s), 1, 0)"
            await cur.execute(query, data_query)
            user_exist = await cur.fetchone()
            user_exist = user_exist[0]

            if user_exist:  # Return pack username and True
                result = await return_pack_name_by_uid(user_id)
                return result, user_exist
            else:  # Add new user if he doesn't exist
                username = await push_uid_and_pack_name_to_db(user_id, )
                return username, user_exist

        except Error as e:
            raise RuntimeError(f"There was an error in getting cursor: {e}") from e


# Add Telegram User ID and created pack link to the database
async def push_uid_and_pack_name_to_db(user_id, ):
    async with await get_cursor() as cur:
        try:
            random_packname = await generate_new_pack_name()

            query = "insert into EmojiAI (TelegramUserID, sticker_set_link) values (%s, %s)"
            data_query = (user_id, random_packname)
            await cur.execute(query, data_query)
            connection = await get_connection()
            await connection.commit()
            return random_packname
        except Error as e:
            raise RuntimeError(f"There was an error in getting cursor: {e}") from e


# Get pack name by Telegram User ID
async def return_pack_name_by_uid(user_id):
    async with await get_cursor() as cur:
        try:
            query = "SELECT sticker_set_link FROM EmojiAI WHERE TelegramUserID = %s"
            data_query = (user_id,)
            await cur.execute(query, data_query)
            return (await cur.fetchall())[0][0]
        except Error as e:
            raise RuntimeError(f"There was an error in getting cursor: {e}") from e


# Update pack name by Telegram User ID
async def update_pack_name_in_db(user_id):
    async with await get_cursor() as cur:
        try:
            random_packname = await generate_new_pack_name()

            query = "UPDATE EmojiAI SET sticker_set_link = %s WHERE TelegramUserID = %s"
            data_query = (random_packname, user_id)
            await cur.execute(query, data_query)
            connection = await get_connection()
            await connection.commit()
            print(f"[x] Had to update a sticker set link for user {user_id}. The old sticker pack was likely deleted")

            return random_packname
        except Error as e:
            raise RuntimeError(f"There was an error in getting cursor: {e}") from e


# Generate new pack name
async def generate_new_pack_name():
    return await generator.GenerateUsername()
