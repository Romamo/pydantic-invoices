# Changelog

## 1.4.1

- Added `TaxId` Value Object with multi-format validation via `python-stdnum` (EU VAT, UK VAT, US EIN, AU ABN) and a generic alphanumeric fallback.
- Applied `TaxId` to `tax_id` fields in `CompanyBase`, `CompanyUpdate`, `ClientBase`, and `ClientUpdate` schemas.
- Simplified `InvoiceBase.issue_date` to use `date` instead of `datetime`, removing the now-redundant `parse_issue_date` validator.

## 1.3.1

- Relaxed `postal_code` validation in `Company` schema to support integer inputs (e.g. from YAML).
- Updated release workflows.


## 1.3.0

- Added `py.typed` marker.
- Updated repository interfaces (`ClientRepository` searches).
- Added system diagram documentation.

## 1.2.2

- Added smoke test.
- Added GitHub Actions CI workflow.

## 1.2.1

- Added release workflow (`release_new_version`).
- Added GitHub Actions workflow for publishing.
- Fixed repository URLs in `pyproject.toml`.
- Refactored tests structure.

## 1.2.0

- Initial release with tag.
