import os
import argparse
import xmltodict
import urllib.request
import json
import logging


def get_elevation(lon, lat):
    api_key = os.environ['MAPBOX_API_KEY']
    request_string = "https://api.mapbox.com/v4/mapbox.mapbox-terrain-v2/tilequery/{},{}.json?&access_token={}".format(
            float(lon),
            float(lat),
            api_key
            )
    response = urllib.request.urlopen(request_string).read()
    response_dict = json.loads(response)['features']
    try:
        elevation = response_dict[1]['properties']['ele']
    except:
        try:
            elevation = len(response_dict)
        except:
            logger.debug('Could not fetch elevation data')
            raise
    return elevation


def make_forecast_message(mlist, step=12, days=3):
    full_message = "".join(["---\nWeather forecast by MET Norway, delivered by NPI\n",
        "Lat: {}, Lon: {}, Elev: {}\n".format(
                mlist[0]['location']['@latitude'],
                mlist[0]['location']['@longitude'],
                mlist[0]['location']['@altitude']),
        "---\n\n"])
    for elem in mlist[::step][0:int(24/step*days)]:
        message = "".join([
            'Date: {}\n'.format(elem['@to']),
            '\tTemperature: {}, Pressure: {}, Wind: {} {}\n\n'.format(
                elem['location']['temperature']['@value'],
                elem['location']['pressure']['@value'],
                elem['location']['windSpeed']['@mps'],
                elem['location']['windDirection']['@name'])])
        full_message += message

    return full_message


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log-file", default=None)
    p.add_argument("--output-file", default=None)
    p.add_argument("--request-file", default=None)

    args = p.parse_args()

    logger = logging.getLogger('yrforecast')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

    file_handler = logging.FileHandler(args.log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    with open(args.request_file) as request_string:
        request_dict = json.loads(request_string.read())
        lat = request_dict['lat']
        lon = request_dict['lon']

    msl = get_elevation(lon, lat)

    api_request = "https://api.met.no/weatherapi/locationforecast/1.9/?lat={}&lon={}&msl={}".format(
            float(lat),
            float(lon),
            int(msl))

    try:
        response = urllib.request.urlopen(api_request)
        weather_dict = xmltodict.parse(response.read())
        # acquire parts of the response which contain wind (it also has temperature, pressure, etc)
        wind = [ d for d in weather_dict['weatherdata']['product']['time'] if 'windSpeed' in d['location'] ]
        logger.info('Retrieved forecast successfully')
    except:
        logger.info('Could not retrieve forecast')
        raise

    with open(args.output_file, 'w') as ofile:
        ofile.write(make_forecast_message(wind))


if __name__ == "__main__":
    main()
