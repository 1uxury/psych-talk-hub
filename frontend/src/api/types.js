/**
 * Public read-only JSON types. Source of truth:
 * memory-bank/tech-stack.md#public-api-contract (repository root).
 * JSDoc documents the contract; it does not validate data at runtime.
 *
 * @typedef {Object} EventSummary
 * @property {number} id Integer event identity.
 * @property {string} title Non-empty title.
 * @property {string} description Optional text, empty string when absent.
 * @property {string} topic Optional text, empty string when absent.
 * @property {string} starts_at UTC ISO 8601 instant ending in Z.
 * @property {string} speaker Optional text, empty string when absent.
 * @property {boolean} is_example Whether the talk is fictional demo content.
 * @property {number} resource_count Non-negative integer association count.
 * @property {string} cover_image_url Optional HTTPS or bundled poster path; empty when absent.
 * @property {string} cover_image_alt Optional image description; empty for decorative art.
 *
 * @typedef {Object} EventReading
 * @property {number} association_id Integer EventResource identity.
 * @property {number} resource_id Integer shared Resource identity.
 * @property {string} title Non-empty shared title.
 * @property {string} authors Display string, empty when absent; authors use ; separators.
 * @property {number|null} year Integer 1–9999 or null when absent.
 * @property {string} original_url Required HTTP(S) original URL.
 * @property {string|null} doi Normalised bare DOI or null when absent.
 * @property {'research_paper'|'article'} resource_type Bibliographic type.
 * @property {'crossref'|'manual'} metadata_source Original metadata source.
 * @property {string} recommendation Current talk's text, empty when absent.
 * @property {number} display_order Signed integer, default 0; negative values allowed.
 *
 * @typedef {EventSummary & {resources: EventReading[]}} EventDetail
 * Detail readings are ordered by display_order then association_id.
 * Empty reading lists are []; no internal seed/session/admin fields are public.
 *
 * @typedef {Object} ApiError
 * @property {string} detail Non-empty safe message; errors include 404, 405 and 500.
 */

export {}
