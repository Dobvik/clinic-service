"""Запуск: python -m app [--demo] [--port 8000]."""

import argparse

import uvicorn

from app.main import create_app


def port_number(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("порт должен быть целым числом") from error
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("порт должен быть от 1 до 65535")
    return port


def main() -> None:
    parser = argparse.ArgumentParser(description="Учебная информационная система поликлиник")
    parser.add_argument(
        "--demo", action="store_true", help="добавить примеры в полностью пустую базу"
    )
    parser.add_argument(
        "--port", type=port_number, default=8000, help="порт сервера (по умолчанию 8000)"
    )
    args = parser.parse_args()
    uvicorn.run(create_app(demo=args.demo), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
