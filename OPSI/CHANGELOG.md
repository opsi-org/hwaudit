# Changelog hwaudit

## [4.3.2.7-1] - 2026-06-10

### Changed

- refactored hwaudit installation script. Copying windows binary only if incorporated version changed (doerrer <n.doerrer@uib.de>)

## [4.3.2.6-1] - 2026-06-05

### Fixed

- fixed string operations on int value in getHardwareInformationFromWMI (doerrer <n.doerrer@uib.de>)

## [4.3.2.5-1] - 2026-06-03

### Fixed

- fixed getHardwareInformationFromRegistry in case of custom classes (doerrer <n.doerrer@uib.de>)

## [4.3.2.4-1] - 2026-05-28

### Fixed

- Fixed Problem with old windows machines (doerrer <n.doerrer@uib.de>)

## [4.3.2.3-1] - 2026-01-21

### Fixed

- Use UTC timestamps for firstSeen and lastSeen (Jan Schneider <j.schneider@uib.de>)

## [4.3.2.2-1] - 2026-01-20

### Fixed

- Fix reading SecureBoot CAs on Windows (Jan Schneider <j.schneider@uib.de>)

## [4.3.2.1-1] - 2026-01-20

### Fixed

- Fixed timeout handling (Jan Schneider <j.schneider@uib.de>)

## [4.3.2.0-1] - 2025-12-02

### Changed

- Added BIOS.UEFIBootActive, BIOS.SecureBootActive and BIOS.SecureBootWindowsCA2023 (Jan Schneider <j.schneider@uib.de>)
- Use Python 3.13 and update dependencies

## [4.3.1.0-2] - 2025-05-27

### Changed

- Added opsi-meta-data.toml and changed control to control.toml (doerrer <n.doerrer@uib.de>)

## [4.3.0.1-1] - 2025-01-22

### Changed

- Updated python packages. Reenabled win7 support (doerrer <n.doerrer@uib.de>)

## [4.3.0.0-1] - 2024-10-08

### Changed

- Update python packages (Jan Schneider <j.schneider@uib.de>)
- updated python packages, switched to python 3.11 (doerrer <n.doerrer@uib.de>)
