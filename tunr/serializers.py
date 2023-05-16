from rest_framework import serializers

"""
Book:

Title
ISBN (unique)
Publisher
Publication date
Description
Cover image (optional)
Author (Foreign Key)
Genre (ManyToMany Field)
Author:

Name
Bio
Date of birth
Country of origin
Genre:

Name
Description
"""