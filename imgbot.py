import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot's token from BotFather
TOKEN = '6940579564:AAEzFNFbGpZfmGyzE2J6JDi7WXMCtUKpoq8'

# Pexels API key and endpoints
PEXELS_API_KEY = 'pwEmwe1I7cJ9i17zRt4kWRMJJqjQ8dFA2eeIOZgXWi5PmBw5b7v7V7uH'
PEXELS_PHOTO_URL = 'https://api.pexels.com/v1/search'
PEXELS_VIDEO_URL = 'https://api.pexels.com/videos/search'

# Helper function to fetch media from Pexels API
def fetch_media(query: str, url: str, api_key: str, media_type: str) -> dict:
    try:
        response = requests.get(
            url,
            headers={'Authorization': api_key},
            params={'query': query, 'per_page': 5}  # Fetch up to 5 results
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        logger.error(f'HTTP request error: {e}')
        return {'error': str(e)}

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! Send me a description and specify whether you want photos or videos. For example: "Photos of nature" or "Videos of cats".')

# Function to handle when a user sends a description
async def handle_description(update: Update, context: CallbackContext) -> None:
    description = update.message.text
    chat_id = update.message.chat_id
    
    # Determine whether user is requesting photos or videos
    if 'video' in description.lower() or 'videos' in description.lower():
        search_type = 'video'
        query = description.lower().replace('video', '').replace('videos', '').strip()
        url = PEXELS_VIDEO_URL
    else:
        search_type = 'photo'
        query = description.lower().replace('photos', '').strip()
        url = PEXELS_PHOTO_URL

    # Acknowledge the user’s description
    await update.message.reply_text(f'You asked for {search_type}s related to: "{query}". Fetching {search_type}s...')

    # Fetch the media from Pexels API
    media_data = fetch_media(query, url, PEXELS_API_KEY, search_type)

    if 'error' in media_data:
        await update.message.reply_text(f'Sorry, an error occurred: {media_data["error"]}')
        return

    if (search_type == 'photo' and media_data.get('photos')) or (search_type == 'video' and media_data.get('videos')):
        for item in (media_data['photos'] if search_type == 'photo' else media_data['videos']):
            media_url = item['src']['original'] if search_type == 'photo' else item['video_files'][0]['link']
            if search_type == 'photo':
                await context.bot.send_photo(chat_id=chat_id, photo=media_url)
            else:
                await context.bot.send_video(chat_id=chat_id, video=media_url)
    else:
        await update.message.reply_text(f'Sorry, no {search_type}s found for your description.')

# Function to handle errors
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')
    await update.message.reply_text('An error occurred. Please try again later.')

def main() -> None:
    # Create the application and pass your bot token
    application = Application.builder().token(TOKEN).build()

    # Define command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Handle text messages sent by the user
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))

    # Log all errors
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
