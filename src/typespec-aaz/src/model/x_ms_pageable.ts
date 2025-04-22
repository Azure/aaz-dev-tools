export type XmsPageable = {
  itemName?: string;
  nextLinkName: string;
  operationName?: string; // TODO: # Optional (default: <operationName>Next). Specifies the name of the operation for retrieving the next page.
};
