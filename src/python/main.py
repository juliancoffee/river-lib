from parse import tokenize, ParseError
from os import PathLike, listdir


def tokenize_file(src_file: PathLike):
    with open(src_file) as src:
        return tokenize(src.read())


def tests():
    print("TESTS")
    for src_file in listdir("riv"):
        print(">>>", src_file)
        try:
            tokenized = tokenize_file("riv/" + src_file)
            print(tokenized, end="\n\n")
        except ParseError as e:
            print("fail", e, end="\n\n")
    print("TESTS\n\n")


def test_file(src_file):
    print(src_file)
    tokenized = tokenize_file("riv/" + src_file)
    print(tokenized)


def main():
    tests()
    test_file("setOfSet.riv")
    # test_file("listOfInt.riv")
    # test_file("listOfSetOfList.riv")


if __name__ == "__main__":
    main()
