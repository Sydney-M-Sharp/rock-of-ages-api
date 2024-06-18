from django.db import models

# classes are blue prints for objects
#django creates an object that looks like this class.
# the object has a label property
#instance = object
# it then takes the data from the data base and assign the data to label
class Type(models.Model):
    label = models.CharField(max_length=155)