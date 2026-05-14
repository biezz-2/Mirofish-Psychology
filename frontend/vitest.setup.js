// Vitest: router pulls Vue views that import axios/i18n (localStorage).
globalThis.localStorage = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {},
  clear: () => {},
  key: () => null,
  length: 0
}
