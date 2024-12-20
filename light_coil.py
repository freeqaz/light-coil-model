import datetime
import json
import math

from build123d import *
from ocp_vscode import *

MM = 1

DEBUG_MODE = False
# Can be 'coil' or 'bar'
GENERATED_SHAPE = 'coil'
# GENERATED_SHAPE = 'bar'
# short
# number_of_coils = 32
# mid-length
# number_of_coils = 36
# long
# number_of_coils = 38
# TJ
number_of_coils = 46

layer_height_small = 0.18 * MM
layer_height_medium = 0.2 * MM
layer_height_06 = 0.24 * MM
layer_height_08 = 0.34 * MM
# layer_height_large = 0.3 * MM

# 0.8mm nozzle
layer_width = 0.82 * MM
# 0.6mm nozzle
# layer_width = 0.62 * MM
# 0.4mm nozzle
# layer_width = 0.42 * MM

# PC gap
# gap_modifier_small = 2.3
# PETG gap
gap_modifier_small = 2.5
# PETG-CF gap
# gap_modifier_smaller = 1.5
# gap_modifier_small = 1.75
# gap_modifier_big = 2.0
# gap_modifier_bigger = 2.25
# gap_modifier_biggest = 2.5

# variations for both of these
# Hardcoded for 0.8mm nozzle
# TODO: Tweak these for 0.4mm and 0.6mm nozzles
wide_width = 0.82 * 7
narrow_width = 0.82 * 6

normal_height = 24
# coil_diameter = 85.3
coil_diameter = 84.6
# for griffin's big hands
# coil_diameter = 87.5
# for nova's small hands
# coil_diameter = 80

# Size of the hole in the coil
cutout_height = 1.6 * MM
bottom_cutout_size_small = 1 * MM
bottom_cutout_size_medium = 1.2 * MM
bottom_cutout_size_large = 1.4 * MM

# Not used for print configs
length_debug = 30.0

class LightCoilPrintConfig:
    gap_modifier: float
    width_units: int
    height_units: int
    layer_height: float
    layer_width: float
    coil_width: float
    number_of_coils: int
    cutout_height: float
    bottom_cutout_size: float
    output_name: str

    def __init__(
            self,
            gap_modifier,
            width_units,
            height_units,
            layer_height,
            layer_width,
            coil_width,
            number_of_coils,
            cutout_height,
            bottom_cutout_size,
            output_name
    ):
        self.gap_modifier = gap_modifier
        self.width_units = width_units
        self.height_units = height_units
        self.layer_height = layer_height
        self.layer_width = layer_width
        self.coil_width = coil_width
        self.number_of_coils = number_of_coils
        self.cutout_height = cutout_height
        self.bottom_cutout_size = bottom_cutout_size
        self.output_name = output_name

    # JSON serialize function
    def __dict__(self):
        return {
            'gap_modifier': self.gap_modifier,
            'width_units': self.width_units,
            'height_units': self.height_units,
            'layer_height': self.layer_height,
            'layer_width': self.layer_width,
            'coil_width': self.coil_width,
            'number_of_coils': self.number_of_coils,
            'cutout_height': self.cutout_height,
            'bottom_cutout_size': self.bottom_cutout_size,
            'output_name': self.output_name
        }


def get_print_configs():
    # Generate the print configurations
    print_configs = []
    # The gap (2x layer height) had best adhesion during testing.
    for gap_modifier in [
        # gap_modifier_smaller,
        gap_modifier_small,
        # gap_modifier_big,
        # gap_modifier_bigger,
        # gap_modifier_biggest
    ]:
        for width_units in [
            wide_width,
            # narrow_width
        ]:
            for height_units in [normal_height]:
                for layer_height in [layer_height_08]:
                    for bottom_cutout_size in [
                        0,
                        # bottom_cutout_size_small, bottom_cutout_size_medium, bottom_cutout_size_large
                        ]:
                        current_date_with_hour = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        slinky_config = LightCoilPrintConfig(
                            gap_modifier,
                            width_units,
                            height_units,
                            layer_height,
                            layer_width,
                            coil_diameter * MM,
                            number_of_coils,
                            cutout_height,
                            bottom_cutout_size,
                            f"generated/{current_date_with_hour}_{GENERATED_SHAPE}__{number_of_coils}c_{layer_height}h_{layer_width}mm_{width_units}w_{normal_height}h_{gap_modifier}x.3mf"
                        )
                        print_configs.append(slinky_config)
                        if (DEBUG_MODE == False):
                            # Serialize config to JSON file
                            with open(f"generated/json/{current_date_with_hour}_{GENERATED_SHAPE}__{number_of_coils}c_{layer_height}h_{layer_width}mm_{width_units}w_{normal_height}h_{gap_modifier}x.json", 'w') as f:
                                f.write(json.dumps(slinky_config.__dict__(), indent=4))
    return print_configs


def generate_part(config):
    # Unpack config variables
    gap_modifier = config.gap_modifier
    width_units = config.width_units
    height_units = config.height_units
    layer_height = config.layer_height
    layer_width = config.layer_width
    coil_width = config.coil_width
    number_of_coils = config.number_of_coils
    cutout_height = config.cutout_height
    bottom_cutout_size = config.bottom_cutout_size

    # Calculate size_modifier based on layer_height
    size_modifier = 0.12 / layer_height

    # Calculate derived variables
    height = math.ceil(height_units * size_modifier) * layer_height * MM
    width = width_units * MM #math.ceil(width_units) * layer_width * MM

    print(f"height: {height}, width: {width}")

    # Printing parameters
    coil_spacer = layer_height * gap_modifier

    # Parameters for the coil
    coil_radius = coil_width / 2  # Radius of the coil
    turns = 1  # Generate only a single turn (faster and easier to debug)
    pitch = height + coil_spacer  # Distance between consecutive loops
    coil_height = turns * pitch  # Total height of the coil

    # with BuildPart() as fiber_optic_holder:
    #     with BuildSketch() as triangle_sketch:
    #         # Create an equilateral triangle with sides of 5mm
    #         triangle_radius = 5 / (2 * math.sin(math.pi / 3))
    #         RegularPolygon(radius=triangle_radius, side_count=3)
    #         # Create a hexagonal hole in the middle
    #         RegularPolygon(radius=1.5 / 2, side_count=6, mode=Mode.SUBTRACT)
    #     # Extrude the 2D triangle to a 3D shape of 10mm height
    #     extrude(amount=5 * MM)

    # show(
    #     fiber_optic_holder,
    #     axes=True,
    #     axes0=True,
    #     grid=(True, True, True),
    #     ticks=25,
    #     transparent=True
    # )
    with BuildPart() as light_coil_ring:
        if GENERATED_SHAPE == 'coil':
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

        slinky_start = Plane.ZY

        if GENERATED_SHAPE == 'coil':
            # Positions the block at the start of the coil
            slinky_start = Plane(origin=helix @ 0, z_dir=helix % 0)
            slinky_end = Plane(origin=helix @ 1, z_dir=helix % 1)

        # switch based on GENERATED_SHAPE
        with BuildSketch(
            slinky_start
        ) as base_slinky:
            # OG
            # slant_offset = 1.5
            # Test
            slant_offset = 1.25

            Rectangle(width, height, rotation=90)
            # with Locations((height / 2 - cutout_height / 2, 0)):
            #     RegularPolygon(
            #         1.5 / 2,
            #         side_count=6,
            #         align=[Align.MAX, Align.CENTER],
            #         mode=Mode.SUBTRACT
            #     )
            with Locations((height / 2 * -1 + slant_offset, width / 2 * -1)):
                Rectangle(
                    2,
                    width / 2,
                    mode=Mode.SUBTRACT,
                    rotation=45,
                    align=[Align.MAX, Align.MIN]
                )
            with Locations((height / 2 * -1 + slant_offset, width / 2)):
                Rectangle(
                    2,
                    width / 2,
                    mode=Mode.SUBTRACT,
                    rotation=-45,
                    align=[Align.MAX, Align.MAX]
                )

            # Create a small cut at the center to help reduce layers binding
            # with Locations((height / 2 * -1 + bottom_cutout_size, 0)):
            #     Rectangle(
            #         bottom_cutout_size,
            #         bottom_cutout_size,
            #         mode=Mode.SUBTRACT,
            #         rotation=-45,
            #         align=[Align.MAX, Align.MAX]
            #     )

        if GENERATED_SHAPE == 'coil':
            # Makes the 2D shape into a coil
            sweep(
                # Required to make the coil "straight" as it spirals
                is_frenet=True,
            )

        if GENERATED_SHAPE == 'bar':
            extrude(
                amount=length_debug
            )

    # Stack the coils
    with BuildPart() as light_coil:
        stack_height = number_of_coils if GENERATED_SHAPE == 'coil' else 3
        for i in range(stack_height):
            with Locations((0, 0, i * pitch)):
                add(light_coil_ring.part)

        # coil_offset = 2.8
        coil_offset = 3.2

        if GENERATED_SHAPE == 'coil':
            # Add a spacer at the bottom of the coil
            with Locations((0, 0, 0)):
                Cylinder(
                    height=height,
                    radius=coil_radius + coil_offset,
                    mode=Mode.ADD
                )

                Cylinder(
                    height=height,
                    radius=coil_radius - width + coil_offset - 0.2,
                    mode=Mode.SUBTRACT
                )

            # Delete a cutout at the start of the coil
            with Locations(slinky_start.location.position - (0, 0, 0)):
                Box(
                    0.4,
                    width + 2,
                    height + 1.125,
                    mode=Mode.SUBTRACT,
                    rotation=(20, -10, 70),
                )

            top_spacer = 0.1

            # Add a spacer at the top of the coil
            with Locations((0, 0, number_of_coils * pitch - top_spacer)):
                Cylinder(
                    height=height + top_spacer * 2,
                    radius=coil_radius + coil_offset,
                    mode=Mode.ADD
                )

                Cylinder(
                    height=height + top_spacer * 2,
                    radius=coil_radius - width + coil_offset - 0.2,
                    mode=Mode.SUBTRACT
                )

            # Delete a cutout at the end of the coil
            with Locations(
                    slinky_end.location.position +
                    (0, 0, number_of_coils * pitch - pitch - top_spacer / 2)
            ):
                Box(
                    0.44,
                    width + 2.2,
                    height + 1 + top_spacer * 2,
                    mode=Mode.SUBTRACT,
                    rotation=(20, -10, 70),
                    )

    return config, light_coil


def export_shape(build_part, file_name):
    build_part.part.color = Color("blue")
    build_part.part.label = "blue"

    exporter = Mesher()
    exporter.add_shape(
        build_part.part,
        # linear_deflection=0.1,
        part_number="light-coil",
        # uuid_value='0c6717c9-8fc9-41c9-8519-d0d5984f6e95'
    )
    exporter.add_meta_data(
        name_space="custom",
        name=file_name,
        value="hello world",
        metadata_type="str",
        must_preserve=False,
    )
    exporter.add_code_to_metadata()
    exporter.write(file_name)


# Generate and export parts based on configurations
print_configs = get_print_configs()
for config in print_configs:
    config, build_part = generate_part(config)
    if DEBUG_MODE:
        show(
            build_part,
            axes=True,
            axes0=True,
            grid=(True, True, True),
            ticks=25,
            transparent=True
        )
    if DEBUG_MODE == False:
        export_shape(build_part, config.output_name)
