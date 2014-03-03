import time
import mcpi.block
import mcpi.minecraft
import pifacedigitalio


TNT_START_X, TNT_START_Y, TNT_START_Z = 0, 0, 0
TNT_END_X, TNT_END_Y, TNT_END_Z = 3, 3, 3

TNT_FUSE = 4
RELAY_ON_TIME = 5


def activate_tnt(event):
    mc.setBlocks(TNT_START_X,
                 TNT_START_Y,
                 TNT_START_Z,
                 TNT_END_X,
                 TNT_END_Y,
                 TNT_END_Z,
                 mcpi.block.TNT.id,
                 1)  # sets data to 1 so that TNT explodes!
    global tnt_activated
    tnt_activated = True
    mc.postToChat("TNT activated!")
    event.chip.output_pins[7].turn_on()  # turn button light on


def tnt_is_still_there():
    """Returns True is the TNT is still there, False otherwise."""
    for x in range(TNT_END_X):
        for y in range(TNT_END_Y):
            for z in range(TNT_END_Z):
                b = mc.getBlockWithData(x, y, z)
                if b.id != mcpi.block.TNT.id:
                    print "Uh-oh, ({},{},{}) had id:{}".format(x, y, z, b.id)
                    return False
    else:
        return True


if __name__ == '__main__':
    global mc
    mc = mcpi.minecraft.Minecraft.create()

    global pfd
    pfd = pifacedigitalio.PiFaceDigital()
    pfd.output_port.all_off()

    # air -- clear and area (coordinated are two corners of a cuboid)
    mc.setBlocks(-20, 0, -20, 20, 20, 20, mcpi.block.AIR.id)
    # ground
    mc.setBlocks(-20, -20, -20, 20, 0, 20, mcpi.block.DIRT.id)
    # build a BIG bookshelf!
    mc.setBlocks(0, 0, 0, 20, 20, 20, mcpi.block.BOOKSHELF.id)
    # TNT!!!!!!!
    mc.setBlocks(TNT_START_X,
                 TNT_START_Y,
                 TNT_START_Z,
                 TNT_END_X,
                 TNT_END_Y,
                 TNT_END_Z,
                 mcpi.block.TNT.id)

    global tnt_activated
    tnt_activated = False
    # start listening for the *activate* button press
    listener = pifacedigitalio.InputEventListener(pfd)
    listener.register(0, pifacedigitalio.IODIR_FALLING_EDGE, activate_tnt)
    listener.activate()
    mc.postToChat("Press button 0 to activate TNT")

    # check for tnt to not be tnt
    try:
        while True:
            if tnt_activated and not tnt_is_still_there():
                time.sleep(TNT_FUSE)
                print "KA-BOOM!"
                pfd.relays[0].turn_on()  # EXPLOSION! KA-POW!
                time.sleep(RELAY_ON_TIME)
                pfd.relays[0].turn_off()
                pfd.output_pins[7].turn_off()  # turn off the button light
                break
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print "KeyboardInterrupt"

    listener.deactivate()
