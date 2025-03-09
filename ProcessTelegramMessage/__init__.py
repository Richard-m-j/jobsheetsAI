# from typing import Optional, List
# from langchain_openai import AzureChatOpenAI
# from pydantic import BaseModel, Field
# from dotenv import load_dotenv
# import asyncio
# import traceback
# import logging
# from telethon import TelegramClient, events
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import os
# from datetime import datetime
# import glob

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
# )

# logging.info("Starting the application...")

# # Load environment variables
# load_dotenv()

# # Validate and log environment variables
# def validate_env_vars():
#     logging.info("Validating environment variables...")
#     env_vars = {
#         "GOOGLE_SHEET_NAME": os.getenv("GOOGLE_SHEET_NAME"),
#         "TELEGRAM_API_ID": os.getenv("TELEGRAM_API_ID"),
#         "TELEGRAM_API_HASH": os.getenv("TELEGRAM_API_HASH"),
#         "TELEGRAM_PHONE": os.getenv("TELEGRAM_PHONE"),
#         "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
#         "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
#         "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
#         "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
#     }

#     missing_vars = [key for key, value in env_vars.items() if not value]
#     if missing_vars:
#         logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
#         return False

#     for key, value in env_vars.items():
#         logging.info(f"Environment variable '{key}' is correctly set.")
    
#     return True

# if not validate_env_vars():
#     logging.error("Exiting due to missing environment variables.")
#     exit(1)

# GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
# API_ID = os.getenv("TELEGRAM_API_ID")
# API_HASH = os.getenv("TELEGRAM_API_HASH")
# PHONE_NUM = os.getenv("TELEGRAM_PHONE")
# CHANNELS = ["https://t.me/dot_aware", "https://t.me/OceanOfJobs"]

# # Azure OpenAI Configuration
# AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
# AZURE_API_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# # Initialize the Azure OpenAI client
# try:
#     logging.info("Initializing Azure OpenAI client...")
#     client = AzureChatOpenAI(
#         azure_deployment=AZURE_DEPLOYMENT_NAME,
#         api_version=AZURE_API_VERSION,
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#     )
#     logging.info("Azure OpenAI client initialized successfully.")
# except Exception as e:
#     logging.error(f"Failed to initialize Azure OpenAI client: {e}")
#     logging.error(traceback.format_exc())
#     exit(1)

# CREDENTIALS_FILES = glob.glob("*.json")
# logging.info(f"Found {len(CREDENTIALS_FILES)} Google Sheets credentials files: {CREDENTIALS_FILES}")

# # Structured Output Schema with Pydantic
# class JobDetails(BaseModel):
#     company_name: str = Field(description="The name of the company.")
#     job_role: str = Field(description="The specific job role or position.")
#     ctc: Optional[str] = Field(description="Cost to Company or salary information.")
#     application_link: Optional[str] = Field(description="The URL or link to apply for the job.")

# structured_client = client.with_structured_output(JobDetails)

# # Azure OpenAI Function to Extract Job Details
# def extract_job_details(message: str) -> JobDetails:
#     logging.info(f"Extracting job details from message: {message[:100]}...")
#     prompt = [
#         {
#             "role": "system",
#             "content": """
#             Extract the following details from the message if it's a job posting:
#             - Company Name
#             - Job Role
#             - CTC (Cost to Company / Salary)
#             - Application Link
#             Return the details as a JSON object with keys: company_name, job_role, ctc, application_link.
#             If any information is missing, leave its value as an empty string.
#             """
#         },
#         {"role": "user", "content": message},
#     ]
#     try:
#         response = structured_client.invoke(prompt)
#         logging.info(f"Extracted job details: {response}")
#         return response
#     except Exception as e:
#         logging.error(f"Error in Azure OpenAI: {e}")
#         logging.error(traceback.format_exc())
#         return JobDetails(company_name="", job_role="", ctc="", application_link="")

# # Google Sheets Helper Functions
# def connect_to_google_sheet(credentials_file: str):
#     logging.info(f"Connecting to Google Sheet with credentials: {credentials_file}")
#     scope = [
#         "https://spreadsheets.google.com/feeds",
#         "https://www.googleapis.com/auth/drive",
#     ]
#     try:
#         creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
#         client = gspread.authorize(creds)
#         sheet = client.open(GOOGLE_SHEET_NAME).sheet1
#         logging.info(f"Connected to Google Sheet: {sheet.title}")
#         return sheet
#     except Exception as e:
#         logging.error(f"Failed to connect to Google Sheet ({credentials_file}): {e}")
#         logging.error(traceback.format_exc())
#         raise e

# def append_to_google_sheets(sheets, data: JobDetails):
#     logging.info(f"Appending data to sheets: {data}")
#     for sheet in sheets:
#         try:
#             sheet.append_row(
#                 [
#                     data.company_name,
#                     data.job_role,
#                     data.ctc,
#                     data.application_link,
#                 ]
#             )
#             logging.info(f"Appended data to Google Sheet: {sheet.title}")
#         except Exception as e:
#             logging.error(f"Failed to append data to Google Sheet: {sheet.title}: {e}")
#             logging.error(traceback.format_exc())

# # Process Messages
# def process_message(message_text: str, sheets):
#     logging.info(f"Processing message: {message_text[:100]}")
#     try:
#         job_details = extract_job_details(message_text)
#         if any([job_details.company_name, job_details.job_role, job_details.ctc, job_details.application_link]):
#             logging.info("Valid job details found.")
#             append_to_google_sheets(sheets, job_details)
#         else:
#             logging.warning("No job details extracted from the message.")
#     except Exception as e:
#         logging.error(f"Error processing message: {e}")
#         logging.error(traceback.format_exc())

# # Telegram Event Handlers
# async def handle_new_message(event, sheets):
#     logging.info(f"New message received: {event.raw_text[:100]}")
#     process_message(event.raw_text, sheets)

# # Main Workflow
# async def main():
#     try:
#         logging.info("Initializing Telegram client...")
#         client_telegram = TelegramClient("Session", API_ID, API_HASH)
#         await client_telegram.start()
#         logging.info("Successfully connected to Telegram!")

#         # Connect to Google Sheets
#         sheets = []
#         logging.info("Connecting to Google Sheets...")
#         for credentials_file in CREDENTIALS_FILES:
#             try:
#                 sheet = connect_to_google_sheet(credentials_file)
#                 sheets.append(sheet)
#             except Exception as e:
#                 logging.warning(f"Skipping Google Sheets credentials file: {credentials_file}")

#         if not sheets:
#             logging.error("No Google Sheets connections available. Exiting.")
#             return

#         # Get channel entities
#         channel_entities = []
#         for channel in CHANNELS:
#             try:
#                 entity = await client_telegram.get_entity(channel.strip())
#                 channel_entities.append(entity)
#                 logging.info(f"Listening to messages from channel: {entity.title}")
#             except Exception as e:
#                 logging.error(f"Failed to get entity for channel {channel}: {e}")

#         # Fetch and process messages
#         now = datetime.utcnow()
#         start_of_day = datetime(now.year, now.month, now.day)
#         logging.info(f"Fetching messages since: {start_of_day}")

#         for entity in channel_entities:
#             try:
#                 async for msg in client_telegram.iter_messages(entity, offset_date=start_of_day, reverse=True):
#                     if msg.message:
#                         process_message(msg.message, sheets)
#             except Exception as e:
#                 logging.error(f"Error processing messages from channel {entity.title}: {e}")

#         # Event listener for new messages
#         @client_telegram.on(events.NewMessage(chats=channel_entities))
#         async def new_message_listener(event):
#             await handle_new_message(event, sheets)

#         logging.info("Listening for new messages...")
#         await client_telegram.run_until_disconnected()

#     except Exception as e:
#         logging.error(f"Error in main workflow: {e}")
#         logging.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        logging.info("Starting main function...")
#         # asyncio.run(main())
#     # except KeyboardInterrupt:
#     #     logging.info("Program terminated by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        logging.error(traceback.format_exc())
