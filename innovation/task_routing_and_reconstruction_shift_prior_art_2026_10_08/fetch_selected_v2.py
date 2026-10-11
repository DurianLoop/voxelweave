"""New output attempt and read-only resource guard; original failed source retained."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
import fetch_selected as runner

def main():
    resources=resource_guard(); runner.OUT=HERE/'primary_attempt02'; original=runner.base.new
    def write(path,value):
        if path.name=='receipt.json':
            value['source_bindings'].extend(runner.base.entry(p) for p in (Path(__file__),HERE/'NETWORK_ATTEMPT02.md',ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py'))
            value.update(resources_before=resources,resources_after=resource_guard(),network_attempt=2,
                         attempt01_failed_source_and_receipt_retained=True,TLS_verification_disabled=False)
        return original(path,value)
    runner.base.new=write
    return runner.main()
if __name__=='__main__':raise SystemExit(main())
