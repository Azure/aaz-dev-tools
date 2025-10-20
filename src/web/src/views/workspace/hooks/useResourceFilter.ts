import { useState, useCallback } from "react";

export const useResourceFilter = () => {
  const [filterText, setFilterText] = useState("");
  const [realFilterText, setRealFilterText] = useState("");

  const updateFilter = useCallback((newFilterText: string) => {
    const reg = /\{.*?\}/g;
    setFilterText(newFilterText);
    setRealFilterText(newFilterText.toLocaleLowerCase().replace(reg, "{}"));
  }, []);

  const filterResources = useCallback(
    (resources: any[]) => {
      if (realFilterText.trim().length > 0) {
        return resources.filter((resource) => resource.id.toLowerCase().indexOf(realFilterText) > -1);
      }
      return resources;
    },
    [realFilterText],
  );

  return {
    filterText,
    updateFilter,
    filterResources,
  };
};
