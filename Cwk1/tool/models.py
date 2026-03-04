from django.db import models

"""
AI_Name: The official or most common name of the artificial intelligence tool or platform.
Developer: The company, startup, or individual creator responsible for building the tool.
Release_Year: The year the tool was first launched or significantly updated for the 2026 market.
Intelligence_Type:Technical classification of the AI model (e.g., Generative, Agentic, Multimodal).
Primary_Domain: The main industry or area of application, such as Coding, Video, or Automation.
Key_Functionality:A descriptive summary detailing the specific tasks and features the tool performs.
Pricing_Model:The cost structure of the tool, categorized as Free, Freemium, or Paid.
API_Availability:Indicates whether the tool offers an API for third-party developer integration.
Context_Window: The maximum amount of data (tokens/chars) the model can process at one time.
Accessibility:Information on how the tool is accessed (e.g., Web App, Desktop, Mobile, or API).
Website_URL:The direct hyperlink to the tool's official landing page or documentation.
"""
class Domain(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name

class Developer(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name


class Accessibility(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name

class ContextWindow(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name

class Tool(models.Model):
    ai_name = models.CharField(max_length=255)
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True)
    release_year = models.IntegerField()
    intelligence_type = models.CharField(max_length=255)
    primary_domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True)
    key_functionality = models.TextField()
    pricing_model = models.CharField(max_length=255)
    api_availability = models.CharField(max_length=255)
    context_window = models.ForeignKey(ContextWindow, on_delete=models.SET_NULL, null=True)
    accessibility = models.ForeignKey(Accessibility, on_delete=models.SET_NULL, null=True)
    popularity_votes = models.IntegerField(default=0)
    website_url = models.URLField()
