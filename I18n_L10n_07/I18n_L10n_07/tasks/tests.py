from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils.translation import activate
from tasks.models import Task
from tasks.serializers import TaskSerializer
from datetime import date

class TaskViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', is_staff=True)
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            due_date=date(2025, 8, 3),
            priority="high",
            assigned_to=self.user
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def test_create_task_invalid_priority_telugu(self):
        activate('te')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            "title": "పరీక్ష టాస్క్",
            "description": "వివరణ",
            "due_date": "2025-08-03",
            "priority": "invalid",
            "assigned_to": self.user.id
        }
        response = self.client.post('/te/tasks/api/tasks/', data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("ప్రాధాన్యత 'తక్కువ', 'మధ్యస్థ' లేదా 'అధిక' అయి ఉండాలి", str(response.data))

    def test_create_task_invalid_priority_urdu(self):
        activate('ur')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            "title": "ٹیسٹ ٹاسک",
            "description": "تفصیل",
            "due_date": "2025-08-03",
            "priority": "invalid",
            "assigned_to": self.user.id
        }
        response = self.client.post('/ur/tasks/api/tasks/', data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("ترجیح 'کم'، 'درمیانہ' یا 'زیادہ' ہونی چاہیے", str(response.data))

    def test_list_tasks_telugu(self):
        activate('te')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get('/te/tasks/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['title'], "Test Task")
        self.assertEqual(response.data['results'][0]['priority_display'], "అధిక")

    def test_list_tasks_urdu(self):
        activate('ur')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get('/ur/tasks/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['priority_display'], "زیادہ")

    def test_localized_due_date_telugu(self):
        activate('te')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(f'/te/tasks/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['formatted_due_date'], "03/08/2025")