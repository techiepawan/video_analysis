# Use official Python image as base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the required files
COPY requirements.txt .  
COPY main.py .  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# Expose the application port
EXPOSE 8000  

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
