"""Routes classified intents to action handlers."""
import logging
from whatsapp.intent import IntentResult
from whatsapp import actions

logger = logging.getLogger('whatsapp.dispatcher')

_INTENT_MAP = {
    'greeting':             actions.handle_greeting,
    'help':                 actions.handle_help,
    'get_feedback':         actions.handle_get_feedback,
    'get_history':          actions.handle_get_history,
    'get_score':            actions.handle_get_score,
    'schedule_interview':   actions.handle_schedule_interview,
    'schedule_provide_time':actions.handle_schedule_provide_time,
    'schedule_provide_type':actions.handle_schedule_provide_type,
    'cancel_schedule':      actions.handle_cancel_schedule,
    'start_interview':      actions.handle_start_interview,
    'link_account':         actions.handle_link_account,
    'link_verify_otp':      actions.handle_link_verify_otp,
}


def dispatch(intent_result: IntentResult, wa_user, conv) -> str:
    handler = _INTENT_MAP.get(intent_result.intent)

    if handler is None:
        return actions.handle_unknown(wa_user, conv, intent_result.entities,
                                      ask=intent_result.ask)

    try:
        return handler(wa_user, conv, intent_result.entities)
    except Exception as e:
        logger.exception(f"Action handler failed for intent={intent_result.intent}: {e}")
        return (
            "Something went wrong on my end. Please try again or "
            "visit beaver.ai for support."
        )
