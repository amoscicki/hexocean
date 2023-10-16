from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import auth
from django.test import TestCase
from accounts.models import CustomUser, Plan, Thumbnail_size
from django.urls import reverse, resolve
from api.views import ImageViewSet, GenerateExpiringLinkViewSet, ExpiringLinkViewSet
import PIL.Image as PILImage
from io import BytesIO

PASSED_STR = '\033[92m PASSED \033[0m'
FAILED_STR = '\033[91m FAILED \033[0m'

class TestUrls(APITestCase):

    def test_image_view_set_url_resolves(self):
        url = reverse('image-list')
        
        msg = f'URL {url} resolves: '
        self.assertEquals(resolve(url).func.cls, ImageViewSet, msg=f'{msg}{FAILED_STR}')
        print(f'{msg}{PASSED_STR}')

    def test_generate_expiring_link_view_set_url_resolves(self):
        url = reverse('link-list')
        
        msg = f'URL {url} resolves: '
        self.assertEquals(resolve(url).func.cls, GenerateExpiringLinkViewSet, msg=f'{msg}{FAILED_STR}')
        print(f'{msg}{PASSED_STR}')

    def test_expiring_link_view_set_url_resolves(self):
        url = reverse('templink', args=[1])
        
        msg = f'URL {url} resolves: '
        self.assertEquals(resolve(url).func.cls, ExpiringLinkViewSet, msg=f'{msg}{FAILED_STR}')
        print(f'{msg}{PASSED_STR}')

class TestViews(TestCase):

    def setUp(self):
        self.client = APIClient()
        
        Thumbnail_size.objects.create(height=200)
        Thumbnail_size.objects.create(height=400)
        Plan.objects.create(name='Basic', 
                            expiring_link=False, 
                            original_available=False
        ).thumbnail_sizes.set(Thumbnail_size.objects.filter(height=200))
        Plan.objects.create(name='Premium', 
                            expiring_link=False, 
                            original_available=True
        ).thumbnail_sizes.set(Thumbnail_size.objects.all())
        Plan.objects.create(name='Enterprise', 
                            expiring_link=True, 
                            original_available=True
        ).thumbnail_sizes.set(Thumbnail_size.objects.all())

        for p in Plan.objects.all():
            CustomUser.objects.create_user(username=f'testuser_{p.name}', plan=p) 
        
        self.image_formats = {
            'png':True,
            'bmp':False,
            'gif':False,
            'jpg':True
        }

        self.image_list_url = reverse('image-list')

    def mockup_image(self, format):
        file_object = BytesIO()
        img = PILImage.new('RGB', (500, 500))
        img.save(file_object, format='JPEG' if format == 'jpg' else format.upper())
        file_object.seek(0)
        image_file = SimpleUploadedFile(name=f'test_image.{format}',
                                        content=file_object.read(),
                                        content_type=f'image/{format}')
        return image_file
        
    def test_image_view_set_list_GET(self):
        for user in CustomUser.objects.all(): 
            print(f'== testing image list GET ==')

            msg = f'USER {user} not logged in: '
            self.assertFalse(auth.get_user(self.client).is_authenticated, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')
            
            msg = f'Access denied: '
            response = self.client.get(self.image_list_url)
            self.assertEquals(response.status_code, 403, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')

            self.client.force_login(user)
            msg = f'USER {user} logged in: '
            self.assertTrue(auth.get_user(self.client).is_authenticated, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')

            self.client.logout()
            msg = f'USER {user} logged out: '
            self.assertFalse(auth.get_user(self.client).is_authenticated, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')

    def test_image_view_set_list_POST(self):

        for user in CustomUser.objects.all():         
            print(f'== testing image list POST ==')

            msg = f'USER {user} not logged in: '       
            self.assertFalse(auth.get_user(self.client).is_authenticated, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')
            response = self.client.post(self.image_list_url)

            msg = f'Access denied: '
            self.assertEquals(response.status_code, 403, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')

            self.client.force_login(user)
            msg = f'USER {user} logged in: '
            self.assertTrue(auth.get_user(self.client).is_authenticated, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')

            response = self.client.post(self.image_list_url)
            msg = f'Invalid request: '
            self.assertEquals(response.status_code, 400, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')

            self.test_image_files = [
                (
                    self.mockup_image(file_format), 
                    self.image_formats[file_format]
                ) for file_format in self.image_formats.keys()
            ]

            for entry in self.test_image_files:
                image_file, allowed = entry
                response = self.client.post(self.image_list_url, {'image':image_file})
                
                if not allowed:
                    msg = f'Invalid image format: '
                    self.assertEquals(response.status_code, 400, msg=f'{msg}{FAILED_STR}')
                    print(f'{msg}{PASSED_STR}')

                else:
                    msg = f'Valid image format: '
                    self.assertEquals(response.status_code, 201, msg=f'{msg}{FAILED_STR}')
                    print(f'{msg}{PASSED_STR}')

                    number_of_images = user.plan.thumbnail_sizes.count()
                    if user.plan.original_available:
                        number_of_images += 1
                        msg = f'Original image available and link provided: '
                        self.assertTrue('original' in list(response.data.keys()), msg=f'{msg}{FAILED_STR}')
                        self.assertTrue(len(response.data['original']) > 0, msg=f'{msg}{FAILED_STR}')
                        print(f'{msg}{PASSED_STR}')

                    for t in user.plan.thumbnail_sizes.all():
                        key = f'thumbnail_{str(t.height)}'
                        msg = f'{key} generated and link provided: '
                        self.assertTrue(key in list(response.data.keys()), msg=f'{msg}{FAILED_STR}')
                        self.assertTrue(len(response.data[key]) > 0, msg=f'{msg}{FAILED_STR}')
                        print(f'{msg}{PASSED_STR}')

                    msg = f'Correct number of images generated: '
                    self.assertEquals(len(response.data.keys()), number_of_images, msg=f'{msg}{FAILED_STR}')
                    print(f'{msg}{PASSED_STR}')

            self.client.logout()
            msg = f'USER {user} logged out: '
            self.assertFalse(auth.get_user(self.client).is_authenticated, msg=f'{msg}{FAILED_STR}')
            print(f'{msg}{PASSED_STR}')
    
