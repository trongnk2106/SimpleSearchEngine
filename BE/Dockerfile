# Base image
FROM python:3.8

# Create work directory
WORKDIR /app

# Copy forder BE vào trong container
COPY . .

# COPY requirements.txt .
# COPY your_fastapi_app.py .
RUN pip install --upgrade pip
# install dependencies
RUN pip install -r requirements.txt

# publish port 8000
EXPOSE 8000

# run app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
