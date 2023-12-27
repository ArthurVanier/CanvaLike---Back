from collections import OrderedDict
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Template, TemplateShapeRelation
from .serializers import TemplateSerializer
from django.contrib.contenttypes.models import ContentType
from django.core import management
from .utils import ordered_dict_to_dict


# Create your tests here.

BASE_API_URL = "http://127.0.0.1:8000/api/"

user = User.objects.first()
client = APIClient()
client.login(username=user.username, password=user.password)

#client.force_authenticate

class APITestBase(APITestCase):

    @property
    def bearer_token(self):
        # assuming there is a user in User model
        user = User.objects.get(id=1)

        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION":f'Bearer {refresh.access_token}'}


TEST_USER_1 = {'username': 'test', 'first_name': 'John', 'last_name': 'Doe', 'email': 'user1@example.com'}
TEST_USER_CREATE = {'username': 'testC', 'first_name': 'test', 'last_name': 'test', 'email': 'test@email.com'}

class UserTests(APITestBase):
    fixtures = ['users.json']
    def test_list_users(self):
        url = "/api/users/" 
        response = client.get(url, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_retrieve_users(self):
        url = "/api/users/1/" 
        response = client.get(url, **self.bearer_token)
        self.assertEqual(response.data, TEST_USER_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_create_users(self):
        url = "/api/users/" 
        data = {"username": "testC", "password": "testC", "first_name": "test", "last_name": "test", "email": "test@email.com"}
        response = client.post(url, data, **self.bearer_token)
        self.assertEqual(response.data, TEST_USER_CREATE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


TEST_TEMPLATE_POST = {'id': 1, 
                      'user': 1,
                      'name': 'test',
                      'shapes': [OrderedDict([('id', 1), ('content_type', 3),('object', {'id': 1, 'x': 1.0, 'y': 30.0, 'width': 1000.0, 'height': 2000.0}), ('props', OrderedDict([('id', 1), ('fill_color', 'red'), ('stroke', 'blue'), ('strokeWidth', 2.0), ('opacity', 0.8)])), ('shadow', OrderedDict([('id', 1), ('shadow_color', 'black'), ('shadow_blurr', 0.5), ('shadow_offset_x', 2.0), ('shadow_offset_y', 2.0), ('shadow_opacity', 0.6)])), ('template', 1), ('shape_id', 1)])]}

class TemplateTests(APITestBase):
    fixtures = ['templates.json', 'users.json', 'circles.json', 'rectangles.json',
                'media.json', 'template_shape_relation.json',
                'shapes.json', 'shapeshadow.json', 'shapeprops.json']


    def test_list_templates(self):

        url = "/api/templates/" 
        response = client.get(url, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_retrieve_template(self):

        url = "/api/templates/1/" 
        response = client.get(url, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, TEST_TEMPLATE_POST)
    

    def test_create_template(self):

        url = "/api/templates/1/" 
        template_data = {
            "user": 1,
            "name": "test",
            "shapes": [1]
        }
        response = client.get(url, template_data, **self.bearer_token)

        self.assertEqual(response.data, TEST_TEMPLATE_POST)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_update_template(self):
        pk_object = 1
        url = f"/api/templates/{pk_object}/" 

        template_data = {
            "name": "test updated",
            "user": 2,
            "shapes": [1]
        }

        response = client.put(url, template_data, **self.bearer_token)

        instance = Template.objects.get(pk=pk_object)
        self.assertEqual(instance.name, "test updated")
        self.assertEqual(instance.user.id, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_delete_template(self):

        url = "/api/templates/1/"

        response = client.delete(url, **self.bearer_token)
        template = None if len(Template.objects.filter(pk=1)) == 0 else 1
        self.assertEqual(template, None)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    


TEST_SHAPE_CREATE = {'id': 1, 'content_type': 3, 'object': {'id': 1, 'x': 1.0, 'y': 30.0, 'width': 1000.0, 'height': 2000.0}, 'props': OrderedDict([('id', 1), ('fill_color', 'red'), ('stroke', 'blue'), ('strokeWidth', 2.0), ('opacity', 0.8)]), 'shadow': OrderedDict([('id', 1), ('shadow_color', 'black'), ('shadow_blurr', 0.5), ('shadow_offset_x', 2.0), ('shadow_offset_y', 2.0), ('shadow_opacity', 0.6)]), 'template': 1, 'shape_id': 1}
class ShapeTests(APITestBase):
    fixtures = ['templates.json', 'users.json', 'circles.json', 'rectangles.json',
                'media.json', 'template_shape_relation.json',
                'shapes.json', 'shapeshadow.json', 'shapeprops.json']
    

    def test_list_shapes(self):
        url = "/api/shapes/" 
        response = client.get(url, **self.bearer_token)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_retrieve_shape(self):
        url = "/api/shapes/1/" 
        response = client.get(url, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, TEST_SHAPE_CREATE)
    

    def test_create_shape(self):
        url = "/api/shapes/" 
        data = {
            "template": 1,
            "content_type": 3,
            "shape_id": 1,
            "props": 1,
            "shadow": 1
        }
        response = client.post(url, data, **self.bearer_token)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, TEST_SHAPE_CREATE)


    def test_update_shape(self):
        url = "/api/shapes/1/" 
        data = {
            "update_object": {
                "x": 100
            },
            "props": {
                "fill_color": "green"
            }
        }
        response = client.put(url, data, **self.bearer_token)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        

    

