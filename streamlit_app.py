import openai
import streamlit as st
import PyPDF2
from main import chat, ChatRequest, asyncio

# Change with your Assistant ID and OpenAI API Key
CHATBOT_ASSISTANT_ID = ""
OPENAI_API_KEY = ""

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Create an OpenAI client with your API key
openai_client = openai.Client(api_key=OPENAI_API_KEY)

# Retrieve the assistant you want to use
assistant = openai_client.beta.assistants.retrieve(CHATBOT_ASSISTANT_ID)

# Display an image of a robot assistant
st.image("robot_image.png", width=150)

# Create the title and subheader for the Streamlit page
st.title("Strumento AI di riassunto dei documenti")
st.subheader("Carica un documento e ti fornirò un titolo adeguato e un riassunto dei contenuti!")

# Create a file input for the user to upload a PDF
uploaded_file = st.file_uploader(
    "Upload a Document", type="pdf", label_visibility="collapsed"
)

# If the user has uploaded a file, start the assistant process...
if uploaded_file is not None:
    # Extract text from the uploaded file
    document_text = extract_text_from_pdf(uploaded_file)

    # Automatically start the assistant process without requiring user input
    user_question = "Start assistant process"

    # Create a status indicator to show the user the assistant is working
    with st.status("Processing your request...", expanded=False) as status_box:
        # Create a new thread with the document text and the user's question
        thread = openai_client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": document_text
                }
            ]
        )

        # Once the run is complete, update the status box and show the content
        status_box.update(label="Sto generando il titolo e il riassunto...", state="complete", expanded=True)

        response = asyncio.run(chat(ChatRequest(thread_id=thread.id, message=user_question, )))

        if "response" in response:
            st.markdown(response["response"])
        elif "request_problem" in response and response["request_problem"]:
            st.error("OpenAI request error: process cancelled or expired.")
        else:
            st.error("Error: OpenAI request failed.")

