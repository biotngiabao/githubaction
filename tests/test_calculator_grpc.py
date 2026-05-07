import grpc
import pytest

import calculator_pb2


def test_calculator_basic_operations(grpc_stub):
    request = calculator_pb2.CalculationRequest(a=10, b=5)

    assert grpc_stub.Add(request).result == 15
    assert grpc_stub.Subtract(request).result == 5
    assert grpc_stub.Multiply(request).result == 50
    assert grpc_stub.Divide(request).result == 2


def test_calculator_divide_by_zero_returns_invalid_argument(grpc_stub):
    request = calculator_pb2.CalculationRequest(a=10, b=0)

    with pytest.raises(grpc.RpcError) as exc_info:
        grpc_stub.Divide(request)

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert "Cannot divide by zero" in exc_info.value.details()
