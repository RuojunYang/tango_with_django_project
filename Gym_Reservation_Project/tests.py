from django.test import TestCase
from Gym_Reservation_Project.models import *
from django.contrib.auth.hashers import check_password

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="customer", password="password123", type=User.Types.CUSTOMER)
        User.objects.create_user(username="manager", password="managerpassword", type=User.Types.CUSTOMER)
        Customer.objects.create(user=User.objects.get(username="customer"),)
        Manager.objects.create(user=User.objects.get(username="manager"),)

    def test_user(self):
        customer = Customer.objects.get(user=User.objects.get(username="customer"))
        self.assertTrue("CUSTOMER", customer.user.type)
        self.assertTrue("password123" != customer.user.password)
        self.assertTrue(check_password("password123", customer.user.password))
        
        manager = Manager.objects.get(user=User.objects.get(username="manager"))
        self.assertTrue("Manager", manager.user.type)

        # encrypt password
        self.assertTrue("managerpassword" != manager.user.password)
        self.assertTrue(check_password("managerpassword", manager.user.password))

class ViewTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="customer", password="password123", type=User.Types.CUSTOMER)
        User.objects.create_user(username="manager", password="managerpassword", type=User.Types.CUSTOMER)
        Customer.objects.create(user=User.objects.get(username="customer"),)
        Manager.objects.create(user=User.objects.get(username="manager"),)

    def test_view(self):
        response = self.client.get('/after_login_customer/', follow=True)
        self.assertAlmostEqual(response.status_code, 404)

        # customer
        self.client.login(username='customer', password='password123')

        # asscess own website
        response = self.client.get('/after_login_customer/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'after_login_customer.html')

        response = self.client.get('/after_login_customer/coach_list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'after_login_customer_coach_list.html')
        
        response = self.client.get('/after_login_customer/my_profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'after_login_customer_my_profile.html')

        response = self.client.get('/after_login_customer/my_profile/my_reports/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'after_login_customer_my_report_list.html')

        # access other role website
        response = self.client.get('/after_login_manager/')
        self.assertRedirects(response, '/')

        response = self.client.get('/after_login_operator/my_reports/')
        self.assertRedirects(response, '/')

        # manager
        self.client.login(username='manager', password='managerpassword')

        response = self.client.get('/after_login_manager/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'after_login_manager.html')

        response = self.client.get('/after_login_operator/my_reports/')
        self.assertRedirects(response, '/')

        response = self.client.get('/after_login_customer/coach_list/')
        self.assertRedirects(response, '/')
