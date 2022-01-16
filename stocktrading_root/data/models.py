from django.db import models

class Symbol(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Sybmol"
        verbose_name_plural = "Sybmols"

    def __str__(self):
        return self.name.upper()


class TimeframeAlias(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = "Timeframe alias"
        verbose_name_plural = "Timeframe aliases"

    def __str__(self):
        return self.name.upper()

class Timeframe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    alias_id = models.ManyToManyField(
        TimeframeAlias, related_name="timeframe_other_name"
    )

    class Meta:
        verbose_name = "Timeframe"
        verbose_name_plural = "Timeframes"

    def __str__(self):
        return self.name

class Data(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    timeframe = models.ForeignKey(Timeframe, on_delete=models.CASCADE, related_name = "data_timeframe")
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name = "data_symbol")
    open_bid = models.FloatField()
    close_bid = models.FloatField()
    high_bid = models.FloatField()
    low_bid = models.FloatField()
    open_ask = models.FloatField(blank = True, null = True)
    close_ask = models.FloatField(blank = True, null = True)
    high_ask = models.FloatField(blank = True, null = True)
    low_ask = models.FloatField(blank = True, null = True)
    volume = models.FloatField(blank = True, null = True)
        
    class Meta:
        unique_together = ("datetime", "timeframe", "symbol")
        verbose_name = "Data"
        verbose_name_plural = "Data"

