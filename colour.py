###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

from Numeric import Float64, array


class Colour:
    def __init__(self):
        """Class for all functions relating to colour."""


    def linear_gradient(self, value=None, start=None, colour_list='molmol', end=None):
        """Return an RGB colour array of the value placed on a linear colour gradient.

        The argment value should be a number between zero and one.  The start and end colours can
        either be strings or RGB colour arrays.
        """

        # Translate the end colour to RGB arrays if necessary.
        if type(start) == str:
            if colour_list == 'molmol':
                start = self.molmol_colours(start)

        # Translate the end colour to RGB arrays if necessary.
        if type(end) == str:
            if colour_list == 'molmol':
                end = self.molmol_colours(end)

        # Truncate the value to be between zero and one.
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0

        # The position on the linear gradient.
        return value * (end - start) + start


    def molmol_colours(self, name):
        """
        Molmol RGB colour arrays
        ~~~~~~~~~~~~~~~~~~~~~~~~

        The following table is a list of colours used in Molmol and their corresponding RGB colour
        values ranging from 0 to 1.
        _______________________________________________________________
        |                               |         |         |         |
        | Name                          | Red     | Green   | Blue    |
        |_______________________________|_________|_________|_________|
        |                               |         |         |         |
        | 'black'                       | 0.000   | 0.000   | 0.000   |
        | 'navy'                        | 0.000   | 0.000   | 0.502   |
        | 'blue'                        | 0.000   | 0.000   | 1.000   |
        | 'dark green'                  | 0.000   | 0.392   | 0.000   |
        | 'green'                       | 0.000   | 1.000   | 0.000   |
        | 'cyan'                        | 0.000   | 1.000   | 1.000   |
        | 'turquoise'                   | 0.251   | 0.878   | 0.816   |
        | 'royal blue'                  | 0.255   | 0.412   | 0.882   |
        | 'aquamarine'                  | 0.498   | 1.000   | 0.831   |
        | 'sky green'                   | 0.529   | 0.808   | 0.922   |
        | 'dark violet'                 | 0.580   | 0.000   | 0.827   |
        | 'pale green'                  | 0.596   | 0.984   | 0.596   |
        | 'purple'                      | 0.627   | 0.125   | 0.941   |
        | 'brown'                       | 0.647   | 0.165   | 0.165   |
        | 'light blue'                  | 0.678   | 0.847   | 0.902   |
        | 'grey'                        | 0.745   | 0.745   | 0.745   |
        | 'light grey'                  | 0.827   | 0.827   | 0.827   |
        | 'violet'                      | 0.933   | 0.510   | 0.933   |
        | 'light coral'                 | 0.941   | 0.502   | 0.502   |
        | 'khaki'                       | 0.941   | 0.902   | 0.549   |
        | 'beige'                       | 0.961   | 0.961   | 0.863   |
        | 'red'                         | 1.000   | 0.000   | 0.000   |
        | 'magenta'                     | 1.000   | 0.000   | 1.000   |
        | 'deep pink'                   | 1.000   | 0.078   | 0.576   |
        | 'orange red'                  | 1.000   | 0.271   | 0.000   |
        | 'hot pink'                    | 1.000   | 0.412   | 0.706   |
        | 'coral'                       | 1.000   | 0.498   | 0.314   |
        | 'dark orange'                 | 1.000   | 0.549   | 0.000   |
        | 'orange'                      | 1.000   | 0.647   | 0.000   |
        | 'pink'                        | 1.000   | 0.753   | 0.796   |
        | 'gold'                        | 1.000   | 0.843   | 0.000   |
        | 'yellow'                      | 1.000   | 1.000   | 0.000   |
        | 'light yellow'                | 1.000   | 1.000   | 0.878   |
        | 'ivory'                       | 1.000   | 1.000   | 0.941   |
        | 'white'                       | 1.000   | 1.000   | 1.000   |
        |_______________________________|_________|_________|_________|

        """

        # Initialise the dictionary of colours.
        colours = {}

        # The colours sorted by the RGB float values.
        colours['black']        = [0.000, 0.000, 0.000]
        colours['navy']         = [0.000, 0.000, 0.502]
        colours['blue']         = [0.000, 0.000, 1.000]
        colours['dark green']   = [0.000, 0.392, 0.000]
        colours['green']        = [0.000, 1.000, 0.000]
        colours['cyan']         = [0.000, 1.000, 1.000]
        colours['turquoise']    = [0.251, 0.878, 0.816]
        colours['royal blue']   = [0.255, 0.412, 0.882]
        colours['aquamarine']   = [0.498, 1.000, 0.831]
        colours['sky green']    = [0.529, 0.808, 0.922]
        colours['dark violet']  = [0.580, 0.000, 0.827]
        colours['pale green']   = [0.596, 0.984, 0.596]
        colours['purple']       = [0.627, 0.125, 0.941]
        colours['brown']        = [0.647, 0.165, 0.165]
        colours['light blue']   = [0.678, 0.847, 0.902]
        colours['grey']         = [0.745, 0.745, 0.745]
        colours['light grey']   = [0.827, 0.827, 0.827]
        colours['violet']       = [0.933, 0.510, 0.933]
        colours['light coral']  = [0.941, 0.502, 0.502]
        colours['khaki']        = [0.941, 0.902, 0.549]
        colours['beige']        = [0.961, 0.961, 0.863]
        colours['red']          = [1.000, 0.000, 0.000]
        colours['magenta']      = [1.000, 0.000, 1.000]
        colours['deep pink']    = [1.000, 0.078, 0.576]
        colours['orange red']   = [1.000, 0.271, 0.000]
        colours['hot pink']     = [1.000, 0.412, 0.706]
        colours['coral']        = [1.000, 0.498, 0.314]
        colours['dark orange']  = [1.000, 0.549, 0.000]
        colours['orange']       = [1.000, 0.647, 0.000]
        colours['pink']         = [1.000, 0.753, 0.796]
        colours['gold']         = [1.000, 0.843, 0.000]
        colours['yellow']       = [1.000, 1.000, 0.000]
        colours['light yellow'] = [1.000, 1.000, 0.878]
        colours['ivory']        = [1.000, 1.000, 0.941]
        colours['white']        = [1.000, 1.000, 1.000]

        # Convert to Numeric arrays.
        for key in colours:
            colours[key] = array(colours[key], Float64)

        # Invalid colour string.
        if not colours.has_key(name):
            raise RelaxInvalidColourError, name

        # Return the RGB colour array.
        return colours[name]


    def x11_colours(self, name):
        """
        X11 RGB colour arrays
        ~~~~~~~~~~~~~~~~~~~~~

        The following table is the list of X11 colour names and their corresponding RGB colour
        values ranging from 0 to 255.
        _______________________________________________________________
        |                               |         |         |         |
        | Name                          | Red     | Green   | Blue    |
        |_______________________________|_________|_________|_________|
        |                               |         |         |         |
        | snow                          |     255 |     250 |     250 |
        | ghost white                   |     248 |     248 |     255 |
        | ghost white                   |     248 |     248 |     255 |
        | white smoke                   |     245 |     245 |     245 |
        | gainsboro                     |     220 |     220 |     220 |
        | floral white                  |     255 |     250 |     240 |
        | floral white                  |     255 |     250 |     240 |
        | old lace                      |     253 |     245 |     230 |
        | old lace                      |     253 |     245 |     230 |
        | linen                         |     250 |     240 |     230 |
        | antique white                 |     250 |     235 |     215 |
        | antique white                 |     250 |     235 |     215 |
        | papaya whip                   |     255 |     239 |     213 |
        | papaya whip                   |     255 |     239 |     213 |
        | blanched almond               |     255 |     235 |     205 |
        | blanched almond               |     255 |     235 |     205 |
        | bisque                        |     255 |     228 |     196 |
        | peach puff                    |     255 |     218 |     185 |
        | peach puff                    |     255 |     218 |     185 |
        | navajo white                  |     255 |     222 |     173 |
        | navajo white                  |     255 |     222 |     173 |
        | moccasin                      |     255 |     228 |     181 |
        | cornsilk                      |     255 |     248 |     220 |
        | ivory                         |     255 |     255 |     240 |
        | lemon chiffon                 |     255 |     250 |     205 |
        | lemon chiffon                 |     255 |     250 |     205 |
        | seashell                      |     255 |     245 |     238 |
        | honeydew                      |     240 |     255 |     240 |
        | mint cream                    |     245 |     255 |     250 |
        | mint cream                    |     245 |     255 |     250 |
        | azure                         |     240 |     255 |     255 |
        | alice blue                    |     240 |     248 |     255 |
        | alice blue                    |     240 |     248 |     255 |
        | lavender                      |     230 |     230 |     250 |
        | lavender blush                |     255 |     240 |     245 |
        | lavender blush                |     255 |     240 |     245 |
        | misty rose                    |     255 |     228 |     225 |
        | misty rose                    |     255 |     228 |     225 |
        | white                         |     255 |     255 |     255 |
        | black                         |       0 |       0 |       0 |
        | dark slate gray               |      47 |      79 |      79 |
        | dim gray                      |     105 |     105 |     105 |
        | slate gray                    |     112 |     128 |     144 |
        | slate gray                    |     112 |     128 |     144 |
        | slate grey                    |     112 |     128 |     144 |
        | slate grey                    |     112 |     128 |     144 |
        | light slate gray              |     119 |     136 |     153 |
        | light slate gray              |     119 |     136 |     153 |
        | light slate grey              |     119 |     136 |     153 |
        | light slate grey              |     119 |     136 |     153 |
        | gray                          |     190 |     190 |     190 |
        | light grey                    |     211 |     211 |     211 |
        | midnight blue                 |      25 |      25 |     112 |
        | midnight blue                 |      25 |      25 |     112 |
        | navy                          |       0 |       0 |     128 |
        | navy blue                     |       0 |       0 |     128 |
        | navy blue                     |       0 |       0 |     128 |
        | cornflower blue               |     100 |     149 |     237 |
        | cornflower blue               |     100 |     149 |     237 |
        | dark slate blue               |      72 |      61 |     139 |
        | dark slate blue               |      72 |      61 |     139 |
        | slate blue                    |     106 |      90 |     205 |
        | slate blue                    |     106 |      90 |     205 |
        | medium slate blue             |     123 |     104 |     238 |
        | medium slate blue             |     123 |     104 |     238 |
        | light slate blue              |     132 |     112 |     255 |
        | light slate blue              |     132 |     112 |     255 |
        | medium blue                   |       0 |       0 |     205 |
        | medium blue                   |       0 |       0 |     205 |
        | royal blue                    |      65 |     105 |     225 |
        | royal blue                    |      65 |     105 |     225 |
        | blue                          |       0 |       0 |     255 |
        | dodger blue                   |      30 |     144 |     255 |
        | dodger blue                   |      30 |     144 |     255 |
        | deep sky blue                 |       0 |     191 |     255 |
        | deep sky blue                 |       0 |     191 |     255 |
        | sky blue                      |     135 |     206 |     235 |
        | sky blue                      |     135 |     206 |     235 |
        | light sky blue                |     135 |     206 |     250 |
        | light sky blue                |     135 |     206 |     250 |
        | steel blue                    |      70 |     130 |     180 |
        | steel blue                    |      70 |     130 |     180 |
        | light steel blue              |     176 |     196 |     222 |
        | light steel blue              |     176 |     196 |     222 |
        | light blue                    |     173 |     216 |     230 |
        | light blue                    |     173 |     216 |     230 |
        | powder blue                   |     176 |     224 |     230 |
        | powder blue                   |     176 |     224 |     230 |
        | pale turquoise                |     175 |     238 |     238 |
        | dark turquoise                |       0 |     206 |     209 |
        | dark turquoise                |       0 |     206 |     209 |
        | medium turquoise              |      72 |     209 |     204 |
        | medium turquoise              |      72 |     209 |     204 |
        | turquoise                     |      64 |     224 |     208 |
        | cyan                          |       0 |     255 |     255 |
        | light cyan                    |     224 |     255 |     255 |
        | cadet blue                    |      95 |     158 |     160 |
        | cadet blue                    |      95 |     158 |     160 |
        | medium aquamarine             |     102 |     205 |     170 |
        | medium aquamarine             |     102 |     205 |     170 |
        | aquamarine                    |     127 |     255 |     212 |
        | dark green                    |       0 |     100 |       0 |
        | dark green                    |       0 |     100 |       0 |
        | dark olive green              |      85 |     107 |      47 |
        | dark olive green              |      85 |     107 |      47 |
        | dark sea green                |     143 |     188 |     143 |
        | dark sea green                |     143 |     188 |     143 |
        | sea green                     |      46 |     139 |      87 |
        | sea green                     |      46 |     139 |      87 |
        | medium sea green              |      60 |     179 |     113 |
        | medium sea green              |      60 |     179 |     113 |
        | light sea green               |      32 |     178 |     170 |
        | light sea green               |      32 |     178 |     170 |
        | pale green                    |     152 |     251 |     152 |
        | pale green                    |     152 |     251 |     152 |
        | spring green                  |       0 |     255 |     127 |
        | spring green                  |       0 |     255 |     127 |
        | lawn green                    |     124 |     252 |       0 |
        | lawn green                    |     124 |     252 |       0 |
        | green                         |       0 |     255 |       0 |
        | chartreuse                    |     127 |     255 |       0 |
        | medium spring green           |       0 |     250 |     154 |
        | medium spring green           |       0 |     250 |     154 |
        | green yellow                  |     173 |     255 |      47 |
        | green yellow                  |     173 |     255 |      47 |
        | lime green                    |      50 |     205 |      50 |
        | lime green                    |      50 |     205 |      50 |
        | yellow green                  |     154 |     205 |      50 |
        | yellow green                  |     154 |     205 |      50 |
        | forest green                  |      34 |     139 |      34 |
        | forest green                  |      34 |     139 |      34 |
        | olive drab                    |     107 |     142 |      35 |
        | olive drab                    |     107 |     142 |      35 |
        | dark khaki                    |     189 |     183 |     107 |
        | dark khaki                    |     189 |     183 |     107 |
        | khaki                         |     240 |     230 |     140 |
        | pale goldenrod                |     238 |     232 |     170 |
        | pale goldenrod                |     238 |     232 |     170 |
        | light goldenrod yellow        |     250 |     250 |     210 |
        | light goldenrod yellow        |     250 |     250 |     210 |
        | light yellow                  |     255 |     255 |     224 |
        | light yellow                  |     255 |     255 |     224 |
        | yellow                        |     255 |     255 |       0 |
        | gold                          |     255 |     215 |       0 |
        | light goldenrod               |     238 |     221 |     130 |
        | light goldenrod               |     238 |     221 |     130 |
        | goldenrod                     |     218 |     165 |      32 |
        | dark goldenrod                |     184 |     134 |      11 |
        | dark goldenrod                |     184 |     134 |      11 |
        | rosy brown                    |     188 |     143 |     143 |
        | indian red                    |     205 |      92 |      92 |
        | saddle brown                  |     139 |      69 |      19 |
        | saddle brown                  |     139 |      69 |      19 |
        | sienna                        |     160 |      82 |      45 |
        | peru                          |     205 |     133 |      63 |
        | burlywood                     |     222 |     184 |     135 |
        | beige                         |     245 |     245 |     220 |
        | wheat                         |     245 |     222 |     179 |
        | sandy brown                   |     244 |     164 |      96 |
        | sandy brown                   |     244 |     164 |      96 |
        | tan                           |     210 |     180 |     140 |
        | chocolate                     |     210 |     105 |      30 |
        | firebrick                     |     178 |      34 |      34 |
        | brown                         |     165 |      42 |      42 |
        | dark salmon                   |     233 |     150 |     122 |
        | dark salmon                   |     233 |     150 |     122 |
        | salmon                        |     250 |     128 |     114 |
        | light salmon                  |     255 |     160 |     122 |
        | light salmon                  |     255 |     160 |     122 |
        | orange                        |     255 |     165 |       0 |
        | dark orange                   |     255 |     140 |       0 |
        | dark orange                   |     255 |     140 |       0 |
        | coral                         |     255 |     127 |      80 |
        | light coral                   |     240 |     128 |     128 |
        | tomato                        |     255 |      99 |      71 |
        | orange red                    |     255 |      69 |       0 |
        | orange red                    |     255 |      69 |       0 |
        | red                           |     255 |       0 |       0 |
        | hot pink                      |     255 |     105 |     180 |
        | hot pink                      |     255 |     105 |     180 |
        | deep pink                     |     255 |      20 |     147 |
        | deep pink                     |     255 |      20 |     147 |
        | pink                          |     255 |     192 |     203 |
        | light pink                    |     255 |     182 |     193 |
        | light pink                    |     255 |     182 |     193 |
        | pale violet red               |     219 |     112 |     147 |
        | pale violet red               |     219 |     112 |     147 |
        | maroon                        |     176 |      48 |      96 |
        | medium violet red             |     199 |      21 |     133 |
        | medium violet red             |     199 |      21 |     133 |
        | violet red                    |     208 |      32 |     144 |
        | violet red                    |     208 |      32 |     144 |
        | magenta                       |     255 |       0 |     255 |
        | violet                        |     238 |     130 |     238 |
        | plum                          |     221 |     160 |     221 |
        | orchid                        |     218 |     112 |     214 |
        | medium orchid                 |     186 |      85 |     211 |
        | medium orchid                 |     186 |      85 |     211 |
        | dark orchid                   |     153 |      50 |     204 |
        | dark orchid                   |     153 |      50 |     204 |
        | dark violet                   |     148 |       0 |     211 |
        | dark violet                   |     148 |       0 |     211 |
        | blue violet                   |     138 |      43 |     226 |
        | blue violet                   |     138 |      43 |     226 |
        | purple                        |     160 |      32 |     240 |
        | medium purple                 |     147 |     112 |     219 |
        | medium purple                 |     147 |     112 |     219 |
        | thistle                       |     216 |     191 |     216 |
        | snow 1                        |     255 |     250 |     250 |
        | snow 2                        |     238 |     233 |     233 |
        | snow 3                        |     205 |     201 |     201 |
        | snow 4                        |     139 |     137 |     137 |
        | seashell 1                    |     255 |     245 |     238 |
        | seashell 2                    |     238 |     229 |     222 |
        | seashell 3                    |     205 |     197 |     191 |
        | seashell 4                    |     139 |     134 |     130 |
        | antique white 1               |     255 |     239 |     219 |
        | antique white 2               |     238 |     223 |     204 |
        | antique white 3               |     205 |     192 |     176 |
        | antique white 4               |     139 |     131 |     120 |
        | bisque 1                      |     255 |     228 |     196 |
        | bisque 2                      |     238 |     213 |     183 |
        | bisque 3                      |     205 |     183 |     158 |
        | bisque 4                      |     139 |     125 |     107 |
        | peach puff 1                  |     255 |     218 |     185 |
        | peach puff 2                  |     238 |     203 |     173 |
        | peach puff 3                  |     205 |     175 |     149 |
        | peach puff 4                  |     139 |     119 |     101 |
        | navajo white 1                |     255 |     222 |     173 |
        | navajo white 2                |     238 |     207 |     161 |
        | navajo white 3                |     205 |     179 |     139 |
        | navajo white 4                |     139 |     121 |      94 |
        | lemon chiffon 1               |     255 |     250 |     205 |
        | lemon chiffon 2               |     238 |     233 |     191 |
        | lemon chiffon 3               |     205 |     201 |     165 |
        | lemon chiffon 4               |     139 |     137 |     112 |
        | cornsilk 1                    |     255 |     248 |     220 |
        | cornsilk 2                    |     238 |     232 |     205 |
        | cornsilk 3                    |     205 |     200 |     177 |
        | cornsilk 4                    |     139 |     136 |     120 |
        | ivory 1                       |     255 |     255 |     240 |
        | ivory 2                       |     238 |     238 |     224 |
        | ivory 3                       |     205 |     205 |     193 |
        | ivory 4                       |     139 |     139 |     131 |
        | honeydew 1                    |     240 |     255 |     240 |
        | honeydew 2                    |     224 |     238 |     224 |
        | honeydew 3                    |     193 |     205 |     193 |
        | honeydew 4                    |     131 |     139 |     131 |
        | lavender blush 1              |     255 |     240 |     245 |
        | lavender blush 2              |     238 |     224 |     229 |
        | lavender blush 3              |     205 |     193 |     197 |
        | lavender blush 4              |     139 |     131 |     134 |
        | misty rose 1                  |     255 |     228 |     225 |
        | misty rose 2                  |     238 |     213 |     210 |
        | misty rose 3                  |     205 |     183 |     181 |
        | misty rose 4                  |     139 |     125 |     123 |
        | azure 1                       |     240 |     255 |     255 |
        | azure 2                       |     224 |     238 |     238 |
        | azure 3                       |     193 |     205 |     205 |
        | azure 4                       |     131 |     139 |     139 |
        | slate blue 1                  |     131 |     111 |     255 |
        | slate blue 2                  |     122 |     103 |     238 |
        | slate blue 3                  |     105 |      89 |     205 |
        | slate blue 4                  |      71 |      60 |     139 |
        | royal blue 1                  |      72 |     118 |     255 |
        | royal blue 2                  |      67 |     110 |     238 |
        | royal blue 3                  |      58 |      95 |     205 |
        | royal blue 4                  |      39 |      64 |     139 |
        | blue 1                        |       0 |       0 |     255 |
        | blue 2                        |       0 |       0 |     238 |
        | blue 3                        |       0 |       0 |     205 |
        | blue 4                        |       0 |       0 |     139 |
        | dodger blue 1                 |      30 |     144 |     255 |
        | dodger blue 2                 |      28 |     134 |     238 |
        | dodger blue 3                 |      24 |     116 |     205 |
        | dodger blue 4                 |      16 |      78 |     139 |
        | steel blue 1                  |      99 |     184 |     255 |
        | steel blue 2                  |      92 |     172 |     238 |
        | steel blue 3                  |      79 |     148 |     205 |
        | steel blue 4                  |      54 |     100 |     139 |
        | deep sky blue 1               |       0 |     191 |     255 |
        | deep sky blue 2               |       0 |     178 |     238 |
        | deep sky blue 3               |       0 |     154 |     205 |
        | deep sky blue 4               |       0 |     104 |     139 |
        | sky blue 1                    |     135 |     206 |     255 |
        | sky blue 2                    |     126 |     192 |     238 |
        | sky blue 3                    |     108 |     166 |     205 |
        | sky blue 4                    |      74 |     112 |     139 |
        | light sky blue 1              |     176 |     226 |     255 |
        | light sky blue 2              |     164 |     211 |     238 |
        | light sky blue 3              |     141 |     182 |     205 |
        | light sky blue 4              |      96 |     123 |     139 |
        | slate gray 1                  |     198 |     226 |     255 |
        | slate gray 2                  |     185 |     211 |     238 |
        | slate gray 3                  |     159 |     182 |     205 |
        | slate gray 4                  |     108 |     123 |     139 |
        | light steel blue 1            |     202 |     225 |     255 |
        | light steel blue 2            |     188 |     210 |     238 |
        | light steel blue 3            |     162 |     181 |     205 |
        | light steel blue 4            |     110 |     123 |     139 |
        | light blue 1                  |     191 |     239 |     255 |
        | light blue 2                  |     178 |     223 |     238 |
        | light blue 3                  |     154 |     192 |     205 |
        | light blue 4                  |     104 |     131 |     139 |
        | light cyan 1                  |     224 |     255 |     255 |
        | light cyan 2                  |     209 |     238 |     238 |
        | light cyan 3                  |     180 |     205 |     205 |
        | light cyan 4                  |     122 |     139 |     139 |
        | pale turquoise 1              |     187 |     255 |     255 |
        | pale turquoise 2              |     174 |     238 |     238 |
        | pale turquoise 3              |     150 |     205 |     205 |
        | pale turquoise 4              |     102 |     139 |     139 |
        | cadet blue 1                  |     152 |     245 |     255 |
        | cadet blue 2                  |     142 |     229 |     238 |
        | cadet blue 3                  |     122 |     197 |     205 |
        | cadet blue 4                  |      83 |     134 |     139 |
        | turquoise 1                   |       0 |     245 |     255 |
        | turquoise 2                   |       0 |     229 |     238 |
        | turquoise 3                   |       0 |     197 |     205 |
        | turquoise 4                   |       0 |     134 |     139 |
        | cyan 1                        |       0 |     255 |     255 |
        | cyan 2                        |       0 |     238 |     238 |
        | cyan 3                        |       0 |     205 |     205 |
        | cyan 4                        |       0 |     139 |     139 |
        | dark slate gray 1             |     151 |     255 |     255 |
        | dark slate gray 2             |     141 |     238 |     238 |
        | dark slate gray 3             |     121 |     205 |     205 |
        | dark slate gray 4             |      82 |     139 |     139 |
        | aquamarine 1                  |     127 |     255 |     212 |
        | aquamarine 2                  |     118 |     238 |     198 |
        | aquamarine 3                  |     102 |     205 |     170 |
        | aquamarine 4                  |      69 |     139 |     116 |
        | dark sea green 1              |     193 |     255 |     193 |
        | dark sea green 2              |     180 |     238 |     180 |
        | dark sea green 3              |     155 |     205 |     155 |
        | dark sea green 4              |     105 |     139 |     105 |
        | sea green 1                   |      84 |     255 |     159 |
        | sea green 2                   |      78 |     238 |     148 |
        | sea green 3                   |      67 |     205 |     128 |
        | sea green 4                   |      46 |     139 |      87 |
        | pale green 1                  |     154 |     255 |     154 |
        | pale green 2                  |     144 |     238 |     144 |
        | pale green 3                  |     124 |     205 |     124 |
        | pale green 4                  |      84 |     139 |      84 |
        | spring green 1                |       0 |     255 |     127 |
        | spring green 2                |       0 |     238 |     118 |
        | spring green 3                |       0 |     205 |     102 |
        | spring green 4                |       0 |     139 |      69 |
        | green 1                       |       0 |     255 |       0 |
        | green 2                       |       0 |     238 |       0 |
        | green 3                       |       0 |     205 |       0 |
        | green 4                       |       0 |     139 |       0 |
        | chartreuse 1                  |     127 |     255 |       0 |
        | chartreuse 2                  |     118 |     238 |       0 |
        | chartreuse 3                  |     102 |     205 |       0 |
        | chartreuse 4                  |      69 |     139 |       0 |
        | olive drab 1                  |     192 |     255 |      62 |
        | olive drab 2                  |     179 |     238 |      58 |
        | olive drab 3                  |     154 |     205 |      50 |
        | olive drab 4                  |     105 |     139 |      34 |
        | dark olive green 1            |     202 |     255 |     112 |
        | dark olive green 2            |     188 |     238 |     104 |
        | dark olive green 3            |     162 |     205 |      90 |
        | dark olive green 4            |     110 |     139 |      61 |
        | khaki 1                       |     255 |     246 |     143 |
        | khaki 2                       |     238 |     230 |     133 |
        | khaki 3                       |     205 |     198 |     115 |
        | khaki 4                       |     139 |     134 |      78 |
        | light goldenrod 1             |     255 |     236 |     139 |
        | light goldenrod 2             |     238 |     220 |     130 |
        | light goldenrod 3             |     205 |     190 |     112 |
        | light goldenrod 4             |     139 |     129 |      76 |
        | light yellow 1                |     255 |     255 |     224 |
        | light yellow 2                |     238 |     238 |     209 |
        | light yellow 3                |     205 |     205 |     180 |
        | light yellow 4                |     139 |     139 |     122 |
        | yellow 1                      |     255 |     255 |       0 |
        | yellow 2                      |     238 |     238 |       0 |
        | yellow 3                      |     205 |     205 |       0 |
        | yellow 4                      |     139 |     139 |       0 |
        | gold 1                        |     255 |     215 |       0 |
        | gold 2                        |     238 |     201 |       0 |
        | gold 3                        |     205 |     173 |       0 |
        | gold 4                        |     139 |     117 |       0 |
        | goldenrod 1                   |     255 |     193 |      37 |
        | goldenrod 2                   |     238 |     180 |      34 |
        | goldenrod 3                   |     205 |     155 |      29 |
        | goldenrod 4                   |     139 |     105 |      20 |
        | dark goldenrod 1              |     255 |     185 |      15 |
        | dark goldenrod 2              |     238 |     173 |      14 |
        | dark goldenrod 3              |     205 |     149 |      12 |
        | dark goldenrod 4              |     139 |     101 |       8 |
        | rosy brown 1                  |     255 |     193 |     193 |
        | rosy brown 2                  |     238 |     180 |     180 |
        | rosy brown 3                  |     205 |     155 |     155 |
        | rosy brown 4                  |     139 |     105 |     105 |
        | indian red 1                  |     255 |     106 |     106 |
        | indian red 2                  |     238 |      99 |      99 |
        | indian red 3                  |     205 |      85 |      85 |
        | indian red 4                  |     139 |      58 |      58 |
        | sienna 1                      |     255 |     130 |      71 |
        | sienna 2                      |     238 |     121 |      66 |
        | sienna 3                      |     205 |     104 |      57 |
        | sienna 4                      |     139 |      71 |      38 |
        | burlywood 1                   |     255 |     211 |     155 |
        | burlywood 2                   |     238 |     197 |     145 |
        | burlywood 3                   |     205 |     170 |     125 |
        | burlywood 4                   |     139 |     115 |      85 |
        | wheat 1                       |     255 |     231 |     186 |
        | wheat 2                       |     238 |     216 |     174 |
        | wheat 3                       |     205 |     186 |     150 |
        | wheat 4                       |     139 |     126 |     102 |
        | tan 1                         |     255 |     165 |      79 |
        | tan 2                         |     238 |     154 |      73 |
        | tan 3                         |     205 |     133 |      63 |
        | tan 4                         |     139 |      90 |      43 |
        | chocolate 1                   |     255 |     127 |      36 |
        | chocolate 2                   |     238 |     118 |      33 |
        | chocolate 3                   |     205 |     102 |      29 |
        | chocolate 4                   |     139 |      69 |      19 |
        | firebrick 1                   |     255 |      48 |      48 |
        | firebrick 2                   |     238 |      44 |      44 |
        | firebrick 3                   |     205 |      38 |      38 |
        | firebrick 4                   |     139 |      26 |      26 |
        | brown 1                       |     255 |      64 |      64 |
        | brown 2                       |     238 |      59 |      59 |
        | brown 3                       |     205 |      51 |      51 |
        | brown 4                       |     139 |      35 |      35 |
        | salmon 1                      |     255 |     140 |     105 |
        | salmon 2                      |     238 |     130 |      98 |
        | salmon 3                      |     205 |     112 |      84 |
        | salmon 4                      |     139 |      76 |      57 |
        | light salmon 1                |     255 |     160 |     122 |
        | light salmon 2                |     238 |     149 |     114 |
        | light salmon 3                |     205 |     129 |      98 |
        | light salmon 4                |     139 |      87 |      66 |
        | orange 1                      |     255 |     165 |       0 |
        | orange 2                      |     238 |     154 |       0 |
        | orange 3                      |     205 |     133 |       0 |
        | orange 4                      |     139 |      90 |       0 |
        | dark orange 1                 |     255 |     127 |       0 |
        | dark orange 2                 |     238 |     118 |       0 |
        | dark orange 3                 |     205 |     102 |       0 |
        | dark orange 4                 |     139 |      69 |       0 |
        | coral 1                       |     255 |     114 |      86 |
        | coral 2                       |     238 |     106 |      80 |
        | coral 3                       |     205 |      91 |      69 |
        | coral 4                       |     139 |      62 |      47 |
        | tomato 1                      |     255 |      99 |      71 |
        | tomato 2                      |     238 |      92 |      66 |
        | tomato 3                      |     205 |      79 |      57 |
        | tomato 4                      |     139 |      54 |      38 |
        | orange red 1                  |     255 |      69 |       0 |
        | orange red 2                  |     238 |      64 |       0 |
        | orange red 3                  |     205 |      55 |       0 |
        | orange red 4                  |     139 |      37 |       0 |
        | red 1                         |     255 |       0 |       0 |
        | red 2                         |     238 |       0 |       0 |
        | red 3                         |     205 |       0 |       0 |
        | red 4                         |     139 |       0 |       0 |
        | deep pink 1                   |     255 |      20 |     147 |
        | deep pink 2                   |     238 |      18 |     137 |
        | deep pink 3                   |     205 |      16 |     118 |
        | deep pink 4                   |     139 |      10 |      80 |
        | hot pink 1                    |     255 |     110 |     180 |
        | hot pink 2                    |     238 |     106 |     167 |
        | hot pink 3                    |     205 |      96 |     144 |
        | hot pink 4                    |     139 |      58 |      98 |
        | pink 1                        |     255 |     181 |     197 |
        | pink 2                        |     238 |     169 |     184 |
        | pink 3                        |     205 |     145 |     158 |
        | pink 4                        |     139 |      99 |     108 |
        | light pink 1                  |     255 |     174 |     185 |
        | light pink 2                  |     238 |     162 |     173 |
        | light pink 3                  |     205 |     140 |     149 |
        | light pink 4                  |     139 |      95 |     101 |
        | pale violet red 1             |     255 |     130 |     171 |
        | pale violet red 2             |     238 |     121 |     159 |
        | pale violet red 3             |     205 |     104 |     137 |
        | pale violet red 4             |     139 |      71 |      93 |
        | maroon 1                      |     255 |      52 |     179 |
        | maroon 2                      |     238 |      48 |     167 |
        | maroon 3                      |     205 |      41 |     144 |
        | maroon 4                      |     139 |      28 |      98 |
        | violet red 1                  |     255 |      62 |     150 |
        | violet red 2                  |     238 |      58 |     140 |
        | violet red 3                  |     205 |      50 |     120 |
        | violet red 4                  |     139 |      34 |      82 |
        | magenta 1                     |     255 |       0 |     255 |
        | magenta 2                     |     238 |       0 |     238 |
        | magenta 3                     |     205 |       0 |     205 |
        | magenta 4                     |     139 |       0 |     139 |
        | orchid 1                      |     255 |     131 |     250 |
        | orchid 2                      |     238 |     122 |     233 |
        | orchid 3                      |     205 |     105 |     201 |
        | orchid 4                      |     139 |      71 |     137 |
        | plum 1                        |     255 |     187 |     255 |
        | plum 2                        |     238 |     174 |     238 |
        | plum 3                        |     205 |     150 |     205 |
        | plum 4                        |     139 |     102 |     139 |
        | medium orchid 1               |     224 |     102 |     255 |
        | medium orchid 2               |     209 |      95 |     238 |
        | medium orchid 3               |     180 |      82 |     205 |
        | medium orchid 4               |     122 |      55 |     139 |
        | dark orchid 1                 |     191 |      62 |     255 |
        | dark orchid 2                 |     178 |      58 |     238 |
        | dark orchid 3                 |     154 |      50 |     205 |
        | dark orchid 4                 |     104 |      34 |     139 |
        | purple 1                      |     155 |      48 |     255 |
        | purple 2                      |     145 |      44 |     238 |
        | purple 3                      |     125 |      38 |     205 |
        | purple 4                      |      85 |      26 |     139 |
        | medium purple 1               |     171 |     130 |     255 |
        | medium purple 2               |     159 |     121 |     238 |
        | medium purple 3               |     137 |     104 |     205 |
        | medium purple 4               |      93 |      71 |     139 |
        | thistle 1                     |     255 |     225 |     255 |
        | thistle 2                     |     238 |     210 |     238 |
        | thistle 3                     |     205 |     181 |     205 |
        | thistle 4                     |     139 |     123 |     139 |
        | gray 0                        |       0 |       0 |       0 |
        | gray 1                        |       3 |       3 |       3 |
        | gray 2                        |       5 |       5 |       5 |
        | gray 3                        |       8 |       8 |       8 |
        | gray 4                        |      10 |      10 |      10 |
        | gray 5                        |      13 |      13 |      13 |
        | gray 6                        |      15 |      15 |      15 |
        | gray 7                        |      18 |      18 |      18 |
        | gray 8                        |      20 |      20 |      20 |
        | gray 9                        |      23 |      23 |      23 |
        | gray 10                       |      26 |      26 |      26 |
        | gray 11                       |      28 |      28 |      28 |
        | gray 12                       |      31 |      31 |      31 |
        | gray 13                       |      33 |      33 |      33 |
        | gray 14                       |      36 |      36 |      36 |
        | gray 15                       |      38 |      38 |      38 |
        | gray 16                       |      41 |      41 |      41 |
        | gray 17                       |      43 |      43 |      43 |
        | gray 18                       |      46 |      46 |      46 |
        | gray 19                       |      48 |      48 |      48 |
        | gray 20                       |      51 |      51 |      51 |
        | gray 21                       |      54 |      54 |      54 |
        | gray 22                       |      56 |      56 |      56 |
        | gray 23                       |      59 |      59 |      59 |
        | gray 24                       |      61 |      61 |      61 |
        | gray 25                       |      64 |      64 |      64 |
        | gray 26                       |      66 |      66 |      66 |
        | gray 27                       |      69 |      69 |      69 |
        | gray 28                       |      71 |      71 |      71 |
        | gray 29                       |      74 |      74 |      74 |
        | gray 30                       |      77 |      77 |      77 |
        | gray 31                       |      79 |      79 |      79 |
        | gray 32                       |      82 |      82 |      82 |
        | gray 33                       |      84 |      84 |      84 |
        | gray 34                       |      87 |      87 |      87 |
        | gray 35                       |      89 |      89 |      89 |
        | gray 36                       |      92 |      92 |      92 |
        | gray 37                       |      94 |      94 |      94 |
        | gray 38                       |      97 |      97 |      97 |
        | gray 39                       |      99 |      99 |      99 |
        | gray 40                       |     102 |     102 |     102 |
        | gray 41                       |     105 |     105 |     105 |
        | gray 42                       |     107 |     107 |     107 |
        | gray 43                       |     110 |     110 |     110 |
        | gray 44                       |     112 |     112 |     112 |
        | gray 45                       |     115 |     115 |     115 |
        | gray 46                       |     117 |     117 |     117 |
        | gray 47                       |     120 |     120 |     120 |
        | gray 48                       |     122 |     122 |     122 |
        | gray 49                       |     125 |     125 |     125 |
        | gray 50                       |     127 |     127 |     127 |
        | gray 51                       |     130 |     130 |     130 |
        | gray 52                       |     133 |     133 |     133 |
        | gray 53                       |     135 |     135 |     135 |
        | gray 54                       |     138 |     138 |     138 |
        | gray 55                       |     140 |     140 |     140 |
        | gray 56                       |     143 |     143 |     143 |
        | gray 57                       |     145 |     145 |     145 |
        | gray 58                       |     148 |     148 |     148 |
        | gray 59                       |     150 |     150 |     150 |
        | gray 60                       |     153 |     153 |     153 |
        | gray 61                       |     156 |     156 |     156 |
        | gray 62                       |     158 |     158 |     158 |
        | gray 63                       |     161 |     161 |     161 |
        | gray 64                       |     163 |     163 |     163 |
        | gray 65                       |     166 |     166 |     166 |
        | gray 66                       |     168 |     168 |     168 |
        | gray 67                       |     171 |     171 |     171 |
        | gray 68                       |     173 |     173 |     173 |
        | gray 69                       |     176 |     176 |     176 |
        | gray 70                       |     179 |     179 |     179 |
        | gray 71                       |     181 |     181 |     181 |
        | gray 72                       |     184 |     184 |     184 |
        | gray 73                       |     186 |     186 |     186 |
        | gray 74                       |     189 |     189 |     189 |
        | gray 75                       |     191 |     191 |     191 |
        | gray 76                       |     194 |     194 |     194 |
        | gray 77                       |     196 |     196 |     196 |
        | gray 78                       |     199 |     199 |     199 |
        | gray 79                       |     201 |     201 |     201 |
        | gray 80                       |     204 |     204 |     204 |
        | gray 81                       |     207 |     207 |     207 |
        | gray 82                       |     209 |     209 |     209 |
        | gray 83                       |     212 |     212 |     212 |
        | gray 84                       |     214 |     214 |     214 |
        | gray 85                       |     217 |     217 |     217 |
        | gray 86                       |     219 |     219 |     219 |
        | gray 87                       |     222 |     222 |     222 |
        | gray 88                       |     224 |     224 |     224 |
        | gray 89                       |     227 |     227 |     227 |
        | gray 90                       |     229 |     229 |     229 |
        | gray 91                       |     232 |     232 |     232 |
        | gray 92                       |     235 |     235 |     235 |
        | gray 93                       |     237 |     237 |     237 |
        | gray 94                       |     240 |     240 |     240 |
        | gray 95                       |     242 |     242 |     242 |
        | gray 96                       |     245 |     245 |     245 |
        | gray 97                       |     247 |     247 |     247 |
        | gray 98                       |     250 |     250 |     250 |
        | gray 99                       |     252 |     252 |     252 |
        | gray 100                      |     255 |     255 |     255 |
        | dark grey                     |     169 |     169 |     169 |
        | dark blue                     |       0 |       0 |     139 |
        | dark blue                     |       0 |       0 |     139 |
        | dark cyan                     |       0 |     139 |     139 |
        | dark magenta                  |     139 |       0 |     139 |
        | dark magenta                  |     139 |       0 |     139 |
        | dark red                      |     139 |       0 |       0 |
        | light green                   |     144 |     238 |     144 |
        | light green                   |     144 |     238 |     144 |
        |_______________________________|_________|_________|_________|

        """

        # Initialise the dictionary of colours.
        colours = {}

        # The colours as sorted in the /usr/X11R6/lib/X11/rgb.txt file.
        colours['snow']                     = [255, 250, 250]
        colours['ghost white']              = [248, 248, 255]
        colours['ghost white']              = [248, 248, 255]
        colours['white smoke']              = [245, 245, 245]
        colours['gainsboro']                = [220, 220, 220]
        colours['floral white']             = [255, 250, 240]
        colours['floral white']             = [255, 250, 240]
        colours['old lace']                 = [253, 245, 230]
        colours['old lace']                 = [253, 245, 230]
        colours['linen']                    = [250, 240, 230]
        colours['antique white']            = [250, 235, 215]
        colours['antique white']            = [250, 235, 215]
        colours['papaya whip']              = [255, 239, 213]
        colours['papaya whip']              = [255, 239, 213]
        colours['blanched almond']          = [255, 235, 205]
        colours['blanched almond']          = [255, 235, 205]
        colours['bisque']                   = [255, 228, 196]
        colours['peach puff']               = [255, 218, 185]
        colours['peach puff']               = [255, 218, 185]
        colours['navajo white']             = [255, 222, 173]
        colours['navajo white']             = [255, 222, 173]
        colours['moccasin']                 = [255, 228, 181]
        colours['cornsilk']                 = [255, 248, 220]
        colours['ivory']                    = [255, 255, 240]
        colours['lemon chiffon']            = [255, 250, 205]
        colours['lemon chiffon']            = [255, 250, 205]
        colours['seashell']                 = [255, 245, 238]
        colours['honeydew']                 = [240, 255, 240]
        colours['mint cream']               = [245, 255, 250]
        colours['mint cream']               = [245, 255, 250]
        colours['azure']                    = [240, 255, 255]
        colours['alice blue']               = [240, 248, 255]
        colours['alice blue']               = [240, 248, 255]
        colours['lavender']                 = [230, 230, 250]
        colours['lavender blush']           = [255, 240, 245]
        colours['lavender blush']           = [255, 240, 245]
        colours['misty rose']               = [255, 228, 225]
        colours['misty rose']               = [255, 228, 225]
        colours['white']                    = [255, 255, 255]
        colours['black']                    = [  0,   0,   0]
        colours['dark slate gray']          = [ 47,  79,  79]
        colours['dim gray']                 = [105, 105, 105]
        colours['slate gray']               = [112, 128, 144]
        colours['slate gray']               = [112, 128, 144]
        colours['slate grey']               = [112, 128, 144]
        colours['slate grey']               = [112, 128, 144]
        colours['light slate gray']         = [119, 136, 153]
        colours['light slate gray']         = [119, 136, 153]
        colours['light slate grey']         = [119, 136, 153]
        colours['light slate grey']         = [119, 136, 153]
        colours['gray']                     = [190, 190, 190]
        colours['light grey']               = [211, 211, 211]
        colours['midnight blue']            = [ 25,  25, 112]
        colours['midnight blue']            = [ 25,  25, 112]
        colours['navy']                     = [  0,   0, 128]
        colours['navy blue']                = [  0,   0, 128]
        colours['navy blue']                = [  0,   0, 128]
        colours['cornflower blue']          = [100, 149, 237]
        colours['cornflower blue']          = [100, 149, 237]
        colours['dark slate blue']          = [ 72,  61, 139]
        colours['dark slate blue']          = [ 72,  61, 139]
        colours['slate blue']               = [106,  90, 205]
        colours['slate blue']               = [106,  90, 205]
        colours['medium slate blue']        = [123, 104, 238]
        colours['medium slate blue']        = [123, 104, 238]
        colours['light slate blue']         = [132, 112, 255]
        colours['light slate blue']         = [132, 112, 255]
        colours['medium blue']              = [  0,   0, 205]
        colours['medium blue']              = [  0,   0, 205]
        colours['royal blue']               = [ 65, 105, 225]
        colours['royal blue']               = [ 65, 105, 225]
        colours['blue']                     = [  0,   0, 255]
        colours['dodger blue']              = [ 30, 144, 255]
        colours['dodger blue']              = [ 30, 144, 255]
        colours['deep sky blue']            = [  0, 191, 255]
        colours['deep sky blue']            = [  0, 191, 255]
        colours['sky blue']                 = [135, 206, 235]
        colours['sky blue']                 = [135, 206, 235]
        colours['light sky blue']           = [135, 206, 250]
        colours['light sky blue']           = [135, 206, 250]
        colours['steel blue']               = [ 70, 130, 180]
        colours['steel blue']               = [ 70, 130, 180]
        colours['light steel blue']         = [176, 196, 222]
        colours['light steel blue']         = [176, 196, 222]
        colours['light blue']               = [173, 216, 230]
        colours['light blue']               = [173, 216, 230]
        colours['powder blue']              = [176, 224, 230]
        colours['powder blue']              = [176, 224, 230]
        colours['pale turquoise']           = [175, 238, 238]
        colours['dark turquoise']           = [  0, 206, 209]
        colours['dark turquoise']           = [  0, 206, 209]
        colours['medium turquoise']         = [ 72, 209, 204]
        colours['medium turquoise']         = [ 72, 209, 204]
        colours['turquoise']                = [ 64, 224, 208]
        colours['cyan']                     = [  0, 255, 255]
        colours['light cyan']               = [224, 255, 255]
        colours['cadet blue']               = [ 95, 158, 160]
        colours['cadet blue']               = [ 95, 158, 160]
        colours['medium aquamarine']        = [102, 205, 170]
        colours['medium aquamarine']        = [102, 205, 170]
        colours['aquamarine']               = [127, 255, 212]
        colours['dark green']               = [  0, 100,   0]
        colours['dark green']               = [  0, 100,   0]
        colours['dark olive green']         = [ 85, 107,  47]
        colours['dark olive green']         = [ 85, 107,  47]
        colours['dark sea green']           = [143, 188, 143]
        colours['dark sea green']           = [143, 188, 143]
        colours['sea green']                = [ 46, 139,  87]
        colours['sea green']                = [ 46, 139,  87]
        colours['medium sea green']         = [ 60, 179, 113]
        colours['medium sea green']         = [ 60, 179, 113]
        colours['light sea green']          = [ 32, 178, 170]
        colours['light sea green']          = [ 32, 178, 170]
        colours['pale green']               = [152, 251, 152]
        colours['pale green']               = [152, 251, 152]
        colours['spring green']             = [  0, 255, 127]
        colours['spring green']             = [  0, 255, 127]
        colours['lawn green']               = [124, 252,   0]
        colours['lawn green']               = [124, 252,   0]
        colours['green']                    = [  0, 255,   0]
        colours['chartreuse']               = [127, 255,   0]
        colours['medium spring green']      = [  0, 250, 154]
        colours['medium spring green']      = [  0, 250, 154]
        colours['green yellow']             = [173, 255,  47]
        colours['green yellow']             = [173, 255,  47]
        colours['lime green']               = [ 50, 205,  50]
        colours['lime green']               = [ 50, 205,  50]
        colours['yellow green']             = [154, 205,  50]
        colours['yellow green']             = [154, 205,  50]
        colours['forest green']             = [ 34, 139,  34]
        colours['forest green']             = [ 34, 139,  34]
        colours['olive drab']               = [107, 142,  35]
        colours['olive drab']               = [107, 142,  35]
        colours['dark khaki']               = [189, 183, 107]
        colours['dark khaki']               = [189, 183, 107]
        colours['khaki']                    = [240, 230, 140]
        colours['pale goldenrod']           = [238, 232, 170]
        colours['pale goldenrod']           = [238, 232, 170]
        colours['light goldenrod yellow']   = [250, 250, 210]
        colours['light goldenrod yellow']   = [250, 250, 210]
        colours['light yellow']             = [255, 255, 224]
        colours['light yellow']             = [255, 255, 224]
        colours['yellow']                   = [255, 255,   0]
        colours['gold']                     = [255, 215,   0]
        colours['light goldenrod']          = [238, 221, 130]
        colours['light goldenrod']          = [238, 221, 130]
        colours['goldenrod']                = [218, 165,  32]
        colours['dark goldenrod']           = [184, 134,  11]
        colours['dark goldenrod']           = [184, 134,  11]
        colours['rosy brown']               = [188, 143, 143]
        colours['indian red']               = [205,  92,  92]
        colours['saddle brown']             = [139,  69,  19]
        colours['saddle brown']             = [139,  69,  19]
        colours['sienna']                   = [160,  82,  45]
        colours['peru']                     = [205, 133,  63]
        colours['burlywood']                = [222, 184, 135]
        colours['beige']                    = [245, 245, 220]
        colours['wheat']                    = [245, 222, 179]
        colours['sandy brown']              = [244, 164,  96]
        colours['sandy brown']              = [244, 164,  96]
        colours['tan']                      = [210, 180, 140]
        colours['chocolate']                = [210, 105,  30]
        colours['firebrick']                = [178,  34,  34]
        colours['brown']                    = [165,  42,  42]
        colours['dark salmon']              = [233, 150, 122]
        colours['dark salmon']              = [233, 150, 122]
        colours['salmon']                   = [250, 128, 114]
        colours['light salmon']             = [255, 160, 122]
        colours['light salmon']             = [255, 160, 122]
        colours['orange']                   = [255, 165,   0]
        colours['dark orange']              = [255, 140,   0]
        colours['dark orange']              = [255, 140,   0]
        colours['coral']                    = [255, 127,  80]
        colours['light coral']              = [240, 128, 128]
        colours['tomato']                   = [255,  99,  71]
        colours['orange red']               = [255,  69,   0]
        colours['orange red']               = [255,  69,   0]
        colours['red']                      = [255,   0,   0]
        colours['hot pink']                 = [255, 105, 180]
        colours['hot pink']                 = [255, 105, 180]
        colours['deep pink']                = [255,  20, 147]
        colours['deep pink']                = [255,  20, 147]
        colours['pink']                     = [255, 192, 203]
        colours['light pink']               = [255, 182, 193]
        colours['light pink']               = [255, 182, 193]
        colours['pale violet red']          = [219, 112, 147]
        colours['pale violet red']          = [219, 112, 147]
        colours['maroon']                   = [176,  48,  96]
        colours['medium violet red']        = [199,  21, 133]
        colours['medium violet red']        = [199,  21, 133]
        colours['violet red']               = [208,  32, 144]
        colours['violet red']               = [208,  32, 144]
        colours['magenta']                  = [255,   0, 255]
        colours['violet']                   = [238, 130, 238]
        colours['plum']                     = [221, 160, 221]
        colours['orchid']                   = [218, 112, 214]
        colours['medium orchid']            = [186,  85, 211]
        colours['medium orchid']            = [186,  85, 211]
        colours['dark orchid']              = [153,  50, 204]
        colours['dark orchid']              = [153,  50, 204]
        colours['dark violet']              = [148,   0, 211]
        colours['dark violet']              = [148,   0, 211]
        colours['blue violet']              = [138,  43, 226]
        colours['blue violet']              = [138,  43, 226]
        colours['purple']                   = [160,  32, 240]
        colours['medium purple']            = [147, 112, 219]
        colours['medium purple']            = [147, 112, 219]
        colours['thistle']                  = [216, 191, 216]
        colours['snow 1']                   = [255, 250, 250]
        colours['snow 2']                   = [238, 233, 233]
        colours['snow 3']                   = [205, 201, 201]
        colours['snow 4']                   = [139, 137, 137]
        colours['seashell 1']               = [255, 245, 238]
        colours['seashell 2']               = [238, 229, 222]
        colours['seashell 3']               = [205, 197, 191]
        colours['seashell 4']               = [139, 134, 130]
        colours['antique white 1']          = [255, 239, 219]
        colours['antique white 2']          = [238, 223, 204]
        colours['antique white 3']          = [205, 192, 176]
        colours['antique white 4']          = [139, 131, 120]
        colours['bisque 1']                 = [255, 228, 196]
        colours['bisque 2']                 = [238, 213, 183]
        colours['bisque 3']                 = [205, 183, 158]
        colours['bisque 4']                 = [139, 125, 107]
        colours['peach puff 1']             = [255, 218, 185]
        colours['peach puff 2']             = [238, 203, 173]
        colours['peach puff 3']             = [205, 175, 149]
        colours['peach puff 4']             = [139, 119, 101]
        colours['navajo white 1']           = [255, 222, 173]
        colours['navajo white 2']           = [238, 207, 161]
        colours['navajo white 3']           = [205, 179, 139]
        colours['navajo white 4']           = [139, 121,  94]
        colours['lemon chiffon 1']          = [255, 250, 205]
        colours['lemon chiffon 2']          = [238, 233, 191]
        colours['lemon chiffon 3']          = [205, 201, 165]
        colours['lemon chiffon 4']          = [139, 137, 112]
        colours['cornsilk 1']               = [255, 248, 220]
        colours['cornsilk 2']               = [238, 232, 205]
        colours['cornsilk 3']               = [205, 200, 177]
        colours['cornsilk 4']               = [139, 136, 120]
        colours['ivory 1']                  = [255, 255, 240]
        colours['ivory 2']                  = [238, 238, 224]
        colours['ivory 3']                  = [205, 205, 193]
        colours['ivory 4']                  = [139, 139, 131]
        colours['honeydew 1']               = [240, 255, 240]
        colours['honeydew 2']               = [224, 238, 224]
        colours['honeydew 3']               = [193, 205, 193]
        colours['honeydew 4']               = [131, 139, 131]
        colours['lavender blush 1']         = [255, 240, 245]
        colours['lavender blush 2']         = [238, 224, 229]
        colours['lavender blush 3']         = [205, 193, 197]
        colours['lavender blush 4']         = [139, 131, 134]
        colours['misty rose 1']             = [255, 228, 225]
        colours['misty rose 2']             = [238, 213, 210]
        colours['misty rose 3']             = [205, 183, 181]
        colours['misty rose 4']             = [139, 125, 123]
        colours['azure 1']                  = [240, 255, 255]
        colours['azure 2']                  = [224, 238, 238]
        colours['azure 3']                  = [193, 205, 205]
        colours['azure 4']                  = [131, 139, 139]
        colours['slate blue 1']             = [131, 111, 255]
        colours['slate blue 2']             = [122, 103, 238]
        colours['slate blue 3']             = [105,  89, 205]
        colours['slate blue 4']             = [ 71,  60, 139]
        colours['royal blue 1']             = [ 72, 118, 255]
        colours['royal blue 2']             = [ 67, 110, 238]
        colours['royal blue 3']             = [ 58,  95, 205]
        colours['royal blue 4']             = [ 39,  64, 139]
        colours['blue 1']                   = [  0,   0, 255]
        colours['blue 2']                   = [  0,   0, 238]
        colours['blue 3']                   = [  0,   0, 205]
        colours['blue 4']                   = [  0,   0, 139]
        colours['dodger blue 1']            = [ 30, 144, 255]
        colours['dodger blue 2']            = [ 28, 134, 238]
        colours['dodger blue 3']            = [ 24, 116, 205]
        colours['dodger blue 4']            = [ 16,  78, 139]
        colours['steel blue 1']             = [ 99, 184, 255]
        colours['steel blue 2']             = [ 92, 172, 238]
        colours['steel blue 3']             = [ 79, 148, 205]
        colours['steel blue 4']             = [ 54, 100, 139]
        colours['deep sky blue 1']          = [  0, 191, 255]
        colours['deep sky blue 2']          = [  0, 178, 238]
        colours['deep sky blue 3']          = [  0, 154, 205]
        colours['deep sky blue 4']          = [  0, 104, 139]
        colours['sky blue 1']               = [135, 206, 255]
        colours['sky blue 2']               = [126, 192, 238]
        colours['sky blue 3']               = [108, 166, 205]
        colours['sky blue 4']               = [ 74, 112, 139]
        colours['light sky blue 1']         = [176, 226, 255]
        colours['light sky blue 2']         = [164, 211, 238]
        colours['light sky blue 3']         = [141, 182, 205]
        colours['light sky blue 4']         = [ 96, 123, 139]
        colours['slate gray 1']             = [198, 226, 255]
        colours['slate gray 2']             = [185, 211, 238]
        colours['slate gray 3']             = [159, 182, 205]
        colours['slate gray 4']             = [108, 123, 139]
        colours['light steel blue 1']       = [202, 225, 255]
        colours['light steel blue 2']       = [188, 210, 238]
        colours['light steel blue 3']       = [162, 181, 205]
        colours['light steel blue 4']       = [110, 123, 139]
        colours['light blue 1']             = [191, 239, 255]
        colours['light blue 2']             = [178, 223, 238]
        colours['light blue 3']             = [154, 192, 205]
        colours['light blue 4']             = [104, 131, 139]
        colours['light cyan 1']             = [224, 255, 255]
        colours['light cyan 2']             = [209, 238, 238]
        colours['light cyan 3']             = [180, 205, 205]
        colours['light cyan 4']             = [122, 139, 139]
        colours['pale turquoise 1']         = [187, 255, 255]
        colours['pale turquoise 2']         = [174, 238, 238]
        colours['pale turquoise 3']         = [150, 205, 205]
        colours['pale turquoise 4']         = [102, 139, 139]
        colours['cadet blue 1']             = [152, 245, 255]
        colours['cadet blue 2']             = [142, 229, 238]
        colours['cadet blue 3']             = [122, 197, 205]
        colours['cadet blue 4']             = [ 83, 134, 139]
        colours['turquoise 1']              = [  0, 245, 255]
        colours['turquoise 2']              = [  0, 229, 238]
        colours['turquoise 3']              = [  0, 197, 205]
        colours['turquoise 4']              = [  0, 134, 139]
        colours['cyan 1']                   = [  0, 255, 255]
        colours['cyan 2']                   = [  0, 238, 238]
        colours['cyan 3']                   = [  0, 205, 205]
        colours['cyan 4']                   = [  0, 139, 139]
        colours['dark slate gray 1']        = [151, 255, 255]
        colours['dark slate gray 2']        = [141, 238, 238]
        colours['dark slate gray 3']        = [121, 205, 205]
        colours['dark slate gray 4']        = [ 82, 139, 139]
        colours['aquamarine 1']             = [127, 255, 212]
        colours['aquamarine 2']             = [118, 238, 198]
        colours['aquamarine 3']             = [102, 205, 170]
        colours['aquamarine 4']             = [ 69, 139, 116]
        colours['dark sea green 1']         = [193, 255, 193]
        colours['dark sea green 2']         = [180, 238, 180]
        colours['dark sea green 3']         = [155, 205, 155]
        colours['dark sea green 4']         = [105, 139, 105]
        colours['sea green 1']              = [ 84, 255, 159]
        colours['sea green 2']              = [ 78, 238, 148]
        colours['sea green 3']              = [ 67, 205, 128]
        colours['sea green 4']              = [ 46, 139,  87]
        colours['pale green 1']             = [154, 255, 154]
        colours['pale green 2']             = [144, 238, 144]
        colours['pale green 3']             = [124, 205, 124]
        colours['pale green 4']             = [ 84, 139,  84]
        colours['spring green 1']           = [  0, 255, 127]
        colours['spring green 2']           = [  0, 238, 118]
        colours['spring green 3']           = [  0, 205, 102]
        colours['spring green 4']           = [  0, 139,  69]
        colours['green 1']                  = [  0, 255,   0]
        colours['green 2']                  = [  0, 238,   0]
        colours['green 3']                  = [  0, 205,   0]
        colours['green 4']                  = [  0, 139,   0]
        colours['chartreuse 1']             = [127, 255,   0]
        colours['chartreuse 2']             = [118, 238,   0]
        colours['chartreuse 3']             = [102, 205,   0]
        colours['chartreuse 4']             = [ 69, 139,   0]
        colours['olive drab 1']             = [192, 255,  62]
        colours['olive drab 2']             = [179, 238,  58]
        colours['olive drab 3']             = [154, 205,  50]
        colours['olive drab 4']             = [105, 139,  34]
        colours['dark olive green 1']       = [202, 255, 112]
        colours['dark olive green 2']       = [188, 238, 104]
        colours['dark olive green 3']       = [162, 205,  90]
        colours['dark olive green 4']       = [110, 139,  61]
        colours['khaki 1']                  = [255, 246, 143]
        colours['khaki 2']                  = [238, 230, 133]
        colours['khaki 3']                  = [205, 198, 115]
        colours['khaki 4']                  = [139, 134,  78]
        colours['light goldenrod 1']        = [255, 236, 139]
        colours['light goldenrod 2']        = [238, 220, 130]
        colours['light goldenrod 3']        = [205, 190, 112]
        colours['light goldenrod 4']        = [139, 129,  76]
        colours['light yellow 1']           = [255, 255, 224]
        colours['light yellow 2']           = [238, 238, 209]
        colours['light yellow 3']           = [205, 205, 180]
        colours['light yellow 4']           = [139, 139, 122]
        colours['yellow 1']                 = [255, 255,   0]
        colours['yellow 2']                 = [238, 238,   0]
        colours['yellow 3']                 = [205, 205,   0]
        colours['yellow 4']                 = [139, 139,   0]
        colours['gold 1']                   = [255, 215,   0]
        colours['gold 2']                   = [238, 201,   0]
        colours['gold 3']                   = [205, 173,   0]
        colours['gold 4']                   = [139, 117,   0]
        colours['goldenrod 1']              = [255, 193,  37]
        colours['goldenrod 2']              = [238, 180,  34]
        colours['goldenrod 3']              = [205, 155,  29]
        colours['goldenrod 4']              = [139, 105,  20]
        colours['dark goldenrod 1']         = [255, 185,  15]
        colours['dark goldenrod 2']         = [238, 173,  14]
        colours['dark goldenrod 3']         = [205, 149,  12]
        colours['dark goldenrod 4']         = [139, 101,   8]
        colours['rosy brown 1']             = [255, 193, 193]
        colours['rosy brown 2']             = [238, 180, 180]
        colours['rosy brown 3']             = [205, 155, 155]
        colours['rosy brown 4']             = [139, 105, 105]
        colours['indian red 1']             = [255, 106, 106]
        colours['indian red 2']             = [238,  99,  99]
        colours['indian red 3']             = [205,  85,  85]
        colours['indian red 4']             = [139,  58,  58]
        colours['sienna 1']                 = [255, 130,  71]
        colours['sienna 2']                 = [238, 121,  66]
        colours['sienna 3']                 = [205, 104,  57]
        colours['sienna 4']                 = [139,  71,  38]
        colours['burlywood 1']              = [255, 211, 155]
        colours['burlywood 2']              = [238, 197, 145]
        colours['burlywood 3']              = [205, 170, 125]
        colours['burlywood 4']              = [139, 115,  85]
        colours['wheat 1']                  = [255, 231, 186]
        colours['wheat 2']                  = [238, 216, 174]
        colours['wheat 3']                  = [205, 186, 150]
        colours['wheat 4']                  = [139, 126, 102]
        colours['tan 1']                    = [255, 165,  79]
        colours['tan 2']                    = [238, 154,  73]
        colours['tan 3']                    = [205, 133,  63]
        colours['tan 4']                    = [139,  90,  43]
        colours['chocolate 1']              = [255, 127,  36]
        colours['chocolate 2']              = [238, 118,  33]
        colours['chocolate 3']              = [205, 102,  29]
        colours['chocolate 4']              = [139,  69,  19]
        colours['firebrick 1']              = [255,  48,  48]
        colours['firebrick 2']              = [238,  44,  44]
        colours['firebrick 3']              = [205,  38,  38]
        colours['firebrick 4']              = [139,  26,  26]
        colours['brown 1']                  = [255,  64,  64]
        colours['brown 2']                  = [238,  59,  59]
        colours['brown 3']                  = [205,  51,  51]
        colours['brown 4']                  = [139,  35,  35]
        colours['salmon 1']                 = [255, 140, 105]
        colours['salmon 2']                 = [238, 130,  98]
        colours['salmon 3']                 = [205, 112,  84]
        colours['salmon 4']                 = [139,  76,  57]
        colours['light salmon 1']           = [255, 160, 122]
        colours['light salmon 2']           = [238, 149, 114]
        colours['light salmon 3']           = [205, 129,  98]
        colours['light salmon 4']           = [139,  87,  66]
        colours['orange 1']                 = [255, 165,   0]
        colours['orange 2']                 = [238, 154,   0]
        colours['orange 3']                 = [205, 133,   0]
        colours['orange 4']                 = [139,  90,   0]
        colours['dark orange 1']            = [255, 127,   0]
        colours['dark orange 2']            = [238, 118,   0]
        colours['dark orange 3']            = [205, 102,   0]
        colours['dark orange 4']            = [139,  69,   0]
        colours['coral 1']                  = [255, 114,  86]
        colours['coral 2']                  = [238, 106,  80]
        colours['coral 3']                  = [205,  91,  69]
        colours['coral 4']                  = [139,  62,  47]
        colours['tomato 1']                 = [255,  99,  71]
        colours['tomato 2']                 = [238,  92,  66]
        colours['tomato 3']                 = [205,  79,  57]
        colours['tomato 4']                 = [139,  54,  38]
        colours['orange red 1']             = [255,  69,   0]
        colours['orange red 2']             = [238,  64,   0]
        colours['orange red 3']             = [205,  55,   0]
        colours['orange red 4']             = [139,  37,   0]
        colours['red 1']                    = [255,   0,   0]
        colours['red 2']                    = [238,   0,   0]
        colours['red 3']                    = [205,   0,   0]
        colours['red 4']                    = [139,   0,   0]
        colours['deep pink 1']              = [255,  20, 147]
        colours['deep pink 2']              = [238,  18, 137]
        colours['deep pink 3']              = [205,  16, 118]
        colours['deep pink 4']              = [139,  10,  80]
        colours['hot pink 1']               = [255, 110, 180]
        colours['hot pink 2']               = [238, 106, 167]
        colours['hot pink 3']               = [205,  96, 144]
        colours['hot pink 4']               = [139,  58,  98]
        colours['pink 1']                   = [255, 181, 197]
        colours['pink 2']                   = [238, 169, 184]
        colours['pink 3']                   = [205, 145, 158]
        colours['pink 4']                   = [139,  99, 108]
        colours['light pink 1']             = [255, 174, 185]
        colours['light pink 2']             = [238, 162, 173]
        colours['light pink 3']             = [205, 140, 149]
        colours['light pink 4']             = [139,  95, 101]
        colours['pale violet red 1']        = [255, 130, 171]
        colours['pale violet red 2']        = [238, 121, 159]
        colours['pale violet red 3']        = [205, 104, 137]
        colours['pale violet red 4']        = [139,  71,  93]
        colours['maroon 1']                 = [255,  52, 179]
        colours['maroon 2']                 = [238,  48, 167]
        colours['maroon 3']                 = [205,  41, 144]
        colours['maroon 4']                 = [139,  28,  98]
        colours['violet red 1']             = [255,  62, 150]
        colours['violet red 2']             = [238,  58, 140]
        colours['violet red 3']             = [205,  50, 120]
        colours['violet red 4']             = [139,  34,  82]
        colours['magenta 1']                = [255,   0, 255]
        colours['magenta 2']                = [238,   0, 238]
        colours['magenta 3']                = [205,   0, 205]
        colours['magenta 4']                = [139,   0, 139]
        colours['orchid 1']                 = [255, 131, 250]
        colours['orchid 2']                 = [238, 122, 233]
        colours['orchid 3']                 = [205, 105, 201]
        colours['orchid 4']                 = [139,  71, 137]
        colours['plum 1']                   = [255, 187, 255]
        colours['plum 2']                   = [238, 174, 238]
        colours['plum 3']                   = [205, 150, 205]
        colours['plum 4']                   = [139, 102, 139]
        colours['medium orchid 1']          = [224, 102, 255]
        colours['medium orchid 2']          = [209,  95, 238]
        colours['medium orchid 3']          = [180,  82, 205]
        colours['medium orchid 4']          = [122,  55, 139]
        colours['dark orchid 1']            = [191,  62, 255]
        colours['dark orchid 2']            = [178,  58, 238]
        colours['dark orchid 3']            = [154,  50, 205]
        colours['dark orchid 4']            = [104,  34, 139]
        colours['purple 1']                 = [155,  48, 255]
        colours['purple 2']                 = [145,  44, 238]
        colours['purple 3']                 = [125,  38, 205]
        colours['purple 4']                 = [ 85,  26, 139]
        colours['medium purple 1']          = [171, 130, 255]
        colours['medium purple 2']          = [159, 121, 238]
        colours['medium purple 3']          = [137, 104, 205]
        colours['medium purple 4']          = [ 93,  71, 139]
        colours['thistle 1']                = [255, 225, 255]
        colours['thistle 2']                = [238, 210, 238]
        colours['thistle 3']                = [205, 181, 205]
        colours['thistle 4']                = [139, 123, 139]
        colours['gray 0']                   = [  0,   0,   0]
        colours['gray 1']                   = [  3,   3,   3]
        colours['gray 2']                   = [  5,   5,   5]
        colours['gray 3']                   = [  8,   8,   8]
        colours['gray 4']                   = [ 10,  10,  10]
        colours['gray 5']                   = [ 13,  13,  13]
        colours['gray 6']                   = [ 15,  15,  15]
        colours['gray 7']                   = [ 18,  18,  18]
        colours['gray 8']                   = [ 20,  20,  20]
        colours['gray 9']                   = [ 23,  23,  23]
        colours['gray 10']                  = [ 26,  26,  26]
        colours['gray 11']                  = [ 28,  28,  28]
        colours['gray 12']                  = [ 31,  31,  31]
        colours['gray 13']                  = [ 33,  33,  33]
        colours['gray 14']                  = [ 36,  36,  36]
        colours['gray 15']                  = [ 38,  38,  38]
        colours['gray 16']                  = [ 41,  41,  41]
        colours['gray 17']                  = [ 43,  43,  43]
        colours['gray 18']                  = [ 46,  46,  46]
        colours['gray 19']                  = [ 48,  48,  48]
        colours['gray 20']                  = [ 51,  51,  51]
        colours['gray 21']                  = [ 54,  54,  54]
        colours['gray 22']                  = [ 56,  56,  56]
        colours['gray 23']                  = [ 59,  59,  59]
        colours['gray 24']                  = [ 61,  61,  61]
        colours['gray 25']                  = [ 64,  64,  64]
        colours['gray 26']                  = [ 66,  66,  66]
        colours['gray 27']                  = [ 69,  69,  69]
        colours['gray 28']                  = [ 71,  71,  71]
        colours['gray 29']                  = [ 74,  74,  74]
        colours['gray 30']                  = [ 77,  77,  77]
        colours['gray 31']                  = [ 79,  79,  79]
        colours['gray 32']                  = [ 82,  82,  82]
        colours['gray 33']                  = [ 84,  84,  84]
        colours['gray 34']                  = [ 87,  87,  87]
        colours['gray 35']                  = [ 89,  89,  89]
        colours['gray 36']                  = [ 92,  92,  92]
        colours['gray 37']                  = [ 94,  94,  94]
        colours['gray 38']                  = [ 97,  97,  97]
        colours['gray 39']                  = [ 99,  99,  99]
        colours['gray 40']                  = [102, 102, 102]
        colours['gray 41']                  = [105, 105, 105]
        colours['gray 42']                  = [107, 107, 107]
        colours['gray 43']                  = [110, 110, 110]
        colours['gray 44']                  = [112, 112, 112]
        colours['gray 45']                  = [115, 115, 115]
        colours['gray 46']                  = [117, 117, 117]
        colours['gray 47']                  = [120, 120, 120]
        colours['gray 48']                  = [122, 122, 122]
        colours['gray 49']                  = [125, 125, 125]
        colours['gray 50']                  = [127, 127, 127]
        colours['gray 51']                  = [130, 130, 130]
        colours['gray 52']                  = [133, 133, 133]
        colours['gray 53']                  = [135, 135, 135]
        colours['gray 54']                  = [138, 138, 138]
        colours['gray 55']                  = [140, 140, 140]
        colours['gray 56']                  = [143, 143, 143]
        colours['gray 57']                  = [145, 145, 145]
        colours['gray 58']                  = [148, 148, 148]
        colours['gray 59']                  = [150, 150, 150]
        colours['gray 60']                  = [153, 153, 153]
        colours['gray 61']                  = [156, 156, 156]
        colours['gray 62']                  = [158, 158, 158]
        colours['gray 63']                  = [161, 161, 161]
        colours['gray 64']                  = [163, 163, 163]
        colours['gray 65']                  = [166, 166, 166]
        colours['gray 66']                  = [168, 168, 168]
        colours['gray 67']                  = [171, 171, 171]
        colours['gray 68']                  = [173, 173, 173]
        colours['gray 69']                  = [176, 176, 176]
        colours['gray 70']                  = [179, 179, 179]
        colours['gray 71']                  = [181, 181, 181]
        colours['gray 72']                  = [184, 184, 184]
        colours['gray 73']                  = [186, 186, 186]
        colours['gray 74']                  = [189, 189, 189]
        colours['gray 75']                  = [191, 191, 191]
        colours['gray 76']                  = [194, 194, 194]
        colours['gray 77']                  = [196, 196, 196]
        colours['gray 78']                  = [199, 199, 199]
        colours['gray 79']                  = [201, 201, 201]
        colours['gray 80']                  = [204, 204, 204]
        colours['gray 81']                  = [207, 207, 207]
        colours['gray 82']                  = [209, 209, 209]
        colours['gray 83']                  = [212, 212, 212]
        colours['gray 84']                  = [214, 214, 214]
        colours['gray 85']                  = [217, 217, 217]
        colours['gray 86']                  = [219, 219, 219]
        colours['gray 87']                  = [222, 222, 222]
        colours['gray 88']                  = [224, 224, 224]
        colours['gray 89']                  = [227, 227, 227]
        colours['gray 90']                  = [229, 229, 229]
        colours['gray 91']                  = [232, 232, 232]
        colours['gray 92']                  = [235, 235, 235]
        colours['gray 93']                  = [237, 237, 237]
        colours['gray 94']                  = [240, 240, 240]
        colours['gray 95']                  = [242, 242, 242]
        colours['gray 96']                  = [245, 245, 245]
        colours['gray 97']                  = [247, 247, 247]
        colours['gray 98']                  = [250, 250, 250]
        colours['gray 99']                  = [252, 252, 252]
        colours['gray 100']                 = [255, 255, 255]
        colours['dark grey']                = [169, 169, 169]
        colours['dark blue']                = [  0,   0, 139]
        colours['dark blue']                = [  0,   0, 139]
        colours['dark cyan']                = [  0, 139, 139]
        colours['dark magenta']             = [139,   0, 139]
        colours['dark magenta']             = [139,   0, 139]
        colours['dark red']                 = [139,   0,   0]
        colours['light green']              = [144, 238, 144]
        colours['light green']              = [144, 238, 144]

        # Invalid colour string.
        if not colours.has_key(name):
            raise RelaxInvalidColourError, name

        # Return the RGB colour array (in Numeric format and between 0 and 1).
        return array(colours[name], Float64) / 255.
