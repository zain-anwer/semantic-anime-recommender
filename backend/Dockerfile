FROM python:3.13

WORKDIR /code

# requirement file path to get python packages
COPY ./backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# fastapi server port number
EXPOSE 7860

# Command to run the backend
# 'app.main:app' assumes your FastAPI instance is named 'app' inside 'app/main.py'
# Hugging Face requires port 7860
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "7860"]