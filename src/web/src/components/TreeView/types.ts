export type CustomData = {
  hasChildren: boolean;
  type: string;
};

export type CheckData = {
  type: string;
  currVersion?: string;
  versions?: string[];
};
