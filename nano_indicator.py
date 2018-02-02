#!/usr/bin/python3

####################################
# Name: Nano Indicator
# Author: Jason Pawlak
# Donations: xrb_1hi54n577fag69bgts53fwiq9ns45rrkgomyhk3smxti1sdgsscwrag1rnk1
# Description: This is an indicator for Unity menu bar that displays
#  information about Nano
# Refs:
#  API: https://lazka.github.io/pgi-docs/AppIndicator3-0.1/classes/Indicator.html
#

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

_version = '0.1.0'

currency_mark = {
    'price_usd': '$',
    'price_btc': '฿',
}

def fetch_github_version():
    try:
        url = 'https://raw.githubusercontent.com/pawapps/nano_indicator/master/nano_indicator.py'
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        lines = response.readlines()
        for line in lines:
            line = line.decode('utf-8').strip()
            if line.startswith('_version'):
                data = line.split('\'')[1]
                return data
    except:
        return None

class Nano_Indicator():

    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.appindicator_id = 'nano_indicator'
        self.icon = b'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'
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
        self.ind.set_label('Nano', 'Nano')
        self.ind.set_menu(self.build_menu())
        
        notify.init(self.appindicator_id)

        self.update_timer = None
        self.update()

        gtk.main()

    def fetch_bitgrail(self):
        try:
            request = urllib.request.Request('https://api.bitgrail.com/v1/markets', headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('utf-8'))['response']['BTC']['markets']['XRB/BTC']
        except:
            data = {}
        return data

    def fetch_kucoin(self):
        try:
            request = urllib.request.Request('https://api.kucoin.com/v1/open/tick', headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('utf-8'))['data']
            for d in data:
                if d['symbol'] == 'XRB-BTC':
                    return d
        except:
            return {}
        return None

    def fetch_coinmarket(self):
        try:
            request = urllib.request.Request('https://api.coinmarketcap.com/v1/ticker/', headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('utf-8'))
            nano = None
            for d in data:
                if d['id'] == 'raiblocks':
                    nano = d
        except:
            return {}, {}
        return nano, data[:20]

    def fetch_club(self):
        try:
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
        except:
            data = {}
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

        item_nano_cmc = gtk.MenuItem('CoinMarketcap.com/currencies/raiblocks/')
        item_nano_cmc.connect('activate', self.launch_website)
        menu.append(item_nano_cmc)

        item_nano_net = gtk.MenuItem('Nano.org')
        item_nano_net.connect('activate', self.launch_website)
        menu.append(item_nano_net)

        item_nano_club = gtk.MenuItem('Nanode.co')
        item_nano_club.connect('activate', self.launch_website)
        menu.append(item_nano_club)

        item_nano_watch = gtk.MenuItem('Nanowat.ch')
        item_nano_watch.connect('activate', self.launch_website)
        menu.append(item_nano_watch)

        item_nano_reddit = gtk.MenuItem('reddit.com/r/nanocurrency')
        item_nano_reddit.connect('activate', self.launch_website)
        menu.append(item_nano_reddit)

        item_nano_wallet = gtk.MenuItem('NanoWallet.io')
        item_nano_wallet.connect('activate', self.launch_website)
        menu.append(item_nano_wallet)

        menu.append(gtk.SeparatorMenuItem())

        self.item_version = gtk.MenuItem('Version: ')
        self.item_version.connect('activate', self.go_github)
        menu.append(self.item_version)

        menu.append(gtk.SeparatorMenuItem())

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        #menu_top20.show_all()
        return menu

    def go_github(self, w=None):
        webbrowser.open_new_tab('https://github.com/pawapps/nano_indicator')

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
        try:
            self.item_bitgrail_btc.set_label('BitGrail (BTC): {} | {}'.format(bitgrail_data['ask'], bitgrail_data['bid']))
        except:
            self.item_bitgrail_btc.set_label('BitGrail (BTC): {} | {}'.format('Error Rx', 'Error Rx'))

        kucoin_data = self.fetch_kucoin()
        try:
            self.item_kucoin_btc.set_label('Kucoin (BTC): {} | {}'.format(kucoin_data['sell'], kucoin_data['buy']))
        except:
            self.item_kucoin_btc.set_label('Kucoin (BTC): {} | {}'.format('Error Rx', 'Error Rx'))

        try:
            ret = (float(bitgrail_data['bid']) - float(kucoin_data['sell'])) / float(kucoin_data['sell'])
            best_ret = ret
            label = 'Arb: {} | B:Ku S:BG | {} | {:1.2}%'.format(kucoin_data['sell'], bitgrail_data['bid'], best_ret*100)
        except:
            best_ret = 0.0
            label = 'Error receiving data'

        try:
            ret = (float(kucoin_data['buy']) - float(bitgrail_data['ask'])) / float(bitgrail_data['ask'])
            if ret > best_ret:
                best_ret = ret
                label = 'Arb: {} | B:BG S:Ku | {} | {:1.2}%'.format(bitgrail_data['ask'], kucoin_data['buy'], best_ret*100)
        except:
            best_ret = 0.0
            label = 'Error receiving data'

        self.item_arb.set_label(label)
        if self.arb_notify and best_ret > 0.01:
            notify.Notification.new("<b>Arbitrage Opportunity</b>", label, None).show()

        version = fetch_github_version()
        label = 'Version: {}'.format(_version)
        if (version and version != _version):
            label += ' (update available {})'.format(version)
        self.item_version.set_label(label)
        
        self.ind.set_label(self.default.get_label(), '')

        self.update_timer = glib.timeout_add_seconds(self.update_period, self.update)



    def quit(self, w=None):
        notify.uninit()
        gtk.main_quit()


if __name__ == "__main__":
    nano_indicator = Nano_Indicator()