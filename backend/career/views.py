import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .apps import get_career_orchestrator

logger = logging.getLogger('career')


CAREER_OPTIONS_SCHEMA = [
    {
        "id": "match_report",
        "title": "Match Report",
        "description": "Compares your resume against a job description to give you a match score.",
        "inputs": [
            {"name": "resume_text", "label": "Resume Text", "type": "textarea", "required": True},
            {"name": "jd_text", "label": "Job Description", "type": "textarea", "required": True}
        ]
    },
    {
        "id": "cover_letter",
        "title": "Cover Letter",
        "description": "Generates a customized cover letter based on your resume and the JD.",
        "inputs": [
            {"name": "resume_text", "label": "Resume Text", "type": "textarea", "required": True},
            {"name": "jd_text", "label": "Job Description", "type": "textarea", "required": True},
            {"name": "tone", "label": "Tone", "type": "text", "required": False, "default": "professional"}
        ]
    },
    {
        "id": "skill_gap",
        "title": "Skill Gap Analysis",
        "description": "Identifies missing skills between you and the job.",
        "inputs": [
            {"name": "resume_text", "label": "Resume Text", "type": "textarea", "required": True},
            {"name": "jd_text", "label": "Job Description", "type": "textarea", "required": True}
        ]
    },
    {
        "id": "roadmap",
        "title": "Learning Roadmap",
        "description": "Generates a step-by-step learning roadmap for a specific topic.",
        "inputs": [
            {"name": "topic", "label": "Topic", "type": "text", "required": True},
            {"name": "context", "label": "Context/Current Level", "type": "textarea", "required": False}
        ]
    },
    {
        "id": "recruiter_sim",
        "title": "Recruiter Simulator",
        "description": "Simulates a recruiter's evaluation of your profile.",
        "inputs": [
            {"name": "resume_text", "label": "Resume Text", "type": "textarea", "required": True},
            {"name": "jd_text", "label": "Job Description", "type": "textarea", "required": True}
        ]
    },
    {
        "id": "extract_projects",
        "title": "Extract Projects",
        "description": "Extracts project details from a raw resume.",
        "inputs": [
            {"name": "raw_text", "label": "Resume Text", "type": "textarea", "required": True}
        ]
    },
    {
        "id": "industry_calibrate",
        "title": "Industry Calibrate",
        "description": "Calibrates resume phrasing for different industries.",
        "inputs": [
            {"name": "resume_text", "label": "Resume Text", "type": "textarea", "required": True},
            {"name": "mode", "label": "Industry Mode", "type": "text", "required": False, "default": "startup"}
        ]
    }
]

class CareerOptionsView(APIView):
    """
    Returns the schema of all available career actions to help the frontend
    render the dynamic forms and options list.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"options": CAREER_OPTIONS_SCHEMA}, status=status.HTTP_200_OK)


class CareerActionView(APIView):
    """
    Handle ML career actions dynamically based on 'action' parameter in POST request.
    Example payload:
    {
        "action": "tone_detect",
        "text": "I lead the team to success"
    }
    """
    # Using AllowAny for now as per generic structure, 
    # but could be changed to IsAuthenticated later if needed.
    permission_classes = [AllowAny]

    def post(self, request):
        action = request.data.get('action')
        if not action:
            return Response(
                {"error": "Missing 'action' parameter in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            orch = get_career_orchestrator()
        except Exception as e:
            logger.error(f"Failed to load the career orchestrator: {e}")
            return Response(
                {"error": "ML Orchestrator failed to initialize", "detail": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Map action names to orchestrator methods
        allowed_actions = {
            "match_report": orch.match_report,
            "cover_letter": orch.cover_letter,
            "skill_gap": orch.skill_gap,
            "roadmap": orch.roadmap,
            "recruiter_sim": orch.recruiter_sim,
            "extract_projects": orch.extract_projects,
            "rank_projects": orch.rank_projects,
            "industry_calibrate": orch.industry_calibrate,
            "tone_detect": orch.tone_detect,
            "bias_detect": orch.bias_detect,
        }

        if action not in allowed_actions:
            return Response(
                {"error": f"Invalid action: '{action}'. Allowed actions: {list(allowed_actions.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        method = allowed_actions[action]
        
        # Prepare arguments: exclude 'action' from kwargs
        kwargs = {k: v for k, v in request.data.items() if k != 'action'}

        try:
            # Call the ML method
            result = method(**kwargs)
            return Response(result, status=status.HTTP_200_OK)
        except TypeError as e:
            return Response(
                {"error": "Invalid arguments for the specified action.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}")
            return Response(
                {"error": "An error occurred during execution.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
