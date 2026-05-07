import grpc

import calculator_pb2
import calculator_pb2_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)

        request = calculator_pb2.CalculationRequest(a=10, b=5)

        print("10 + 5 =", stub.Add(request).result)
        print("10 - 5 =", stub.Subtract(request).result)
        print("10 * 5 =", stub.Multiply(request).result)
        print("10 / 5 =", stub.Divide(request).result)


if __name__ == "__main__":
    main()
