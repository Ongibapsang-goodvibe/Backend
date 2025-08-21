from django.db import models
from django.conf import settings


# Create your models here.

class Disease(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    
    
class DiseaseRules(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="disease_rules")
    nutrient = models.ForeignKey("restaurants.Nutrient", on_delete=models.CASCADE, related_name="nutrient_rules")   
    # 1회 제공량 기준치 (절대값 기준) mg 단위로 저장
    min_once = models.FloatField(null=True, blank=True, help_text="1회 제공 최소 섭취량 (mg 단위)")
    max_once = models.FloatField(null=True, blank=True, help_text="1회 제공 최대 섭취량 (mg 단위)")
    # 비율 기준 (열량 대비 %)
    percent_min = models.FloatField(null=True, blank=True, help_text="열량 대비 최소 비율 (%)")
    percent_max = models.FloatField(null=True, blank=True, help_text="열량 대비 최대 비율 (%)")

    use_per_1000kcal = models.BooleanField(default=False)
    per_1000kcal_min = models.FloatField(null=True, blank=True, help_text="1000kcal 당 최소 (mg 단위)")
    per_1000kcal_max = models.FloatField(null=True, blank=True, help_text="1000kcal 당 최대 (mg 단위)")

    note = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        unique_together = ("disease", "nutrient")

    def __str__(self):
        return f"{self.disease.name} - {self.nutrient.name}({self.rule_type})"
    
    
class NutritionReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="users_with_diseases")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="users_disease")
    date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "disease")
    
    def __str__(self):
        return f"{self.user} - {self.disease.name}"