from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from apps.page.models import Page

User = get_user_model()


class UserAPITests(TestCase):
    def setUp(self):
        cache.clear()
        self.alice = User.objects.create_user("alice", password="pass12345", email="alice@example.com")
        self.bob = User.objects.create_user("bob", password="pass12345", email="bob@example.com")
        self.root = User.objects.create_superuser("root", password="pass12345")
        self.client = APIClient()

    def login(self, user):
        self.client.force_authenticate(user)

    # --- registration ---

    def test_anyone_can_register_and_password_is_hashed(self):
        r = self.client.post("/api/user/", {"username": "new", "password": "pass12345"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertNotIn("password", r.json())
        user = User.objects.get(username="new")
        self.assertTrue(user.check_password("pass12345"))

    def test_registration_cannot_set_permission_flags(self):
        self.client.post("/api/user/", {"username": "evil", "password": "pass12345",
                                        "is_superuser": True, "is_staff": True}, format="json")
        user = User.objects.get(username="evil")
        self.assertFalse(user.is_superuser or user.is_staff)

    # --- listing and reading ---

    def test_user_list_requires_login(self):
        self.assertEqual(self.client.get("/api/user/").status_code, 401)

    def test_user_list_does_not_expose_private_fields(self):
        self.login(self.alice)
        item = self.client.get("/api/user/").json()["results"][0]
        for field in ("password", "email", "is_superuser", "is_staff", "last_login"):
            self.assertNotIn(field, item)

    def test_reading_another_user_exposes_no_secrets(self):
        self.login(self.alice)
        data = self.client.get(f"/api/user/{self.bob.pk}/").json()
        for field in ("password", "email", "is_superuser", "is_staff", "user_permissions"):
            self.assertNotIn(field, data)

    def test_user_detail_requires_login(self):
        self.assertEqual(self.client.get(f"/api/user/{self.bob.pk}/").status_code, 401)

    # --- updating ---

    def test_user_can_update_own_profile(self):
        self.login(self.alice)
        r = self.client.patch(f"/api/user/{self.alice.pk}/", {"first_name": "Alice"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, "Alice")

    def test_user_cannot_promote_themselves(self):
        self.login(self.alice)
        self.client.patch(f"/api/user/{self.alice.pk}/",
                          {"is_superuser": True, "is_staff": True, "is_active": True}, format="json")
        self.alice.refresh_from_db()
        self.assertFalse(self.alice.is_superuser)
        self.assertFalse(self.alice.is_staff)

    def test_password_change_is_hashed_and_login_keeps_working(self):
        self.login(self.alice)
        r = self.client.patch(f"/api/user/{self.alice.pk}/", {"password": "newpass12345"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.alice.refresh_from_db()
        self.assertNotEqual(self.alice.password, "newpass12345")
        self.assertTrue(self.alice.check_password("newpass12345"))

    def test_user_cannot_edit_or_delete_someone_else(self):
        self.login(self.alice)
        self.assertEqual(self.client.patch(f"/api/user/{self.bob.pk}/", {"first_name": "x"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(f"/api/user/{self.bob.pk}/").status_code, 403)

    def test_superuser_can_edit_other_users(self):
        self.login(self.root)
        r = self.client.patch(f"/api/user/{self.bob.pk}/", {"first_name": "Bob"}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_superuser_can_deactivate_a_user_but_users_cannot_reactivate_themselves(self):
        self.login(self.root)
        self.assertEqual(self.client.patch(f"/api/user/{self.bob.pk}/", {"is_active": False}, format="json").status_code, 200)
        self.bob.refresh_from_db()
        self.assertFalse(self.bob.is_active)
        self.login(self.alice)
        self.client.patch(f"/api/user/{self.alice.pk}/", {"is_active": False}, format="json")
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.is_active)  # field is ignored for non-superusers

    # --- auth ---

    def test_token_login_and_refresh(self):
        r = self.client.post("/api/token/", {"username": "alice", "password": "pass12345"}, format="json")
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post("/api/refresh/", {"refresh": r.json()["refresh"]}, format="json")
        self.assertEqual(r2.status_code, 200)

    def test_public_page_listing_does_not_leak_author_email(self):
        Page.objects.create(user=self.alice, title="Hello", description="First page", html="<h1>Hi</h1>")
        data = self.client.get("/api/page/").json()["results"][0]
        self.assertEqual(data["user"]["username"], "alice")
        self.assertNotIn("email", data["user"])