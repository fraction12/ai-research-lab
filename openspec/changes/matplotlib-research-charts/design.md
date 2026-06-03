## Design

Use Matplotlib because it is the common Python research-figure stack and can export vector graphics for papers while preserving a scriptable data-to-figure path.

The generator should:

- load raw benchmark JSON files directly
- compute the same summary metrics as the current chart page
- export `svg`, `pdf`, and `png` for each figure
- use a restrained research style with clear axes, legends, labels, and captions
- avoid overlapping text by reserving figure space for legends and annotations
- mark projections as projections and not measured benchmark data

The projection figure should use measured 16KB, 32KB, and 64KB Flashcache ladder data. The 128KB projection may use a simple linear fit, but the figure and docs must label it as directional.

This change does not alter benchmark data, Flashcache runtime behavior, or benchmark execution semantics.
