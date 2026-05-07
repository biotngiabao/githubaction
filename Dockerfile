FROM python:3.13-slim

WORKDIR /src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /src
COPY tests/ /tests


RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    calculator.proto

CMD [ "python", "server.py" ]
