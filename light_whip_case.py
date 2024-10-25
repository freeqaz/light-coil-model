from build123d import *
from ocp_vscode import *
from bd_warehouse.thread import IsoThread

MM = 1

# 18650 dimensions
length = 65 * MM
diameter = 18 * MM

# Board dimensions
board_width = 30.2 * MM
board_height = 70.0 * MM

# Light whip head dimensions
fiber_head_fibers_diameter = 15 * MM
fiber_head_fibers_tolerance = 2 * MM
fiber_head_outer_diameter = 26.8 * MM
fiber_head_height = 12.17 * MM
fiber_head_tolerance = 0.5 * MM

led_funnel_height = 12.0 * MM
led_funnel_height_tolerance = 1 * MM

# Enclosure dimensions
enclosure_thickness = 5.0 * MM
thread_radius = 2 * MM
thread_tolerance = 0.2 * MM

# LED dimensions
led_width = 8.0 * MM
led_height = 9.0 * MM
led_tolerance = 0.5 * MM
led_total_width = 14.8 * MM

with BuildPart() as whip_head_enclosure:
    cylinder_interior_height = fiber_head_height + fiber_head_tolerance
    cylinder_interior_radius = fiber_head_outer_diameter / 2 + fiber_head_tolerance / 2

    # Outer cylinder of the enclosure
    head_enclosure = Cylinder(
        height=cylinder_interior_height + enclosure_thickness,
        radius=cylinder_interior_radius + enclosure_thickness + thread_radius,
    )

    with Locations(head_enclosure.faces().sort_by(Axis.Z)[0]):
        # Creates the interior of the enclosure
        interior = Cylinder(
            height=cylinder_interior_height,
            radius=cylinder_interior_radius,
            mode=Mode.SUBTRACT,
            align=[Align.CENTER, Align.CENTER, Align.MAX]
        )

    # Cutout for the fiber head
    with Locations(head_enclosure.faces().sort_by(Axis.Z)[-1]):
        Cylinder(
            height=enclosure_thickness * 2,
            radius=fiber_head_fibers_diameter / 2 + fiber_head_fibers_tolerance,
            mode=Mode.SUBTRACT,
        )

    led_spacer_height = led_funnel_height + led_funnel_height_tolerance

    # Added space for the LED funnel
    with Locations(interior.faces().sort_by(Axis.Z)[0]):
        spacer = Cylinder(
            height=led_spacer_height,
            radius=cylinder_interior_radius + enclosure_thickness + thread_radius,
            mode=Mode.ADD,
            align=[Align.CENTER, Align.CENTER, Align.MIN]
        )

    # Cutout for the LED funnel, offset from by the spacer
    with Locations(interior.faces().sort_by(Axis.Z)[0]):
        # Cone(
        #     height=led_funnel_height,
        #     top_radius=cylinder_interior_radius,
        #     bottom_radius=led_height / 2 + led_tolerance,
        #     rotation=(0, 0, 0),
        #     mode=Mode.SUBTRACT,
        # )
        led_cutout = Cylinder(
            height=led_spacer_height,
            radius=cylinder_interior_radius + thread_radius,
            mode=Mode.SUBTRACT,
            align=[Align.CENTER, Align.CENTER, Align.MIN]
        )

    # Threads for attaching to LED head
    with Locations(led_cutout.faces().sort_by(Axis.Z)[-1].position - (0, 0, led_spacer_height)):
        IsoThread(
            external=False,
            major_diameter=cylinder_interior_radius * 2 + thread_radius * 2 + thread_tolerance / 2,
            pitch=3.5 * MM,
            length=led_spacer_height - 5 * MM,
            # align=[Align.CENTER, Align.CENTER, Align.MAX]
        )


with BuildPart() as whip_led_head:
    # LED funnel
    # Connects with threads into the whip head
    # Has a "cone" that acts as a flashlight reflector (will be painted silver)
    # Threads are female
    # Has a small hole for the LED to shine through at the bottom of the cone.

    # Compute necessary dimensions
    cylinder_interior_radius = fiber_head_outer_diameter / 2 + fiber_head_tolerance / 2 - 0.35
    thread_radius = 2 * MM
    thread_tolerance = 0.2 * MM
    major_diameter = cylinder_interior_radius * 2 + thread_radius * 2 - thread_tolerance / 2
    pitch = 3.5 * MM
    thread_length = led_funnel_height + led_funnel_height_tolerance + 2 * MM

    outer_radius = cylinder_interior_radius + thread_radius
    height = 20.0 * MM

    with Locations((0, 0, -22)):
        # Create the main body
        body = Cylinder(
            height=led_funnel_height,
            radius=outer_radius,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    # Subtract internal threads from the top
    with Locations(body.faces().sort_by(Axis.Z)[-1].position):
        thread = IsoThread(
            external=False,
            major_diameter=major_diameter,
            pitch=pitch,
            length=thread_length,
            hand="right",
            end_finishes=("raw", "raw"),
            mode=Mode.SUBTRACT,
        )

    # Create the cone that acts as a reflector
    cone_height = height - thread_length + 6 * MM  # Leave 1 mm wall at the bottom
    cone_top_radius = major_diameter / 2 - 3  # Inner diameter at the top of the cone
    cone_bottom_radius = (led_width / 2) + led_tolerance  # Small hole at the bottom

    # The cone needs to be subtracted from the body
    with Locations(body.faces().sort_by(Axis.Z)[-1]):
        led_cone = Cone(
            height=cone_height,
            bottom_radius=cone_top_radius,
            top_radius=cone_bottom_radius,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            rotation=(180, 0, 0),
            mode=Mode.SUBTRACT
        )

    # Create the small hole at the bottom of the cone for the LED to shine through
    led_hole_radius = (led_width / 2) + led_tolerance  # 4.0 * MM + 0.5 * MM = 4.5 * MM

    with Locations(led_cone.faces().sort_by(Axis.Z)[0]):
        Cylinder(
            height=1 * MM,
            radius=led_hole_radius,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT
        )


show(
    [whip_led_head, whip_head_enclosure],
    axes=True,
    axes0=True,
    grid=(True, True, True),
    ticks=25,
    transparent=True
)
