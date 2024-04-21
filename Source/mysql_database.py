import os
import asyncio
import aiomysql
from aiomysql import Error
from dotenv import load_dotenv
from Username_Generator import generator

# Load secrets from environment
load_dotenv()

# - - - - - - - - - - #
loop = asyncio.get_event_loop()


# Function to connect to the database with credentials
async def connect_db():
    try:
        connection = await aiomysql.connect(
            host=os.getenv("HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DATABASE"),
            loop=loop,
        )

        if connection:
            return connection
        else:
            raise Exception("Database is not connected")

    except Error as e:
        print(f'[!] There was an error in connecting to MySQL Server: {e}')


# Function to get database cursor
async def get_cursor():
    global mydb
    try:
        await mydb.ping(reconnect=True)
    except Error:
        mydb = loop.run_until_complete(connect_db())
    return mydb.cursor()


mydb = loop.run_until_complete(connect_db())

# - - - - - - - - - - #


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
            print(f'[!] There was an error in getting cursor: {e}')
            pass


# Add Telegram User ID and created pack link to the database
async def push_uid_and_pack_name_to_db(user_id, ):
    async with await get_cursor() as cur:
        try:
            random_packname = await generate_new_pack_name()

            query = "insert into EmojiAI (TelegramUserID, sticker_set_link) values (%s, %s)"
            data_query = (user_id, random_packname)
            await cur.execute(query, data_query)
            await mydb.commit()
            return random_packname
        except Error as e:
            print(f'[!] There was an error in getting cursor: {e}')
            pass


# Get pack name by Telegram User ID
async def return_pack_name_by_uid(user_id):
    async with await get_cursor() as cur:
        try:
            query = "SELECT sticker_set_link FROM EmojiAI WHERE TelegramUserID = %s"
            data_query = (user_id,)
            await cur.execute(query, data_query)
            return (await cur.fetchall())[0][0]
        except Error as e:
            print(f'[!] There was an error in getting cursor: {e}')
            pass


# Update pack name by Telegram User ID
async def update_pack_name_in_db(user_id):
    async with await get_cursor() as cur:
        try:
            random_packname = await generate_new_pack_name()

            query = "UPDATE EmojiAI SET sticker_set_link = %s WHERE TelegramUserID = %s"
            data_query = (random_packname, user_id)
            await cur.execute(query, data_query)
            await mydb.commit()
            print(f"[x] Had to update a sticker set link for user {user_id}. The old sticker pack was likely deleted")

            return random_packname
        except Error as e:
            print(f'[!] There was an error in getting cursor: {e}')
            pass


# Generate new pack name
async def generate_new_pack_name():
    return await generator.GenerateUsername()
