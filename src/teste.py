
from pyboy import PyBoy

p = PyBoy(
    "mario.gb", window_type = "SDL2"
)

p.set_emulation_speed( 0 )

with open( "state.bin", "rb" ) as f:
    p.load_state( f )

last_scroll = 0
acc = 0

while True:

    p.tick()
    
    local = p.get_memory_value(0xC202)
    scroll = p.get_memory_value(0xFF43)

    if ( scroll < last_scroll):
        acc += 256

    last_scroll = scroll

    print(local + acc + scroll)
