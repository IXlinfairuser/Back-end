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
import base64, requests, sys, json, smtplib, time

from akamai_token_v2 import *
# from akamai.authtoken import *


#########################################
#UPDATE THESE VARIABLES TO USE THIS SCRIPT

# Live URL returned from Alive API
playbackUrl = ""

# Akamai Token Information
akamaiKey=''
windowSeconds=1209600
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
receivers = ['','']
errorSubject = 'Sth Went Wrong !'
###############################################

def main(argv):

    signedUrl = SignUrl(playbackUrl)
    remote_url_compare = updateRemoteAsset(signedUrl)
    if remote_url_compare == signedUrl:
        compare_result = 'Updating Success!'
    else:
        compare_result = 'Sth Went Wrong While Updating the Url'
        SendErrorMail(signedUrl)
    print compare_result
    # return render(argv, 'getURL.html', {
    #     'signedUrl': signedUrl,
    #     'compare_result': compare_result,
    # })
    
# Update the New Url with Token
###############################################
def SignUrl(url):
    generator = AkamaiToken(window_seconds=windowSeconds,
                            key=akamaiKey,
                            acl=acl)

    new_token = generator.generateToken()
    signedUrl = "{}?{}".format(url,new_token)
    return signedUrl


def updateRemoteAsset(signedUrl):
    authToken = getAuthToken()

    asset_id = getRemoteAssetId(authToken)
    remote_url_compare = updateHLSManifest(authToken, signedUrl, asset_id)
    print 'updateRemoteAsset'
    print updateHLSManifest(authToken, signedUrl, asset_id)
    return remote_url_compare

def getRemoteAssetId(authToken):
    print 'getRemoteAssetId'
    headersMap = {
        "Authorization": "Bearer " + authToken,
        "Content-Type": "application/json"
    }

    # Get the assets for the video
    url = "https://cms.api.brightcove.com/v1/accounts/{}/videos/{}/assets".format(account_id, video_id)
    r = requests.get(url,headers=headersMap)
    if  r.status_code in [200,201]:
        #print json.dumps(assetId, indent=4)

        assetId = None
        for asset in r.json():
            if asset.get('type') == 'HLS_MANIFEST':
                assetId = asset.get('id')
                break

        if not assetId:
            raise Exception('Could not find valid HLS_MANIEST')
        return assetId


def updateHLSManifest(authToken, signedUrl, asset_id):
    print 'updateHLSManifest'
    headersMap = {
        "Authorization": "Bearer " + authToken,
        "Content-Type": "application/json"
    }

    # Get the assets for the video
    baseUrl = "https://cms.api.brightcove.com/v1/accounts/{account_id}/videos/{video_id}/assets/hls_manifest/{asset_id}"
    url = baseUrl.format(account_id=account_id,
                         video_id=video_id,
                         asset_id=asset_id)

    # body = { "remote_url": 'https://tvbs-alive1.akamaized.net/c3f920d0a52946c287327174357a4fb1/ap-southeast-1/4862438529001/playlist.m3u8?hdnts=exp=1507271779~acl=/*~hmac=16812c36c69c0dbc1500eddd836957f9cf493e8970ac7c0a374ec560dfb50466' }
    body = { "remote_url": signedUrl }

    r = requests.patch(url,data=json.dumps(body), headers=headersMap)
    print r.status_code
    if  r.status_code in [200,201]:
        print "Success!"
        remote_url_compare = getRemoteManiFestUrl(authToken)
        return remote_url_compare
    else:
        raise Exception('Unable to update: {}'.format(r.reason))

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


#Compare the NewUrl
###############################################

def getRemoteManiFestUrl(authToken):
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

def SendErrorMail(signedUrl):
    
    msg = MIMEMultipart()
    msg['Subject'] = errorSubject
    msg['From'] = "IPsystems"

    errorContent = 'We are sorry to inform you something went wrong while updating the RemoteUrl, \nPlease replace the new Url to Video Cloud. \nBelow is the New URL:\n{}\n\nThank you'.format(signedUrl)


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



if __name__ == "__main__":
    # while True:
    main(sys.argv)
        # time.sleep(1800)

# sys.exit()