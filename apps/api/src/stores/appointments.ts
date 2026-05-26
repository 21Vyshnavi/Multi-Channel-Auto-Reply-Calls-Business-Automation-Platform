import { randomUUID } from "node:crypto";

export type Appointment = {
  id: string;
  createdAt: string;
  name?: string;
  phone?: string;
  email?: string;
  startAt: string;
  reason?: string;
  status: "booked" | "cancelled";
};

export type AppointmentsStore = {
  list: () => Appointment[];
  add: (appt: Omit<Appointment, "id" | "createdAt" | "status">) => Appointment;
  cancel: (id: string) => Appointment | null;
};

export function createInMemoryAppointmentsStore(limit = 500): AppointmentsStore {
  const appts: Appointment[] = [];
  return {
    list() {
      return [...appts].sort((a, b) => (a.startAt < b.startAt ? 1 : -1));
    },
    add(appt) {
      const item: Appointment = {
        ...appt,
        id: randomUUID(),
        createdAt: new Date().toISOString(),
        status: "booked"
      };
      appts.unshift(item);
      if (appts.length > limit) appts.length = limit;
      return item;
    },
    cancel(id) {
      const idx = appts.findIndex((a) => a.id === id);
      if (idx === -1) return null;
      appts[idx] = { ...appts[idx], status: "cancelled" };
      return appts[idx];
    }
  };
}

