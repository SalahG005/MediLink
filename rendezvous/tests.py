from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import TimeSlot, RendezVous, Notification
import datetime


class CancelRendezVousTests(TestCase):
	def setUp(self):
		User = get_user_model()
		# Create a medecin user
		self.medecin = User.objects.create_user(
			email='medecin@example.com',
			password='password',
			first_name='Med',
			last_name='One',
			phone='12345678',
			date_of_birth=datetime.date(1980, 1, 1),
			gouvernorat='Tunis',
			ville='Tunis',
			role='medecin'
		)

		# Create a patient user
		self.patient = User.objects.create_user(
			email='patient@example.com',
			password='password',
			first_name='Pat',
			last_name='One',
			phone='87654321',
			date_of_birth=datetime.date(1990, 1, 1),
			gouvernorat='Tunis',
			ville='Tunis',
			role='patient'
		)

		# Create a TimeSlot for the medecin
		self.slot = TimeSlot.objects.create(
			medecin=self.medecin,
			date=timezone.now() + datetime.timedelta(days=1),
			is_available=False
		)

		# Create an active rendezvous for the patient
		self.rdv = RendezVous.objects.create(
			patient=self.patient,
			slot=self.slot,
			status='pending'
		)

		self.client = Client()

	def test_cancel_creates_notification_and_frees_slot(self):
		# Log in as patient
		self.client.force_login(self.patient)

		url = reverse('rendezvous:cancel_rdv', kwargs={'rdv_id': self.rdv.id})
		response = self.client.post(url)

		# Refresh objects from db
		self.rdv.refresh_from_db()
		self.slot.refresh_from_db()

		# The rendezvous should be canceled and the slot freed
		self.assertEqual(self.rdv.status, 'canceled')
		self.assertTrue(self.slot.is_available)

		# A notification should exist for the medecin
		notif = Notification.objects.filter(user=self.medecin).first()
		self.assertIsNotNone(notif)
		self.assertIn('annulé', notif.message)


class ChooseMedecinFlowTests(TestCase):
	def setUp(self):
		User = get_user_model()

		# verified medecin
		self.medecin = User.objects.create_user(
			email='med2@example.com',
			password='password',
			first_name='Doc',
			last_name='Two',
			phone='11112222',
			date_of_birth=datetime.date(1975, 1, 1),
			gouvernorat='Tunis',
			ville='Tunis',
			role='medecin',
			statut='verifie'
		)

		# patient
		self.patient = User.objects.create_user(
			email='patient2@example.com',
			password='password',
			first_name='Pat',
			last_name='Two',
			phone='22223333',
			date_of_birth=datetime.date(1990, 1, 1),
			gouvernorat='Tunis',
			ville='Tunis',
			role='patient'
		)

		# create some available & non-available slots for the medecin
		self.slot_available = TimeSlot.objects.create(medecin=self.medecin, date=timezone.now() + datetime.timedelta(days=3), is_available=True)
		self.slot_taken = TimeSlot.objects.create(medecin=self.medecin, date=timezone.now() + datetime.timedelta(days=7), is_available=False)

		self.client = Client()

	def test_choisir_medecin_shows_verified_medecin_and_counts(self):
		self.client.force_login(self.patient)
		url = reverse('rendezvous:choisir_medecin')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# the medecin should be in the context
		self.assertContains(resp, self.medecin.first_name)
		# available_count should show 1 available slot
		self.assertContains(resp, 'Créneaux disponibles: <strong>1</strong>', html=True)

	def test_medecin_slots_only_shows_available_slots(self):
		self.client.force_login(self.patient)
		url = reverse('rendezvous:medecin_slots', kwargs={'medecin_id': self.medecin.id})
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# should contain available slot time
		self.assertContains(resp, self.slot_available.date.strftime('%d/%m/%Y'))
		# should NOT contain the taken slot time
		self.assertNotContains(resp, self.slot_taken.date.strftime('%d/%m/%Y'))
