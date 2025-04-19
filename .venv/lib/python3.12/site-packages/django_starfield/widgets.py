from django.conf import settings
from django.forms.widgets import Widget

STARFIELD_COLOUR = '#f5b301'
STARFIELD_CODEPOINT = '2605'
STARFIELD_STARS = 5

class Stars(Widget):
    template_name = 'django_starfield/stars.html'

    def __init__(self, attrs=None, stars=None, codepoint=None, colour=None):
        super(Stars, self).__init__(attrs)

        self.stars = stars if stars else getattr(settings, 'STARFIELD_STARS', STARFIELD_STARS)
        self.codepoint = codepoint if codepoint else getattr(settings, 'STARFIELD_CODEPOINT', STARFIELD_CODEPOINT)
        self.colour = colour if colour else getattr(settings, 'STARFIELD_COLOUR', STARFIELD_COLOUR)

    def get_context(self, name, value, attrs):
        context = super(Stars, self).get_context(name, value, attrs)
        context['stars'] = range(self.stars, 0, -1)
        if not self.codepoint == STARFIELD_CODEPOINT:
            context['codepoint'] = self.codepoint
        if not self.colour == STARFIELD_COLOUR:
            context['colour'] = self.colour
        return context
