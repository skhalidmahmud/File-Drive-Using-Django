from django import template

register = template.Library()

@register.filter
def filesizeformat(value):
    """
    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB, 102 bytes, etc).
    """
    if value is None:
        return "0 bytes"
    
    try:
        value = float(value)
    except (TypeError, ValueError, UnicodeDecodeError):
        return "0 bytes"
    
    if value < 1:
        return "0 bytes"
    
    if value < 1024:
        return f"{int(value)} bytes"
    
    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    
    if value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.1f} MB"
    
    return f"{value / (1024 * 1024 * 1024):.1f} GB"