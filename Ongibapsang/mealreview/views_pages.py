from django.views.generic import TemplateView

class OverallPage(TemplateView):
    template_name = "overall.html"

class SelectPage(TemplateView):
    template_name = "select.html"

class VoicePage(TemplateView):
    template_name = "voice.html"

class ConfirmPage(TemplateView):
    template_name = "confirm.html"
