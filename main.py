from packaging import version
import openai
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import time
import uvicorn

# Change with your Assistant ID and OpenAI API Key
CHATBOT_ASSISTANT_ID = ""
OPENAI_API_KEY = ""

# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

# Check if the OpenAI version is compatible
if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

# Create FastAPI app
app = FastAPI()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Request Model for Chat
class ChatRequest(BaseModel):
    thread_id: str
    message: str

# Start conversation thread
@app.get('/start')
async def start_conversation():
    print("Starting a new conversation...")
    thread = client.beta.threads.create()
    print(f"New thread created with ID: {thread.id}")
    return {"thread_id": thread.id}

# Generate response
@app.post('/chat')
async def chat(chat_request: ChatRequest):
    thread_id = chat_request.thread_id
    user_input = chat_request.message

    if not thread_id:
        print("Error: Missing thread_id")
        raise HTTPException(status_code=400, detail="Missing thread_id")

    print(f"Received message: {user_input} for thread ID: {thread_id}")
    timeinit = time.time()
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=CHATBOT_ASSISTANT_ID)
    end = False
    request_problem = False
    while not end:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed' or run_status.status == "cancelled" or run_status.status == "expired":
            end = True
            if run_status.status == "cancelled" or run_status.status == "expired":
                request_problem = True
        
        await asyncio.sleep(1)  # Using asyncio.sleep instead of time.sleep

    if not request_problem:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value
        # print elapsed seconds
        print(f"Elapsed time: {time.time() - timeinit}")
        print(f"Assistant response: {response}")
    else:
         response = "OpenAI request error"
    return {"response": response}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)