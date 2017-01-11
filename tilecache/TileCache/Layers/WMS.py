# BSD Licensed, Copyright (c) 2006-2010 TileCache Contributors

import urllib2

from TileCache.Layer import MetaLayer
import TileCache.Client as WMSClient

class WMS(MetaLayer):
    config_properties = [
      {'name':'name', 'description': 'Name of Layer'}, 
      {'name':'url', 'description': 'URL of Remote Layer'},
      {'name':'user', 'description': 'Username of remote server: used for basic-auth protected backend WMS layers.'},
      {'name':'password', 'description': 'Password of remote server: Use for basic-auth protected backend WMS layers.'},
    ] + MetaLayer.config_properties  
     
    def __init__ (self, name, url = None, user = None, password = None, **kwargs):
        MetaLayer.__init__(self, name, **kwargs) 
        self.url = url
        self.user = user
        self.password = password

    def renderTile(self, tile):
        url = self.url
        if self.current_token:
            url += '&token=%s' % self.current_token
        wms = WMSClient.WMS(url, {
          "bbox": tile.bbox(),
          "width": tile.size()[0],
          "height": tile.size()[1],
          "srs": self.srs,
          "format": self.mime_type,
          "layers": self.layers,
        }, self.user, self.password)
        try:
                tile.data, response = wms.fetch()
                self._inside_token_retry = False
                return tile.data
        except urllib2.HTTPError, e:
                if self._inside_token_retry:
                        raise
                if e.getcode() in (498, 499):
                        self.set_auth_token()
                        self._inside_token_retry = True
                        return self.renderTile(tile)
        return tile.data 
