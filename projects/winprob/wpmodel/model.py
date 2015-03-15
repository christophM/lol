## Code for model training (for production) and to use model in production
"""
Contains the whole model pipeline 
match dictionairy -> win probability path
"""
import json
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
from features import FeatureBuilder, get_labels
from sklearn.pipeline import Pipeline
import cPickle
import os

class WinProbabilityPipeline():

    def __init__(self):
        pass

    def from_file(self, filename):
        # load it again
        with open(filename, 'rb') as fid:
            self.pipeline = cPickle.load(fid)

    def predict(self, match, reference_team=100):
        flag = 1 if reference_team == 100 else 0
        return [x[flag] for x in self.pipeline.predict_proba([match])]

    def train(self, matches):
        fb = FeatureBuilder(kind="production")
        clf = RandomForestClassifier(n_estimators=200, verbose=0, min_samples_leaf=100, 
                                 min_samples_split=100, random_state=42, n_jobs=2)        
        self.pipeline = Pipeline([("build features", fb), ("classifier", clf)])
        labels = get_labels(matches)
        self.pipeline.fit(matches, labels)
        

    def load_match(self, filename, matches_dir):
        with open(matches_dir + "/" + filename) as f:
            match = json.load(f)
        return match

    def load_matches(self, matches_dir):
        matches_dict = [self.load_match(fn, matches_dir) for fn in os.listdir(matches_dir)]
        ## Keep only matches with included timeline
        matches_dict = [match for match in matches_dict if "timeline" in match.keys()]
        return matches_dict


    def to_file(self, pipeline_filename):
        # save the classifier
        with open(pipeline_filename, 'wb') as fid:
            cPickle.dump(self.pipeline, fid)    



if __name__ == "__main__":
    wp = WinProbabilityPipeline()
    matches_dir = "../data/timelines"
    matches = wp.load_matches(matches_dir)[0:10]
    print "Training random forest"
    wp.train(matches)
    print "Writing pipeline to disk"
    wp.to_file("../model-serialized/wp-pipeline.pkl")
