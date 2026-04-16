FROM python:3.13

WORKDIR /code

# 1. Changed path: Simply copy it from the current directory
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# fastapi server port number
EXPOSE 7860

# 2. Changed CMD: Since server.py is in the same folder, we don't need 'backend.'
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]