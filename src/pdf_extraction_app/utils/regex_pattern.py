import logging
import json
import os 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RegexPattern:
    def __init__(self):
        logging.info("Loading regex patterns from regex.json")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        regex_path = os.path.join(current_dir, "../utils/regex.json")
        self.regex_path = os.path.normpath(regex_path)

        with open(self.regex_path, "r") as f:
            self.patterns = json.load(f)
        logging.info(f"Loaded {len(self.patterns)} patterns")

    def get_pattern(self, pattern_name):
        return self.patterns[pattern_name]["pattern"]
    
    def _save_patterns(self):
        logging.info("Saving patterns to regex.json")
        with open(self.regex_path, "w") as f:
            json.dump(self.patterns, f, indent=4)
    
    def new_pattern(self, pattern_name, pattern, description):

        self.patterns[pattern_name] = {
            "pattern": pattern,
            "description": description
        }
        
        self._save_patterns()