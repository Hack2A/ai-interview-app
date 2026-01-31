import json
import logging
from config import settings
from llama_cpp import Llama

logger = logging.getLogger("Evaluator")

class Evaluator:
    def __init__(self, model_path):
        self.model_path = model_path

    def generate_report(self, history):
        
        logger.info("Generating Final Evaluation Report...")
        
        
        if len(history) < 1:
            return {
                "score": 0,
                "mistakes": ["Interview was terminated too early."],
                "suggestions": ["Please complete a full session for analysis."],
                "domain_rating": {"status": "Insufficient Data"},
                "swot_analysis": {
                    "strengths": ["Insufficient data"],
                    "weaknesses": ["Interview incomplete"],
                    "opportunities": ["Complete full interview for detailed analysis"],
                    "threats": ["Unable to assess"]
                }
            }

        llm = Llama(
            model_path=str(self.model_path),
            n_ctx=4096,
            verbose=False
        )

        
        prompt = (
            "You are a strict Senior Technical Hiring Manager. Analyze the interview transcript below.\n"
            "RULES:\n"
            "1. If a topic (HR, DSA, System Design) was NOT discussed, set its rating to -1.\n"
            "2. If the candidate gave short, lazy, or refusal answers (e.g., 'I am not ready'), score them 0.\n"
            "3. Do not hallucinate. Only evaluate what is explicitly in the text.\n"
            "4. Output strictly valid JSON.\n\n"
            "Transcript:\n" + json.dumps(history) + "\n\n"
            "Output Format:\n"
            "{\n"
            '  "score": (int 0-100, be harsh),\n'
            '  "mistakes": [list of specific errors],\n'
            '  "suggestions": [list of actionable advice],\n'
            '  "domain_rating": {"hr": int, "technical": int, "communication": int},\n'
            '  "swot_analysis": {\n'
            '    "strengths": [list of 3-5 key strengths],\n'
            '    "weaknesses": [list of 3-5 weaknesses],\n'
            '    "opportunities": [list of 3-5 growth opportunities],\n'
            '    "threats": [list of 3-5 potential concerns]\n'
            '  }\n'
            "}"
        )

        output = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(output['choices'][0]['message']['content'])
        except Exception as e:
            logger.error(f"Failed to parse JSON evaluation: {e}")
            return {"error": "Report Generation Failed", "raw": output}