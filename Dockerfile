FROM python:3.13-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY tests/ ./tests


RUN python -m grpc_tools.protoc \
    -I src \
    --python_out=src \
    --grpc_python_out=src \
    src/calculator.proto

CMD [ "python", "src/server.py" ]
