import Marshall

api = Marshall.MultiRoomAPI('192.168.192.33')

def playPreset(preset):
    if api.power() == 0:
        api.power(1)
    api.state(1)
    api.selectPreset(preset)


#api.power(0)

playPreset(3)
#api.volume(2)
#print(api.name())
