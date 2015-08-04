__author__ = 'jwely'

def build_dev_env():
    """
    builds the development environment used to create autodocs through
    sphinx.
    """
    import pip
    sphinx = pip.main(["install","sphinx"])
    graphviz = pip.main(["install","graphviz"])

    if sphinx == 0 and graphviz == 0:
        print("Modules ready!, ensure sphinx-build is added to PATH and continue!")


def main():
    build_dev_env()


if __name__ == "__main__":
    main()

