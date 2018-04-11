# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from datetime import datetime
from django.template.loader import render_to_string
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import base64, requests, sys, json, smtplib, time, re, urlparse, time, datetime

from akamai_token_v2 import *
# from akamai.authtoken import *


#########################################
#UPDATE THESE VARIABLES TO USE THIS SCRIPT


acl='/*'   # Leave this one alone

#Video Cloud information
account_id    = ""
client_id     = ""
client_secret = ""
video_id      = ""

#Send Error Mail
sender = ''
passwd = ''
# receivers = ['']
receivers = ['']
errorSubject = 'Sth Went Wrong !'
TokenLifeWarning = 2340

GenerateSite = ''
###############################################

def main(argv):
	print 'Start Programe'

	signedUrl = getRemoteManiFestUrl()
	sUrl = SeparateUrl(signedUrl)
	ExpTime = findExpTime(sUrl)
	ttt = CompareTime(ExpTime, signedUrl)
	# print signedUrl

# verification the Url
###############################################

def SendErrorMail(signedUrl):

	msg = MIMEMultipart()
	msg['Subject'] = errorSubject
	msg['From'] = "IPsystems"

	errorContent = 'We are sorry to inform you something went wrong while updating the RemoteUrl, \nplease use the the website to generate the New Token and update it.\nBelow is the website link:\n{}\nThank you'.format(GenerateSite)


	msg.preamble = 'Multipart message. \n'
	part = MIMEText(errorContent)
	msg.attach(part)

	smtp = smtplib.SMTP('smtp.gmail.com:587')
	smtp.ehlo()
	smtp.starttls()
	smtp.login(sender, passwd)
	smtp.sendmail(msg['From'], receivers, msg.as_string())

	print msg['From'], receivers, msg.as_string()
	print 'SendMail Success'

def find(pattern, string):
	match = re.search(pattern, string)
	if match: 
		return match.group()
	else: 
		print "Found Nothing by Regular Expression !"

def findExpTime(signedUrl):
	print 'findExpTime'
	string = signedUrl
	pat = r'exp=\d+'
	match = find(pat, string)
	if match:
		string = match
		pat = r'\d+'
		ExpTime = find(pat, string)
		return ExpTime
	else:
		print "There is no Attribute Exp in The Url String !"

def SeparateUrl(signedUrl):
	sUrl = urlparse.urlparse(signedUrl)
	sUrl = urlparse.parse_qs(sUrl.query, True)
	sUrl = sUrl['hdnts'][0]
	return sUrl

def CompareTime(ExpTime, signedUrl):
	print 'CompareTime'
	now = time.time()
	DelaySpike = int(ExpTime) - now
	print str(DelaySpike)
	if DelaySpike < TokenLifeWarning:
		print 'snedNotice'
		SendErrorMail(signedUrl)
	else:
		print 'Token\'s life is good'

def getAuthToken():
	print 'getAuthToken'

	url="https://oauth.brightcove.com/v3/access_token"
	authString = base64.encodestring('%s:%s' % (client_id, client_secret)).replace('\n', '')

	headersMap = {
		"Content-Type": "application/x-www-form-urlencoded",
		"Authorization": "Basic " + authString
	}

	paramsMap = {
		"grant_type": "client_credentials"
	}
	r = requests.post(url, params=paramsMap,headers=headersMap)

	if r.status_code == 200 or r.status_code == 201:
		res = r.json()
		return res['access_token']
	else:
		raise Exception("Error retrieving Access Token: {}".format(res))

def getRemoteManiFestUrl():
	authToken = getAuthToken()
	print 'getRemoteManiFestUrl'
	headersMap = {
		"Authorization": "Bearer " + authToken,
		"Content-Type": "application/json"
	}

	# Get the assets for the video
	url = "https://cms.api.brightcove.com/v1/accounts/{}/videos/{}/assets".format(account_id, video_id)
	r = requests.get(url,headers=headersMap)
	if  r.status_code in [200,201]:
		#print json.dumps(remote_url, indent=4)

		remote_url_compare = None
		for asset in r.json():
			if asset.get('type') == 'HLS_MANIFEST':
				remote_url_compare = asset.get('remote_url')
				break

		if not remote_url_compare:
			raise Exception('Could not find valid HLS_MANIEST')
		return remote_url_compare

if __name__ == "__main__":
	# sched_Timer = datetime.datetime.now()
	# while True:
		# now = datetime.datetime.now()
		# if now>=sched_Timer:
	main(sys.argv)
			# sched_Timer=sched_Timer+datetime.timedelta(minutes=1)
		# else:
			# print 'Not 1min Yet, it only{}'.format(str(sched_Timer-now))




