import logging

from assignment_3.part3_server import part3_server


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    part3_server()


if __name__ == "__main__":
    main()
