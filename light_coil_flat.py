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

number_of_coils = 1

with BuildLine() as coil_path_ignored:
    upper_coil = CenterArc(
        center=(0, 0, pitch),
        radius=coil_radius,
        start_angle=350,
        arc_size=360,
    )

    upper_coil2 = CenterArc(
        center=(0, 0, pitch * 2),
        radius=coil_radius,
        start_angle=350,
        arc_size=360,
    )

with BuildPart() as light_coil_ring:


    with BuildLine() as coil_path:
        main_coil = CenterArc(
            center=(0, 0, 0),
            radius=coil_radius,
            start_angle=0,
            arc_size=350,
        )
        mid_x = coil_radius * math.cos(math.radians(354))
        mid_y = coil_radius * math.sin(math.radians(354))
        end_x = coil_radius * math.cos(math.radians(359))
        end_y = coil_radius * math.sin(math.radians(359))
        print(main_coil % 1)
        print( upper_coil % 0)
        connector = TangentArc(
            [
                main_coil @ 1,
                (mid_x, mid_y, coil_height / 2),
                # upper_coil @ 0
                # (0, 0, coil_height),
            ],
            tangent=main_coil % 1,
            # tangents=[
            #     main_coil % 1,
            #     (0, 1, 0)
            # ],
        )
        connector2 = TangentArc(
            [
                # main_coil @ 1,
                (mid_x, mid_y, coil_height / 2),
                # (0, 0, coil_height),
                upper_coil @ 1
            ],
            tangent=upper_coil % 1,
            # tangent_from_first=False,
            # tangents=[
            #     main_coil % 1,
            #     (0, 1, 0)
            # ],
        )
        #
        # JernArc(
        #     start=connector2 @ 1,
        #     radius=coil_radius,
        #     tangent=upper_coil % 0,
        #     arc_size=2,
        # )
        # # Make flush with the start of next ring
        # DoubleTangentArc(
        #     [
        #         connector2 @ 1,
        #         upper_coil @ 0
        #     ],
        #     tangent=connector2 % 1,
        #     other=upper_coil % 0
        # )

    with BuildSketch(
        # Positions the block at the start of the coil
        Plane(origin=main_coil @ 0, z_dir=main_coil % 0),
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

    # with Locations((coil_radius, 0, 0)):
    #     num_steps = pitch / layer_height
    #     for i in range(math.ceil(num_steps)):
    #         theta_i = (2 * math.pi / num_steps) * i
    #         offset = (pitch / (2 * math.pi)) * theta_i
    #         # TODO: Offset it by half the width of the spacer so that it doesn't "overhang" at all on the first support
    #         # circumference = coil_radius * 2 * math.pi
    #         # offset_theta = 0.5 / circumference
    #         with PolarLocations(coil_radius, 1, start_angle=math.degrees(theta_i), rotate=True):
    #             # Calculate for each ring of the slinky
    #             for j in range(turns):
    #                 with Locations((0, 0, offset + (height / 2) + (j * pitch) + 0.06)):
    #                     Box(
    #                         1,
    #                         width,
    #                         0.12,
    #                         align=[Align.CENTER, Align.CENTER, Align.MIN],
    #                         rotation=(0, 0, 90),
    #                         mode=Mode.ADD
    #                     )

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
    # with Locations((0, 0, 0)):
    #     Cylinder(
    #         height=height,
    #         radius=coil_radius + 3,
    #         mode=Mode.SUBTRACT
    #     )

# light_coil = light_coil_ring


show(
    light_coil,
    axes=True,
    axes0=True,
    grid=(True, True, True),
    ticks=25,
    transparent=True
)

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
exporter.write("light_coil_flat-test1.3mf")
# # exporter.write("example.stl")
print("successful export")

# exporter = ExportDXF(unit=Unit.MM)
# exporter.add_layer("Layer 1", color=ColorIndex.RED, line_type=LineType.DASHED)
# exporter.add_shape(light_coil.part, layer="Layer 1")
# exporter.write("output.dxf")

