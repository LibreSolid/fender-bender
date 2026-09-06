# FENDER BENDER FILAMENT BUFFER

## Overview

<img src="docs/assets/logo.svg" align="right" width=33%>

FENDER BENDER is an open-source filament buffering system. Filament buffers are necessary for reliable operation of multi-material systems such as Prusa's MMU3 or earlier revisions of the ERCF.

The 3d modeling in this project is made possible by Build123d -- a python-based, parametric, boundary representation (BREP) modeling framework for 2D and 3D CAD. You can learn more by reading the [build123d documentation](https://build123d.readthedocs.io/en/latest/).

FENDER BENDER begins with an opinionated design for building the most effective buffering system that eliminates as much friction from the system as possible. This was done through careful measurement of resistance *all the way through the system* for hundreds of prototypes. The final reference design uses 6mm OD x 3mm ID PTFE tubing wherever possible in our internal filament passages to minimize any friction introduced by the buffering system. This attention to performance was matched by focus on creating a design that maintains a reasonable aesthetic.

We believe the reference design represents the best choices for a buffering system. However, because FENDER BENDER was built using a flexible, parametric tool, the design can easily be modified to build buffering systems representing differing opinions on design; allowing for different tubes, connectors, and bearings to be built without having to modify the Python/Build123d source code.

This flexibility comes from having as many elements as possible calculated on a few critical elements. While this approach allows for tremendous flexibility without a lot of knowledge of Python, there's no guarantee that any combination of values will work. If you're struggling to get something to work, please reach out with enough details for us to assist.

## Documentation
Complete documentation for the Fender-Bender project is maintained in the docs folder and on the [fender-bender documentation](https://fender-bender.readthedocs.io/en/latest/) site.

## Modifying the Source

The included source file relies on the build123d library. I recommend following the [build123d installation instructions](https://build123d.readthedocs.io/en/latest/installation.html).

[Fender-bender developer documentation](https://fender-bender.readthedocs.io/en/latest/developers/) will walk you through the general philosophy of the fender-bender project.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

If you're not a python developer but want to help, we can always use volunteers willing to print and test new prototypes :smile:

## License

This project is licensed under the terms of the MIT license [MIT](https://choosealicense.com/licenses/mit/)

## Simulation

`simulation/` is a [solid-node](https://pypi.org/project/solid-node/) model
of one complete Fender-Bender, assembled from the part generators in `src/`
without changing them: the model imports the upstream classes, places what
they return, repeats the channel parts, adds the bought parts, colours the
families and drives the machine. `pyproject.toml` names it
(`simulation.fender_bender:FenderBender`); the design record is under
`openspec/`.

    solid build                          # publish the model into _build/
    solid test simulation/fender_bender.py   # the whole-buffer contracts
    solid build --set filament_count=3   # a three-channel buffer

### The option built

One choice from the site's part selector, stated in `simulation/config.py`:
five filament channels (Prusa MMU3), the **standing** frame, **hex** walls,
6 mm OD x 3 mm ID PTFE tubing with **no connector**, **forward** flow, and
the **lock pin** as the frame lock. The other options remain upstream
alternatives the model does not build. Root parameters: `filament_count`,
`wheel_diameter`, `chamber_depth`, `tolerance` (the upstream fit tolerance).

### Sourced and not modelled

- Modelled from the bill of materials: the MR126 bearing (12 x 6 x 4 mm)
  in each bracket, and the 1.75 mm filament as a flexible loop in each
  chamber (a molejo shape; its depth follows the buffered slack).
- Not modelled: PTFE tubes and connectors, the wall hanger, the surface
  mount bracket, the print-in-place bearing.

### Drivers and instructions

| driver | meaning |
| --- | --- |
| `channel` | which channel `slack` and `lift` act on (0 at the -Y end) |
| `slack` | mm of filament hanging below that channel's wheel; its wheel turns with it |
| `pin_draw` | how far the lock pin is drawn out (+Y) |
| `lift` | that bracket's travel along the release path; ignored until the pin is clear of the frame |

Buttons: `Retract` / `Feed` (slack 150 / 0 mm), `Unlock` / `Lock`,
`Lift bracket` / `Seat bracket`. The timeline runs every channel through a
retract-and-feed cycle in turn.

### Environment

The model needs the upstream libraries at versions that coexist with
solid-node: `partomatic==0.7.0` (0.8 renamed the `_config` attribute the
`src/` classes use), `bd_warehouse==0.2.0` (0.3 pulls build123d 0.11 and
`cadquery-ocp-novtk`, which conflicts with the OCP build cadquery binds),
`fb-library`, `ocp_vscode`, and build123d 0.10 as solid-node pins it.

### Findings about the upstream design

Measured on the exact geometry while writing the contracts; none changes
the printed parts, all are recorded in the specs:

- The guide wall is 1.5 mm shorter than the gap between frames, so its
  click-fit bumps sit 0.65 mm off their pockets and overlap the frame by
  about 1.1 mm³ each at rest (the snap).
- The connector frame's flat sidewall cut does not locate a side wall
  laterally (free to 1.7 mm either way); the core-cut frames hold the walls.
- The bracket pocket admits no rigid interference-free release: the
  retaining rim needs 8 mm of forward shift during the tilt, the pocket's
  narrow base allows 5.8 mm. The stated path keeps the bracket body under
  the click-fit detent volume (3.5 mm³) and the cap's kiss under 1.5 mm³.
- The bracket's 0.2 mm pocket tolerance is one-sided: the rear corner of
  its lower channel block sits 0.04 mm from the frame on the +Y side.
- The lock pin has more than 2 mm of play along the frame's long axis in
  the bracket channel, though it is held to 0.3 mm vertically.
- The bracket post (6.1 mm) is a 0.05 mm-per-side press fit into the
  MR126's 6.0 mm bore; the model's bearing bore follows the post.

The whole-model interference and support-under-gravity contracts are the
framework's own; trimesh calls seven of the upstream STLs non-watertight,
and the framework now lets the mesh engine, which accepts them, judge.
