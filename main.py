from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from agent.agent import get_chat_agent
from contextlib import asynccontextmanager
import asyncio
import httpx
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()


PING_URL = os.getenv("PING_URL")


async def ping_self():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(PING_URL)
                print(f"Pinged {PING_URL} | Status: {response.status_code}")
        except Exception as e:
            print(f"Ping failed: {e}")
        await asyncio.sleep(600)  # every 10 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(ping_self())
    yield
    # Shutdown (optional cleanup logic can go here)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "FastAPI is alive!"}


@app.post("/reply")
async def reply(request: Request):
    try:

        # Parse incoming WhatsApp message from Twilio
        form = await request.form()
        incoming_msg = form.get("Body", "").strip().lower()
        sender = form.get("From", "")

        # Initialize the chat agent
        agent = get_chat_agent(user_id=sender, session_id=sender)

        # Prepare TwiML response
        response = MessagingResponse()
        msg = response.message()

        # Simple logic to personalize response
        reply = agent.run(incoming_msg, stream=False)
        msg.body(reply.content)

        # Return valid TwiML XML with correct content-type
        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        # If something goes wrong, return a basic TwiML error
        error_response = MessagingResponse()
        error_response.message(f"An error occurred: {str(e)}")
        return Response(content=str(error_response), media_type="application/xml")
    
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=5)
