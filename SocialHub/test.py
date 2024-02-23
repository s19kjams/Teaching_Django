import unittest

from django.contrib.auth.models import User
from django.test import Client

from SocialHub.models import Profile, Post, Follow


class TestSocialHub(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        try:
            self.user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            self.user = User.objects.create_user(username='testuser', password='testpassword')

        try:
            self.target_user = User.objects.get(username='testuser2')

        except User.DoesNotExist:
            self.target_user = User.objects.create_user(username='testuser2', password='testpassword')

        self.client.login(username='testuser', password='testpassword')

        try:
            self.post = Post.objects.get(user=self.user, content="test_content")
        except Post.DoesNotExist:
            self.post = Post.objects.create(user=self.user, content='test_content')

    def test_create_profile(self):
        response = self.client.post("/signup", {
            'username': 'brew install ffmpeg',
            'password': 'testpassword',
            'email': 'test2@gmail.com',
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
        })

        self.assertEqual(response.status_code, 302)

        profile_exists = Profile.objects.filter(user__username='testuser3').exists()
        self.assertEqual(profile_exists, True)
        profile = Profile.objects.get(user__username='testuser3')
        self.assertEqual(profile.user.email, 'test2@gmail.com')

        profile.delete()

    def test_read_post(self):
        response = self.client.get(f"/read_post/{self.post.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.content, 'test_content')

    def test_delete_post(self):
        post_id = self.post.id
        response = self.client.post(f"/delete_post", {
            'username': 'testuser',
            'post_number': 1,
        })

        self.assertEqual(response.status_code, 302)
        post_exists = Post.objects.filter(pk=post_id).exists()
        self.assertEqual(post_exists, False)

    def test_follow_unfollow_user(self):
        response = self.client.post(f'/follow_unfollow_user/{self.target_user.username}')
        self.assertEqual(response.status_code, 302)

        follow_exists = Follow.objects.filter(follower=self.user, followed_user=self.target_user).exists()
        self.assertTrue(follow_exists)

        response_unfollow = self.client.post(f'/follow_unfollow_user/{self.target_user.username}')
        self.assertEqual(response_unfollow.status_code, 302)
        follow_exists = Follow.objects.filter(follower=self.user, followed_user=self.target_user).exists()
        self.assertFalse(follow_exists)

    def tearDown(self):
        self.user.delete()
        self.target_user.delete()
        self.post.delete()



if __name__ == '__main__':
    unittest.main()
