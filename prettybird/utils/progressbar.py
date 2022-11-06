from progressbar import *

def get_progressbar(max_value):
    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('/'), ' ', RotatingMarker()]
    return ProgressBar(widgets=widgets, max_value=max_value), widgets
