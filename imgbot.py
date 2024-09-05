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

# Function to handle the /about command
async def about(update: Update, context: CallbackContext) -> None:
    about_text_1 = (
        "Hello! I am **Temesgen**, a Software Engineer from Ethiopia specializing in full-stack development. "
        "I focus on building modern, scalable web applications using the latest technologies.\n\n"
        "**Key Skills**:\n"
        "- Frontend: React, Next.js, Tailwind CSS, Material UI\n"
        "- Backend: Python, Django, Node.js, Express.js\n"
        "- Databases: PostgreSQL, MongoDB, MySQL\n"
        "- APIs & Authentication: REST API development, JWT\n"
        "- Version Control: Git, GitHub"
    )

    about_text_2 = (
        "**Highlighted Projects**:\n"
        "- **Uniconnect Ethiopia**: A social media platform combining features of LinkedIn and Facebook.\n"
        "- **Ethiopian Sign Language Detection**: AI-based interpretation of Ethiopian sign language.\n"
        "- **Book Rental Application**: A JWT-based book rental platform with role-based access.\n"
        "- **Blue Homes Sell**: A real estate platform for buying and selling properties.\n"
        "- **AI-Based Short Note Generation Platform**: AI tool for generating student notes from textbooks."
    )

    about_text_3 = (
        "**Certifications**:\n"
        "- Cisco Networking Academy: Network programming and configuration.\n"
        "- FreeCodeCamp: Responsive Web Design and Machine Learning with Python.\n"
        "- National Exit Exam: Software Engineering degree with a 3.2 GPA.\n\n"
        "You can explore my work through the following links:\n"
        "- **Portfolio**: [https://temesgen-lala.vercel.app/]\n"
        "- **GitHub**: [https://github.com/Temu-Lala]"
    )

    # Send the description in multiple parts
    await update.message.reply_text(about_text_1, parse_mode='Markdown')
    await update.message.reply_text(about_text_2, parse_mode='Markdown')
    await update.message.reply_text(about_text_3, parse_mode='Markdown')

# Function to handle the /portfolio command
async def portfolio(update: Update, context: CallbackContext) -> None:
    portfolio_link = "Check out my portfolio here: https://temesgen-lala.vercel.app/"
    await update.message.reply_text(portfolio_link)

# Function to handle errors
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')
    if update and update.message:
        await update.message.reply_text('An error occurred. Please try again later.')
    else:
        logger.error('No message context available for error handling.')

def main() -> None:
    # Create the application and pass your bot token
    application = Application.builder().token(TOKEN).build()

    # Define command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))  # Handler for /about command
    application.add_handler(CommandHandler("portfolio", portfolio))  # Handler for /portfolio command
    
    # Handle text messages sent by the user
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))

    # Log all errors
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
