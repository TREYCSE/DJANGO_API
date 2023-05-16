# DJANGO_API

## 1. Set Up Django in Project
We're going to start from the solution for Django views lesson. You'll need to clone this solution down and get it set up before proceeding:

    Create a new virtual environment: pipenv shell
    Install the dependencies: pipenv install
   
Before getting the app up and running, you'll probably want to delete the old database and recreate it:

    Sign into Postgres: psql / psql -d <database>
    Delete the existing database: drop database tunr;
    (optional) Create the user: create user tunr_admin with password 'tunr';
    Grant privileges to tunruser: grant all privileges on database tunr to tunruser;
Now we need to get the app up and running:
   
    Run the migrations: python manage.py migrate
    Run the application: python manage.py runserver
    
Now we need to get the Django Rest Framework installed and set up. Before we get started, install the djangorestframework dependency:

    pipenv install djangorestframework
    Also, add it to your INSTALLED_APPS list in your settings.py so that you can use it within your project.

    INSTALLED_APPS = [
        # ...
        'tunr',
        'rest_framework',
    ]
Note that you may have django_extensions installed here too. Keep both!

#### Serializers
Serializers allow us to convert our data from QuerySets (the data type returned by Django's ORM) to data that can easily be converted to JSON (or XML) and returned by our API.

There are several types of serializers built into Django REST framework; however, we will be using the HyperlinkedModelSerializer today. This serializer allows us to specify model fields that we want to include in our API and it will generate our JSON accordingly. It will also allow us to link from one model to another.

In this case, we want all of the fields from the Artist model in our serializer, so we will include all of them in our fields tuple. We will create a new file in our tunr app folder, called serializers.py to hold our serializer class.

    touch tunr/serializers.py
    Import the base serializer class and model.

    from rest_framework import serializers
    from .models import Artist

    class ArtistSerializer(serializers.HyperlinkedModelSerializer):
        songs = serializers.HyperlinkedRelatedField(
            view_name='song_detail',
            many=True,
            read_only=True
        )
Awesome, this is a great start. We also want to describe all the fields in artist. We'll do this using a Meta class.

Add a Meta class inside the ArtistSerializer class:

    class ArtistSerializer(serializers.HyperlinkedModelSerializer):
        songs = serializers.HyperlinkedRelatedField(
            view_name='song_detail',
            many=True,
            read_only=True
        )
    +   class Meta:
    +       model = Artist
    +       fields = ('id', 'photo_url', 'nationality', 'name', 'songs',)
Lets break down what's going on here.

We are creating a HyperlinkedRelatedField and pointing it to the song_detail view. This allows us to link one model to another using a hyperlink. So when we inspect the json response, we'll be able to just follow a url that takes us to from the current Artist to the related Song. There are a couple of ways to represent relationships when serializing models. The default provided by the ModelSerializer is to provide the primary keys. Here, we're providing the URL to the related record. Check out the documentation on serializer relations for more options, including Nested Relationships. The Meta class within our Artist serializer class specifies meta data about our serializer. In this class, we tell it the model and what fields we want to serialize. The view_name specifies the name of the view given in the urls.py file. If we look at our tunr/urls.py file, we already have a path like this:

    path('songs/<int:pk>', views.song_detail, name='song_detail')"

#### Authentication
Now that you have a functional API, it's time to add authentication using the Django Rest Framework's built-in session-based authentication system. You'll need to require authentication for any actions that modify the book inventory (e.g. creating a new book, updating an existing book, or deleting a book).
Authentication is the mechanism of associating an incoming request with a set of identifying credentials, such as the user the request came from, or the token that it was signed with. The permission and throttling policies can then use those credentials to determine if the request should be permitted.

REST framework provides several authentication schemes out of the box, and also allows you to implement custom schemes. Authentication always runs at the very start of the view, before the permission and throttling checks occur, and before any other code is allowed to proceed.

    The request.user property will typically be set to an instance of the contrib.auth package's User class.
    The request.auth property is used for any additional authentication information, for example, it may be used to represent an authentication token that the request was signed with.
    Note: Don't forget that authentication by itself won't allow or disallow an incoming request, it simply identifies the credentials that the request was made with.

For information on how to set up the permission policies for your API please see the permissions documentation.

## 2. Django Models, Views, & Templates
Models
Build the base API using Django and the Django Rest Framework. You'll need to define the models necessary to track the books in the library's inventory. Your models should include Book, Author, and Genre. Here are the properties for each model:

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

#### Views
Once you have defined your models, you'll need to create the necessary serializers and views to expose the API endpoints for CRUD (Create, Read, Update, Delete) operations on the Book model. You should also be able to link between models (i.e. your Book model should return URLs to your Author and Genre models). Django REST framework has a bunch of utility functions and classes for implementing sets of views in Django. Instead of creating each view individually, Django REST framework will create multiple views for us in a few lines of code.

    Class-based views
    Generic views
    ViewSets

For example, we can use the ListCreateAPIView to create both our list view for our API and our create view. We can also use RetrieveUpdateDestroyAPIView to create show, update, and delete routes for our API. In this code example, we'll allow permissions for List and Create (CR in CRUD) on the ArtistList view. For ArtistDetail, we'll allow Retrieve, Update, Delete (RUD in CRUD) permissions. We'll start by removing the views we created for artist_list and artist_detail inside of tunr/views.py. Then we'll replace those views with the ArtistList class which will inherit generics.ListCreateAPIView, and ArtistDetail which will inherit generics.RetrieveUpdateDestroyAPIView

    # views.py

    from rest_framework import generics
    from .serializers import ArtistSerializer
    from .models import Artist

    class ArtistList(generics.ListCreateAPIView):
        queryset = Artist.objects.all()
        serializer_class = ArtistSerializer

    class ArtistDetail(generics.RetrieveUpdateDestroyAPIView):
        queryset = Artist.objects.all()
        serializer_class = ArtistSerializer"

#### URLs
DRF comes with some pre-configured conventions for URLs, in what they call a router. These URLs map to views that follow a naming convention.
Since Django can handle multiple request types in one view and using one url, we just need to set up two routes: one for the single view and one for the list view.

    # tunr/urls.py
    from django.urls import path
    from . import views
    + from rest_framework.routers import DefaultRouter

    urlpatterns = [
    +    path('artists/', views.ArtistList.as_view(), name='artist_list'),
    +    path('artists/<int:pk>', views.ArtistDetail.as_view(), name='artist_detail'),
    ]
Adding Fields with URLs to Detail Views
Wouldn't it be cool if each Artist and Song in the List view contained a link to their details? We can add this by updating the serializers with custom field mappings:

    class ArtistSerializer(serializers.HyperlinkedModelSerializer):
        songs = serializers.HyperlinkedRelatedField(
            view_name='song_detail',
            many=True,
            read_only=True,
        )

    +    artist_url = serializers.ModelSerializer.serializer_url_field(
    +        view_name='artist_detail'
    +    )

        class Meta:
            model = Artist
    -        fields = ('id', 'photo_url', 'nationality', 'name', 'songs',)
    +        fields = ('id', 'artist_url', 'photo_url', 'nationality', 'name', 'songs',)
#### Testing
Now let's hit the urls we just built out and see what happens.

    http://localhost:8000/artists/
    http://localhost:8000/artists/1/
    http://localhost:8000/songs/
    http://localhost:8000/songs/1/
#### Cors
We need to configure CORS in order for other applications to use the API we just created. The Django Rest Documentation page on AJAX is a great place to get started. It endorses the Django Cors Headers middleware, which can be installed like any other dependency with pipenv and is configured in the Project's settings.py

## 3. Bonus Feature (req. & tbd)
For the final part of the assignment, you can choose one of the following features to implement in your API:

    Validation: Implement validation on the Book model to ensure that required fields are not left blank, and that ISBNs are unique.
    Throttling: Add throttling to limit the number of requests a client can make in a given time period.
    Pagination: Implement pagination to limit the number of books returned in a single API response, and provide links to additional pages of results.
    Filtering: Add filtering to allow clients to search for books by various criteria, such as title, author, genre, or publication date.
    
