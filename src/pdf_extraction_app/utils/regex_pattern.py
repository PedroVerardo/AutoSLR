import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RegexPattern:
    """Class for storing regex patterns and their descriptions."""
    
    def __init__(self):
        logging.info("Loading regex patterns from regex.json")
        with open("./regex.json", "r") as f:
            self.patterns = json.load(f)
        logging.info(f"Loaded {len(self.patterns)} patterns")

    def get_pattern(self, pattern_name):
        return self.patterns[pattern_name]["pattern"]
    
    def _save_patterns(self):
        logging.info("Saving patterns to regex.json")
        with open("./regex.json", "w") as f:
            json.dump(self.patterns, f, indent=4)
    
    def new_pattern(self, pattern_name, pattern, description):

        self.patterns[pattern_name] = {
            "pattern": pattern,
            "description": description
        }
        
        self._save_patterns()