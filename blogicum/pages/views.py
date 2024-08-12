from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "pages/about.html"


class RulesView(TemplateView):
    template_name = "pages/rules.html"


class Error404View(TemplateView):
    template_name = "pages/404.html"


class Error500View(TemplateView):
    template_name = "pages/500.html"


class Error403View(TemplateView):
    template_name = "pages/403csrf.html"
