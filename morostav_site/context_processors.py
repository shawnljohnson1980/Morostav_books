
def timestamp_context(request):  # Check for typos in the function name
    from datetime import datetime
    return {'timestamp': datetime.now()}

'morostav_site.context_processors.timestamp_context'  # ✅ This is key
