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


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 0, 0),
        (-10, 5, -5),
        (10, -5, 5),
        (-10, -5, -15),
        (2.5, 1.25, 3.75),
    ],
)
def test_calculator_add_cases(grpc_stub, a, b, expected):
    request = calculator_pb2.CalculationRequest(a=a, b=b)

    assert grpc_stub.Add(request).result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 0, 0),
        (-10, 5, -15),
        (10, -5, 15),
        (-10, -5, -5),
        (2.5, 1.25, 1.25),
    ],
)
def test_calculator_subtract_cases(grpc_stub, a, b, expected):
    request = calculator_pb2.CalculationRequest(a=a, b=b)

    assert grpc_stub.Subtract(request).result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 10, 0),
        (-10, 5, -50),
        (10, -5, -50),
        (-10, -5, 50),
        (2.5, 4, 10),
    ],
)
def test_calculator_multiply_cases(grpc_stub, a, b, expected):
    request = calculator_pb2.CalculationRequest(a=a, b=b)

    assert grpc_stub.Multiply(request).result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 10, 0),
        (-10, 5, -2),
        (10, -5, -2),
        (-10, -5, 2),
        (7, 2, 3.5),
    ],
)
def test_calculator_divide_cases(grpc_stub, a, b, expected):
    request = calculator_pb2.CalculationRequest(a=a, b=b)

    assert grpc_stub.Divide(request).result == pytest.approx(expected)
