__author__ = 'jwely'


from subprocess import call

def build_sphinx():
    """
    runs sphinx build command to update website docs
    """
    call(["sphinx-build", "-b", "html", "docs/source", "docs/build"])

if __name__ == "__main__":
    build_sphinx()

    