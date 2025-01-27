from django.db import models


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=32)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.category_name)


class Product(models.Model):
    pr_name = models.CharField(max_length=128)
    pr_des = models.TextField()
    pr_price = models.FloatField()
    pr_count = models.IntegerField()
    pr_photo = models.ImageField(upload_to='media')
    pr_category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pr_name)


class Cart(models.Model):
    user_id = models.IntegerField()
    user_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_pr_count = models.IntegerField()

    def __str__(self):
        return str(self.user_id)

