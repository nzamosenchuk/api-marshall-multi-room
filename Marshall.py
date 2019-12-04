# This module is a low-level API abstraction for Marshall Multi Room speakers
import xml.etree.ElementTree as ET
import requests


# API Group is the collection of the same resources supporting few operations, e.g. SET and GET
# Base API Group class with HTTP request method
class ApiAction:
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
        if len(value_list) > 0:
            if value_list[0].tag != "c8_array" and value_list[0].text is not None:
                return int(value_list[0].text)
            else:
                return value_list[0].text
        return None

    def set(self, value: int):
        xml_root = self.http('SET',  {'value': value})
        status = xml_root.find('status').text
        print("SET", self.resource, status)
        return xml_root.find('status').text == 'FS_OK'

    def get_set(self, value = None):
        if value is None:
            return self.get()
        else:
            return self.set(value)


# API Group to list presets
class ApiListPresets(ApiAction):
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
class ApiListModes(ApiAction):
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
        self.name = ApiAction(ip, 'netremote.sys.info.friendlyname').get
        self.mac = ApiAction(ip, 'netremote.sys.net.wlan.macaddress').get
        self.version = ApiAction(ip, 'netremote.sys.info.version').get
        self.vendorId = ApiAction(ip, 'netremote.sys.info.netremotevendorid').get

        self.mute = ApiAction(ip, 'netremote.sys.audio.mute').get_set
        self.volume = ApiAction(ip, 'netremote.sys.audio.volume').get_set
        self.volumeSteps = ApiAction(ip, 'netremote.sys.caps.volumesteps').get

        self.groupMasterVolume = ApiAction(ip, 'netremote.multiroom.group.mastervolume').get_set
        self.groupId = ApiAction(ip, 'netremote.multiroom.group.id').get
        self.groupName = ApiAction(ip, 'netremote.multiroom.group.name').get
        self.groupState = ApiAction(ip, 'netremote.multiroom.group.state').get

        self.eqCustom0 = ApiAction(ip, 'netremote.sys.audio.eqcustom.param0').get_set
        self.eqCustom1 = ApiAction(ip, 'netremote.sys.audio.eqcustom.param1').get_set

        self.currentPreset = ApiAction(ip, 'netremote.nav.preset.currentpreset').get # cant set

        # 0: Nothing while Bluetooth not connected / AUX 2: Playing  / or RCA  3: Paused while spotify 6: Stopped while streaming
        self.playStatus = ApiAction(ip, 'netremote.play.status').get
        self.playCaps = ApiAction(ip, 'netremote.play.caps').get
        self.playDuration = ApiAction(ip, 'netremote.play.info.duration').get
        self.playImgUri = ApiAction(ip, 'netremote.play.info.graphicuri').get
        self.playArtist = ApiAction(ip, 'netremote.play.info.artist').get
        self.playAlbum = ApiAction(ip, 'netremote.play.info.album').get
        self.playName = ApiAction(ip, 'netremote.play.info.name').get
        self.playPosition = ApiAction(ip, 'netremote.play.position').get
        self.playShuffle = ApiAction(ip, 'netremote.play.shuffle').get_set
        self.playRepeat = ApiAction(ip, 'netremote.play.repeat').get_set
        self.playSpotifyPlaylist = ApiAction(ip, 'netremote.spotify.playlist.name').get
        self.playSpotifyPlaylistUri = ApiAction(ip, 'netremote.spotify.playlist.uri').get

        self.power = ApiAction(ip, 'netremote.sys.power').get_set

        self.listPresets = ApiListPresets(ip).list
        self.listModes = ApiListModes(ip).list
        self.selectPreset = ApiAction(ip, 'netremote.nav.action.selectpreset').set
        self.state = ApiAction(ip, 'netremote.nav.state').set # 1 on selecting preset
        self.playControl = ApiAction(ip, 'netremote.play.control').set # 0: Play/Stop (on Radio) 2: Play/Pause (on Spotify) 3: Next 4: Prev

        # TODO
        # "http://192.168.192.33/fsapi/LIST_GET_NEXT/netremote.bluetooth.connecteddevices/-1?pin=1234&maxItems=20"
        # "http://192.168.192.33/fsapi/LIST_GET_NEXT/netremote.multiroom.device.listall/-1?pin=1234&maxItems=20"
        #
        # TODO : not clear what does it actually do
        # "http://192.168.192.33/fsapi/CREATE_SESSION?pin=1234"
        # "http://192.168.192.33/fsapi/GET_NOTIFIES?pin=1234&sid=527929965d"
