# Base image
FROM python:3.8

# create work directory
WORKDIR /app

# copy folder FE into container
COPY FE/ .
# COPY requirements.txt .
# COPY your_streamlit_app.py .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# publish port 8501
EXPOSE 8501

# run app
CMD ["streamlit", "run", "your_streamlit_app.py"]