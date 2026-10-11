# QIN prostate repeat-T2 source: frozen header-only pilot

Frozen before downloading the two selected DICOM series or decoding any image pixels. This is a **source eligibility** study, not a brain-model external validation or an original-acquisition causal experiment.

## Official source and fixed selection

Use TCIA [QIN-PROSTATE-Repeatability](https://www.cancerimagingarchive.net/collection/qin-prostate-repeatability/), DOI `10.7937/K9/TCIA.2018.MR1CKGND`, Version 3 public collection, CC BY 4.0 plus TCIA usage restrictions. The official page says 15 patients had baseline/repeat prostate mpMRI within two weeks; scanner hardware/software settings were held similar within patient, including T2-weighted axial imaging. Obtain and archive the raw official `getSeries?Collection=QIN-PROSTATE-Repeatability` JSON and its SHA-256.

Select only `PatientID=PCAMPMRI-00001`, `Modality=MR`, `SeriesDescription=T2 Weighted Axial`, `ImageCount>=24`, ordered by StudyDate then SeriesInstanceUID. The official first-page metadata identifies exactly two series:

- `1.3.6.1.4.1.14519.5.2.1.3671.4754.983460207615355998147518323000` (StudyDate 1994-06-20, 30 images).
- `1.3.6.1.4.1.14519.5.2.1.3671.4754.609837242670719860929372097937` (StudyDate 1994-07-02, 30 images).

Use official NBIA `getImage?SeriesInstanceUID=...` to download just these two DICOM ZIPs under `innovation/data/qin_prostate_repeat_t2/`, recording bytes and SHA-256. Do not download other series, segmentations or derived measurements. Never deserialize PixelData in this pilot; call `pydicom.dcmread(..., stop_before_pixels=True)` and record no private tags, names, birth dates or full UIDs in the public-facing report.

## Header qualification and stopping rule

For every DICOM object, count SOPInstanceUID uniqueness and read only public technical tags: PatientID/StudyInstanceUID/SeriesInstanceUID only for matching (hash or abbreviate in reports), StudyDate, AcquisitionDate/Time, SeriesDate/Time, ImageType, MRAcquisitionType, SequenceName/ScanningSequence, Rows/Columns, PixelSpacing, SliceThickness, SpacingBetweenSlices, ImageOrientationPatient, ImagePositionPatient, EchoTime, RepetitionTime and InstanceNumber. Report missingness explicitly. Sort planes by projection onto the row/column cross-product; require unique physical centers and orientation within each series. Require both ZIPs to contain exactly the expected 30 nonpixel DICOM headers, different study and series UIDs, nonidentical study dates, identical matrix and pixel spacing within 1e-3 mm, orientation within 1e-4, TR/TE within 5%, and center grid matching after sorted one-to-one pairing to at most 0.5 mm in all three coordinates. These strict thresholds are only a screen for an exact-plane identity design, not a clinical registration rule.

List each failed condition and the maximum center displacement. If any condition fails, **do not** replace the patient, loosen tolerances or decode pixels in this pilot. An `ORIGINAL/PRIMARY` and 2D header plus separate studies would strengthen independent-acquisition provenance, but still not prove unchanged anatomy, motion-free registration or identical reconstruction processing. A passing header gate would justify a separate, prospectively frozen pixel/registration protocol; it would not authorize immediate target-pixel scoring or incorporation into the current brain T2 manuscript.
