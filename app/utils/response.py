from datetime import datetime

def success_response(message: str, data=None):
    return {
        "success": True,
        "message": message,
        "data": data or {},
        "meta": {
            "timestamp": datetime.utcnow().isoformat()
        }
    }

def error_response(message: str, errors=None):
    return {
        "success": False,
        "message": message,
        "errors": errors or {},
        "meta": {
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    