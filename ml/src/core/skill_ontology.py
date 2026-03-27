import re

class SkillOntology:
    """Centralized taxonomy and normalizer for technical and soft skills."""
    
    def __init__(self):
        # Maps variations to a canonical skill name
        self.abbreviations = {
            "js": "javascript",
            "ts": "typescript",
            "reactjs": "react",
            "react.js": "react",
            "node.js": "node",
            "nodejs": "node",
            "vuejs": "vue",
            "vue.js": "vue",
            "k8s": "kubernetes",
            "aws": "amazon web services",
            "gcp": "google cloud platform",
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "nlp": "natural language processing",
            "db": "database",
            "cpp": "c++",
            "c#": "csharp",
            "golang": "go",
            "postgres": "postgresql"
        }
        
    def normalize_skill(self, skill: str) -> str:
        """Returns the canonical lowercase string of a skill."""
        if not skill:
            return ""
        s = skill.lower().strip()
        return self.abbreviations.get(s, s)

ontology = SkillOntology()
