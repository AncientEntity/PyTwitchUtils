import time, requests
from PyTwitchUtils.main import Log


class TwitchApplication:
	def __init__(self,appID,appSecret):
		self._appID = appID
		self._appSecret = appSecret
		self._tempAppAuth = ""
		self._grantType = "client_credentials"
		self._expirationTime = None
		success = self.GetApplicationAuth(self._appID, self._appSecret)
		if(success):
			Log("Application Setup Success: AppID(" + self._appID + ", Verified)")
		else:
			raise CouldntValidateApplicationAuthException("Double check your application ID and secret to make sure they are valid.")
	def RawTwitchRequest(self, url):
		if (self._appID == ""):
			Log("Couldn't complete Twitch API Request, Application must first be setup.")
			return
		if time.time() - 60 >= self._expirationTime:
			self.GetApplicationAuth(self._appID, self._appSecret)
		# Regenerate auth token which is about to expire.
		head = requests.structures.CaseInsensitiveDict()
		head["Client-ID"] = self._appID
		head["Authorization"] = "Bearer " + self._tempAppAuth
		r = requests.get(url, headers=head).json()
		return r
	def ValidateApplicationOAuth(self):
		authTest = self.RawTwitchRequest("https://id.twitch.tv/oauth2/validate")
		if ("message" in authTest and authTest["message"] == "invalid access token"):
			return False
		return True
	def GetApplicationAuth(self, appID, appSecret):
		AuthHeaders = {
			'client_id': appID,
			'client_secret': appSecret,
			'grant_type': 'client_credentials',
		}
		self._appID = appID
		self._appSecret = appSecret
		authUrl = 'https://id.twitch.tv/oauth2/token'
		AutCall = requests.post(url=authUrl, params=AuthHeaders)
		autJson = AutCall.json()
		if("access_token" not in autJson):
			raise NeverRecievedApplicationAuthException("Twitch never gave us your application's auth, double check to make sure your appID/appSecret is correct.")
		access_token = autJson["access_token"]
		self._tempAppAuth = access_token
		self._expirationTime = autJson["expires_in"] + time.time()

		return self.ValidateApplicationOAuth()

class NeverRecievedApplicationAuthException(Exception):
	"""Twitch never gave us your application's auth, double check to make sure your appID/appSecret is correct."""

class CouldntValidateApplicationAuthException(Exception):
	"""Couldn't validate your twitch application auth, double check your appID/appSecret"""
	pass




