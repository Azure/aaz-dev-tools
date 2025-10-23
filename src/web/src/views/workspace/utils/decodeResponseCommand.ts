import { DecodeArgs } from "./decodeArgs";
import type { Command, ResponseCommand } from "../interfaces";

const DecodeResponseCommand = (command: ResponseCommand): Command => {
  let cmd: Command = {
    id: "command:" + command.names.join("/"),
    names: command.names,
    help: command.help,
    stage: command.stage ?? "Stable",
    examples: command.examples,
    outputs: command.outputs,
    resources: command.resources,
    version: command.version,
  };

  if (command.confirmation) {
    cmd.confirmation = command.confirmation;
  }

  if (command.argGroups) {
    cmd = {
      ...cmd,
      ...DecodeArgs(command.argGroups!),
    };
  }

  return cmd;
};

export { DecodeResponseCommand };
