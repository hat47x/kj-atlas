import { JA_MESSAGES, type MessageKey } from "./messages";

export function t(key: MessageKey | string, values?: Record<string, string | number>): string {
  const template: string = JA_MESSAGES[key as MessageKey] ?? key;
  if (!values) {
    return template;
  }

  return Object.entries(values).reduce((acc, [name, value]) => {
    return acc.split(`{${name}}`).join(String(value));
  }, template);
}
