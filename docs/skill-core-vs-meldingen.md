# Skill: Deciding What Belongs in meldingen-core vs meldingen

## Purpose
This skill provides guidelines for developers to determine whether code should be placed in `meldingen-core` (the framework-agnostic core package) or in `meldingen` (the application/framework-specific project).

---

## General Principles

### meldingen-core
- **Contains:**
  - Domain models (e.g., `Melding`, `Classification`, `AssetType`)
  - Stateless business logic and core algorithms
  - Abstract base classes, interfaces, and protocols
  - Exceptions, repositories, and managers that are not tied to any framework or infrastructure
- **Does NOT contain:**
  - Framework-specific code (e.g., FastAPI, SQLAlchemy, Typer)
  - Database, API, or UI code
  - Concrete implementations that depend on external libraries or infrastructure
- **Goal:**
  - Be reusable across different frameworks and applications
  - Remain free of infrastructure and framework dependencies

### meldingen
- **Contains:**
  - Framework bindings (e.g., FastAPI endpoints, Typer CLI commands)
  - Infrastructure and orchestration code (e.g., dependency injection, database session management)
  - Concrete implementations of repositories, adapters, and services
  - Application entrypoints, migrations, and integration with external services
- **Imports:**
  - Uses `meldingen-core` for domain logic and abstractions
- **Goal:**
  - Wire up the core logic for a specific deployment or application

---

## Edge Cases & Patterns

### Example: Location Type (WKBElement)
- **Problem:** The concept of a location belongs in the domain model (core), but the WKBElement type is implementation-specific and not available in core.
- **Guideline:**
  - Define the concept abstractly in core (e.g., as a protocol, interface, or simple type like `dict` or `tuple`).
  - Implement the concrete type (e.g., WKBElement) and its serialization/deserialization in meldingen.
  - If needed, provide hooks or interfaces in core for serialization, but do not depend on external libraries.

---

## Decision Checklist
1. **Is the code generic, stateless, and reusable across frameworks?**
   - Yes → Place in `meldingen-core`.
2. **Does the code depend on a specific framework, library, or infrastructure?**
   - Yes → Place in `meldingen`.
3. **Is the code a domain model or business rule?**
   - Yes → Place in `meldingen-core`.
4. **Is the code an adapter, repository, or service with concrete dependencies?**
   - Yes → Place in `meldingen`.
5. **Is the code an application entrypoint, migration, or CLI command?**
   - Yes → Place in `meldingen`.
6. **Is there a type or feature that is conceptually core but has implementation-specific dependencies?**
   - Abstract the concept in core; implement the concrete type in meldingen.

---

## Examples
- **meldingen-core:**
  - `class Melding(BaseModel): ...` (no framework dependencies)
  - `class ClassificationManager: ...` (stateless logic)
  - `class Location(Protocol): ...` (abstract location type)
- **meldingen:**
  - `class SQLAlchemyMeldingRepository(MeldingRepository): ...`
  - `@app.post("/meldingen") ...` (FastAPI endpoint)
  - `def main(): typer.run(...)` (CLI entrypoint)
  - `class LocationWKB(Location): ...` (concrete implementation)

---

## Review & Updates
- Review these guidelines regularly as the codebase evolves.
- For ambiguous cases, discuss with the team and update this skill as needed.
