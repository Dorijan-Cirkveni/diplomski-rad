def differing_parameters(ins1, ins2):
    attrs1 = vars(ins1)
    attrs2 = vars(ins2)

    differing_params = {key: (attrs1[key], attrs2[key]) for key in attrs1 if attrs1[key] != attrs2[key]}

    return differing_params


def main():
    return


if __name__ == "__main__":
    main()
