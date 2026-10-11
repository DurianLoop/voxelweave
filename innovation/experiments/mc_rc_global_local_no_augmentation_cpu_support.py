"""Use frozen legacy draws and equal source patch support; disable the whole bundle."""
from mc_rc_coverage_augmentation_draw_cpu_support import legacy_primitive, example_from_record


def no_augmentation_training_example(item, rng, step):
    # Frozen primitive consumes two integers(1); the independent preflight checks
    # equality of both resulting RNG states against original training_example.
    record = legacy_primitive(item, rng, step, {})
    return example_from_record(item, record, 'legacy_none'), record
