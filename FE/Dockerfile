# Base image
FROM python:3.8

# create work directory
WORKDIR /app

# copy folder FE into container
COPY . .
# COPY requirements.txt .
# COPY your_streamlit_app.py .
RUN pip install --upgrade pip
# install dependencies
RUN pip install -r requirements.txt

# publish port 8501
EXPOSE 8501

# run app
CMD ["streamlit", "run", "FE.py"]