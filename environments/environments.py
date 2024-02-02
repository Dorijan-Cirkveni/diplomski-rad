import GridEnvironment as gren

ALL_ENVIRONMENTS = dict()


def getEnvironment(type, filename, ID):
    if type == "base":
        env = gren.readPlaneEnvironment(filename, ID)
        return env


def getEnvironments(type, ):
    if type == "base":
        env = gren.readPlaneEnvironment(filename, ID)
        return env


def getEnvironmentGroups(type, filename, ID):
    if type == "base":
        env = gren.readPlaneEnvironment(filename, ID)
        return env


def main():
    return


if __name__ == "__main__":
    main()
