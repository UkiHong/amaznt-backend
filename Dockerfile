#Start from the official lightweight Python runtime image.
FROM python:3.14-slim

#Use /app as the project root inside the container.
WORKDIR /app

#Copy dependency definitions first to reuse Docker build cache.
COPY requirements.txt .

#Install Python dependencies without keeping pip download cache.
RUN pip install --no-cache-dir -r requirements.txt

#Copy the FastAPI source package into the image.
COPY app ./app

#Ensure the local media directory exists for uploaded post images.
RUN mkdir -p media/post-images

#Document that the app listens on container port 8000.
EXPOSE 8000

#Run the FastAPI app with uvicorn when the container starts.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
