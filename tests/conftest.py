import os
import sys
from concurrent import futures
from pathlib import Path
from typing import Any, Sequence

import grpc
import pytest
from grpc_tools import protoc


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from src import calculator_pb2_grpc 
from server import CalculatorService  # noqa: E402


class _ClientCallDetails(grpc.ClientCallDetails):
    def __init__(
        self,
        method: str,
        timeout: float | None,
        metadata: Sequence[tuple[str, str]] | None,
        credentials: grpc.CallCredentials | None,
        wait_for_ready: bool | None,
        compression: grpc.Compression | None,
    ):
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


class _AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, token: str):
        self._token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = list(client_call_details.metadata or [])
        metadata.append(("x-authorization", self._token))

        new_details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=metadata,
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready,
            compression=client_call_details.compression,
        )
        return continuation(new_details, request)


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--grpc-target",
        action="store",
        default=os.getenv("CALCULATOR_GRPC_TARGET", ""),
        help="External calculator gRPC server target (host:port).",
    )
    parser.addoption(
        "--grpc-timeout",
        action="store",
        type=float,
        default=float(os.getenv("CALCULATOR_GRPC_TIMEOUT", "10")),
        help="Timeout (seconds) used while waiting for gRPC channel readiness.",
    )
    parser.addoption(
        "--grpc-api-token",
        action="store",
        default=os.getenv("CALCULATOR_API_TOKEN", ""),
        help="Optional x-authorization token added to every gRPC call.",
    )


@pytest.fixture(scope="session")
def grpc_timeout(pytestconfig) -> float:
    return float(pytestconfig.getoption("grpc_timeout"))


@pytest.fixture(scope="session")
def grpc_api_token(pytestconfig) -> str:
    return pytestconfig.getoption("grpc_api_token")


@pytest.fixture(scope="session")
def grpc_address(pytestconfig) -> str:
    external_target = pytestconfig.getoption("grpc_target")
    if external_target:
        return external_target

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorService(), server)
    port = server.add_insecure_port("[::]:0")
    server.start()

    pytestconfig._calculator_grpc_server = server
    return f"127.0.0.1:{port}"


@pytest.fixture(scope="session", autouse=True)
def stop_grpc_server(pytestconfig):
    yield

    server = getattr(pytestconfig, "_calculator_grpc_server", None)
    if server is not None:
        server.stop(grace=0)


@pytest.fixture
def grpc_channel(grpc_address: str, grpc_timeout: float, grpc_api_token: str):
    base_channel = grpc.insecure_channel(grpc_address)
    channel = (
        grpc.intercept_channel(base_channel, _AuthInterceptor(grpc_api_token))
        if grpc_api_token
        else base_channel
    )
    grpc.channel_ready_future(base_channel).result(timeout=grpc_timeout)

    try:
        yield channel
    finally:
        base_channel.close()


@pytest.fixture
def grpc_stub(grpc_channel) -> calculator_pb2_grpc.CalculatorStub:
    return calculator_pb2_grpc.CalculatorStub(grpc_channel)
