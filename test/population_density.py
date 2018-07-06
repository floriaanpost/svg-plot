from svgplot import PlotSVG
import random


province_codes = ['DR', 'FL', 'FR', 'GE', 'GR', 'LI',
                  'NB', 'NH', 'OV', 'UT', 'ZE', 'ZH']

values = [random.random() for dummy in province_codes]

svg = PlotSVG('netherlands.svg', province_codes,
              mincolor='#00cc66',
              maxcolor='#FF0000')
svg.plot(values)
svg.colorbar()
svg.save('output.svg')
