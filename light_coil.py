from build123d import *
from ocp_vscode import *

MM = 1

(length_debug, height, width, thickness) = (50.0, 3.5 * MM, 4.5 * MM, 1.5 * MM)

cutout_height = 1.5 * MM
cutout_bottom_width = 1.8 * MM
cutout_top_width = 0.8 * MM

cutout_pnts = [
    (width / 2 - cutout_bottom_width / 2, height / 2 - cutout_height),
    (width / 2 + cutout_bottom_width / 2, height / 2 - cutout_height),
    (width / 2 + cutout_top_width / 2, height / 2),
    (width / 2 - cutout_top_width / 2, height / 2),
]

# Printing parameters
coil_spacing = 4

# Parameters for the coil
coil_width = 88.3 * MM
coil_radius = coil_width / 2  # Radius of the coil
wire_radius = height / 2  # Radius of the coil wire
turns = 30  # Number of turns
pitch = height * coil_spacing  # Distance between consecutive loops
coil_height = turns * pitch  # Total height of the coil

with BuildPart() as ex8:
    with BuildLine() as coil_path:
        # Defines a coil shape
        helix = Helix(
            pitch=pitch,
            height=coil_height,
            radius=coil_radius,
            cone_angle=0,
            center=(0, 0, 0),
            direction=(0, 0, 1)  # Helix along the Z-axis
        )

    with BuildSketch(
        # Positions the block at the start of the coil
        Plane(origin=helix @ 0, z_dir=helix % 0)
    ) as ex8_sk:
        Rectangle(height, width)
        with Locations((height / 2 - thickness / 2, 0)):
            Polygon(cutout_pnts, rotation=-90, mode=Mode.SUBTRACT)        

    # Makes the 2d shape into a coil
    # sweep(
    #     # Required to make the coil "straight" as it spirals
    #     is_frenet=True,
    # )

    # Uncomment to view design as "block"
    extrude(amount=length_debug)


show(
    ex8,
    axes=True,
    axes0=True,
    grid=(True, True, True),
    ticks=25,
    transparent=True
)
