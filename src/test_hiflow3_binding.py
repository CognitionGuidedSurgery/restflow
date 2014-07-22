__author__ = "Alexander Weigl"

from restflow.hiflow3 import Hiflow3Session

def main():
    session = Hiflow3Session("tmp/")
    session.hf3['Param']['Mesh']['Filename'] = 'tmp/bunny.vtu'
    session.run()

"__main__" == __name__ and main()