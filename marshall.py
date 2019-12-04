# This module is a low-level API abstraction for Marshall Multi Room speakers
import xml.etree.ElementTree as ET
import requests


# API Group is the collection of the same resources supporting few operations, e.g. SET and GET
# Base API Group class with HTTP request method
class ApiGroupBase:
    def __init__(self, ip, resource):
        self.ip = ip
        self.resource = resource

    def http(self, resource_action: str, parameters={}, resource_id=""):
        URL = "http://{}/fsapi/{}/{}/{}".format(self.ip, resource_action, self.resource, resource_id)
        parameters['pin'] = '1234' # inject pim
        response = requests.get(url=URL, params=parameters)
        return ET.fromstring(response.content)


# API group with GET String
class ApiGroupGet(ApiGroupBase):
    def get(self):
        xml_root = self.http('GET')
        value_list = list(xml_root.find('value'))
        return value_list[0].text if len(value_list)>0 else ''


# API Group with SET only
class ApiGroupSet(ApiGroupBase):
    def set(self, value: int):
        xml_root = self.http('SET',  {'value': value})
        return xml_root.find('status').text == 'FS_OK'


# API Group with GET and SET For SInt
class ApiGroupGetSet(ApiGroupGet):
    def set(self, value: int):
        xml_root = self.http('SET',  {'value': value})
        return xml_root.find('status').text == 'FS_OK'

# API Group to list presets
class ApiListPresets(ApiGroupBase):
    def __init__(self, ip):
        self.ip = ip
        self.resource = "netremote.nav.presets"

    def list(self):
        xml_root = self.http('LIST_GET_NEXT', {"maxItems":7}, "-1")
        presets = []
        for item in xml_root.iter("item"):
            preset = {"key": item.attrib["key"]}
            presets.append(preset)
            for field in item.iter():
                if field.tag == "field":
                    if field.attrib["name"] == "name":
                        preset["name"] = field.find("c8_array").text
                    if field.attrib["name"] == "type":
                        preset["type"] = field.find("c8_array").text
                    if field.attrib["name"] == "artworkurl":
                        preset["artworkurl"] = field.find("c8_array").text
                    if field.attrib["name"] == "blob":
                        preset["blob"] = field.find("c8_array").text
                    if field.attrib["name"] == "playlisturl":
                        preset["playlisturl"] = field.find("c8_array").text
                    if field.attrib["name"] == "uniqid":
                        preset["uniqid"] = field.find("c8_array").text
        return presets


# API Group to list modes
class ApiListModes(ApiGroupBase):
    def __init__(self, ip):
        self.ip = ip
        self.resource = "netremote.sys.caps.validmodes"

    def list(self):
        xml_root = self.http('LIST_GET_NEXT', {"maxItems":20}, "-1")
        modes = []
        for item in xml_root.iter("item"):
            mode = {"key": item.attrib["key"]}
            modes.append(mode)
            for field in item.iter():
                if field.tag == "field":
                    if field.attrib["name"] == "id":
                        mode["id"] = field.find("c8_array").text
                    if field.attrib["name"] == "label":
                        mode["label"] = field.find("c8_array").text
                    if field.attrib["name"] == "selectable":
                        mode["selectable"] = field.find("u8").text == '1'
                    if field.attrib["name"] == "streamable":
                        mode["streamable"] = field.find("u8").text == '1'
                    if field.attrib["name"] == "modetype":
                        mode["modetype"] = field.find("u8").text == '1'
        return modes


# API
class MultiRoomApi:
    def __init__(self, ip):
        self.name = ApiGroupGet(ip, 'netremote.sys.info.friendlyname')
        self.mac = ApiGroupGet(ip, 'netremote.sys.net.wlan.macaddress')
        self.version = ApiGroupGet(ip, 'netremote.sys.info.version')
        self.vendorId = ApiGroupGet(ip, 'netremote.sys.info.netremotevendorid')

        self.mute = ApiGroupGetSet(ip, 'netremote.sys.audio.mute')
        self.volume = ApiGroupGetSet(ip, 'netremote.sys.audio.volume')
        self.volumeSteps = ApiGroupGet(ip, 'netremote.sys.caps.volumesteps')

        self.groupMasterVolume = ApiGroupGetSet(ip, 'netremote.multiroom.group.mastervolume')
        self.groupId = ApiGroupGet(ip, 'netremote.multiroom.group.id')
        self.groupName = ApiGroupGet(ip, 'netremote.multiroom.group.name')
        self.groupState = ApiGroupGet(ip, 'netremote.multiroom.group.state')

        self.eqCustom0 = ApiGroupGetSet(ip, 'netremote.sys.audio.eqcustom.param0')
        self.eqCustom1 = ApiGroupGetSet(ip, 'netremote.sys.audio.eqcustom.param1')

        self.currentPreset = ApiGroupGet(ip, 'netremote.nav.preset.currentpreset') # cant set

        # 0: Nothing while Bluetooth not connected / AUX 2: Playing  / or RCA  3: Paused while spotify 6: Stopped while streaming
        self.playStatus = ApiGroupGet(ip, 'netremote.play.status')
        self.playCaps = ApiGroupGet(ip, 'netremote.play.caps')
        self.playDuration = ApiGroupGet(ip, 'netremote.play.info.duration')
        self.playImgUri = ApiGroupGet(ip, 'netremote.play.info.graphicuri')
        self.playArtist = ApiGroupGet(ip, 'netremote.play.info.artist')
        self.playAlbum = ApiGroupGet(ip, 'netremote.play.info.album')
        self.playName = ApiGroupGet(ip, 'netremote.play.info.name')
        self.playPosition = ApiGroupGet(ip, 'netremote.play.position')
        self.playShuffle = ApiGroupGetSet(ip, 'netremote.play.shuffle')
        self.playRepeat = ApiGroupGetSet(ip, 'netremote.play.repeat')
        self.playSpotifyPlaylist = ApiGroupGet(ip, 'netremote.spotify.playlist.name')
        self.playSpotifyPlaylistUri = ApiGroupGet(ip, 'netremote.spotify.playlist.uri')

        self.power = ApiGroupGetSet(ip, 'netremote.sys.power')

        self.listPresets = ApiListPresets(ip)
        self.listModes = ApiListModes(ip)
        self.selectPreset = ApiGroupSet(ip, 'netremote.nav.action.selectpreset')
        self.state = ApiGroupSet(ip, 'netremote.nav.state') # 1 on selecting preset
        self.playControl = ApiGroupSet(ip, 'netremote.play.control') # 0: Play/Stop (on Radio) 2: Play/Pause (on Spotify) 3: Next 4: Prev

        # TODO
        # "http://192.168.192.33/fsapi/LIST_GET_NEXT/netremote.bluetooth.connecteddevices/-1?pin=1234&maxItems=20"
        # "http://192.168.192.33/fsapi/LIST_GET_NEXT/netremote.multiroom.device.listall/-1?pin=1234&maxItems=20"
        #
        # TODO : not clear what does it actually do
        # "http://192.168.192.33/fsapi/CREATE_SESSION?pin=1234"
        # "http://192.168.192.33/fsapi/GET_NOTIFIES?pin=1234&sid=527929965d"