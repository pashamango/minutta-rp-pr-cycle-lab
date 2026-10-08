"""Safe placeholder worker entrypoint used by the private launcher contract."""
import argparse
import json


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--task-id", required=True)
    p.add_argument("--source-digest", required=True)
    p.add_argument("--lease-id", required=True)
    args = p.parse_args(argv)
    print(json.dumps(vars(args), sort_keys=True))


if __name__ == "__main__":
    main()
