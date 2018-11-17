## Presentation
This module can be used to parse json files containing a list of raw strings of locations and dates (mostly in english or german) and output a json file containing dicts of format {address:,date_iso,ranking}.
The ranking can be used in multiple ways but if you use it as is, it's just a score of how much information you have in your dict.

## How to use

Just run date_loc_parser.py, don't forget to check the requirements.md for needed libs.
You can change the file to parse and the path to the output file in config.py.
You can also change the scores given to each info to imagine a sort of binary code of presence (i.e. 1000 for info A, 100 for B and so on and then check where there are ones) so you can filter by info presence.

## Choices

- I decided to focus on being thorough rather than being fast as it made more sense if you imagine the usecase being you run the parser on a huge amount of info during the night and come to a clean dataset in the morning.
- With more time and data, it could have been interesting to analyze the data in order to understand what kind of data didn't make it through our parser in order to clean the strings a bit better.
- If no country is found and the address isn't empty, we could either choose to look for any city in both german and english in the string or limit ourselves to german cities (which would make sense considering the dataset). However the time gained was really unsignificant so I decided to go for the most precise way.
- The major issue in my solution is the in the address part. I tried to format it in city, country, road but I only achieved to get the city and country for sure; the road is just the rest of the string.

## Improvement

- One major improvement would be to take the cities in the order of how big they are because right now if there are two cities with one's name inside the others (ex: Nash and Nashua, USA) the first one will be found even if it's not the city we want.
- Mean ranking: 29.07

