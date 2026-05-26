import { randomUUID } from "node:crypto";

export type Lead = {
  id: string;
  createdAt: string;
  name?: string;
  phone?: string;
  email?: string;
  sourceChannel?: string;
  notes?: string;
};

export type LeadsStore = {
  list: () => Lead[];
  add: (lead: Omit<Lead, "id" | "createdAt">) => Lead;
};

export function createInMemoryLeadsStore(limit = 500): LeadsStore {
  const leads: Lead[] = [];
  return {
    list() {
      return [...leads].sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
    },
    add(lead) {
      const item: Lead = { ...lead, id: randomUUID(), createdAt: new Date().toISOString() };
      leads.unshift(item);
      if (leads.length > limit) leads.length = limit;
      return item;
    }
  };
}

