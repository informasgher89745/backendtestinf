import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
token = "7043327981:AAFPWA5Kc_vgmuq-sKocbJiLYvyz2jqlb4g"

# List of allowed chat IDs (you can add the chat IDs where the bot should operate)
allowed_chats = [-1002428161649, -1002178243149]  # Replace these with actual allowed chat IDs

# Regular expression pattern to detect email addresses
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Initialize the learners data dictionary
learners_data = {}

# Function to load data from multiple files
def load_data_from_files(*filenames):
    for filename in filenames:
        with open(filename, 'r') as file:
            lines = file.readlines()[1:]  # Skip the header
            for line in lines:
                columns = line.strip().split('\t')
                learner_code, name, lp, email, type_, batch = columns
                learners_data[learner_code] = {
                    "Name": name,
                    "L.P": lp,
                    "Email": email,
                    "Type": type_,
                    "Batch": batch
                }

# Load data from both data.txt and data1.txt
load_data_from_files('data.txt', 'data1.txt')

# Start command to initialize the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running and will monitor messages for email addresses and learner codes.")

# Function to overlay learner details onto an image based on Type
def overlay_text_on_image(learner_details, learner_type):
    # Select image based on learner type
    if learner_type == 'Reg':
        img_path = "template_reg.png"  # Image for Reg type
    elif learner_type == 'Dist':
        img_path = "template_dist.png"  # Image for Dist type
    
    # Open the template image based on Type
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    
    # Define the font and size (you may need to adjust this based on the font available on your system)
    try:
        font = ImageFont.truetype("arialbd.ttf", size=70)
    except IOError:
        font = ImageFont.load_default()
    
    # Positioning the text on the image (you can adjust the coordinates)
    position = (40, 130)
    line_height = 90  # Adjust line height to avoid overlap

    # Draw the learner details on the image with white text
    for line in learner_details.split('\n'):
        draw.text(position, line, font=font, fill="white")
        position = (position[0], position[1] + line_height)

    # Save the modified image to a new file
    img.save("modified_image.png")
    return "modified_image.png"

# Function to handle messages and detect learner codes or email addresses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the chat is allowed
    if update.effective_chat.id not in allowed_chats:
        return  # If the chat ID is not allowed, do nothing

    # Check if the update is a message and contains text
    if update.message and update.message.text:
        message_text = update.message.text

        # Split the message text by whitespace to find each learner code or L.P.
        identifiers = message_text.split()  # Split the message text by whitespace to find each learner code or L.P.
        
        found_any = False
        messages_sent = 0  # Initialize the counter for messages sent

        for identifier in identifiers:  # Looping through both learner codes and L.P.
            # Check if this identifier matches a learner code
            if identifier in learners_data:  # If the identifier is a learner code
                found_any = True
                learner = learners_data[identifier]
                
                # Format the response text with learner details
                learner_details = (f"Name:- {learner['Name']}\n"
                                   f"L.P:- {learner['L.P']}\n"
                                   f"ID:- {learner['Email']}\n"
                                   f"Type:- {learner['Type']}\n"
                                   f"Batch:- {learner['Batch']}")

                # Overlay the text on the image based on learner's Type
                image_path = overlay_text_on_image(learner_details, learner['Type'])

                # Inline buttons for learner status
                keyboard = [
                    [
                        InlineKeyboardButton("𝑰𝒏 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔 🔄", callback_data="in_progress"),
                        InlineKeyboardButton("𝑰𝒏𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ❌", callback_data="incomplete"),
                    ],
                    [
                        InlineKeyboardButton("𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ✅", callback_data="complete"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Send the image with the learner details
                with open(image_path, 'rb') as img_file:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=InputFile(img_file),
                        caption=f"{learner['Batch']}",
                        reply_markup=reply_markup  # Attach inline buttons below the image
                    )

                # Increase the message counter
                messages_sent += 1

                # Wait for 1.5 seconds before sending the next message
                if messages_sent < 5:
                    await asyncio.sleep(1.5)  # Delay between each message
                else:
                    # If 5 messages are sent, wait for an additional 3 seconds
                    await asyncio.sleep(3)

            # New code to check if this identifier matches an L.P. value (learning platform)
            for learner_code, learner_info in learners_data.items():  # Looping through all learners
                if identifier == learner_info["L.P"]:  # If the identifier matches an L.P.
                    found_any = True
                    learner = learner_info
                    
                    # Format the response text with learner details
                    learner_details = (f"Name:- {learner['Name']}\n"
                                       f"L.P:- {learner['L.P']}\n"
                                       f"ID:- {learner['Email']}\n"
                                       f"Type:- {learner['Type']}\n"
                                       f"Batch:- {learner['Batch']}")  

                    # Overlay the text on the image based on learner's Type
                    image_path = overlay_text_on_image(learner_details, learner['Type'])

                    # Inline buttons for learner status
                    keyboard = [
                        [
                            InlineKeyboardButton("𝑰𝒏 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔 🔄", callback_data="in_progress"),
                            InlineKeyboardButton("𝑰𝒏𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ❌", callback_data="incomplete"),
                        ],
                        [
                            InlineKeyboardButton("𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ✅", callback_data="complete"),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    # Send the image with the learner details
                    with open(image_path, 'rb') as img_file:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=InputFile(img_file),
                            caption=f"{learner['Batch']}",
                            reply_markup=reply_markup  # Attach inline buttons below the image
                        )

                    # Increase the message counter
                    messages_sent += 1

                    # Wait for 1.5 seconds before sending the next message
                    if messages_sent < 5:
                        await asyncio.sleep(1.5)  # Delay between each message
                    else:
                        # If 5 messages are sent, wait for an additional 3 seconds
                        await asyncio.sleep(3)

        # Check if the message contains an email address (not changed from your original code)
        if re.search(email_pattern, message_text):
            found_any = True

            # Extract email address from the message
            email_match = re.search(email_pattern, message_text)
            email_address = email_match.group(0)  # The first matching email

            # Inline buttons for email status (just send buttons, no image)
            keyboard = [
                [
                    InlineKeyboardButton("𝑰𝒏 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔 🔄", callback_data="in_progress"),
                    InlineKeyboardButton("𝑰𝒏𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ❌", callback_data="incomplete"),
                ],
                [
                    InlineKeyboardButton("𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ✅", callback_data="complete"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send the message acknowledging the email detection
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{message_text}",
                reply_markup=reply_markup  # Attach inline buttons
            )

            # Increase the message counter
            messages_sent += 1

            # Wait for 1.5 seconds before sending the next message
            if messages_sent < 5:
                await asyncio.sleep(1.5)  # Delay between each message
            else:
                # If 5 messages are sent, wait for an additional 3 seconds
                await asyncio.sleep(3)

        # Delete the original message if any learner codes, L.P., or emails were found
        if found_any:
            await update.message.delete()

# Function to handle button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    selected_option = query.data

    # Determine the current message and reply markup
    current_message = query.message
    current_markup = current_message.reply_markup

    if selected_option == "remark":
        # Reset the keyboard to allow reselection of any option
        keyboard = [
            [
                InlineKeyboardButton("𝑰𝒏 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔 🔄", callback_data="in_progress"),
                InlineKeyboardButton("𝑰𝒏𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ❌", callback_data="incomplete"),
            ],
            [
                InlineKeyboardButton("𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆 ✅", callback_data="complete"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Update the message with the reset options
        await query.edit_message_reply_markup(reply_markup=reply_markup)

# Main function to set up the bot
async def main():
    # Set up the bot
    application = ApplicationBuilder().token(token).build()

    # Command handler to trigger start message
    application.add_handler(CommandHandler('start', start))

    # Message handler to process incoming messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback query handler to handle inline button clicks
    application.add_handler(CallbackQueryHandler(button_click))

    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
