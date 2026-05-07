FROM python:3.13-slim 

WORKDIR /code
COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt

COPY /src /code
COPY /tests /tests


RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    calculator.proto

CMD [ "python", "server.py" ]
