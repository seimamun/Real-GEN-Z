from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)
import random
import time
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['mining_bot']
users = db['users']

# Define constants
START_BALANCE = 0
MIN_REWARD = 1
MAX_REWARD = 10
COOLDOWN_TIME = 60  # 60 seconds

# Start command
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        # Add a new user to the database
        users.insert_one({"user_id": user_id, "balance": START_BALANCE, "last_mine_time": 0})
        update.message.reply_text("Welcome to the Mining Bot! Start mining with /mine.")
    else:
        update.message.reply_text("Welcome back! Continue mining with /mine.")

# Mine command
def mine(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        update.message.reply_text("You are not registered. Use /start to join.")
        return

    current_time = time.time()
    if current_time - user['last_mine_time'] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - user['last_mine_time']))
        update.message.reply_text(f"Please wait {remaining_time} seconds before mining again.")
        return

    # Generate mining reward
    reward = random.randint(MIN_REWARD, MAX_REWARD)

    # Update user balance
    new_balance = user['balance'] + reward
    users.update_one(
        {"user_id": user_id},
        {"$set": {"balance": new_balance, "last_mine_time": current_time}}
    )

    update.message.reply_text(f"You mined {reward} coins! Your balance is now {new_balance} coins.")

# Balance command
def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        update.message.reply_text("You are not registered. Use /start to join.")
    else:
        update.message.reply_text(f"Your current balance is {user['balance']} coins.")

# Main function to start the bot
def main():
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("mine", mine))
    dispatcher.add_handler(CommandHandler("balance", balance))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
      
