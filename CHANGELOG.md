# Change log
Change log for [siemcli](https://github.com/dogoncouch/siemcli)

## [Unreleased]
### Changed
- Keep database connection between consecutive entries

## [0.8-alpha] - 2018-01-10
### Changed
- `siemparse` sleeps 0.1 on no line (much less idle CPU usage)
- Update column/table names (broke backwards compatibility)
- Update magnitude logic (prioritize severity)

### Added
- `parsed_on` and `source_file` columns
- `date_stamp_utc` column
- Fractional SQL timestamps (not working with siemquery)

## [0.7.1-alpha] - 2017-09-06
### Fixed
- `siemmanage` and `siemtrigger` bugs

## [0.7-alpha] - 2017-08-31
### Added
- `siemmanage` management tool (clear/import/export)

### Changed
- Split parser UI from functions


## [0.6-alpha] - 2017-08-31
### Changed
- Split config into 2 files (db, sections)
- Update example rules
- Update helper logic


## [0.5-alpha] - 2017-08-28
### Added
- `siemparse` now parses from file or stdin
- Example visual rules
- Parse helpers for user-definable extended attributes (json string)
- Example helpers

### Changed
- Trigger rules with TimeInt of 0 automatically start as oneshot
- Updated magnitude logic
- Default rules output to same table


## [0.4-alpha] - 2017-08-26
### Fixed
- siemtrigger table creation bug

### Changed
- Added `Extended` column to event for extended attributes (JSON string)


## [0.3-alpha] - 2017-08-24
- Parsing
- Query module/CLI query tool
- Trigger module/tool
- Config file
