from xml.etree import ElementTree as el
import re


class PlotSVG:
    """Update SVG colors depending on ID of element"""

    def __init__(self, svg, ids, maxcolor='#DB2929', mincolor='#0BB5FF'):
        el.register_namespace('', 'http://www.w3.org/2000/svg')
        self.tree = el.parse(svg)
        self.ids = ids
        self.colormap = []
        self.mincolor = mincolor
        self.maxcolor = maxcolor

    def plot(self, values):
        self.minval = min(values)
        self.maxval = max(values)
        for id, val in zip(self.ids, values):
            factor = self._calc_factor(self.minval, self.maxval, val)
            color = self._interp_color(self.mincolor, self.maxcolor, factor)
            match = self.tree.find('''.//*[@id='{:s}']'''.format(id))
            if match is None:
                raise ValueError('id "{:s}" not found in svg.'.format(id))
            if 'style' not in match.attrib:
                match.attrib['style'] = ''
            style = match.attrib['style']

            # split styles, remove fill if present, input new fill and rejoin!
            parts = style.split(';')
            parts = [p.split(':') for p in parts]
            parts = [x for x in parts if not x[0] == 'fill']
            parts.append(['fill', color])
            parts = [':'.join(x) for x in parts]
            style = ';'.join(parts)
            match.attrib['style'] = style

    def save(self, file):
        self.tree.write(file)

    def colorbar(self,
                 nlabels=5,
                 formatlabel=lambda x: '{:.1f}'.format(x),
                 height=0.75):
        root = self.tree.getroot()
        vb = root.attrib['viewBox']
        im_width = root.attrib['width']
        [posx, posy, width, height] = vb.split(' ')
        root.attrib['width'] = self._new_width(im_width, 100)
        x = float(width)
        y = float(height)/2 - 50

        s = '<g id="legend" transform="translate({:n}, {:n})">'.format(x, y)
        s += '<defs>'
        s += '<linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">'
        s += '<stop offset="0%" '
        s += 'style="stop-color:{:s}" />'.format(self.maxcolor)
        s += '<stop offset="100%" '
        s += 'style="stop-color:{:s}" />'.format(self.mincolor)
        s += '</linearGradient>'
        s += '</defs>'
        s += '<rect x="0" y="0" width="10" height="100" fill="url(#grad1)" '
        s += 'style="stroke-width:0.75;stroke:#000000" />'
        s += self._ticks(nlabels)
        s += self._labels(self.minval, self.maxval, nlabels, formatlabel)
        s += '</g>'

        legend = el.fromstring(s)
        root.append(legend)

    def _toRGB(self, hex_color):
        R = int('0x' + hex_color[1:3], 0)
        G = int('0x' + hex_color[3:5], 0)
        B = int('0x' + hex_color[5:7], 0)
        return [R, G, B]

    def _toHEX(self, rgb_color):
        output = '#'
        for val in rgb_color:
            output += '{:02x}'.format(int(round(val)))  # int needed for numpy
        return output

    def _interp_color(self, start, stop, factor):
        start = self._toRGB(start)
        stop = self._toRGB(stop)
        c = [round((v2 - v1)*factor + v1) for v1, v2 in zip(start, stop)]
        return self._toHEX(c)

    def _calc_factor(self, val1, val2, cur):
        return (cur - val1)/(val2 - val1)

    def _ticks(self, N):
        s = ''
        step = 100/(N - 1)
        for n in range(0, N):
            y = step*n
            s += '<line x1="10" y1="{:n}" x2="13" y2="{:n}" '.format(y, y)
            s += 'style="stroke-width:0.75;stroke:#000000" />'
        return s

    def _labels(self, minval, maxval, N, formatlabel):
        s = ''
        posstep = 100/(N - 1)
        valstep = (maxval - minval)/(N - 1)
        for n in range(0, N):
            y = n*posstep + 3
            v = minval + (N - n - 1)*valstep
            v = formatlabel(v)
            s += '<text x="17" y="{:n}" fill="#000000">{:s}</text>'.format(y, v)
        return s

    def _new_width(self, width, add):
        match = re.match(r"([a-z]+)([0-9]+)", width, re.I)
        if match:
            val, unit = match.groups()
            return str(int(float(val)) + add) + unit
        else:
            return str(int(float(width)) + add)
