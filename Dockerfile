# Use the official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and app files
COPY requirements.txt /app/
COPY app.py /app/
COPY tmp/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Google Cloud Vision credentials
COPY capstone-trial-440104-9d690ddb0c86.json /app/

# Set the environment variable for credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=capstone-trial-440104-9d690ddb0c86.json

# Expose the port that Flask runs on
EXPOSE 8080

# Command to run the Flask app
CMD ["python", "app.py"]
