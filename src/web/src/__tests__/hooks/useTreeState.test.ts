import { renderHook, act } from "@testing-library/react";
import { useTreeState } from "../../views/workspace/hooks/useTreeState";
import type { Command, CommandGroup } from "../../views/workspace/interfaces";

describe("useTreeState", () => {
  const mockCommandGroupMap = {
    "group:automanage": {
      id: "group:automanage",
      names: ["automanage"],
    } as CommandGroup,
    "group:automanage/configuration-profile": {
      id: "group:automanage/configuration-profile",
      names: ["automanage", "configuration-profile"],
    } as CommandGroup,
    "group:automanage/configuration-profile/assignment": {
      id: "group:automanage/configuration-profile/assignment",
      names: ["automanage", "configuration-profile", "assignment"],
    } as CommandGroup,
    "group:storage": {
      id: "group:storage",
      names: ["storage"],
    } as CommandGroup,
    "group:storage/account": {
      id: "group:storage/account",
      names: ["storage", "account"],
    } as CommandGroup,
  };

  const mockCommandMap = {
    "command:automanage/configuration-profile/assignment/create": {
      id: "command:automanage/configuration-profile/assignment/create",
      names: ["automanage", "configuration-profile", "assignment", "create"],
    } as Command,
  };

  const mockCommandTree = [
    {
      id: "group:automanage",
      names: ["automanage"],
      canDelete: true,
      nodes: [
        {
          id: "group:automanage/configuration-profile",
          names: ["automanage", "configuration-profile"],
          canDelete: true,
          nodes: [
            {
              id: "group:automanage/configuration-profile/assignment",
              names: ["automanage", "configuration-profile", "assignment"],
              canDelete: true,
              leaves: [
                {
                  id: "command:automanage/configuration-profile/assignment/create",
                  names: ["automanage", "configuration-profile", "assignment", "create"],
                },
              ],
            },
          ],
        },
      ],
    },
    {
      id: "group:storage",
      names: ["storage"],
      canDelete: true,
      nodes: [
        {
          id: "group:storage/account",
          names: ["storage", "account"],
          canDelete: true,
        },
      ],
    },
  ];

  describe("updateExpanded with autoExpandAll", () => {
    it("should expand all command groups when autoExpandAll is true", () => {
      const { result } = renderHook(() => useTreeState(mockCommandMap, {}, mockCommandTree));

      act(() => {
        result.current.updateExpanded(mockCommandGroupMap, undefined, true);
      });

      const expandedArray = Array.from(result.current.expanded);

      // Should include all command groups
      expect(expandedArray).toContain("group:automanage");
      expect(expandedArray).toContain("group:automanage/configuration-profile");
      expect(expandedArray).toContain("group:automanage/configuration-profile/assignment");
      expect(expandedArray).toContain("group:storage");
      expect(expandedArray).toContain("group:storage/account");

      // Should include all parent paths for hierarchy
      expect(expandedArray).toContain("group:automanage");
      expect(expandedArray).toContain("group:automanage/configuration-profile");
      expect(expandedArray).toContain("group:storage");

      // Total count should be all unique paths
      expect(expandedArray).toHaveLength(5);
    });

    it("should expand all groups regardless of existing expanded state when autoExpandAll is true", () => {
      const { result } = renderHook(() => useTreeState(mockCommandMap, {}, mockCommandTree));

      // First, manually expand only one group
      act(() => {
        result.current.updateExpanded({ "group:storage": mockCommandGroupMap["group:storage"] }, undefined, false);
      });

      // Should only have storage expanded initially
      expect(Array.from(result.current.expanded)).toEqual(["group:storage"]);

      // Now call with autoExpandAll=true
      act(() => {
        result.current.updateExpanded(mockCommandGroupMap, undefined, true);
      });

      const expandedArray = Array.from(result.current.expanded);

      // Should now include ALL groups, not just storage
      expect(expandedArray).toContain("group:automanage");
      expect(expandedArray).toContain("group:automanage/configuration-profile");
      expect(expandedArray).toContain("group:automanage/configuration-profile/assignment");
      expect(expandedArray).toContain("group:storage");
      expect(expandedArray).toContain("group:storage/account");
    });

    it("should only expand new groups when autoExpandAll is false", () => {
      const initialCommandGroupMap = {
        "group:storage": mockCommandGroupMap["group:storage"],
      };

      const { result } = renderHook(() => useTreeState(mockCommandMap, initialCommandGroupMap, mockCommandTree));

      // First, expand storage (which already exists in initial map)
      act(() => {
        result.current.updateExpanded(initialCommandGroupMap, undefined, false);
      });

      // Should be empty since storage already existed in the initial map
      expect(Array.from(result.current.expanded)).toHaveLength(0);

      // Now add new groups with autoExpandAll=false
      act(() => {
        result.current.updateExpanded(mockCommandGroupMap, undefined, false);
      });

      const expandedArray = Array.from(result.current.expanded);

      // Should only include new groups (not storage since it existed before)
      expect(expandedArray).toContain("group:automanage");
      expect(expandedArray).toContain("group:automanage/configuration-profile");
      expect(expandedArray).toContain("group:automanage/configuration-profile/assignment");
      expect(expandedArray).toContain("group:storage/account"); // This is new

      // Should NOT include storage since it existed in the original commandGroupMap
      expect(expandedArray).not.toContain("group:storage");
    });

    it("should include parent paths for deeply nested groups", () => {
      const deeplyNestedMap = {
        "group:level1/level2/level3/level4": {
          id: "group:level1/level2/level3/level4",
          names: ["level1", "level2", "level3", "level4"],
        } as CommandGroup,
      };

      const { result } = renderHook(() => useTreeState(mockCommandMap, {}, mockCommandTree));

      act(() => {
        result.current.updateExpanded(deeplyNestedMap, undefined, true);
      });

      const expandedArray = Array.from(result.current.expanded);

      // Should include the group itself
      expect(expandedArray).toContain("group:level1/level2/level3/level4");

      // Should include all parent paths for proper hierarchy
      expect(expandedArray).toContain("group:level1/level2");
      expect(expandedArray).toContain("group:level1/level2/level3");
    });

    it("should preserve existing expanded state when adding new groups with autoExpandAll=true", () => {
      const { result } = renderHook(() => useTreeState(mockCommandMap, {}, mockCommandTree));

      // Start with some manual expansion
      act(() => {
        result.current.handleCommandTreeToggle(["group:storage"]);
      });

      expect(Array.from(result.current.expanded)).toEqual(["group:storage"]);

      // Now call updateExpanded with autoExpandAll=true
      act(() => {
        result.current.updateExpanded(mockCommandGroupMap, undefined, true);
      });

      const expandedArray = Array.from(result.current.expanded);

      // Should still contain the manually expanded group
      expect(expandedArray).toContain("group:storage");

      // Plus all the auto-expanded groups
      expect(expandedArray).toContain("group:automanage");
      expect(expandedArray).toContain("group:automanage/configuration-profile");
      expect(expandedArray).toContain("group:automanage/configuration-profile/assignment");
      expect(expandedArray).toContain("group:storage/account");
    });
  });

  describe("basic functionality", () => {
    it("should initialize and auto-select first group with its path expanded", () => {
      const { result } = renderHook(() => useTreeState(mockCommandMap, mockCommandGroupMap, mockCommandTree));

      // Should auto-select the first group from commandTree
      expect(result.current.selected?.id).toBe("group:automanage");

      // Should auto-expand the path to the selected group
      expect(result.current.expanded.size).toBe(1);
      expect(Array.from(result.current.expanded)).toContain("group:automanage");
    });

    it("should handle command tree toggle", () => {
      const { result } = renderHook(() => useTreeState(mockCommandMap, mockCommandGroupMap, mockCommandTree));

      act(() => {
        result.current.handleCommandTreeToggle(["group:storage", "group:automanage"]);
      });

      const expandedArray = Array.from(result.current.expanded);
      expect(expandedArray).toContain("group:storage");
      expect(expandedArray).toContain("group:automanage");
      expect(expandedArray).toHaveLength(2);
    });
  });
});
