#!/usr/bin/python3

####################################
# MIT License
#
# Copyright (c) 2018 Jason Pawlak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

####################################
# Name: RaiBlocks Indicator
# Author: Jason Pawlak
# Donations: xrb_1hi54n577fag69bgts53fwiq9ns45rrkgomyhk3smxti1sdgsscwrag1rnk1
# Description: This is an indicator for Unity menu bar that displays
#  information about RaiBlocks
# Refs:
#  API: https://lazka.github.io/pgi-docs/AppIndicator3-0.1/classes/Indicator.html
#

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GLib as glib
import signal
import os
import json
import urllib.request
import base64
import tempfile
import datetime
import webbrowser

currency_mark = {
    'price_usd': '$',
    'price_btc': '฿',
}

class RaiBlocks_Indicator():

    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.appindicator_id = 'raiblocks_indicator'
        self.icon = b'iVBORw0KGgoAAAANSUhEUgAAAN0AAAEACAYAAAA3E3NfAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4gEXBCk26wP0EQAAIABJREFUeNrtnXmcXGWZqJ/vnKqu6qpOd6c7nZ0trJJKARGHC8xV0DtCBXFBQNzBQXSgitHRcRlFkfI69+fckd8IboWCMwgOCnMZgZyAVxZxkAtSgYDshOyVpDu9VNWp9Zzz3T+qOwQIJJ3u6q7lff7pRjvV1d/5nvre91veD4SmIZJMTXy95JzbH9+WWFv8DEA8vUkap4kwpAmaQbbrJr49NZJMZYCfaK0XafSP42l7I/SfXJPPlsYS6YTpGNlAL4okU3cCfwAWvubHDgYeiqftO4H5AJelc9J4Ip0wKdm+/ZOJb1UkmfoKsA04ax//7CxgRzxtf11h+qQVRTphEjz19c8QSab+CvCAf5zkP0+CrsbT9hkScop0wpuwPPmTiZDy8EgytRm4Z4ovuSaetreMh5/E0wVpZJFO2DNvU6iuSDJ1M/AisHSaXn4JsDGetm8D3QWQSOel0UW69iT6yoykEUmmPgXkgA/X6dedA+TiafuzGmVK64t0bYmDRySZigIu8LMZ+rU/Apx42j5m4n+45E9ZeRgiXeuy4pW8LWygXgCemKW38kw8bW+7LG13pE7slgcj0rVi3lYLJZ+84jNEkqmbgDxwxCy/rUUKyvG0fVM8bSuQmc6ZQkkT1JflyZ/y5ysuJpJMXQjcMF2ve2TkbSw59GjQejpezgM+fu3K8M3xtM21K8Py4GSka+ZPNe+ISDI1Mp3C1akf3BRP2yXGZ04vSxfl4Yl0TTS6ffu6idxtHfAC0Nskbz0AbI6n7ScVnkRBIl3z5G5K6+sjyZQLrGjWPwWoxNP2D2ujnuR6Il2D8db/NbFXUn84kkyNAhe1QNv6gL+Jp+2sgvMA4rKwLtLN/shW201SrqolkWTqeeBmoKfF/sw5wK/iafslUIcCJF7Q8vCnlOcLUxVvDXDGTP/eaZ69nAx3Xbsy/B558jLSzYZsyUgypWdDuFnmrHjaduJp+6payCn5nkhX51AykkytiiRT24Cvt3FzmMAV8bS9E3iP5HsiXV1kAxZFkqkHgbuARdIyAAwAd8TT9oOgDpHmEOmmB+0ZkWTqWmqnt/9SGmSv/CWwIZ62r5GmEOkOiGjypxOj3KdQhgtcJq2yX8TjaVvH0/ZF0hQi3X6GkrXFbQ/vbZFkahMzd+Sm1bg+nrYz8bR9EsDfp4ekRUS6V7P82z+eiCXnj1fdegQ4SFpmSiwEHo6n7duLdM4HmekU6fZAacMXSaa+Cuxg31W3hMnxPmpVyr4ApgFwWZvXa2lb6fZYAjgNqALfET/qyv8G142n7dN/sDIk0rWjbNSWALYB94kPM8q98bS9IZ62DwFIPGaLdC2bt135g4lvw5Fk6tfUlgBkvW12OITaEsPNWhEESLRRvtfy0u0ucWf6zUgydTG1UgnnSr9vCD4MFONp+2KvjQaAttjwHEmmDqdWT7JlmMUNz/XCA44Hnmz1chFGi8sWGK+W/CJCM/TFdcCL8bTdAa27xNBy0kWu2j0r+a/A7pofQtNwOLUqZb+8dmW4JTdSt4x0u2clFReMl0r4hPTfpuaCeNp2QF0I8Lm1RZGuUTjqyt3XSh0SSaZywC+RRf9WwQRuiKftIUd7h4h0DUKHqYxIMvUnYAPQJf20JemntsTwBMAVmzNceJ8W6WYjlIwkUz8AysBbpV+2BdF42nZHBrtTPz9diXQzItsrN5SeH0mmxoBLqVWtEtoHA/h0PG0Px9P2+dB8s5zNNdJpdVgkmXoGuAWQmy/am7nALfG0/QzjO4uaRb6mkS6STP0fYD1wjPQ3YQ+OAbbF0/Z/NsuiutHAkk18/UYkmfKA90v/Et6E98bTthdP21fURr1RkW5/Wf7KKYBYJJnaAXwLqc8p7B8KuCqetreC/4xGDTkbRrpX7t7moEgydR+wGpgv/Ug4ABYDa+Jp+wFq96431MHZWZdu+VW1uiRPXXEJkWTqe8Am4DTpN8I08HZgSzxtX63QDXPXekOEbZFk6mPAjdJH9p8WPGUwE3zi2pXhGxNr81xzwuzto5iVkW7FK5MkJ46fAhDhhJng3+Jpe4vW6vjZzPdmVLqJvE1DfySZug14FDkFIMwsS4C18bT9G2oVqrn0kXzrSXfEld8HwFPajCRTnwOGgHPk+QuzyNnAznja/qLhU76Wk+7FKy8nkky93dDKAa6W5y00EP8EVONp+2SAD/9xsHml22Nxe1EkmVoPPCDPV2hgHoqn7e3zAqEFTSfdilcWt/2RZOrfqVXdOkyeqdAELNCwPZ62b4mn7RDUZ7Jl2qXzQEWSqb8GKsCH5DkKTcj5gB1P2x+fcCQ+jYvr07ZONx5OHgM8AXTIc6svsk43oxx+7crw+ul6sSnP2iz/9nUoHVJgvwgsk+cjtCAvxdP2y8Cx164Ml2YtvNy9V1LrX4LtiXBCi3MYUIin7RsA4o/lZ1464JORZKoEXCDPQ2gTFHBhPG07KPXhWq5n10+65a8sASyNJFM7gZ8DAXkOQhtiAjfH0/auA4nwJjWREkmm0sAJ0uazj0ykNBQPX7syfPK0jnSRZOqa8QKuIpwgvJ7/Fk/bTjxtX7M/IafxBpJNfD0nkkwNAXGkgKsg7CvkjMfT9ii1dT4SjxX2Ld3yq3bvJlkcSaaeAm6jVuhTEIT9o4dalbJ1WunD9indn3cdyfiFiVuB5dJ+gnDArADWx9P2r18n3YrkjydCyS9H5r3gIhcmCsJ0cm48bet42v6HiXxPHfuN1DsNPzdSK+YiNAkye9mU7AiaxoVG79H6d4aPAeTZCULdUEDJ1XPvy+QsX8cc6F+hfXZGlQrb8VObhREEYfrw/jxaqjw3Wgr6DFXb8Kw9VGiBDoYW4GU3qHJ5hA5lSIFXQZgKhoLNdrXy6KBtmkoFfUZNqdeeMjC6D9MBbynlsReV6ZbwiXqCMHnZRipu9f/tKLglzwua6tUSvf5ojwbDR6DvLZrSCHZ+iwpqV0JOQdifvK3iaXftrmI5U6iGDIV/b2PWG56n0xoCvYSDfZrcJlUo7SKI7EoRhL37AvqlbKX0xHCh02+okPEmEeI+D7FqD7qW6tCcg/BGnlVVp4hfQk5BeEWR4bJbfXB73jAUnX5j33Ls98lxrTF6j9aGdiiOPKcCniOjntDeoWTZ0+79mZxTdnXAmMRANOlyDcpHZ19EU9pFwd6iOrWWcU9ou1CSRwdtO1NwwkpNfr7Dd6C/NdhHqLNfk31Z2eUxwvIohHZgY75SeHxXsdNQhNUBDjdTKkykNcw5VIfngDP8jPK8ilQBE1oT2/FK92dyHZ4mZEwxtpuuGu6+vrdo3DKlkeeUHy1LDEKr5G7K/e3WrFt0veB0vea0XpxgBgjOi2rKw6qQ3UhIyVSL0KQYCh4ZLNiZQjXMNG+NrMttJYE+HRqYC9mNyq6MEpapFqF5RjbYZFfz64YLYU/XZ67CV893332oDnsOzujzyvGqBOWRCo0sW9HVpQcyuUDZ0131HCfqfi+X4cPXd6w2qzaV0eeVoQx88oiFBgslvfszeWe07AaUQtU7MJspAZQ/TMfACdorDlLKb1ZBJVMtwixjKnh8uFjckKsEgA41Q2nQTI86RucAwWCfdnKbqJTHVEhJvifMuGyKzXal8ORwMVD2dOdMd8FZCfWUia97GT7H1tXsy8r1HMn3hJnJ2wquV3l4p62yFS9kKGZljm/28isNvhD+/oj2l4apZDcoUxmyvifUDfdPQwVns13tMBXKmMUIa9YnNbSGwFw65s/Vbn4r5cJOFZD1PWHaOrhS+rmxUvnp0ZIfCJgNkM40zEyiBjO8FLNzvi7nNqKqedUh63tv8JGtNX6l8LQccHyzvG1HsVp5bKigyp4ONlJXaqzpew2Gn0DvUVAe1aX8ZmV6VTm/t0fz4DcUHzlqKRe9dS5P4nLXkIGjkSZ6dd7mrB0qVneWqp2mUg3XNg25ZqY96Ogm2B/V2FspFXaoDtr8Q73qebxj6TwujhxC1fMouZq/mOtxSo/HrTtNHhlTGG1ungb3mdFS9bmxUsBUymc26NR4Qy9UaxdCCwmGFmknu145lTH8qPb6UHc8zZFzw3xu5eF0mgZVz3v1/6/hAwMuf9UHN2432VBU+NpMPkMpvdWuVB8ZLPgMRdBs8HWo5tgdovF1L9O4ZcrZ9cpwS60fcnoa+oJ+LoocxPK+blyt37AesAbCJsSXujxfUPxqh0nWoeVHPqUgV/HcP+zIVyueDjbL39s8W7I0mB0E+o7VlIYp5DeroPZaM+Q0leKsw+Zz7lGLqbge7n6WTnc0LOvUfHOZw5pdBg+M1PK9Vszbyp52H99VKGcKTshQmM30+dJ0+yC1B4FeQsF+rXMbKZaGVZAWKRmhgWP65vAPbzuSkutScb0Dep2yB6fP9XhXn8f120xeKLROTK5Bb8hVio8PF0KmUqFmHM2bdvOxdlFdS+nsWqrd0eeV4xTpoEkn8TTQH+zgipOOIuQ3KbnutIWoFy1yKXrwL5t9ZJ3mnuUcq7qVe7fmTJ+hQmYT7x9shR3/Zu9R2nQrlEeeUz685tnVooEOw+Az0UM4bqAHrw438GggaMBXD3F4saj4t4zZdCFnpVZ1q1p29e7S5M1MyxyzMTsIzItqyiPkcxtVVzO85/9x8AAfPWYJVU/XRbhXjXrU8r2rljmsHjb4rxGj4S9q0qDTQ4Xi1kI1pFroYpvWOttWq0rdFejVOr9J2aURGlK+Q7pDfO2kI9Eaqt7Mdn0POLPP48w+j2s3+9heacxHudmu2OmhYthQhFptErZVD5SqroN1V/gg9PDTqqwb5BRDwDT41slHMzfY0RB3OcYPcrA9+O4GH26DDHu245Xuy+T8WhNu1SWPlj7FrRSqf7kOuhUqI08rH2p2lhgqrsfnVx5OdKC74doobMCVyxyesxU3bjdnbaJFg3PftpxrO17LH/Nqi9IJZgcd847XurQLO79ZzVihJMfTnHHoAOceuRijgWfbFHBMeDzfGzJ5aGzmFr58huLRnba9pVZ1qy36YzvVK1HBfsKBuVrnNqpCZax+Vcq0hoO7O/ncymXM8fua5mZpU8F7B1ze3Q8/2VrL9+oVGhgKNuYr9rrhYqheVbdEukYxz0B1L9Nhr1q7hUi7BKb7d3zz5KNZOieI1jTdVe4aCBjwuYMdMmXFD7eY05rvKSBf9UoP7cz7iq4Ot+Me7faszFW7+NLoX6E7qjnKYy8q/1TzvaLjctnxyzhpYe/u0a6Z8TQs6NBcucwhnTO4ZYdBxxQNMZVyHtie08NlN6ho3+NI7V0OT6P8XQTmHae94k6K+W2qc7Kn1que5vSD+jnvyCV0+gxabaujAk6c4xEJe9y1y+ThUUXHJNvIZyge31UsvpwrB6DtTyBJDcrxnmV0LqQz0K/d3CZVqYyxT/k8rVkUDnLpcYexpCv4pqcAWiAwIGDAefNd3tGruHm7wbbyvidbDAVb7WrxieGirzILVbdEuuYIOc3eI3RnNU8lu0HhVXhdyQg93pkSxy/jxAW9kzoF0Oy4Gvr9ms8f7PJkXvHvO/ae7ymg6HilR4YK5kjZ7ZytqlsiXbO454EvREf/cq2LuyjnNykTVWunqudxzpGLed+yhbhaH/ApgGbH0fCW8SWGe0cMVg8ZBMYjA6Vw04MFZ6NdCZpKTrOLdJORT6OCfQSCfdrLbaF8pO4OXLTiYOZ0+NpmZNufsPOdcz1O6dHcNmhwZ6ZSfnK46DOUCphSRfiNw25pgn23UXCJF7h61am6pzOotSfCvTqWVGi3qk81R/TaXaWAoaRgvox00/SJjlJqoL8Pu1TSuVwOPN3WH+WqFm7rXL6AdqoKrRDfRLo6hJyaUCCgwsEgo9mcLhaLtOMcgQZyhZIuF4uqtr1NQkmRbgbk65nTpXrmdOldI6O6Wqko1SY5TLFS1fmcTa00ucgm0s1ClNU/t5eK63hjo1nluW5L9kIFlB1PZ3M5DK2VKa6JdLNNh+kz5s/rJ1soeoV83qCFZjc9rRnNFTycqiGzbiJdw4WcczqDRk+ok8HRUc8pV5q6j2ogXyx7lULBUEqudBHpGnxk6O/pMTTowV3D6CYMOUtV17NzOUOBoSRvE+maKA9S8/v7KDuOHh0ZBd34SwyehuGRrDbwZCOJSNe8BHw+tWBgHrlC0bPz+YbtzENZ2zNqeZv4JtK1BnNCnUZ3OMTgyKjnVhon38sWK55TLBiG7E4S6VoRrTXzensMV2uGdg1rPG/WRpWK6+ncWFYpkU2kawdMpVgwr1+VHUcP7xqe8dmKodGsNjxPpkhEuvbM9xYtmE+uUNR2LlffXS1KMZK1PV2tSN4m0glzQp0q3BlkZCznOZWyMb2uKbLFslctFg20llBSpBMmMJSiv7fbqDqu3jUyotUUBVFA2fV0LpdDeSKbSCe8IX6fqRYOzFOlckWPjIxiHMCuYg/02Fgez3FkbbsRP2ClCRqTYKBDLVw4X3WGQ57e372cSpG1i3pkeFRpV4STkU44oBCxOxw2QsFOPZrN4lar6o1C03yp4hULBaW0FtdEOmHKD8k01EDfXIrlsh4dy6LGt5QppSg7rs7nC+BWDSWTks3xPEteQFphH1Q8D7SHnsUjO1prAn6/Wjgwj5xd0K5WZO0i1VK5FkbO8kEApVStNqF4v++2evDZY6XSzr46PGVWzH8OV2dn/4EpKJYKeteuEcrlasN08bwD5//RxC+zBDLSTY90oNGzOtIppShXSzqfy4M2FBg00kyJUtRGOpFOcrpWwPUcnbfzuFUtvVqkE+o9xhaKtlcsVKUGkEgn1JtKtaRz2TxKmSKcSCfUNZR0HT2WHQNtKCneKtIJ9Qwktadz+THtVJHzpCKdUG+KpbxXsKuGktVtkU6oL45T0WNjOZQyJG8T6YR64mmXsbFRrT0pKSnSCXVFoRjLD3tOBUOu3hbphDrrViznvKJdNZBZEpFOmqDOeZtb0tlsQaEljhREujoPbp4eGR1Du8jWe0Gkq6trSpHNj3jVstQlEUS6OmdtikI57xULFQMteZsg0tU3b/MqXj5bUJ5U3RJEunqjdTY3hlMV2QSRru55W97O6lKpKju3BJGu3rKVygVdKBTRnhLhBJGubrIBhqf1cHYE19GyBLAXTGmS/UZykX0L5947PK/8zae+okbLWaWkyV7dgVStKNE/PW/gk6bZvz7126dPkGpgewsBlNbr8qHKmqEecyIiqOoq7+k7m7P6z8bT3qy+v1K5TKVSmdXRH+AXmwxu2KgIyXlbke7AwyTN9rK/cvvgXMYcs+O1H94ajULx1ws/zVu7TqSiK20nnd+ABwYV333ewJPeI9JN5ZO76Bnu3UM9lecKwU6fevNm8fAY8A3w6UWfYUlgKa52W146v4L1BfjOsyabCpLHiXRTQIP3WDZc/t1wd6dfTa45HO1wcvcpnDPvXEJGCI1uOekm8rYfrTe4e7siKKGkSDeFzqS3lDoqv9ze559qQcmSV+KihRdz0pyTWko6T8M9Ow2+97zIJtJNMZS0XcO9MTPPybtGYDqjJBePLx/0VQ7qOKiuo169pTMUvJhXfGGdgSsJiEg3FRyt9D27uu2n86EuQ9XnT9doFnUsIr74cuaY3XWRr17S1T6Q4PNPmGwtyvl2kW5qeZt+1g4W7hrsDc9UR3K1y9t7TuODA+diTPP6Xj2kczT86CUDa4fCJ7KJdFMh55qV1Ob5PqVmZ2Nyxavw2cWXEg0f15DSaeChXYp/fNaQkU2km+pIo/T12+aVc44ZbIT341N+vnrw1+j39TeMdCNV+NSfTMnbRLop5yX67l09hafyneFGfH9LAkv4+6VfmXXpLl1rsqUoEoh0U5wEeLEQzP9msLerGf6oU3v+Ox8Z+ChVXZ0x6QwFP37JYPV2hSf9X6Sbimx51yzfsG2er+ypptkoodH4lZ9PLriQ47pOmNR+zslKZyp4dETxP581qIptIt0UhXNvyvQ7mYq/o1nP3Gg0c319fGHpl+g25+zXEsP+SqeAMQcuW2syUpElAJFuCnQYWt8z1FN6PBcKei1ywE2jOaLzSL649EuUvfKUpTMUfPUpk3VjcgJQpJsCptI8b3cWrF09wbKnWvKD28DgtN53cu7A+VTeQL43k67ThOteNviPrYqqFuFEuinkbTnXLN+6Y64xWPH7TdXac9waTbfZw0cWfJRIaMXrTjHsTboOAx4eVnzvBYNRCSVFuimObtXbd87Vz9lBv9FmhUlc7XJo8DAuXXwZISO8O9/bUzpDwVBF8e1nFM9kFX45wS3SHSgBQ/P7kTnl/xrt8tPmpSWqusop3afyyQUX4Whnt3Q+Bf/8gsHdsnVLpJtq3ra+EChbQ72G7Rl+6Ut7To4YfKD/HE4Ln8KN68v8bIOBI3mbSDeVvM12jfLqoV71cjHQ0ep524HiaY+dwx9k6/DJSBs1Hw1Tgs9Q2r1/uNv541hXwK+0dKZ9jHaOp6Vcgkh34KHk03Zn+Tc75/pMpQN+kU0Q6er1aQ07yv7q7Tt73axrBmVkE0S6OuZtJU85vx3uqTyd7wz5lJaJEkGkqxcavMdzobI11NsZMDyfT0Y3QaSr2+imt5U7qjdl+gxD0RkwZJu7INLVLZS0XcP95fb+6qhjBmVbkiDUUTpPw93DPfZTuVDYVFpmtwWhXtJp4Fk7WLhjcG7Ip3RYZiUFoY7SjTm+0s+3zfO7mpBMkghCHaUzwLlu6zxvzPEFpUkFoY7SmUpz1+Bc+2k7GJamFIQ6SqeAZwvBwpqhnk5XKxFOEOopXck1ijdk5gUKrhGSGUlBqKN0PqW9f902z9le8Xcq5PyWINRNOp/S/N/h7sLabDiooUNkE4Q6SWcqzYuFoL1mqCdY8CSUFIS6SaeAgmuUf7Wjz9xZ8YdNpSWUFIR6SafAu3Owt/pnu7PDp7SS3SSCUCfp/Errh8e6yr8fmePXEJDdJIJQR+k2lzqwhnqdrGsEpVyiINQf4/qtA6fnXWOnCCcIdScDvNuY43fvt2LWUuBLgCvtIgh14auZRHQx8NvXTUzGrNgtwPnSRo3NlsH3MzR2CiD5d4Pzq0wi+qFXhZd7/scqaxVWzPoQsBh4StpLEA6YJ4BDXyvc66RbHVu9O/a0YtYK4P3AkLSfIOw3o8C5mUT0eBQb9/YD+7XuHbNi/wJcBpjSphJeCnvFAX6YSUT/dtE168gkom/4g5PabBKzYn8C3irtK9IJr+KhTCJ66v7+sDEJ4bBi1onj+d6gtLMgMAwcNhnhJiWdFbMmvmasmDUf+DhQlnYX2hAXuCCTiPaD2jDZf3zga+KaX1gxKwjcJM9AaBM08LNMIupDqVsAMokVzJh01ipr4tuPWTFLAS/JMxFamJeAUCYRvRggE19xwC805WpgE2EncARwNLX1iYA8I6GFWJZJRF+erhebti2XVszCilnPaXQn8Cl5TkIL8FHAyCSiLy/6/joaTrpXXtDQVsy6AegAbpbnJjQhN4+HkjeP53FkLo9O24vX7VD4+BIDMSu2EPgDcLg8y+lD1unqQgY4PpOI7qznL6nbiZ49lhi2WzHrCODt8kyFBubk8VMAO+v9i2bkGN3Zd5yNFbMeVCgf8LfyfIUG4u8AXyYRfRh40+1bTSXdHWffAYBGu1bM+j7QD9wqz1uYRW4HBjKJ6NWG8s/oOdIZPTA+EXJqrYetmHUetX2cm+T5CzOZDgPHZRLRD6jxEzRb42+Z0TfQENX1YlbsI8jOlsn1HJlImSwa+HgmEb1pX6cAWmqk26twq2NYMevm8V0t/yx9Q6gD3xvP226aqbytoaWb2E42vsTwRWApcK/0E2EauB9YnElEv6A1XqO8qYYpAjaR7ylPbbVi1ruAGLBD+o1wgHnbuzOJ6OnU1t7YfnkUke4NWH3W7pIRa6yYtRD4BjTOp5TQ0HjA1zOJ6EFg/LYRQsm90TTXFMSs2G3AOdKvxj/KZSLltfxnJhF9fzO80aapMWvFrA8ChwHPSP8S9uBZYGEmEX3/omvWIdJNM1rpDVbMOhY4D8hKf2trhoHzMonoWyZy/0YMJZteujVnrpn49lYrZvUA11CrwiS0Dy7wk0wi2p9JRG9tJtmaUro9Qs2Jr5dTO0L0qPTFtuCJTCLqAz7bzH9E098bEigFtBWz/gI4GMhJv2xJhoCDM4no8c04srWcdLd/4PZavofebMWsbmr3MMgSQ+uEkp/IJKIDps/b3Cp/VMvckLUmVsv3tNK/tmKWCVwvfbap+cV4KHkjwJa/Ob5l/rCWvk48ZsUCwPPjoWdL0cLrdC+YsHxLIlqd7Y3JIt0UWLV61TKt9EsiXcOHksdB5c+ZxIkt3R9b/gLWVXetYvWq1eupXX4iVcoak4u0piOTiLa8cG0h3cRezq5clzdepawLuEX6eWPkbUAwk4j+3DDaZ/Krba4a//X5v5741rZi1gXAImCr9PtZYT1wSCYR/Tiqdh/GtngUka5F2X2ESKvt43etv0McmFFOyySih2cS0U0AmTaSrW2l2x12rlo9IeHvAT/wZfGhrvwdtWrJDyy+9om2bghD+gJ4ynOsmPVdYD7wG2mRaeU/gPmZRPRqxqdat8WPE+nanbvPvHvi20ErZr0POBGpUjZVtgEnZRLRD/rwDQItueYm0k1TvofHY1bMOoTaEoOcEp08F2US0SWZRPQRgM2JY6VF9kBJE7w5777n3cp0ze8D8UZ6Xw26OH5NJhG9XHqNjHRTwnRMbcWsBLUlhgelRfbK76mdAhDhRLppCDlfuXF2uxWz3k6tStk2aRmgdtnGWZlE9B2gNktziHR1yfesmLXGillLgKvaON9zgW9lEtEFwGo4sLu3JacTDohYzcYz2yinuyOTiL5XnryMdLMj3JoYVsyKAYupHSFqZV4CDhXhRLrZDTnPrIWcruFmrJh1NHABMNZif2YOODeTiB6hYKM8dZGuIbjnjHsmvr3Film9wE9p/pIRDvCDTCJ2VC4SAAABsElEQVTarZS+DWCbLG6LdA038k1spkZ9erxkRLNuMlwHdGQS0TjIti2RrglYHdu9mfp44HBgtEneeglYmklEj/OUlp04Il2Tollvxay5wCca+F16wAWZRLST8TOGO2R0E+maNuRcZU3cvXfj+MWXNzbYW7yR2oWJt7RqIaBGQ9bpZpBx+YhZsTCwFjjyQF9rGtbptirNsm2XRyvyZES6tuBd972LjlLHivFJixmWTh+dSRz3PMChV69lw+dPkAci4WXr05nvxIpZTyqlTOCiGfq1l9RCyeN2L+SLcCJd23Dn2XfWxhytPStm/ZxalbKb6vTrbgXmZBLR6zCUK60v0rU1E2t7WmvbilkfA44ApmvH/mZqR27O05o8QOYy2ZgsOZ2wV2JW7J3A76aQ052RSUTvWfz9J9h2uUz/y0gnvLlwd8ewYta95DCYfJWyrwH+TCJ6DyDCiXTCfoWcZ4wfnJ2DHq9StpB9Vym7g1rVre8oreV2WpFOmFK+h94xXqXsFCDzmh/bAJw8fuRmUEY3kU6YBibu3gP+aMWsxcAloDJaG5dkEtHDCPEwSIm7ZuH/A3EF+//SEPhyAAAAAElFTkSuQmCC'
        self.update_period=30
        self.ind = None
        self.last_updated = None
        self.item_updated = None
        self.default = None
        self.arb_notify = True

        # Set Icon
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(base64.decodestring(self.icon))
        icon_name = f.name
        f.close()

        self.ind = appindicator.Indicator.new(
            self.appindicator_id, 
            os.path.abspath(icon_name), 
            appindicator.IndicatorCategory.SYSTEM_SERVICES,
        )
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.ind.set_label('RaiBlocks', 'RaiBlocks')
        self.ind.set_menu(self.build_menu())
        
        notify.init(self.appindicator_id)

        self.update_timer = None
        self.update()

        gtk.main()

    def fetch_joke(self):
        response = urllib.request.urlopen('http://api.icndb.com/jokes/random?limitTo=[nerdy]')
        joke = json.loads(response.read().decode('utf-8'))['value']['joke']
        return joke

    def joke(self, w=None):
        notify.Notification.new("<b>Joke</b>", self.fetch_joke(), None).show()

    def fetch_bitgrail(self):
        request = urllib.request.Request('https://api.bitgrail.com/v1/markets', headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))['response']['BTC']['markets']['XRB/BTC']
        return data

    def fetch_kucoin(self):
        request = urllib.request.Request('https://api.kucoin.com/v1/open/tick', headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))['data']
        for d in data:
            if d['symbol'] == 'XRB-BTC':
                return d
        return None

    def fetch_coinmarket(self):
        request = urllib.request.Request('https://api.coinmarketcap.com/v1/ticker/', headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))
        raiblocks = None
        for d in data:
            if d['id'] == 'raiblocks':
                raiblocks = d
        return raiblocks, data[:20]

    def fetch_club(self):
        request = urllib.request.Request('https://www.nanode.co/blocks', headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        lines = response.readlines()
        for line in lines:
            line = line.decode('utf-8').strip()
            if line.startswith('__NEXT_DATA__'):
                line = line.split('= ')[1]
                data = json.loads(line)
                break
        data = data['props']['networkSummary']
        del(data['latest_transactions'])
        return data

    def build_menu(self):
        menu = gtk.Menu()

        self.item_updated = gtk.MenuItem('Last Updated: Never')
        self.item_updated.connect('activate', self.update)
        menu.append(self.item_updated)

        menu.append(gtk.SeparatorMenuItem())

        menu_top20 = gtk.Menu()
        item_top20 = gtk.MenuItem('Top 20 Crypto')
        menu.append(item_top20)
        item_top20.set_submenu(menu_top20)

        self.item_crypto = []
        for i in range(20):
            self.item_crypto.append(gtk.MenuItem('Unknown'))
            self.item_crypto[-1].connect('activate', self.set_default_display)
            menu_top20.append(self.item_crypto[-1])

        menu_exchanges = gtk.Menu()
        item_exchanges = gtk.MenuItem('Exchanges')
        menu.append(item_exchanges)
        item_exchanges.set_submenu(menu_exchanges)

        self.item_arb = gtk.MenuItem('Arb: Unknown')
        self.item_arb.connect('activate', self.set_default_display)
        menu_exchanges.append(self.item_arb)

        self.item_notify_arb = gtk.MenuItem('Disable Arb Notifications')
        self.item_notify_arb.connect('activate', self.toggle_arb_notify)
        menu_exchanges.append(self.item_notify_arb)

        self.item_bitgrail_btc = gtk.MenuItem('BitGrail (BTC): Unknown')
        self.item_bitgrail_btc.connect('activate', self.set_default_display)
        menu_exchanges.append(self.item_bitgrail_btc)

        self.item_kucoin_btc = gtk.MenuItem('Kucoin (BTC): Unknown')
        self.item_kucoin_btc.connect('activate', self.set_default_display)
        menu_exchanges.append(self.item_kucoin_btc)

        menu.append(gtk.SeparatorMenuItem())

        self.item_price_usd = gtk.MenuItem('USD: Unknown')
        self.item_price_usd.connect('activate', self.set_default_display)
        menu.append(self.item_price_usd)
        self.default = self.item_price_usd

        self.item_price_btc = gtk.MenuItem('BTC: Unknown')
        self.item_price_btc.connect('activate', self.set_default_display)
        menu.append(self.item_price_btc)

        self.item_price_1h = gtk.MenuItem('1h: Unknown')
        self.item_price_1h.connect('activate', self.set_default_display)
        menu.append(self.item_price_1h)

        self.item_price_24h = gtk.MenuItem('24h: Uknown')
        self.item_price_24h.connect('activate', self.set_default_display)
        menu.append(self.item_price_24h)

        self.item_price_7d = gtk.MenuItem('7d: Unknown')
        self.item_price_7d.connect('activate', self.set_default_display)
        menu.append(self.item_price_7d)

        self.item_24h_volume_usd = gtk.MenuItem('Volume: Unknown')
        self.item_24h_volume_usd.connect('activate', self.set_default_display)
        menu.append(self.item_24h_volume_usd)

        self.item_market_cap = gtk.MenuItem('Market Cap: Unknown')
        self.item_market_cap.connect('activate', self.set_default_display)
        menu.append(self.item_market_cap)

        self.item_rank = gtk.MenuItem('CMC Rank: Unknown')
        self.item_rank.connect('activate', self.set_default_display)
        menu.append(self.item_rank)

        menu.append(gtk.SeparatorMenuItem())

        self.item_block_count = gtk.MenuItem('Block Count: Unknown')
        self.item_block_count.connect('activate', self.set_default_display)
        menu.append(self.item_block_count)

        self.item_peer_count = gtk.MenuItem('Peer Count: Unknown')
        self.item_peer_count.connect('activate', self.set_default_display)
        menu.append(self.item_peer_count)

        self.item_5s_tps = gtk.MenuItem('5s: Unknown')
        self.item_5s_tps.connect('activate', self.set_default_display)
        menu.append(self.item_5s_tps)

        self.item_1m_tps = gtk.MenuItem('1m: Unknown')
        self.item_1m_tps.connect('activate', self.set_default_display)
        menu.append(self.item_1m_tps)

        self.item_30m_tps = gtk.MenuItem('30m: Unknown')
        self.item_30m_tps.connect('activate', self.set_default_display)
        menu.append(self.item_30m_tps)

        self.item_24h_tps = gtk.MenuItem('24h: Unknown')
        self.item_24h_tps.connect('activate', self.set_default_display)
        menu.append(self.item_24h_tps)

        self.item_frontiers = gtk.MenuItem('Frontiers: Unknown')
        self.item_frontiers.connect('activate', self.set_default_display)
        menu.append(self.item_frontiers)

        menu.append(gtk.SeparatorMenuItem())

        item_raiblocks_cmc = gtk.MenuItem('CoinMarketcap.com/currencies/raiblocks/')
        item_raiblocks_cmc.connect('activate', self.launch_website)
        menu.append(item_raiblocks_cmc)

        item_raiblocks_net = gtk.MenuItem('RaiBlocks.net')
        item_raiblocks_net.connect('activate', self.launch_website)
        menu.append(item_raiblocks_net)

        item_raiblocks_club = gtk.MenuItem('RaiBlocks.club')
        item_raiblocks_club.connect('activate', self.launch_website)
        menu.append(item_raiblocks_club)

        item_raiblocks_watch = gtk.MenuItem('Rai.watch')
        item_raiblocks_watch.connect('activate', self.launch_website)
        menu.append(item_raiblocks_watch)

        item_raiblocks_reddit = gtk.MenuItem('reddit.com/r/RaiBlocks')
        item_raiblocks_reddit.connect('activate', self.launch_website)
        menu.append(item_raiblocks_reddit)

        item_raiblocks_wallet = gtk.MenuItem('RaiWallet.com')
        item_raiblocks_wallet.connect('activate', self.launch_website)
        menu.append(item_raiblocks_wallet)

        menu.append(gtk.SeparatorMenuItem())

        item_joke = gtk.MenuItem('Joke')
        item_joke.connect('activate', self.joke)
        menu.append(item_joke)

        menu.append(gtk.SeparatorMenuItem())

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        #menu_top20.show_all()
        return menu

    def set_default_display(self, w=None):
        self.default = w
        self.ind.set_label(self.default.get_label(), '')

    def launch_website(self, w=None):
        webbrowser.open_new_tab('http://www.{}'.format(w.get_label()))

    def toggle_arb_notify(self, w=None):
        self.arb_notify = not self.arb_notify
        if self.arb_notify:
            self.item_notify_arb.set_label('Disable Arb Notifications')
        else:
            self.item_notify_arb.set_label('Enable Arb Notifications')

    def update(self, w=None):
        if self.update_timer:
            glib.source_remove(self.update_timer)

        self.last_updated = datetime.datetime.now()
        self.item_updated.set_label('Last Updated: {:%Y-%m-%d %H:%M:%S}'.format(self.last_updated))
        
        cm_data_rai, cm_data_top20 = self.fetch_coinmarket()
        self.item_price_usd.set_label('${}'.format(cm_data_rai['price_usd']))
        self.item_price_btc.set_label('฿{}'.format(cm_data_rai['price_btc']))
        self.item_price_1h.set_label('1h: {}%'.format(cm_data_rai['percent_change_1h']))
        self.item_price_24h.set_label('24h: {}%'.format(cm_data_rai['percent_change_24h']))
        self.item_price_7d.set_label('7d: {}%'.format(cm_data_rai['percent_change_7d']))
        self.item_24h_volume_usd.set_label('Volume: ${}'.format(cm_data_rai['24h_volume_usd']))
        self.item_market_cap.set_label('Market Cap: ${}'.format(cm_data_rai['market_cap_usd']))
        self.item_rank.set_label('CMC Rank: #{}'.format(cm_data_rai['rank']))

        for i in range(20):
            self.item_crypto[i].set_label('{}.) {}: ${} ( 1h:{}% | 24h:{}% | 7d:{}% )'.format(
                i+1, cm_data_top20[i]['name'], 
                cm_data_top20[i]['price_usd'], 
                cm_data_top20[i]['percent_change_1h'],
                cm_data_top20[i]['percent_change_24h'],
                cm_data_top20[i]['percent_change_7d']
                )
            )
        
        club_data = self.fetch_club()
        self.item_block_count.set_label('Block Count: {}'.format(club_data['block_count']))
        self.item_peer_count.set_label('Peer Count: {}'.format(club_data['peer_count']))
        self.item_5s_tps.set_label('5s: {:1.3f} tps'.format(club_data['tx_rate_5_sec']))
        self.item_1m_tps.set_label('1m: {:1.3f} tps'.format(club_data['tx_rate_1_min']))
        self.item_30m_tps.set_label('30m: {:1.3f} tps'.format(club_data['tx_rate_30_min']))
        self.item_24h_tps.set_label('24h: {:1.3f} tps'.format(club_data['tx_rate_24_hr']))
        self.item_frontiers.set_label('Frontiers: {}'.format(club_data['frontier_count']))

        bitgrail_data = self.fetch_bitgrail()
        self.item_bitgrail_btc.set_label('BitGrail (BTC): {} | {}'.format(bitgrail_data['ask'], bitgrail_data['bid']))

        kucoin_data = self.fetch_kucoin()
        self.item_kucoin_btc.set_label('Kucoin (BTC): {} | {}'.format(kucoin_data['sell'], kucoin_data['buy']))

        #if float(bitgrail_data['bid']) > float(kucoin_data['sell']):
        ret = (float(bitgrail_data['bid']) - float(kucoin_data['sell'])) / float(kucoin_data['sell'])
        best_ret = ret
        label = 'Arb: {} | B:Ku S:BG | {} | {:1.2}%'.format(kucoin_data['sell'], bitgrail_data['bid'], best_ret*100)

        #if float(kucoin_data['buy']) > float(bitgrail_data['ask']):
        ret = (float(kucoin_data['buy']) - float(bitgrail_data['ask'])) / float(bitgrail_data['ask'])
        if ret > best_ret:
            best_ret = ret
            label = 'Arb: {} | B:BG S:Ku | {} | {:1.2}%'.format(bitgrail_data['ask'], kucoin_data['buy'], best_ret*100)

        self.item_arb.set_label(label)
        if self.arb_notify and best_ret > 0.01:
            notify.Notification.new("<b>Arbitrage Opportunity</b>", label, None).show()
        
        self.ind.set_label(self.default.get_label(), '')

        self.update_timer = glib.timeout_add_seconds(self.update_period, self.update)



    def quit(self, w=None):
        notify.uninit()
        gtk.main_quit()


if __name__ == "__main__":
    raiblocks_indicator = RaiBlocks_Indicator()