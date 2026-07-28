## Using IDs In Model Dataclasses

### Status
Accepted

### Date accepted
2026-07-28

### Context
Our core models in [models.py](../../meldingen_core/models.py) are simple dataclasses without an `id` field.
At the same time, our repository ports in [repositories.py](../../meldingen_core/repositories.py) already expose identity-driven operations such as `retrieve(pk: int)`, `delete(pk: int)`, and methods that accept `melding_id`, `answer_id`, `note_id`, `attachment_id`, or `asset_type_id`.

In practice this means the system already depends heavily on identifiers, but those identifiers live outside the models themselves.
As a result, actions and repositories need to pass IDs around separately and then look objects up again before they can do useful work.

Examples in the current core are:

- [melding.py](../../meldingen_core/actions/melding.py) updates a melding via `pk`, while also handling related values such as `source_id` and `label_ids`.
- [melding.py](../../meldingen_core/actions/melding.py) and [note.py](../../meldingen_core/actions/note.py) use combinations such as `melding_id`, `answer_id`, `note_id`, and `asset_id` to find or mutate related records.
- [attachment.py](../../meldingen_core/actions/attachment.py) uses `melding_id` and `attachment_id` together for lookup and deletion flows.
- [managers.py](../../meldingen_core/managers.py) introduces a `RelationshipManager` to smooth over relationship handling differences between the core and the implementation.

The `RelationshipManager` solves a real problem, but it is also a good example of the extra indirection we accept when our core models do not carry stable identifiers themselves.
A helper like this may still be useful for adapter-specific relationship handling, but it should not also have to compensate for missing model identity.

Using IDs on the model dataclasses makes the core easier to work with.
The calling code can pass around a model and still know which stored object it refers to.
Repositories, actions, and adapters can coordinate using the same identifier instead of maintaining separate ID parameters, object references, and helper abstractions.

We therefore decide that core model dataclasses that are persisted and retrieved through repository ports should define an `id` field.

We also prefer repository interfaces to use explicit names such as `melding_id` or `attachment_id` instead of generic `pk` where possible.

### Consequences
- Makes it easier to fetch, update, delete, and relate models across the core and implementation.
- Reduces the need to pass raw IDs separately from the model object in actions and service code.
- Makes repository interfaces and action signatures easier to understand.
- Reduces workaround-style abstractions and adapter-specific handling when working with relationships.

### Alternatives Considered

- Keep IDs only in repository method parameters and not on the models. This was rejected because the code already depends on identifiers heavily, so this only spreads identity concerns across method signatures instead of keeping them on the models.
- Rely only on object references and helper abstractions such as `RelationshipManager`. This was rejected because it makes the core harder to align with implementations that load related objects lazily or operate through repository lookups.
- Use only alternative model-specific identifiers instead of a shared `id` field. This was rejected because many current operations already rely on a simple internal identifier pattern.

### References
- [models.py](../../meldingen_core/models.py)
- [repositories.py](../../meldingen_core/repositories.py)
- [melding.py](../../meldingen_core/actions/melding.py)
- [attachment.py](../../meldingen_core/actions/attachment.py)
- [note.py](../../meldingen_core/actions/note.py)
- [managers.py](../../meldingen_core/managers.py)
