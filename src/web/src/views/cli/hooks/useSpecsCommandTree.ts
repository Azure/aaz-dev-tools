import { useCallback, useRef } from "react";
import { cliApi } from "../../../services";

export interface CLISpecsHelp {
  short: string;
  lines?: string[];
}

export interface CLISpecsResource {
  plane: string;
  id: string;
  version: string;
  subresource?: string;
}

export interface CLISpecsCommandExample {
  name: string;
  commands: string[];
}

export interface CLISpecsCommandVersion {
  name: string;
  stage?: string;
  resources: CLISpecsResource[];
  examples?: CLISpecsCommandExample[];
}

export interface CLISpecsCommand {
  names: string[];
  help: CLISpecsHelp;
  versions: CLISpecsCommandVersion[];
}

const retrieveCommand = async (names: string[]): Promise<CLISpecsCommand> => {
  return await cliApi.getSpecsCommand(names);
};

const retrieveCommands = async (namesList: string[][]): Promise<CLISpecsCommand[]> => {
  return await cliApi.retrieveCommands(namesList);
};

export const useSpecsCommandTree = (): ((namesList: string[][]) => Promise<CLISpecsCommand[]>) => {
  const commandCache = useRef(new Map<string, Promise<CLISpecsCommand>>());

  const fetchCommands = useCallback(
    async (namesList: string[][]) => {
      const promiseResults = [];
      const uncachedNamesList = [];
      for (const names of namesList) {
        const cachedPromise = commandCache.current.get(names.join("/"));
        if (!cachedPromise) {
          uncachedNamesList.push(names);
        } else {
          promiseResults.push(cachedPromise);
        }
      }
      if (uncachedNamesList.length === 0) {
        return await Promise.all(promiseResults);
      } else if (uncachedNamesList.length === 1) {
        const commandPromise = retrieveCommand(uncachedNamesList[0]);
        commandCache.current.set(uncachedNamesList[0].join("/"), commandPromise);
        return await Promise.all(promiseResults.concat(commandPromise));
      } else {
        const uncachedCommandsPromise = retrieveCommands(uncachedNamesList);
        uncachedNamesList.forEach((names, idx) => {
          commandCache.current.set(
            names.join("/"),
            uncachedCommandsPromise.then((commands) => commands[idx]),
          );
        });
        return (await Promise.all(promiseResults)).concat(await uncachedCommandsPromise);
      }
    },
    [commandCache],
  );
  return fetchCommands;
};
