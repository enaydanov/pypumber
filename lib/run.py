#!/usr/bin/env python

import os
from step_definitions import StepDefinitions
from gherkin.feature import FeatureParser
#~ from reporter import load_reporters
#~ from multiplexer import Multiplexer

#~ _default_reporters_dir = os.path.join(os.path.dirname(__file__), 'reporters')


class Run(object):
    def __init__(self):
        for var in ['scenario_names', 'excludes', 'path', 'require']:
            setattr(self, var, [])
        
        for var in ['tags', 'dry_run', 'strict', 'autoformat', 'reporter', 'backtrace']:
            setattr(self, var, None)

    def __call__():
        rules = StepDefinitions()
        parser = FeatureParser()
        reporter = reporter.Multiplexer(self.reporters)

# Walk thru path, exclude  

        for path in self.path:
            rules.load(path, self.require)
        
      #~ def feature_files
        #~ potential_feature_files = @paths.map do |path|
          #~ path = path.gsub(/\\/, '/') # In case we're on windows. Globs don't work with backslashes.
          #~ path = path.chomp('/')
          #~ File.directory?(path) ? Dir["#{path}/**/*.feature"] : path
        #~ end.flatten.uniq

        #~ @options[:excludes].each do |exclude|
          #~ potential_feature_files.reject! do |path|
            #~ path =~ /#{Regexp.escape(exclude)}/
          #~ end
        #~ end

        #~ potential_feature_files
      #~ end
        
        #~ for gen in [[(os.path.dirname(path), [], os.path.basename(f))] if os.path.isfile(f) else os.walk(f) for f in self.path]:
            #~ for root, dirs, files in gen:
                
                #~ pass
        #~ for all feature under path except excluded:
            #~ run all scenarios named like scenario and with specific tags 
