from django.db import models


# Create your models here.

class Disease(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    
class DiseaseRules(models.Model):
    RULE_TYPE_CHOICES = [
        ("ABSOLUTE", "절대값"),
        ("PERCENT", "비율"),
    ]

    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="disease_rules")
    nutrient = models.ForeignKey("restaurants.Nutrient", on_delete=models.CASCADE, related_name="nutrient_rules")
    rule_type = models.CharField(max_length=10, choices=RULE_TYPE_CHOICES, default="ABSOLUTE")
    
    # 주간 기준치 (절대값 기준) mg 단위로 저장
    min_week = models.FloatField(null=True, blank=True, help_text="주당 최소 섭취량 (mg 단위)")
    max_week = models.FloatField(null=True, blank=True, help_text="주당 최대 섭취량 (mg 단위)")

    # 비율 기준 (열량 대비 %)
    percent_min = models.FloatField(null=True, blank=True, help_text="열량 대비 최소 비율 (%)")
    percent_max = models.FloatField(null=True, blank=True, help_text="열량 대비 최대 비율 (%)")

    use_per_1000kcal = models.BooleanField(default=False)
    
    note = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        unique_together = ("disease", "nutrient")

    def __str__(self):
        return f"{self.disease.name} - {self.nutrient.name}({self.rule_type})"