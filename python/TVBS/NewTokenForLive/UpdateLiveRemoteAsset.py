#!/usr/bin/python

#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import base64, requests, sys, json

from akamai_token_v2 import *


#########################################
#UPDATE THESE VARIABLES TO USE THIS SCRIPT


# Live URL returned from Alive API
playbackUrl = ""

# Akamai Token Information
akamaiKey='put the token auth key here'
windowSeconds=3600
acl='/*'   # Leave this one alone

#Video Cloud information
account_id    = "VideoCloud Account ID"
client_id     = "videocloud API key here"
client_secret = "videocloud API Secret here"
video_id      = "VideoCLoud Video here"
###############################################

def main(argv):
    signedUrl = SignUrl(playbackUrl)
    updateRemoteAsset(signedUrl)


def SignUrl(url):
    generator = AkamaiToken(window_seconds=windowSeconds,
                            key=akamaiKey,
                            acl=acl)

    new_token = generator.generateToken()
    signedUrl = "{}?{}".format(url,new_token)
    print "Updating URL: {} ".format(signedUrl)
    return signedUrl


def updateRemoteAsset(signedUrl):
    authToken = getAuthToken()

    asset_id = getRemoteAssetId(authToken)
    print updateHLSManifest(authToken, signedUrl, asset_id)


#
def getRemoteAssetId(authToken):
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

#
def updateHLSManifest(authToken, signedUrl, asset_id):
    headersMap = {
        "Authorization": "Bearer " + authToken,
        "Content-Type": "application/json"
    }

    # Get the assets for the video
    baseUrl = "https://cms.api.brightcove.com/v1/accounts/{account_id}/videos/{video_id}/assets/hls_manifest/{asset_id}"
    url = baseUrl.format(account_id=account_id,
                         video_id=video_id,
                         asset_id=asset_id)

    body = { "remote_url": signedUrl }

    r = requests.patch(url,data=json.dumps(body), headers=headersMap)
    print r.status_code
    if  r.status_code in [200,201]:
        print "Success!"
        return
    else:
        raise Exception('Unable to update: {}'.format(r.reason))
#
def getAuthToken():

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



if __name__ == "__main__":
	main(sys.argv)
sys.exit()