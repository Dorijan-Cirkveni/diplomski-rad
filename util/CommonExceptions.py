class ImplementAsNeededException(Exception):
    def __init__(self,message="Apparently, we need this now"):
        super().__init__(message)


def main():
    raise ImplementAsNeededException()


if __name__ == "__main__":
    main()
