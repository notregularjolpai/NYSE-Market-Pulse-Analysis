"""Verify historical metrics & provenance; fail closed on synthetic inputs."""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from marketpulse.quality import verify_saved_run

if __name__ == '__main__':
    validation=verify_saved_run(ROOT/'data/processed/adjusted_close.csv',ROOT/'outputs/market/performance_metrics.csv',ROOT/'outputs/market/run_metadata.json')
    target=ROOT/'outputs/market/verification.json'
    target.write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
    print('Independent real-price verification: PASSED')
    print(f"Observations: {validation['run_quality']['observation_count']}, latest session: {validation['run_quality']['last_observation']}")
