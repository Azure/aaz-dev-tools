export type CustomData = {
    hasChildren: boolean,
    type: string,
    allowDelete: boolean
  };

export type CheckData = {
  type: string;
  currVersion?: string;
  versions?: string[];
};
