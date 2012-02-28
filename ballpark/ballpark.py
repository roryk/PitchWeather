import yaml
import os

this_dir, this_filename = os.path.split(__file__)
parkfile = os.path.join(this_dir, "data", "ballparks.yaml")

class BallparkParser(object):

    def __init__(self):
        self.parkdata = None

    def read(self):
        this_dir, this_filename = os.path.split(__file__)
        
        """
        re-read in the yaml data
        gets returned an an array of dicts
        """
        f = open(parkfile, "r")
        self.parkdata = yaml.load(f)
