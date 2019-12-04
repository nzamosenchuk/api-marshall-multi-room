# Sample test to fetch all the available information
import Marshall

api = Marshall.MultiRoomAPI('192.168.192.33')
print(api.name())
print(api.mac())
print(api.version())
print(api.vendorId())

print(api.mute())
print(api.volume())
print(api.volumeSteps())

print(api.groupMasterVolume())
print(api.groupId())
print(api.groupName())
print(api.groupState())

print(api.eqCustom0())
print(api.eqCustom1())

print(api.currentPreset())

print(api.playStatus())
print(api.playCaps())
print(api.playDuration())
print(api.playImgUri())
print(api.playArtist())
print(api.playAlbum())
print(api.playName())
print(api.playPosition())
print(api.playShuffle())
print(api.playRepeat())
print(api.playSpotifyPlaylist())
print(api.playSpotifyPlaylistUri())

print(api.power())

print(api.listPresets())
print(api.listModes())

#print(api.selectPreset(1))
#print(api.state(1))
#print(api.playControl(1))
