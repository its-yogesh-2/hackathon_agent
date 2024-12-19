# Pathway Agents Application

This is an Application that will help you learn.
This will use Autogen agents in FastApi based backend and React for webapp devlopment.
**FastApi Backend**: A FastApi application running autogen.
**Webapp**: React webapp using websocket to communicate with FastApi.

## Running the application

1. **Clone this repo**
```
git clone https://github.com/yogeshjangra/pathway_agent.git
cd agent_chatbot_hackathon
```
2. **Configure backend**

Configure python deps
```
cd backend
pip install -r ./requirements.txt 
```

Add your Openai key to .env inside src folder
```
cd backend/src (edit .env and add your key)
```

Start backend server inside src folder
```
python main.py
```
You should see

```
INFO:     Started server process [85614]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

2. **Configure frontend**

Open a new terminal and go to the react-frontend folder (you need to have nodejs installed and npm >= v14 )
```
cd autogenwebdemo/react-frontend
npm install
npm run dev
```
Open you browser on http://localhost:5173/ or the port shown 

![chat interface](/chat_demo.png "Chat")

Have fun!

