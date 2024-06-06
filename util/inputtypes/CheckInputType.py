def isinteger(s):
    if s[0] in '+-':
        s=s[1:]
    return s.isdigit()

def main():
    return


if __name__ == "__main__":
    print(isinteger('0'))
    main()
