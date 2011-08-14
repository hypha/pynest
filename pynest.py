import urllib
import urllib2
import time
import json


servers = {
    'au':'api.nestoria.com.au',
    'br':'api.nestoria.com.br',
    'de':'api.nestoria.de',
    'es':'api.nestoria.es',
    'fr':'api.nestoria.fr',
    'in':'api.nestoria.in',
    'it':'api.nestoria.it',
    'uk':'api.nestoria.co.uk',
}

country = 'uk'

api_proto = 'http'
api_method = 'GET'
api_server = servers[country]
api_path = 'api'
api_encoding = 'json'
api_url = '%s://%s/%s' % (api_proto, api_server, api_path)
api_throttle = 1.0 # secs to wait between requests

global api_last_call
api_last_call = 0.0

####
# helper methods
#
def _make_call(action, args=[], debug=0):
    ''' 
    action: (string) API method we wish to call
    args: (list of tuples) A list of key,value tuples
    '''
    
    global api_last_call
    if not action: return ''
    if action not in ['echo','keywords'] and args == []: return ''
    if time.time() - api_last_call < api_throttle: return ''
    urldata = urllib.urlencode([('action', action),
                                ('encoding',api_encoding)] + args)
    api_conn = None 
    if api_method == 'GET':
        url = '%s?%s' % (api_url, urldata)
        if debug: 
            print url
            return '{}'
        api_conn = urllib2.urlopen(url)
    else:
        #Untested. Just in case things change in the future.
        url = '%s' %s (api_url)
        if debug: 
            print url
            return '{}'
        api_conn = urllib2.urlopen(url, urldata)
    api_last_call = time.time()
    data = api_conn.read()
    if api_encoding == 'json':
        resp = json.loads(data)
    else:
        resp = data
    api_conn.close()
    return resp

def set_country(country_code):
    '''
    Set country we wish to use.
    Available country codes can be returned by using get_supported_countries(). 
    '''
    if country_code in servers.keys(): country = country_code

def get_supported_countries():
    return servers.keys()

def get_country():
    return country


####
# misc API methods
#
def echo(**kwargs):
    return _make_call('echo', kwargs.items())

def keywords():
    return _make_call('keywords')


####
# metadata methods
#
def metadata_by_area(place_name):
    '''
    place_name: (string) anything you would type into the search 
            box on Nestoria: a place name, post code, 
            tube station, etc.
            e.g. "Chelsea" or "SW14"
    '''
    return metadata(place_name=place_name)
    

def metadata_by_longlat(longlat):
    '''
    longlat: (two-tuple of strings) a bounding box in the format 
        sw_latitude, sw_longitude, ne_latitude2, ne_longitude2             
        e.g ('51.684183,-3.431481', '51.85415,-3.077859')
    '''
    return metadata(south_west=longlat[0], north_east=longlat[1])
    

def metadata_by_center(center, radius='2km'):
    '''
    center: (string) latitude and longitude. A default radius of 2km 
                will be used. 
                e.g. '51.684183,-3.431481'
    radius: (string) radius from center in kilometers or miles 
            (km or mi needs to be set) 
            e.g 10km
    '''
    s = center + ',' + radius
    return metadata(centre_point=s)

def metadata(**kwargs):
    return _make_call('metadata', kwargs.items(), debug=0)


####
# property search methods
#
def search_by_area(place_name, sf, snp):
    '''
    place_name: (string) anything you would type into the search 
            box on Nestoria: a place name, post code, 
            tube station, etc.
            e.g. "Chelsea" or "SW14"
    filter: (dictionary) http://www.nestoria.co.uk/help/api-search-listings
    '''
    d = dict([('place_name', place_name)] + sf.items() + snp.items())
    return search(**d)

def search_by_longlat(longlat, sf, snp):
    '''
    longlat: (two-tuple of strings) a bounding box in the format 
        sw_latitude, sw_longitude, ne_latitude2, ne_longitude2             
        e.g ('51.684183,-3.431481', '51.85415,-3.077859')
    sf: (dictionary) search filter as defined in 
        http://www.nestoria.co.uk/help/api-search-listings
    snp: (dictionary) Sort and pagination parameters as defined in 
        http://www.nestoria.co.uk/help/api-search-listings
    '''
    d = dict([('south_west', longlat[0]), 
                ('north_east', longlat[1]) ] + sf.items() + snp.items())
    return search(**d)

def search_by_center(center, sf, snp, radius='2km'):
    '''
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
    '''
    s = center + ',' + radius
    d = dict([('centre_point', s)] +  sf.items() + snp.items())
    return search(**d)

def search_by_guids(guid_list):
    guids = ','.join(guid_list)
    return search(guid=guids)

def search(**kwargs):
    return _make_call('search_listings', kwargs.items(), debug=0)



########################### TEST #############################################


#print echo(test='success')
#time.sleep(1.0)
#print keywords()

#print metadata_by_area(place_name='Bristol')
#print metadata_by_longlat(('51.684183,-3.431481', '51.85415,-3.077859'))
#print metadata_by_center('51.85415,-3.077859', '20km')

#sf = {}
#sf['listing_type'] = 'rent'
#sf['price_max'] = '1100'
#sf['bedroom_min'] = '2'
#snp = {}
#print search_by_area('bristol', sf, snp)
#print search_by_longlat(('51.684183,-3.431481', '51.85415,-3.077859'), sf, snp)
#print search_by_center('51.85415,-3.077859', sf, snp, radius='20km')
