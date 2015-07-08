import urllib
import requests
import time
import json
from cStringIO import StringIO
import logging

L = logging.getLogger(__name__)
servers = {
    'au': 'api.nestoria.com.au',
    'br': 'api.nestoria.com.br',
    'de': 'api.nestoria.de',
    'es': 'api.nestoria.es',
    'fr': 'api.nestoria.fr',
    'in': 'api.nestoria.in',
    'it': 'api.nestoria.it',
    'uk': 'api.nestoria.co.uk',
}

country = 'uk'

api_proto = 'http'
api_method = 'GET'
api_server = servers[country]
api_path = 'api'
api_encoding = 'json'
api_url = '%s://%s/%s' % (api_proto, api_server, api_path)
api_throttle = 1.0  # secs to wait between requests

api_last_call = 0.0

####
# helper methods
#


def download_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return StringIO(response.content)


def _make_url(action, args=[]):
    global api_last_call
    if not action:
        return ''
    if action not in ['echo', 'keywords'] and args == []:
        return ''
    if time.time() - api_last_call < api_throttle:
        return ''

    url_data = urllib.urlencode([('action', action),
                                ('encoding', api_encoding)] + args)

    url = "{}?{}".format(api_url, url_data)
    L.debug(url)
    return url


def _make_call(action, args=[]):
    url = _make_url(action, args)
    f = download_url(url)
    parsed = json.loads(f.read())
    if 'error_code' in parsed:
        raise RuntimeError("Error {}: {}".format(parsed['error_code'],
                                                 parsed['error_string']))
    return parsed


def set_country(country_code):
    """
    Choose the country we wish to use.
    Available country codes can be returned by using get_supported_countries(). 
    """

    if country_code in servers.keys():
        country = country_code


def get_supported_countries():
    """
    Return list of all supported countries
    """
    return servers.keys()


def get_country():
    """
    Return current country.
    """
    return country


####
# misc API methods
#
def echo(**kwargs):
    """
    Make an 'echo' request. Whatever named arguments are passed to this method
    are used as parameters to the request.
    """
    return _make_call('echo', kwargs.items())


def keywords():
    """
    Make a 'keywords' request. Returns all available keywords from the nestoria
    API.
    """
    return _make_call('keywords')


####
# metadata methods
#
def metadata_by_area(place_name):
    """
    place_name: (string) anything you would type into the search 
            box on Nestoria: a place name, post code, 
            tube station, etc.
            e.g. "Chelsea" or "SW14"
    """
    return metadata(place_name=place_name)
    

def metadata_by_longlat(longlat):
    """
    longlat: (two-tuple of strings) a bounding box in the format 
        sw_latitude, sw_longitude, ne_latitude2, ne_longitude2             
        e.g ('51.684183,-3.431481', '51.85415,-3.077859')
    """
    return metadata(south_west=longlat[0], north_east=longlat[1])
    

def metadata_by_center(center, radius='2km'):
    """
    center: (string) latitude and longitude. A default radius of 2km 
                will be used. 
                e.g. '51.684183,-3.431481'
    radius: (string) radius from center in kilometers or miles 
            (km or mi needs to be set) 
            e.g 10km
    """
    s = center + ',' + radius
    return metadata(centre_point=s)


def metadata(**kwargs):
    return _make_call('metadata', kwargs.items())


####
# property search methods
#
def search_by_area(place_name, sf, snp):
    """
    place_name: (string) anything you would type into the search 
            box on Nestoria: a place name, post code, 
            tube station, etc.
            e.g. "Chelsea" or "SW14"
    filter: (dictionary) http://www.nestoria.co.uk/help/api-search-listings
    """
    d = dict([('place_name', place_name)] + sf.items() + snp.items())
    return search(**d)


def search_by_longlat(longlat, sf, snp):
    """
    longlat: (two-tuple of strings) a bounding box in the format 
        sw_latitude, sw_longitude, ne_latitude2, ne_longitude2             
        e.g ('51.684183,-3.431481', '51.85415,-3.077859')
    sf: (dictionary) search filter as defined in 
        http://www.nestoria.co.uk/help/api-search-listings
    snp: (dictionary) Sort and pagination parameters as defined in 
        http://www.nestoria.co.uk/help/api-search-listings
    """
    d = dict([('south_west', longlat[0]),
              ('north_east', longlat[1])] + sf.items() + snp.items())
    return search(**d)


def search_by_center(center, sf, snp, radius='2km'):
    """
    center: (string) latitude and longitude. A default radius of 2km 
                will be used. 
                e.g. '51.684183,-3.431481'
    radius: (string) radius from center in kilometers or miles 
            (km or mi needs to be set) 
            e.g 10km
    sf: (dictionary) search filter as defined in 
        http://www.nestoria.co.uk/help/api-search-listings
    snp: (dictionary) Sort and pagination parameters as defined in 
        http://www.nestoria.co.uk/help/api-search-listings            
    """
    s = center + ',' + radius
    d = dict([('centre_point', s)] + sf.items() + snp.items())
    return search(**d)


def search_by_guids(guid_list):
    guids = ','.join(guid_list)
    return search(guid=guids)


def search(**kwargs):
    return _make_call('search_listings', kwargs.items())


# ########################## TEST ############################################ #

# print echo(test='success')
# time.sleep(1.0)
# print keywords()

# print metadata_by_area(place_name='Bristol')
# print metadata_by_longlat(('51.684183,-3.431481', '51.85415,-3.077859'))
# print metadata_by_center('51.85415,-3.077859', '20km')

# sf = {}
# sf['listing_type'] = 'rent'
# sf['price_max'] = '1100'
# sf['bedroom_min'] = '2'
# snp = {"number_of_result":50, "page":20}
# print search_by_area('bristol', sf, snp)
# print search_by_longlat(('51.684183,-3.431481', '51.85415,-3.077859'), sf, snp)
# print search_by_center('51.85415,-3.077859', sf, snp, radius='20km')
