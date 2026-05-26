import type { InboxItem } from "../types.js";

export type InboxStore = {
  add: (item: InboxItem) => void;
  list: () => InboxItem[];
};

export function createInMemoryInboxStore(limit = 200): InboxStore {
  const items: InboxItem[] = [];
  return {
    add(item) {
      items.unshift(item);
      if (items.length > limit) items.length = limit;
    },
    list() {
      return items;
    }
  };
}

