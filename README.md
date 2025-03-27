# chat-service

# 🚀 Chat Service Backend

This is the backend service for the **VR4VET Chatbot**, built with **FastAPI**.

## 📦 Installation

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/vr4vet/chat-service.git
cd chat-service
```

### **2️⃣ Set Up a Virtual Environment (Recommended)**
It’s best to install dependencies inside a virtual environment:

follow manual for updating requirements

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

# 🚀 Running the Service Locally

### **1️⃣ Start the FastAPI Server**
Run the following command:

```sh
uvicorn src.main:app --reload
```
The service will now be available at:

Docs UI: http://127.0.0.1:8000/docs
API Root: http://127.0.0.1:8000

### **2️⃣ Verify the /ping Endpoint**
Check if the service is running:
The `/ping` endpoint is used to check if the backend is running.

```sh
curl http://127.0.0.1:8000/ping
```
✅ Expected response:
```sh
{"status":"I AM ALIVE!"}
```



##  Running the Service with Docker

This service can be containerized using **Docker** for easy deployment.

### 1️ Build the Docker Image
Run the following command to build the Docker image:

```sh
docker build -t chat-service .
```

### 2 Run the Docker Container
Once the image is built, start the container:

```sh
docker run -p 8000:8000 chat-service
```
The service should now be running at http://127.0.0.1:8000.

### 3 Verify the Service
Test if the service is running by making a request to the /ping endpoint:

# Using cURL:
```sh
curl http://127.0.0.1:8000/ping
```
Expected Response:
{"status":"I AM ALIVE!"}

### 4 Stop the Running Container
To stop the running container:
```sh
docker ps  # Get container ID
docker stop <container_id>
```

### 5 Debugging (Optional)
If the service is not running as expected:

Check running containers:
```sh
docker ps
```
View logs:
```sh
docker logs <container_id>
```
# 📌 Notes
Make sure Docker is installed and running before executing these commands.
The Dockerfile is designed to expose port 8000, so ensure no other service is using this port.

# Testing
without docker:
```bash
pytest --cov=src --cov-report=term-missing
```

# 6 test enpoint with mock data
### curl command to test the endpoint:

curl -X POST "http://localhost:8000/api/progress" \
-H "Content-Type: application/json" \
-d '{
  "taskName": "Daily Exercise Routine",
  "status": "start",
  "userId": "user123",
  "subtaskProgress": [
    {
      "subtaskName": "Warm Up",
      "description": "Prepare muscles for workout",
      "completed": false,
      "stepProgress": [
        {
          "stepName": "Jumping Jacks",
          "repetitionNumber": 30,
          "completed": false
        },
        {
          "stepName": "Arm Circles",
          "repetitionNumber": 20,
          "completed": false
        }
      ]
    },
    {
      "subtaskName": "Main Workout",
      "description": "Intense exercise session",
      "completed": false,
      "stepProgress": [
        {
          "stepName": "Push Ups",
          "repetitionNumber": 50,
          "completed": false
        }
      ]
    }
  ]
}

curl -X POST "http://localhost:8000/api/progress" \
-H "Content-Type: application/json" \
-d '{
  "taskName": "Daily Exercise Routine",
  "status": "complete",
  "userId": "user123",
  "subtaskProgress": [
    {
      "subtaskName": "Warm Up",
      "description": "Prepare muscles for workout",
      "completed": true,
      "stepProgress": [
        {
          "stepName": "Jumping Jacks",
          "repetitionNumber": 30,
          "completed": true
        },
        {
          "stepName": "Arm Circles",
          "repetitionNumber": 20,
          "completed": true
        }
      ]
    },
    {
      "subtaskName": "Main Workout",
      "description": "Intense exercise session",
      "completed": true,
      "stepProgress": [
        {
          "stepName": "Push Ups",
          "repetitionNumber": 50,
          "completed": true
        }
      ]
    }
  ]
}'

### Receive the log
curl -X GET "http://localhost:8000/api/progress"




## How To Upload Document

### Set-Up

First, make sure [Docker Desktop](https://docs.docker.com/desktop/) is installed and running. 
Then navigate to the right directory
``cd path/to/chat-service``
and run
``docker-compose up -d`` (Make sure ENV = 'prod' in .env)
This starts:

- The FastAPI service (chat-service)
- Redis
- MongoDB

Verify they’re running with:
``docker ps``
You should see containers like chat-service, mongodb, and redis.

### Uploading through the API

If the previous step is successful, you can now access the API by [Clicking Here](http://127.0.0.1:8000/docs) or typing ``http://127.0.0.1:8000/docs`` into your browser.

Use the [Upload Endpoint](http://localhost:8000/docs#/default/upload_document_upload__post) to upload a .md or .txt file by clicking 'Try it out' then clicking the 'Choose File' button and finding the file you want to upload before clicking the 'Execute' button.

### Uploading through the Terminal

To upload through the terminal, you'll still need to go through the set up. Once this is done, follow these instructions:

*PowerShell:*
``
Invoke-WebRequest -Uri "http://localhost:8000/upload/?NPC=0" `
  -Method Post `
  -Form @{ file = Get-Item "EXAMPLE.txt" } `
  -ContentType "multipart/form-data"
``



