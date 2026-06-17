import numpy as np

from mousebrainbench.data.loaders.sensorium import load_sensorium_directory


def test_load_sensorium_static_directory(tmp_path) -> None:
    root = tmp_path / "sensorium"
    (root / "data" / "images").mkdir(parents=True)
    (root / "data" / "responses").mkdir(parents=True)
    (root / "data" / "behavior").mkdir(parents=True)
    (root / "data" / "pupil_center").mkdir(parents=True)
    (root / "meta" / "trials").mkdir(parents=True)
    (root / "meta" / "neurons").mkdir(parents=True)
    for trial in range(4):
        np.save(root / "data" / "images" / f"{trial}.npy", np.full((4, 4), trial))
        np.save(root / "data" / "responses" / f"{trial}.npy", np.asarray([trial, trial + 1]))
        np.save(root / "data" / "behavior" / f"{trial}.npy", np.asarray([trial, 0, 1]))
        np.save(root / "data" / "pupil_center" / f"{trial}.npy", np.asarray([trial + 2, trial + 3]))
    np.save(root / "meta" / "trials" / "tiers.npy", np.asarray(["train", "train", "validation", "validation"]))
    np.save(root / "meta" / "trials" / "frame_image_id.npy", np.asarray([0, 1, 2, 2]))
    np.save(root / "meta" / "neurons" / "unit_ids.npy", np.asarray([10, 11]))

    table = load_sensorium_directory(root)

    assert table.modality == "static"
    assert table.n_trials == 4
    assert table.n_neurons == 2
    assert table.stimulus_features.shape == (4, 71)
    assert table.context_features.shape == (4, 5)
    assert table.stimulus_ids.tolist() == [0, 1, 2, 2]
