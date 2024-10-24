from build123d import *
from ocp_vscode import *
from bd_warehouse.fastener import IsoThread

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

led_funnel_height = 8.0 * MM

# Enclosure dimensions
enclosure_thickness = 5.0 * MM

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
        height=cylinder_interior_height + enclosure_thickness * 2,
        radius=cylinder_interior_radius + enclosure_thickness,
    )

    # Creates the interior of the enclosure
    interior = Cylinder(
        height=cylinder_interior_height,
        radius=cylinder_interior_radius,
        mode=Mode.SUBTRACT,
    )

    # Cutout for the fiber head
    with Locations(head_enclosure.faces().sort_by(Axis.Z)[-1]):
        Cylinder(
            height=enclosure_thickness * 2,
            radius=fiber_head_fibers_diameter / 2 + fiber_head_fibers_tolerance,
            mode=Mode.SUBTRACT,
        )

    # Added space for the LED funnel
    with Locations(interior.faces().sort_by(Axis.Z)[0]):
        spacer = Cylinder(
            # Not sure why I need this specific offset
            height=led_funnel_height - 2,
            radius=cylinder_interior_radius + enclosure_thickness,
            mode=Mode.ADD,
        )

    # Cutout for the LED funnel, offset from by the spacer
    with Locations(spacer.faces().sort_by(Axis.Z)[0].position - (0, 0, led_funnel_height / 2)):
        # Cone(
        #     height=led_funnel_height,
        #     top_radius=cylinder_interior_radius,
        #     bottom_radius=led_height / 2 + led_tolerance,
        #     rotation=(0, 0, 0),
        #     mode=Mode.SUBTRACT,
        # )
        led_cutout = Cylinder(
            height=led_funnel_height,
            radius=cylinder_interior_radius,
            mode=Mode.SUBTRACT,
        )

    # Threads for attaching to LED head
    with Locations(led_cutout.faces().sort_by(Axis.Z)[-1].position - (0, 0, 0)):
        IsoThread(
            external=False,
            major_diameter=cylinder_interior_radius * 2,
            pitch=2.2 * MM,
            length=6 * MM,
        )




show(
    whip_head_enclosure,
    axes=True,
    axes0=True,
    grid=(True, True, True),
    ticks=25,
    transparent=True
)
