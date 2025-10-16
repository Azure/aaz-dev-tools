import type { CMDArg } from "./decodeArgs";

interface CMDArrayArg extends CMDArg {
  item: any;
  singularOptions?: string[];
}

interface CMDClsArg extends CMDArg {
  clsName: string;
  singularOptions?: string[];
}

interface SpliceArgOptionsStringFunction {
  (arg: CMDArg, depth: number): string;
}

const spliceArgOptionsString: SpliceArgOptionsStringFunction = (arg: CMDArg, depth: number) => {
  let optionsString = arg.options
    .map((option: string) => {
      if (depth === 0) {
        if (option.length === 1) {
          return "-" + option;
        } else {
          return "--" + option;
        }
      } else {
        return "." + option;
      }
    })
    .join(" ");

  if ((arg as CMDArrayArg).singularOptions) {
    const singularOptionString = (arg as CMDArrayArg)
      .singularOptions!.map((option: string) => {
        if (depth === 0) {
          if (option.length === 1) {
            return "-" + option;
          } else {
            return "--" + option;
          }
        } else {
          return "." + option;
        }
      })
      .join(" ");
    optionsString += ` (${singularOptionString})`;
  } else if ((arg as CMDClsArg).singularOptions) {
    const singularOptionString = (arg as CMDClsArg)
      .singularOptions!.map((option: string) => {
        if (depth === 0) {
          if (option.length === 1) {
            return "-" + option;
          } else {
            return "--" + option;
          }
        } else {
          return "." + option;
        }
      })
      .join(" ");
    optionsString += ` (${singularOptionString})`;
  }

  return optionsString;
};

export { spliceArgOptionsString };
export type { CMDArrayArg, CMDClsArg, SpliceArgOptionsStringFunction };
