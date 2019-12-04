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

    def get(self):
        xml_root = self.http('GET')
        value_list = list(xml_root.find('value'))
        return value_list[0].text if len(value_list) > 0 else ''

    def set(self, value: int):
        xml_root = self.http('SET',  {'value': value})
        return xml_root.find('status').text == 'FS_OK'

    def get_set(self, value = None):
        if value is None:
            return self.get()
        else:
            return self.set(value)


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


# MultiRoom API
class MultiRoomAPI:
    def __init__(self, ip):
        self.name = ApiGroupBase(ip, 'netremote.sys.info.friendlyname').get
        self.mac = ApiGroupBase(ip, 'netremote.sys.net.wlan.macaddress').get
        self.version = ApiGroupBase(ip, 'netremote.sys.info.version').get
        self.vendorId = ApiGroupBase(ip, 'netremote.sys.info.netremotevendorid').get

        self.mute = ApiGroupBase(ip, 'netremote.sys.audio.mute').get_set
        self.volume = ApiGroupBase(ip, 'netremote.sys.audio.volume').get_set
        self.volumeSteps = ApiGroupBase(ip, 'netremote.sys.caps.volumesteps').get

        self.groupMasterVolume = ApiGroupBase(ip, 'netremote.multiroom.group.mastervolume').get_set
        self.groupId = ApiGroupBase(ip, 'netremote.multiroom.group.id').get
        self.groupName = ApiGroupBase(ip, 'netremote.multiroom.group.name').get
        self.groupState = ApiGroupBase(ip, 'netremote.multiroom.group.state').get

        self.eqCustom0 = ApiGroupBase(ip, 'netremote.sys.audio.eqcustom.param0').get_set
        self.eqCustom1 = ApiGroupBase(ip, 'netremote.sys.audio.eqcustom.param1').get_set

        self.currentPreset = ApiGroupBase(ip, 'netremote.nav.preset.currentpreset').get # cant set

        # 0: Nothing while Bluetooth not connected / AUX 2: Playing  / or RCA  3: Paused while spotify 6: Stopped while streaming
        self.playStatus = ApiGroupBase(ip, 'netremote.play.status').get
        self.playCaps = ApiGroupBase(ip, 'netremote.play.caps').get
        self.playDuration = ApiGroupBase(ip, 'netremote.play.info.duration').get
        self.playImgUri = ApiGroupBase(ip, 'netremote.play.info.graphicuri').get
        self.playArtist = ApiGroupBase(ip, 'netremote.play.info.artist').get
        self.playAlbum = ApiGroupBase(ip, 'netremote.play.info.album').get
        self.playName = ApiGroupBase(ip, 'netremote.play.info.name').get
        self.playPosition = ApiGroupBase(ip, 'netremote.play.position').get
        self.playShuffle = ApiGroupBase(ip, 'netremote.play.shuffle').get_set
        self.playRepeat = ApiGroupBase(ip, 'netremote.play.repeat').get_set
        self.playSpotifyPlaylist = ApiGroupBase(ip, 'netremote.spotify.playlist.name').get
        self.playSpotifyPlaylistUri = ApiGroupBase(ip, 'netremote.spotify.playlist.uri').get

        self.power = ApiGroupBase(ip, 'netremote.sys.power').get_set

        self.listPresets = ApiListPresets(ip).list
        self.listModes = ApiListModes(ip).list
        self.selectPreset = ApiGroupBase(ip, 'netremote.nav.action.selectpreset').set
        self.state = ApiGroupBase(ip, 'netremote.nav.state').set # 1 on selecting preset
        self.playControl = ApiGroupBase(ip, 'netremote.play.control').set # 0: Play/Stop (on Radio) 2: Play/Pause (on Spotify) 3: Next 4: Prev

        # TODO
        # "http://192.168.192.33/fsapi/LIST_GET_NEXT/netremote.bluetooth.connecteddevices/-1?pin=1234&maxItems=20"
        # "http://192.168.192.33/fsapi/LIST_GET_NEXT/netremote.multiroom.device.listall/-1?pin=1234&maxItems=20"
        #
        # TODO : not clear what does it actually do
        # "http://192.168.192.33/fsapi/CREATE_SESSION?pin=1234"
        # "http://192.168.192.33/fsapi/GET_NOTIFIES?pin=1234&sid=527929965d"
