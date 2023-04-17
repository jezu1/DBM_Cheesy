# -*- coding: utf-8 -*-
"""
File that contains functions to simulate data generated by the Cheezy app
"""
import os, json, random
from os.path import join
from faker import Faker
from faker_food import FoodProvider
from datetime import date, datetime

# Parameters
Faker.seed(123)
random.seed(123)

def json_serial(obj):
    """
    JSON serializer for objects not serializable by default json code
    Source: https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def simulate_data(
    path_img='data/images',

    # Number of instances to simulate
    n_users=100,
    n_restos=50,
    n_dishes=10,  # - generate 10 dishes per restaurant
    max_cuisines=5,  # maximum number of cuisines a user can pick that they are interested in
    max_tags=5,  # maximum number of tags for an image

    # Transactions
    n_swipes=int(1e6),
    n_loc=int(1e6),
    savepath='data/cheezy_data.json'
):
    """
    Simulate Cheezy data with user, restaurnat, dish, image, swipe, and geolocation data.
    Note that this needs a repository of images
    """

    # Create list of image addresses to sample from
    img_addresses = [join(path_img, i).replace('\\', '/') for i in os.listdir(path_img)]  

    # Initialize faker classes
    faker = Faker('en')
    faker.add_provider(FoodProvider)
    faker_es = Faker('es_ES') # Create Spanish faker

    # GENERATE USERS
    users = [{**{'id': 'U'+str(i+1).zfill(10)},
              **faker_es.simple_profile(),
              **{'createDate': faker.date_this_month(),
                 'interestedCuisines': list(set(faker.ethnic_category() for i in range(random.randint(1, max_cuisines)))),
                 'phone': faker_es.phone_number(),
                 'nationality': faker.country(),
                 'occupation': faker.job(),
                 'homeLat': float(faker_es.latitude()),
                 'homeLng': float(faker_es.longitude()),
                 }} for i in range(n_users)]

    # GENERATE RESTAURANTS
    restos = [{
        'id': 'R'+str(i+1).zfill(10),
        'name': faker_es.company(),
        'cuisine': faker.ethnic_category(),
        'phone': faker_es.phone_number(),
        'address': faker_es.address(),
        'restoLat': float(faker_es.latitude()),
        'restoLng': float(faker_es.longitude()),
    } for i in range(n_restos)
    ]
    restos[0]

    # GENERATE MENU
    dishes = sum([[{
        'id': 'D'+str(n_dishes*(i)+j+1).zfill(10),
        'name': faker.dish(),
        'description': faker.dish_description(),
        'ingredients': list(set(faker.ingredient() for i in range(random.randint(1, 10)))),
        'vegan': random.choices([0, 1], weights=[0.9,0.1], k=1)[0],
        'vegetarian':random.choices([0, 1], weights=[0.7, 0.3], k=1)[0],
        'restaurantId':'R'+str(i+1).zfill(10),
    } for j in range(n_dishes)] for i in range(n_restos)
    ], [])

    # GENERATE IMAGE INFO
    images = [{
        'id': 'I'+str(i+1).zfill(10),
        'file': j,
        'dishId': 'D'+str(random.choice(range(n_restos*n_dishes))+1).zfill(10),
        'uploaderId': 'U'+str(random.choice(range(n_users))+1).zfill(10),
        'uploadDt': faker.date_time_this_month(),
        'tags': faker.words(nb=random.choice(range(max_tags))),
    } for i, j in enumerate(img_addresses)]

    # GENERATE SWIPE DATA
    swipes = [{
        'id': 'S'+str(i+1).zfill(10),
        'timestamp': faker.date_time(),
        'userId': 'U'+str(random.choice(range(n_users))+1).zfill(10),
        'imageId': 'U'+str(random.choice(range(len(img_addresses)))+1).zfill(10),
        'swipeLeft': random.choice([0, 1])
    } for i in range(n_swipes)]

    # GENERATE USER LOCATION DATA
    # https://location.foursquare.com/developer/docs/geofence-data-schema
    locations = [{
        'id': 'L'+str(i+1).zfill(10),
        'eventType': random.choice(['geofenceEnter', 'geofenceDwell', 'geofencePresence', 'geofenceExit']),
        'eventLat': float(faker_es.latitude()),
        'eventLng': float(faker_es.longitude()),
        'timestamp':faker.date_time(),
        'geofenceId': faker.ssn(),
        'geofenceType': random.choice(['venue', 'chain', 'category', 'circle', 'polygon']),
        'geofenceName': faker.word(),
        'radius': random.randint(1, 1000),
        'geofenceLat':float(faker_es.latitude()),
        'geofenceLng':float(faker_es.longitude())
    } for i in range(n_loc)]

    # Save data into one json string
    data = {}
    for df in ['users', 'restos', 'dishes', 'images', 'swipes', 'locations']:
        print(df)
        data[df] = locals()[df]

    json_string = json.dumps(data, default=json_serial)

    # Save to json file
    with open(savepath, 'w') as outfile:
        outfile.write(json_string)
        
simulate_data()