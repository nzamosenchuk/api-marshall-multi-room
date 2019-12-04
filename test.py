# Sample test to fetch all the available information
import marshall

api = marshall.MultiRoomApi('192.168.192.33')
print(api.name.get())
print(api.mac.get())
print(api.version.get())
print(api.vendorId.get())

print(api.mute.get())
print(api.volume.get())
print(api.volumeSteps.get())

print(api.groupMasterVolume.get())
print(api.groupId.get())
print(api.groupName.get())
print(api.groupState.get())

print(api.eqCustom0.get())
print(api.eqCustom1.get())

print(api.currentPreset.get())

print(api.playStatus.get())
print(api.playCaps.get())
print(api.playDuration.get())
print(api.playImgUri.get())
print(api.playArtist.get())
print(api.playAlbum.get())
print(api.playName.get())
print(api.playPosition.get())
print(api.playShuffle.get())
print(api.playRepeat.get())
print(api.playSpotifyPlaylist.get())
print(api.playSpotifyPlaylistUri.get())

print(api.power.get())

print(api.listPresets.list())
print(api.listModes.list())

#print(api.selectPreset.set())
#print(api.state.set())
#print(api.playControl.set())
