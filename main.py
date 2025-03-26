import google.generativeai as genai
import os

from dotenv import load_dotenv

load_dotenv("./.env")

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("The opposite of hot is")
print(response.text)