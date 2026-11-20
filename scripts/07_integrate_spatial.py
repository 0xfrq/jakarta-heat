
"""Integrate Person2 inputs with strict exact-ID and numerical contracts."""
from pathlib import Path
import argparse
import pandas as pd
from person2_contracts import integrate_spatial

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=DATA)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--demographics', type=Path, help='Versioned corrected demographic estimates; legacy exports remain unchanged')
    parser.add_argument('--support', type=Path, help='Required support contract when --demographics is supplied')
    args = parser.parse_args()
    if bool(args.demographics) != bool(args.support):
        parser.error('--demographics and --support must be supplied together')
    if args.demographics:
        demo = pd.read_csv(args.demographics)
        result = integrate_spatial(pd.read_csv(args.data_dir/'grid_master.csv'),
            demo[['grid_id','population']], demo[['grid_id','pop_child','pop_elderly']],
            pd.read_csv(args.data_dir/'accessibility_grid.csv'), pd.read_csv(args.support))
    else:
        result = integrate_spatial(*[pd.read_csv(args.data_dir / f) for f in
            ['grid_master.csv', 'population_grid.csv', 'vulnerability_grid.csv', 'accessibility_grid.csv']])
    output = args.output or args.data_dir / ('spatial_features_corrected.csv' if args.demographics else 'spatial_features.csv')
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + '.partial')
    result.to_csv(partial, index=False)
    partial.replace(output)
    print(f'{len(result)} source rows; {result.park_distance_m.isna().sum()} unknown routes. Saved {output}')


if __name__ == '__main__':
    main()
