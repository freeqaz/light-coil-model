import math

from build123d import *
from ocp_vscode import *

MM = 1

DEBUG_MODE = False
# Can be 'coil' or 'bar'
GENERATED_SHAPE = 'bar'
number_of_coils = 4

layer_height_small = 0.12 * MM
layer_height_medium = 0.2 * MM
# layer_height_large = 0.3 * MM

layer_width = 0.42 * MM
gap_modifier_small = 1
gap_modifier_big = 2

# variations for both of these
wide_width = 13
narrow_width = 10

normal_height = 27

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


def get_print_configs():
    # Generate the print configurations
    print_configs = []
    # Small gap (1x layer height) had best adhesion during testing.
    for gap_modifier in [gap_modifier_small]:
        for width_units in [wide_width, narrow_width]:
            for height_units in [normal_height]:
                for layer_height in [layer_height_small, layer_height_medium]:
                    for bottom_cutout_size in [0, bottom_cutout_size_small, bottom_cutout_size_medium, bottom_cutout_size_large]:
                        print_configs.append(
                            LightCoilPrintConfig(
                                gap_modifier,
                                width_units,
                                height_units,
                                layer_height,
                                layer_width,
                                85.3 * MM,
                                number_of_coils,
                                cutout_height,
                                bottom_cutout_size,
                                f"generated/light_{GENERATED_SHAPE}__{number_of_coils}-coils_{layer_height}h_{gap_modifier}x-gap_{width_units}-wide_{height_units}-high_{bottom_cutout_size}-bcs.3mf"
                            )
                        )
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
    width = math.ceil(width_units) * layer_width * MM

    # Printing parameters
    coil_spacer = layer_height * gap_modifier

    # Parameters for the coil
    coil_radius = coil_width / 2  # Radius of the coil
    turns = 1  # Generate only a single turn (faster and easier to debug)
    pitch = height + coil_spacer  # Distance between consecutive loops
    coil_height = turns * pitch  # Total height of the coil

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


        plane = Plane.ZY

        if GENERATED_SHAPE == 'coil':
            # Positions the block at the start of the coil
            plane = Plane(origin=helix @ 0, z_dir=helix % 0)


        # switch based on GENERATED_SHAPE
        with BuildSketch(
            plane
        ) as base_slinky:
            Rectangle(height, width)
            with Locations((height / 2 - cutout_height / 2, 0)):
                RegularPolygon(
                    1.5 / 2,
                    side_count=6,
                    align=[Align.MAX, Align.CENTER],
                    mode=Mode.SUBTRACT
                )
            with Locations((height / 2 * -1 + 1.5, width / 2 * -1)):
                Rectangle(
                    2,
                    width / 2,
                    mode=Mode.SUBTRACT,
                    rotation=45,
                    align=[Align.MAX, Align.MIN]
                )
            with Locations((height / 2 * -1 + 1.5, width / 2)):
                Rectangle(
                    2,
                    width / 2,
                    mode=Mode.SUBTRACT,
                    rotation=-45,
                    align=[Align.MAX, Align.MAX]
                )

            # Create a small cut at the center to help reduce layers binding
            with Locations((height / 2 * -1 + bottom_cutout_size, 0)):
                Rectangle(
                    bottom_cutout_size,
                    bottom_cutout_size,
                    mode=Mode.SUBTRACT,
                    rotation=-45,
                    align=[Align.MAX, Align.MAX]
                )

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
        for i in range(number_of_coils):
            with Locations((0, 0, i * pitch)):
                add(light_coil_ring.part)

        if GENERATED_SHAPE == 'coil':
            # Add a spacer at the bottom of the coil
            with Locations((0, 0, 0)):
                Cylinder(
                    height=height,
                    radius=coil_radius + 2.5,
                    mode=Mode.ADD
                )

                Cylinder(
                    height=height,
                    radius=coil_radius - width + 2.5,
                    mode=Mode.SUBTRACT
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
        break
    export_shape(build_part, config.output_name)
