"""Wrapper to perform both the fast retrain and optional hyperparameter search.

Usage:
    python m15_run_full_retrain.py [--trials N]

- "fast" retrain will fit models with default XGB parameters (via
  `14_retrain_models.py`).
- if --trials is provided and greater than zero the script then invokes the
  optimizer module (`9_v3_hyper_optimizer.py`) with the given number of
  trials.  The optimizer will overwrite the models when finished.

This lets you kick off a quick rebuild and then follow up with a longer
search without having to run two separate commands.
"""
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Run quick retrain then optimizer")
    parser.add_argument('--trials', type=int, default=0,
                        help='number of optuna trials to run (0 skips optimizer)')
    parser.add_argument('--rebuild', action='store_true',
                        help='rebuild the market snapshot before training')
    args = parser.parse_args()

    if args.rebuild:
        print("=== rebuilding market snapshot ===")
        try:
            subprocess.run([sys.executable, 'm13_rebuild_snapshot.py'], check=True)
        except subprocess.CalledProcessError as exc:
            print("snapshot rebuild failed with code", exc.returncode)
            sys.exit(exc.returncode)

    print("=== quick retrain ===")
    try:
        subprocess.run([sys.executable, 'm14_retrain_models.py'], check=True)
    except subprocess.CalledProcessError as exc:
        print("retrain_models.py exited with code", exc.returncode)
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        print("Quick retrain interrupted by user")
        sys.exit(1)

    if args.trials > 0:
        print("\n=== hyperparameter search ===")
        try:
            subprocess.run([sys.executable, 'm9_v3_hyper_optimizer.py',
                            '--trials', str(args.trials)], check=True)
        except subprocess.CalledProcessError as exc:
            print("optimizer exited with code", exc.returncode)
            sys.exit(exc.returncode)
        except KeyboardInterrupt:
            print("Hyperparameter search interrupted by user")
            sys.exit(1)

    print("All training steps completed.")


if __name__ == '__main__':
    main()
