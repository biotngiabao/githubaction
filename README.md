# githubaction

## Python gRPC Calculator

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Generate gRPC Python files:

```bash
python3 -m grpc_tools.protoc -I src --python_out=src --grpc_python_out=src src/calculator.proto
```

Run the server:

```bash
python3 src/server.py
```

In another terminal, run the client:

```bash
python3 src/client.py
```

Run integration tests:

```bash
pytest
```

To test against an already-running server instead of the in-process test server:

```bash
pytest --grpc-target 127.0.0.1:50051
```
