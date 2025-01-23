# Use official Python image with slim variant for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies directly using pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
