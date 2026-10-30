import toast from "react-hot-toast";
import { parseApiError } from "./errorHandler";

/** Toast for a failed background action. `what` says what failed ("Couldn't load your
 *  conversations."); the rest comes from parseApiError. Toasts sharing an id replace
 *  each other, so a failure that repeats does not stack up. */
export function notifyError(error, what, id = what) {
  const { title, guidance } = parseApiError(error);
  toast.error(`${what} ${title}. ${guidance}`, { id });
}

/** A missing session is expected (deleted, or created in another browser). */
export const isNotFound = (error) => error?.status === 404;
