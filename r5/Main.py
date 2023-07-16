from r5 import Tasks
from r5.Framework import Log
from r5.Framework import Cli

Log.setup_logger()

cli = Cli.New(name="r5")

cli.add(Tasks.Start)
cli.add(Tasks.Migration)
