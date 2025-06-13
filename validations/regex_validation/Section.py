
class SectionInfo:
    """Class to store section information with metrics for voting."""
    def __init__(self, section_number, section_title, page_number = 0, position = 0, bold = False, size = 0, metrics=None, all_section=""):
        self.section_number = section_number
        self.section_title = section_title
        self.page_number = page_number
        self.all_section = all_section
        self.position = position
        self.content = ""
        self.metrics = metrics or {}
        self.bold = bold
        self.size = size
        self.all_caps = section_title.isupper()
        self.confidence_score = 0
    
    def update_metrics(self, metric_name, value):
        """Update metrics dictionary with new metric."""
        self.metrics[metric_name] = value
        
    def calculate_confidence_score(self):
        """Calculate confidence score based on metrics."""
        score = 0
        weights = {
            "is_bold": 2,
            "is_capital": 2,
            "has_section_number": 3,
            "font_size_larger": 2,
            "has_common_title": 4,
            "has_no_ponctuation": 2,
        }
        
        for metric, value in self.metrics.items():
            if metric in weights and value:
                score += weights[metric]
        
        self.confidence_score = score
        return score

    def get_title(self):
        """Return the section title."""
        return self.section_number + self.section_title
    
    def __str__(self):
        return f"Section {self.section_number}: {self.section_title} (Page {self.page_number}, Score: {self.confidence_score})"