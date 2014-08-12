__author__ = "Alexander Weigl"

from restflow.hf3binding import Hiflow3Session


def main():
    session = Hiflow3Session("/tmp/restflow_test")

    session.update_hf3(
        {"Param":
             {
                 "ElasticityModel": {
                     "density": 2,
                     "gravity": 9.81,
                     "lambda": 1020562,
                     "mu": 22,
                 },
                 'Instationary': {'MaxTimeStepIts': 2},
                 'Mesh': {
                     'Filename': "/homes/students/weigl/workspace1/restflow/tmp/logoz.vtu"
                 }
             }
        })

    ids = session.run()
    print session.get_result_files()
    #print ids

"__main__" == __name__ and main()