import argparse


class New:
    """Command Line Interface"""

    def __init__(self, name):
        self.name = name

        self.args = argparse.ArgumentParser(prog=self.name)
        self.sargs = self.args.add_subparsers()

    def add(self, callback: object):
        """Add new Option"""

        parser = self.sargs.add_parser(callback.__name__.lower(), help=callback.__doc__)

        for k, v in callback.__annotations__.items():
            default = callback.__dict__.get(k, None)

            # Default Actions
            action = "store"
            required = False
            help_msg = None

            if default is None:
                required = True

            if v.__name__ == "bool":
                action = "store_true"

            if hasattr(callback, "__help__"):
                help_msg = callback.__help__.get(k, None)

            parser.add_argument(
                f"--{k}",
                default=default,
                required=required,
                help=help_msg,
                action=action,
            )

        parser.set_defaults(func=callback)

    def module(self, module: object):
        """Load Directory with Modules"""
        for i in module.__dir__():
            if i.startswith("_"):
                continue
            plug = module.__getattribute__(i)

            if not hasattr(plug, "__namespace__"):
                continue

            self.add(plug)

    def run(self):
        """Execute Cli"""
        args = self.args.parse_args()

        if not hasattr(args, "func"):
            args = self.args.parse_args(["-h"])

        opts = dict()

        for k, v in args.__dict__.items():
            if k == "func":
                continue
            if not v:
                continue
            opts[k] = v

        f = args.func(**opts)
        return f.execute()
