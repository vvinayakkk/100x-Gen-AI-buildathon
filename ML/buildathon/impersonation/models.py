# from django.db import models

# class Celebrity(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     background = models.TextField()
#     tone = models.TextField()
#     speaking_style = models.TextField()
#     example_tweets = models.JSONField(default=list)  # Stores example tweets as a JSON array
#     emotional_range = models.JSONField(default=list)  # Stores emotional ranges as a JSON array

#     def __str__(self):
#         return self.name


# class Impersonation(models.Model):
#     celebrity = models.ForeignKey(Celebrity, on_delete=models.CASCADE)
#     input_tweet = models.TextField()
#     response = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']
