import math

from build123d import *
from build123d.exporters import ColorIndex
from ocp_vscode import *

MM = 1

layer_height = 0.12 * MM

wide_width = 43
narrow_width = 35

(length_debug, height, width) = (50.0, 27 * 0.12 * MM, wide_width * 0.12 * MM)

cutout_height = 1.6 * MM
cutout_bottom_width = 1.6 * MM
cutout_top_width = 0.8 * MM

cutout_pnts = [
    (width / 2 - cutout_bottom_width / 2, height / 2 - cutout_height),
    (width / 2 + cutout_bottom_width / 2, height / 2 - cutout_height),
    (width / 2 + cutout_top_width / 2, height / 2),
    (width / 2 - cutout_top_width / 2, height / 2),
]

# Printing parameters
coil_spacer = layer_height * 2

# Parameters for the coil
coil_width = 85.3 * MM
coil_radius = coil_width / 2  # Radius of the coil
wire_radius = height / 2  # Radius of the coil wire
turns = 1  # Number of turns
pitch = height + coil_spacer  # Distance between consecutive loops
coil_height = turns * pitch  # Total height of the coil

number_of_coils = 4


with BuildPart() as light_coil_ring:
    # with Locations((0, 0, -coil_spacing)):
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
        Plane(origin=helix @ 0, z_dir=helix % 0),
    ) as base_slinky:
        Rectangle(height, width)
        with Locations((height / 2 - cutout_height / 2, 0)):
            RegularPolygon(
                1.5 / 2,
                side_count=6,
                align=[Align.MAX, Align.CENTER],
                mode=Mode.SUBTRACT
            )

    # Makes the 2d shape into a coil
    sweep(
        # Required to make the coil "straight" as it spirals
        is_frenet=True,
    )

    with Locations((0, 0, 0)):
        num_steps = pitch / layer_height
        for i in range(math.ceil(num_steps)):
            theta_i = (2 * math.pi / num_steps) * i
            offset = (pitch / (2 * math.pi)) * theta_i
            # TODO: Offset it by half the width of the spacer so that it doesn't "overhang" at all on the first support
            # circumference = coil_radius * 2 * math.pi
            # offset_theta = 0.5 / circumference
            with PolarLocations(coil_radius, 1, start_angle=math.degrees(theta_i), rotate=True):
                # Calculate for each ring of the slinky
                for j in range(turns):
                    with Locations((0, 0, offset + (height / 2) + (j * pitch) + 0.06)):
                        Box(
                            1,
                            width,
                            0.12,
                            align=[Align.CENTER, Align.CENTER, Align.MIN],
                            rotation=(0, 0, 90),
                            mode=Mode.ADD
                        )

    # Delete the button of the slinky
    # with Locations((0, 0, 0)):
    #     Cylinder(
    #         height=height,
    #         radius=coil_radius + 3,
    #         mode=Mode.SUBTRACT
    #     )

    # Uncomment to view design as "block"
    # extrude(amount=length_debug)


# Stack the coils
with BuildPart() as light_coil:
    with Locations((0, 0, 0)):
        for i in range(number_of_coils):
            with Locations((0, 0, i * pitch)):
                add(light_coil_ring.part)

    # Delete the part of the slinky
    with Locations((0, 0, 0)):
        Cylinder(
            height=height,
            radius=coil_radius + 3,
            mode=Mode.SUBTRACT
        )

# light_coil = light_coil_ring

def generate_with_top_hole():
    with Locations((height / 2 - 0.4, width / 2 * -1)):
        Rectangle(
            0.4,
            width / 2 - 1,
            mode=Mode.SUBTRACT,
            align=[Align.MIN, Align.MIN]
        )
    with Locations((height / 2 - 0.4, width / 2)):
        Rectangle(
            0.4,
            width / 2 - 1,
            mode=Mode.SUBTRACT,
            align=[Align.MIN, Align.MAX]
        )
    with Locations((height / 2 * -1 + 0.8, width / 2 * -1)):
        Rectangle(
            0.8,
            width / 2,
            mode=Mode.SUBTRACT,
            rotation=30,
            align=[Align.MAX, Align.MIN]
        )
    with Locations((height / 2 * -1 + 0.8, width / 2)):
        Rectangle(
            0.8,
            width / 2,
            mode=Mode.SUBTRACT,
            rotation=-30,
            align=[Align.MAX, Align.MAX]
        )
    with Locations((height / 2 - cutout_height / 2, 0)):
        Polygon(cutout_pnts, rotation=-90, mode=Mode.SUBTRACT)


show(
    light_coil,
    axes=True,
    axes0=True,
    grid=(True, True, True),
    ticks=25,
    transparent=True
)

# light_coil = Solid.make_cone(20, 0, 50)


light_coil.color = Color("blue")
light_coil.label = "blue"

exporter = Mesher()
exporter.add_shape(
    light_coil.part,
    # linear_deflection=0.1,
    part_number="light-coil",
    # uuid_value='0c6717c9-8fc9-41c9-8519-d0d5984f6e95'
)
exporter.add_meta_data(
    name_space="custom",
    name="test_meta_data",
    value="hello world",
    metadata_type="str",
    must_preserve=False,
)
exporter.add_code_to_metadata()
exporter.write("light_coil_debug-wide_not-touching.3mf")
# exporter.write("example.stl")
print("successful export")

# exporter = ExportDXF(unit=Unit.MM)
# exporter.add_layer("Layer 1", color=ColorIndex.RED, line_type=LineType.DASHED)
# exporter.add_shape(light_coil.part, layer="Layer 1")
# exporter.write("output.dxf")

