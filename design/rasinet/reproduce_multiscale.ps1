$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "D:\MRI\pre;D:\MRI\design"
& D:\conda\envs\MRI\python.exe -B -m rasinet.run_cross_scale_evaluation `
  --config D:\MRI\design\rasinet\configs\multiscale_primary.yaml
& D:\conda\envs\MRI\python.exe -B -m rasinet.cross_scale_paper_assets
