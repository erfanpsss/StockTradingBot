from django.db.models import TextChoices


class ModelType(TextChoices):
    RandomForestClassifier = "RandomForestClassifier"
    LogisticRegression = "LogisticRegression"
    NeuralNetwork = "NeuralNetwork"
    XgBoost = "XgBoost"
    DecisionTree = "DecisionTree"
